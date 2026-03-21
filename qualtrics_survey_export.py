"""
Qualtrics Survey Export
=======================
Exports survey response data from the Qualtrics API, processes the results
(date formatting, column selection), and saves to a local CSV. Optionally
emails the file to a distribution list.

Uses the Qualtrics v3 Response Export API with polling for completion.
Supports proxy configuration for corporate networks.

Environment Variables Required:
    QUALTRICS_API_TOKEN  - Qualtrics API token
    QUALTRICS_SURVEY_ID  - Survey ID (format: SV_xxxxxxxxxx)
    QUALTRICS_DATACENTER - Qualtrics data center / org ID
    QUALTRICS_FORMAT     - Export format: csv, tsv, or spss (default: csv)
    PROXY_HTTP           - HTTP proxy URL (optional, e.g. http://proxy:8080)
    PROXY_HTTPS          - HTTPS proxy URL (optional)
    OUTPUT_DIR           - Directory to save exported CSV
    OUTPUT_PREFIX        - Filename prefix (default: survey_export)
    SMTP_HOST            - SMTP server hostname
    SMTP_PORT            - SMTP port (default 25)
    EMAIL_SENDER         - Sender email address
    EMAIL_RECIPIENTS     - Comma-separated recipient emails
    COLUMNS_TO_KEEP      - JSON list of column names to keep (optional; keeps all if not set)
    SKIP_ROWS            - Comma-separated row indices to skip on CSV read (e.g. "0,2")

Usage:
    python qualtrics_survey_export.py
"""

import sys
import os
import io
import re
import json
import zipfile
import requests
import pandas as pd
import numpy as np
from datetime import date
from email_notification import send_email


def export_survey(api_token, survey_id, data_center, file_format,
                  use_labels=True, proxies=None):
    """
    Export survey responses from Qualtrics API.

    Returns the extracted file content as bytes.
    """
    # Validate inputs
    if file_format not in ('csv', 'tsv', 'spss'):
        raise ValueError(f"fileFormat must be csv, tsv, or spss (got '{file_format}')")
    if not re.match(r'^SV_', survey_id):
        raise ValueError(f"surveyId must match ^SV_* (got '{survey_id}')")

    base_url = f"https://{data_center}.az1.qualtrics.com/API/v3/surveys/{survey_id}/export-responses/"
    headers = {
        "content-type": "application/json",
        "x-api-token": api_token,
    }

    # Step 1: Create export
    payload = json.dumps({'format': file_format, 'useLabels': use_labels})
    response = requests.post(base_url, data=payload, headers=headers, proxies=proxies)
    response.raise_for_status()
    progress_id = response.json()["result"]["progressId"]
    print(f'Export initiated (progressId: {progress_id})')

    # Step 2: Poll for completion
    status = "inProgress"
    while status not in ("complete", "failed"):
        check_url = base_url + progress_id
        check_response = requests.get(check_url, headers=headers, proxies=proxies)
        check_response.raise_for_status()
        result = check_response.json()["result"]
        pct = result["percentComplete"]
        status = result["status"]
        print(f'  Progress: {pct}% ({status})')

    if status == "failed":
        raise RuntimeError("Qualtrics export failed")

    file_id = check_response.json()["result"]["fileId"]

    # Step 3: Download file
    download_url = base_url + file_id + '/file'
    download = requests.get(download_url, headers=headers, proxies=proxies, stream=True)
    download.raise_for_status()

    # Step 4: Extract from zip
    zf = zipfile.ZipFile(io.BytesIO(download.content))
    filenames = zf.namelist()
    print(f'Extracted files: {filenames}')

    return zf, filenames


def main():
    api_token = os.environ['QUALTRICS_API_TOKEN']
    survey_id = os.environ['QUALTRICS_SURVEY_ID']
    data_center = os.environ['QUALTRICS_DATACENTER']
    file_format = os.environ.get('QUALTRICS_FORMAT', 'csv')

    output_dir = os.environ.get('OUTPUT_DIR', '.')
    output_prefix = os.environ.get('OUTPUT_PREFIX', 'survey_export')
    email_sender = os.environ.get('EMAIL_SENDER', 'noreply@example.com')
    email_recipients = os.environ.get('EMAIL_RECIPIENTS', '').split(',')

    # Optional proxy config
    proxies = None
    if os.environ.get('PROXY_HTTP') or os.environ.get('PROXY_HTTPS'):
        proxies = {
            'http': os.environ.get('PROXY_HTTP', ''),
            'https': os.environ.get('PROXY_HTTPS', ''),
        }

    # Optional column filtering
    columns_json = os.environ.get('COLUMNS_TO_KEEP', '')
    columns_to_keep = json.loads(columns_json) if columns_json else None

    # Optional row skipping
    skip_rows_str = os.environ.get('SKIP_ROWS', '')
    skip_rows = [int(x) for x in skip_rows_str.split(',') if x.strip()] if skip_rows_str else None

    os.makedirs(output_dir, exist_ok=True)

    # ---- Export survey ----
    print('Starting Qualtrics survey export...')
    zf, filenames = export_survey(api_token, survey_id, data_center, file_format,
                                  proxies=proxies)

    # Read the first CSV from the zip
    csv_name = [f for f in filenames if f.endswith('.csv')][0]
    with zf.open(csv_name) as f:
        if skip_rows:
            df = pd.read_csv(f, header=0, skiprows=lambda x: x in skip_rows)
        else:
            df = pd.read_csv(f)

    print(f'Loaded {len(df)} rows, {len(df.columns)} columns')

    # Column filtering
    if columns_to_keep:
        available = [c for c in columns_to_keep if c in df.columns]
        df = df[available].copy()
        print(f'Filtered to {len(available)} columns')

    # ---- Date formatting for common date columns ----
    for col in df.columns:
        if 'Launch Date' in col or 'Survey' in col:
            try:
                df[col] = pd.to_datetime(df[col]).dt.strftime('%m/%d/%Y')
            except Exception:
                pass

    # ---- Save output ----
    today_str = date.today().strftime('%m-%Y')
    output_filename = f'{output_prefix}_{today_str}.csv'
    output_path = os.path.join(output_dir, output_filename)
    df.to_csv(output_path, index=False, na_rep='')
    print(f'Saved to: {output_path}')

    # ---- Email notification ----
    if email_recipients and email_recipients[0]:
        subject = f'{today_str} Survey Data Export'
        body = 'Survey data export from Qualtrics is attached to this email.'
        send_email(email_sender, email_recipients, subject, body,
                   attachment_name=output_filename, attachment_path=output_path)
        print('Email sent with attachment.')
    else:
        print('No recipients configured; skipping email.')

    print('Done.')


if __name__ == '__main__':
    main()
