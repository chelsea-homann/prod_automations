"""
Workday-to-Qualtrics Daily Sync
================================
Pulls daily termination and active employee reports from Workday RaaS and
uploads the CSVs to a Qualtrics SFTP server. Runs two sequential jobs:
terminated workers (yesterday's terms) and active employee roster.

Sends email notifications on success or failure for each job.

Environment Variables Required:
    WD_USERNAME          - Workday API username
    WD_PASSWORD          - Workday API password
    WD_TERM_REPORT_URL   - Workday RaaS URL for terminated workers ({start_dt} and {end_dt} placeholders)
    WD_EMPLOYEE_REPORT_URL - Workday RaaS URL for active employee roster (no date params needed)
    SFTP_HOST            - SFTP server hostname
    SFTP_USER            - SFTP username
    SFTP_PASSWORD        - SFTP password
    SFTP_REMOTE_DIR      - Remote SFTP directory
    SMTP_HOST            - SMTP server hostname
    SMTP_PORT            - SMTP port (default 25)
    EMAIL_SENDER         - Sender email address
    EMAIL_RECIPIENTS     - Comma-separated recipient emails

Usage:
    python workday_qualtrics_daily_sync.py
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


def run_sync_job(job_name, report_url, output_filename, wd_username, wd_password,
                 sftp_host, sftp_user, sftp_password, sftp_remote_dir,
                 email_sender, email_recipients):
    """Pull a Workday report, save as CSV, and upload via SFTP."""
    tmp_dir = tempfile.mkdtemp()
    local_path = os.path.join(tmp_dir, output_filename)

    # Pull report
    try:
        print(f'Pulling {job_name} report...')
        df = pull_workday_report(report_url, wd_username, wd_password)
        print(f'{job_name} report pulled: {len(df)} rows')

        df.to_csv(local_path, index=False)
        print('CSV created.')
    except Exception as e:
        print(f'\n{job_name} report pull failed: {e}')
        send_email(email_sender, email_recipients,
                   f'{job_name} Job Failed',
                   f'{job_name} daily sync failed during report pull:\n{e}')
        return False

    # SFTP upload
    try:
        print(f'Beginning {job_name} SFTP transfer...')
        sftp_upload(sftp_host, sftp_user, sftp_password,
                    sftp_remote_dir, local_path, output_filename)
        print(f'{job_name} SFTP transfer complete.')
    except Exception as e:
        print(f'\n{job_name} SFTP transfer failed: {e}')
        send_email(email_sender, email_recipients,
                   f'{job_name} Job Failed',
                   f'{job_name} daily sync failed during SFTP transfer:\n{e}',
                   attachment_name=output_filename, attachment_path=local_path)
        return False

    # Cleanup
    os.remove(local_path)
    return True


def main():
    # ---- Configuration ----
    wd_username = os.environ['WD_USERNAME']
    wd_password = os.environ['WD_PASSWORD']
    term_report_url = os.environ['WD_TERM_REPORT_URL']
    employee_report_url = os.environ['WD_EMPLOYEE_REPORT_URL']

    sftp_host = os.environ['SFTP_HOST']
    sftp_user = os.environ['SFTP_USER']
    sftp_password = os.environ['SFTP_PASSWORD']
    sftp_remote_dir = os.environ.get('SFTP_REMOTE_DIR', '/Home/account/Out/')

    email_sender = os.environ.get('EMAIL_SENDER', 'noreply@example.com')
    email_recipients = os.environ.get('EMAIL_RECIPIENTS', '').split(',')

    # Date range for termination report (yesterday to today)
    start_dt = (date.today() - timedelta(1)).strftime('%Y-%m-%d')
    end_dt = date.today().strftime('%Y-%m-%d')

    # Insert dates into term report URL
    term_url = term_report_url.format(start_dt=start_dt, end_dt=end_dt)

    shared_args = dict(
        wd_username=wd_username, wd_password=wd_password,
        sftp_host=sftp_host, sftp_user=sftp_user,
        sftp_password=sftp_password, sftp_remote_dir=sftp_remote_dir,
        email_sender=email_sender, email_recipients=email_recipients
    )

    # ---- Job 1: Terminated Workers ----
    term_ok = run_sync_job(
        job_name='Terminated Workers',
        report_url=term_url,
        output_filename='term_df.csv',
        **shared_args
    )

    # ---- Job 2: Active Employees ----
    emp_ok = run_sync_job(
        job_name='Active Employees',
        report_url=employee_report_url,
        output_filename='employee_df.csv',
        **shared_args
    )

    # ---- Send summary notification ----
    if term_ok and emp_ok:
        send_email(email_sender, email_recipients,
                   'Daily Workday-Qualtrics Sync Completed',
                   'Both termination and employee sync jobs completed successfully.')
        print('All jobs complete. Notification sent.')
    else:
        failed = []
        if not term_ok:
            failed.append('Terminated Workers')
        if not emp_ok:
            failed.append('Active Employees')
        print(f'Some jobs failed: {", ".join(failed)}')
        sys.exit(1)


if __name__ == '__main__':
    main()
