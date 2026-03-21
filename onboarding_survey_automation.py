"""
Onboarding Survey Automation
=============================
Pulls Qualtrics employee roster from Workday, filters employees into
time-based onboarding cohorts (Day 1, Week 1, Month 1, Month 3, Month 6,
Year 1), and uploads cohort CSVs to a Qualtrics SFTP server.

Day 1 files are generated on Mondays; all other cohorts on Fridays.
Sends email notifications on success or failure.

Environment Variables Required:
    WD_USERNAME             - Workday API username
    WD_PASSWORD             - Workday API password
    WD_QUALTRICS_REPORT_URL - Workday RaaS URL for Qualtrics employee roster
    SFTP_HOST               - SFTP server hostname
    SFTP_USER               - SFTP username
    SFTP_PASSWORD           - SFTP password
    SFTP_REMOTE_DIR         - Remote SFTP directory
    OUTPUT_DIR              - Local temp directory for CSVs (default: system temp)
    SMTP_HOST               - SMTP server hostname
    SMTP_PORT               - SMTP port (default 25)
    EMAIL_SENDER            - Sender email address
    EMAIL_RECIPIENTS        - Comma-separated recipient emails

Usage:
    python onboarding_survey_automation.py
"""

import sys
import os
import io
import tempfile
import requests
import pandas as pd
import paramiko
from datetime import date, timedelta, datetime
import dateutil.relativedelta
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
    qualtrics_report_url = os.environ['WD_QUALTRICS_REPORT_URL']

    sftp_host = os.environ['SFTP_HOST']
    sftp_user = os.environ['SFTP_USER']
    sftp_password = os.environ['SFTP_PASSWORD']
    sftp_remote_dir = os.environ.get('SFTP_REMOTE_DIR', '/Home/account/Out/')

    output_dir = os.environ.get('OUTPUT_DIR', tempfile.mkdtemp())
    email_sender = os.environ.get('EMAIL_SENDER', 'noreply@example.com')
    email_recipients = os.environ.get('EMAIL_RECIPIENTS', '').split(',')

    subject = 'Onboarding Survey Job Completed'
    body = 'Onboarding survey automation completed successfully.'

    today = date.today()
    today_dt = datetime.strptime(today.strftime('%Y-%m-%d'), '%Y-%m-%d')

    # ---- Step 1: Pull employee roster ----
    try:
        print('Pulling Qualtrics employee roster...')
        qual_df = pull_workday_report(qualtrics_report_url, wd_username, wd_password)
        print(f'Roster pulled: {len(qual_df)} rows')
    except Exception as e:
        print(f'\nWorkday report pull failed: {e}')
        send_email(email_sender, email_recipients, 'Onboarding Job Failed',
                   f'Onboarding survey automation failed:\n{e}')
        sys.exit(1)

    # ---- Step 2: Create cohort CSVs ----
    files_to_upload = []

    try:
        if today.strftime('%A') == 'Monday':
            # Day 1 cohort: employees hired today
            day1_df = qual_df[qual_df['Hire_Date'] == today.strftime('%Y-%m-%d')]
            day1_df = day1_df.copy()
            day1_df['Day1_Launch_Date'] = today.strftime('%m-%d-%Y')
            filename = 'DAY1_Onboarding.csv'
            filepath = os.path.join(output_dir, filename)
            day1_df.to_csv(filepath, index=False)
            files_to_upload.append((filepath, filename))
            print(f'Day 1 cohort: {len(day1_df)} employees')
        else:
            # Weekly cohorts: Week 1, Month 1, Month 3, Month 6, Year 1
            cohorts = {
                'WEEK1': (today_dt - timedelta(4), today_dt, 'Week1_Launch_Date'),
                'MONTH1': (today_dt - dateutil.relativedelta.relativedelta(months=1) - timedelta(4),
                           today_dt - dateutil.relativedelta.relativedelta(months=1),
                           'Month1_Launch_Date'),
                'MONTH3': (today_dt - dateutil.relativedelta.relativedelta(months=3) - timedelta(4),
                           today_dt - dateutil.relativedelta.relativedelta(months=3),
                           'Month3_Launch_Date'),
                'MONTH6': (today_dt - dateutil.relativedelta.relativedelta(months=6) - timedelta(4),
                           today_dt - dateutil.relativedelta.relativedelta(months=6),
                           'Month6_Launch_Date'),
                'YEAR1': (today_dt - dateutil.relativedelta.relativedelta(months=12) - timedelta(4),
                          today_dt - dateutil.relativedelta.relativedelta(months=12),
                          'Year1_Launch_Date'),
            }

            for label, (range_start, range_end, launch_col) in cohorts.items():
                cohort_df = qual_df[
                    (qual_df['Hire_Date'] >= range_start.strftime('%Y-%m-%d')) &
                    (qual_df['Hire_Date'] <= range_end.strftime('%Y-%m-%d'))
                ].copy()
                cohort_df[launch_col] = range_end.strftime('%m-%d-%Y')
                filename = f'{label}_Onboarding.csv'
                filepath = os.path.join(output_dir, filename)
                cohort_df.to_csv(filepath, index=False)
                files_to_upload.append((filepath, filename))
                print(f'{label} cohort: {len(cohort_df)} employees')

    except Exception as e:
        print(f'\nCSV creation failed: {e}')
        send_email(email_sender, email_recipients, 'Onboarding Job Failed',
                   f'Onboarding survey CSV creation failed:\n{e}')
        sys.exit(1)

    # ---- Step 3: SFTP upload ----
    try:
        print('Beginning SFTP transfers...')
        for filepath, filename in files_to_upload:
            sftp_upload(sftp_host, sftp_user, sftp_password,
                        sftp_remote_dir, filepath, filename)
            print(f'  Uploaded: {filename}')
        print('All SFTP transfers complete.')
    except Exception as e:
        print(f'\nSFTP transfer failed: {e}')
        send_email(email_sender, email_recipients, 'Onboarding Job Failed',
                   f'Onboarding survey SFTP transfer failed:\n{e}')
        sys.exit(1)

    # ---- Step 4: Cleanup and notify ----
    for filepath, _ in files_to_upload:
        if os.path.exists(filepath):
            os.remove(filepath)
    send_email(email_sender, email_recipients, subject, body)
    print('Notification email sent. Done.')


if __name__ == '__main__':
    main()
