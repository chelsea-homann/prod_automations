"""
Leave Survey Automation
=======================
Pulls leave-return and Qualtrics employee data from Workday RaaS reports,
merges them on employee ID, and uploads the resulting participant list to a
Qualtrics SFTP server. Sends email notifications on success or failure.

Environment Variables Required:
    WD_USERNAME             - Workday API username
    WD_PASSWORD             - Workday API password
    WD_LEAVE_REPORT_URL     - Workday RaaS URL for leave-return data ({start_dt} and {end_dt} placeholders)
    WD_QUALTRICS_REPORT_URL - Workday RaaS URL for Qualtrics employee roster
    SFTP_HOST               - SFTP server hostname
    SFTP_USER               - SFTP username
    SFTP_PASSWORD           - SFTP password
    SFTP_REMOTE_DIR         - Remote SFTP directory
    OUTPUT_FILENAME         - Output CSV filename (default: LEAVE.csv)
    SMTP_HOST               - SMTP server hostname
    SMTP_PORT               - SMTP port (default 25)
    EMAIL_SENDER            - Sender email address
    EMAIL_RECIPIENTS        - Comma-separated recipient emails
    LOOKBACK_DAYS           - Days to look back for leave returns (default 6)

Usage:
    python leave_survey_automation.py
"""

import sys
import os
import io
import tempfile
import requests
import pandas as pd
import paramiko
from datetime import date, timedelta
from email_notification import send_email


def pull_workday_report(url, username, password):
    """Pull a CSV report from Workday RaaS and return as a DataFrame."""
    with requests.Session() as session:
        response = session.get(url, auth=(username, password))
        response.raise_for_status()
        decoded = response.content.decode('utf-8')
    return pd.read_csv(io.StringIO(decoded))


def sftp_upload(hostname, username, password, remote_dir, local_path, remote_filename):
    """Upload a local file to an SFTP server."""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, username=username, password=password)
    sftp = ssh.open_sftp()
    sftp.chdir(remote_dir)

    remote_path = remote_dir.rstrip('/') + '/' + remote_filename
    try:
        sftp.remove(remote_path)
    except FileNotFoundError:
        pass
    sftp.put(local_path, remote_path)

    sftp.close()
    ssh.close()


def main():
    # ---- Configuration ----
    wd_username = os.environ['WD_USERNAME']
    wd_password = os.environ['WD_PASSWORD']
    leave_report_url = os.environ['WD_LEAVE_REPORT_URL']
    qualtrics_report_url = os.environ['WD_QUALTRICS_REPORT_URL']

    sftp_host = os.environ['SFTP_HOST']
    sftp_user = os.environ['SFTP_USER']
    sftp_password = os.environ['SFTP_PASSWORD']
    sftp_remote_dir = os.environ.get('SFTP_REMOTE_DIR', '/Home/account/Out/')

    output_filename = os.environ.get('OUTPUT_FILENAME', 'LEAVE.csv')
    email_sender = os.environ.get('EMAIL_SENDER', 'noreply@example.com')
    email_recipients = os.environ.get('EMAIL_RECIPIENTS', '').split(',')

    lookback = int(os.environ.get('LOOKBACK_DAYS', '6'))

    # Date range with timezone offset formatting
    start_dt = (date.today() - timedelta(lookback)).strftime('%Y-%m-%d') + '-08'
    end_dt = date.today().strftime('%Y-%m-%d') + '-07'

    subject = 'Leave Survey Job Completed'
    body = 'Leave survey automation completed successfully.'

    # ---- Step 1: Pull and merge reports ----
    try:
        print('Pulling leave-return report...')
        leave_url = leave_report_url.format(start_dt=start_dt, end_dt=end_dt)
        leave_df = pull_workday_report(leave_url, wd_username, wd_password)
        print(f'Leave report pulled: {len(leave_df)} rows')

        print('Pulling Qualtrics employee roster...')
        qual_df = pull_workday_report(qualtrics_report_url, wd_username, wd_password)
        print(f'Qualtrics roster pulled: {len(qual_df)} rows')

        # Merge on employee ID
        merged_df = qual_df.merge(
            leave_df[['Unique_Identifier', 'First_Day_Back']],
            left_on='Employee_ID',
            right_on='Unique_Identifier'
        )
        deduped = merged_df.drop_duplicates()
        deduped['Leave_Launch_Date'] = date.today().strftime('%m-%d-%Y')

        # Write to temp CSV
        tmp_dir = tempfile.mkdtemp()
        local_path = os.path.join(tmp_dir, output_filename)
        deduped.to_csv(local_path, index=False)
        print(f'CSV created: {len(deduped)} merged rows')

    except Exception as e:
        print(f'\nReport pull/merge failed: {e}')
        send_email(email_sender, email_recipients, 'Leave Survey Job Failed',
                   f'Leave survey automation failed:\n{e}')
        sys.exit(1)

    # ---- Step 2: SFTP upload ----
    try:
        print('Beginning SFTP transfer...')
        sftp_upload(sftp_host, sftp_user, sftp_password,
                    sftp_remote_dir, local_path, output_filename)
        print('SFTP transfer complete.')
    except Exception as e:
        print(f'\nSFTP transfer failed: {e}')
        send_email(email_sender, email_recipients, 'Leave Survey Job Failed',
                   f'Leave survey SFTP transfer failed:\n{e}',
                   attachment_name=output_filename, attachment_path=local_path)
        sys.exit(1)

    # ---- Step 3: Cleanup and notify ----
    os.remove(local_path)
    send_email(email_sender, email_recipients, subject, body)
    print('Notification email sent. Done.')


if __name__ == '__main__':
    main()
