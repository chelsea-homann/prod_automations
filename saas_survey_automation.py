"""
SAAS Survey Automation
======================
Pulls HRIS report, transforms data for SAAS-platform ingestion, and uploads the CSV to a SAAS SFTP
server. Sends an email notification on success or failure.

Supports both US and UK (or other regional) SAAS survey variants via the
WD_REPORT_URL environment variable.

Environment Variables Required:
    WD_USERNAME      - HRIS API username
    WD_PASSWORD      - HRIS API password
    WD_REPORT_URL    - Full HRIS RaaS custom report URL (use {start_dt} and {end_dt} placeholders)
    SFTP_HOST        - SFTP server hostname
    SFTP_USER        - SFTP username
    SFTP_PASSWORD    - SFTP password
    SFTP_REMOTE_DIR  - Remote SFTP directory (e.g. /Home/account/Out/)
    OUTPUT_FILENAME  - Name of the output CSV (e.g. SAAS_survey_participants.csv)
    SMTP_HOST        - SMTP server for email notifications
    SMTP_PORT        - SMTP port (default 25)
    EMAIL_SENDER     - Sender email address
    EMAIL_RECIPIENTS - Comma-separated list of recipient emails
    LOOKBACK_DAYS    - Number of days to look back for terminations (default 4)
    LOOKFORWARD_DAYS - Number of days to look forward (default 0; set >0 for UK variant)

Usage:
    python SAAS_survey_automation.py
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


def build_report_url(base_url, start_dt, end_dt):
    """Insert date parameters into the HRIS report URL template."""
    return base_url.format(start_dt=start_dt, end_dt=end_dt)


def pull_HRIS_report(url, username, password):
    """Pull a CSV report from HRIS RaaS and return as a DataFrame."""
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
    # ---- Configuration from environment ----
    wd_username = os.environ['WD_USERNAME']
    wd_password = os.environ['WD_PASSWORD']
    report_url = os.environ['WD_REPORT_URL']

    sftp_host = os.environ['SFTP_HOST']
    sftp_user = os.environ['SFTP_USER']
    sftp_password = os.environ['SFTP_PASSWORD']
    sftp_remote_dir = os.environ.get('SFTP_REMOTE_DIR', '/Home/account/Out/')

    output_filename = os.environ.get('OUTPUT_FILENAME', 'SAAS_survey_participants.csv')
    email_sender = os.environ.get('EMAIL_SENDER', 'noreply@example.com')
    email_recipients = os.environ.get('EMAIL_RECIPIENTS', '').split(',')

    lookback = int(os.environ.get('LOOKBACK_DAYS', '4'))
    lookforward = int(os.environ.get('LOOKFORWARD_DAYS', '0'))

    start_dt = (date.today() - timedelta(lookback)).strftime('%Y-%m-%d')
    end_dt = (date.today() + timedelta(lookforward)).strftime('%Y-%m-%d')

    subject = 'SAAS Survey Job Completed'
    body = 'SAAS survey automation completed successfully.'

    # ---- Step 1: Pull report from HRIS ----
    try:
        print('Pulling HRIS report...')
        url = build_report_url(report_url, start_dt, end_dt)
        df = pull_HRIS_report(url, wd_username, wd_password)
        print(f'Report pulled: {len(df)} rows')

        # Add launch date column
        df['SAAS Survey Launch Date'] = date.today().strftime('%m-%d-%Y')

        # Drop original launch date if present
        if 'Survey_Launch_Date' in df.columns:
            df = df.drop(columns=['Survey_Launch_Date'])

        # Rename columns for survey platform
        existing_renames = {k: v for k, v in DEFAULT_COLUMN_RENAMES.items() if k in df.columns}
        df = df.rename(columns=existing_renames)

        # Write to temp CSV
        tmp_dir = tempfile.mkdtemp()
        local_path = os.path.join(tmp_dir, output_filename)
        df.to_csv(local_path, index=False)
        print('CSV created.')

    except Exception as e:
        print(f'\nHRIS report pull failed: {e}')
        send_email(email_sender, email_recipients, 'SAAS Survey Job Failed',
                   f'SAAS survey automation failed during report pull:\n{e}')
        sys.SAAS(1)

    # ---- Step 2: SFTP upload ----
    try:
        print('Beginning SFTP transfer...')
        sftp_upload(sftp_host, sftp_user, sftp_password,
                    sftp_remote_dir, local_path, output_filename)
        print('SFTP transfer complete.')
    except Exception as e:
        print(f'\nSFTP transfer failed: {e}')
        send_email(email_sender, email_recipients, 'SAAS Survey Job Failed',
                   f'SAAS survey automation failed during SFTP transfer:\n{e}',
                   attachment_name=output_filename, attachment_path=local_path)
        sys.SAAS(1)

    # ---- Step 3: Cleanup and notify ----
    os.remove(local_path)
    send_email(email_sender, email_recipients, subject, body)
    print('Notification email sent. Done.')


if __name__ == '__main__':
    main()
