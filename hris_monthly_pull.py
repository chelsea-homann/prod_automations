"""
HRIS Monthly Data Pull
==============================
Pulls multiple workforce reports from HRIS RaaS (hires, job changes,
terminations, candidate pipeline data) and saves them as CSVs to a shared
drive or local directory. Designed for monthly leadership reporting and scorecards.

Each report URL is configurable via environment variables. Column names are
standardized from HRIS underscore format to human-readable format.

Environment Variables Required:
    HRIS_USERNAME          - HRIS API username
    HRIS_PASSWORD          - HRIS API password
    HRIS_HIRE_REPORT_URL   - HRIS RaaS URL for hires report
    HRIS_JOBCHANGE_REPORT_URL - HRIS RaaS URL for job changes ({start_dt} and {end_dt} placeholders)
    HRIS_TERM_REPORT_URL   - HRIS RaaS URL for terminations ({start_dt} and {end_dt} placeholders)
    HRIS_CANDIDATE_URLS    - JSON list of candidate report configs:
                           [{"name": "Program A", "url": "...", "output": "candidates_a.csv"}, ...]
    OUTPUT_DIR           - Directory to write CSVs (e.g. a shared drive path)
    SMTP_HOST            - SMTP server hostname
    SMTP_PORT            - SMTP port (default 25)
    EMAIL_SENDER         - Sender email address
    EMAIL_RECIPIENTS     - Comma-separated recipient emails

Usage:
    python HRIS_monthly_pull.py
"""

import os
import io
import json
import requests
import pandas as pd
from datetime import date
from email_notification import send_email


def pull_HRIS_report(url, username, password):
    """Pull a CSV report from HRIS RaaS and return as a DataFrame."""
    with requests.Session() as session:
        response = session.get(url, auth=(username, password))
        response.raise_for_status()
        decoded = response.content.decode('utf-8')
    return pd.read_csv(io.StringIO(decoded))


def main():
    HRIS_username = os.environ['HRIS_USERNAME']
    HRIS_password = os.environ['HRIS_PASSWORD']
    output_dir = os.environ['OUTPUT_DIR']
    email_sender = os.environ.get('EMAIL_SENDER', 'noreply@example.com')
    email_recipients = os.environ.get('EMAIL_RECIPIENTS', '').split(',')

    today = date.today().strftime('%Y-%m-%d')

    os.makedirs(output_dir, exist_ok=True)

    # ---- 1. Hires Report ----
    if os.environ.get('HRIS_HIRE_REPORT_URL'):
        print('Pulling hires report...')
        hire_df = pull_HRIS_report(os.environ['HRIS_HIRE_REPORT_URL'], HRIS_username, HRIS_password)
        if HIRE_RENAMES:
            hire_df = hire_df.rename(columns=HIRE_RENAMES)
        hire_path = os.path.join(output_dir, 'hire_report.csv')
        hire_df.to_csv(hire_path, index=False)
        print(f'Hires report saved: {len(hire_df)} rows')

    # ---- 2. Job Changes Report ----
    if os.environ.get('HRIS_JOBCHANGE_REPORT_URL'):
        print('Pulling job changes report...')
        jc_url = os.environ['HRIS_JOBCHANGE_REPORT_URL'].format(start_dt='2014-01-01', end_dt=today)
        jc_df = pull_HRIS_report(jc_url, HRIS_username, HRIS_password)
        existing_renames = {k: v for k, v in JOBCHANGE_RENAMES.items() if k in jc_df.columns}
        jc_df = jc_df.rename(columns=existing_renames)
        jc_path = os.path.join(output_dir, 'job_changes.csv')
        jc_df.to_csv(jc_path, index=False)
        print(f'Job changes report saved: {len(jc_df)} rows')

    # ---- 3. Terminations Report ----
    if os.environ.get('HRIS_TERM_REPORT_URL'):
        print('Pulling terminations report...')
        term_url = os.environ['HRIS_TERM_REPORT_URL'].format(start_dt='2000-01-01', end_dt=today)
        term_df = pull_HRIS_report(term_url, HRIS_username, HRIS_password)
        existing_renames = {k: v for k, v in TERMINATION_RENAMES.items() if k in term_df.columns}
        term_df = term_df.rename(columns=existing_renames)
        term_path = os.path.join(output_dir, 'term_worker_details.csv')
        term_df.to_csv(term_path, index=False)
        print(f'Terminations report saved: {len(term_df)} rows')

    # ---- 4. Candidate Reports ----
    candidate_configs = os.environ.get('HRIS_CANDIDATE_URLS', '[]')
    for config in json.loads(candidate_configs):
        name = config['name']
        url = config['url']
        output_file = config['output']
        print(f'Pulling {name} candidates report...')
        cand_df = pull_HRIS_report(url, HRIS_username, HRIS_password)
        existing_renames = {k: v for k, v in CANDIDATE_RENAMES.items() if k in cand_df.columns}
        cand_df = cand_df.rename(columns=existing_renames)
        cand_path = os.path.join(output_dir, output_file)
        cand_df.to_csv(cand_path, index=False)
        print(f'{name} candidates saved: {len(cand_df)} rows')

    # ---- Notify ----
    send_email(email_sender, email_recipients,
               'Monthly Pull Completed',
               'All  HRIS data pulls completed successfully.')
    print('All reports complete. Notification sent.')


if __name__ == '__main__':
    main()
