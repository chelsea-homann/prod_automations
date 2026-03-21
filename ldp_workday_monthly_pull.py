"""
LDP Workday Monthly Data Pull
==============================
Pulls multiple workforce reports from Workday RaaS (hires, job changes,
terminations, candidate pipeline data) and saves them as CSVs to a shared
drive or local directory. Designed for monthly leadership development program
(LDP) reporting and scorecards.

Each report URL is configurable via environment variables. Column names are
standardized from Workday underscore format to human-readable format.

Environment Variables Required:
    WD_USERNAME          - Workday API username
    WD_PASSWORD          - Workday API password
    WD_HIRE_REPORT_URL   - Workday RaaS URL for hires report
    WD_JOBCHANGE_REPORT_URL - Workday RaaS URL for job changes ({start_dt} and {end_dt} placeholders)
    WD_TERM_REPORT_URL   - Workday RaaS URL for terminations ({start_dt} and {end_dt} placeholders)
    WD_CANDIDATE_URLS    - JSON list of candidate report configs:
                           [{"name": "Program A", "url": "...", "output": "candidates_a.csv"}, ...]
    OUTPUT_DIR           - Directory to write CSVs (e.g. a shared drive path)
    SMTP_HOST            - SMTP server hostname
    SMTP_PORT            - SMTP port (default 25)
    EMAIL_SENDER         - Sender email address
    EMAIL_RECIPIENTS     - Comma-separated recipient emails

Usage:
    python ldp_workday_monthly_pull.py
"""

import os
import io
import json
import requests
import pandas as pd
from datetime import date
from email_notification import send_email


def pull_workday_report(url, username, password):
    """Pull a CSV report from Workday RaaS and return as a DataFrame."""
    with requests.Session() as session:
        response = session.get(url, auth=(username, password))
        response.raise_for_status()
        decoded = response.content.decode('utf-8')
    return pd.read_csv(io.StringIO(decoded))


# ---- Column rename mappings ----

HIRE_RENAMES = {}  # Customize per your Workday report field names

JOBCHANGE_RENAMES = {
    'Job_Change_Date': 'Job Change Date',
    'Job_Change_Reason': 'Job Change Reason',
    'Job_Change_Type': 'Job Change Type',
    'Years_in_Job_Profile_Before_Change': 'Years in Job Profile Before Change',
    'Time_in_Job_Profile_Before_Change': 'Time in Job Profile Before Change',
    'Time_in_Position_Before_Change': 'Time in Position Before Change',
    'Job_Code_-_From': 'Job Code - From',
    'Job_Code_-_To': 'Job Code - To',
    'Job_Profile_-_From': 'Job Profile - From',
    'Job_Profile_-_To': 'Job Profile - To',
    'Grade_-_From': 'Grade - From',
    'Grade_-_To': 'Grade - To',
    'Job_Level_From': 'Job Level From',
    'Job_Level_To': 'Job Level To',
    'Is_Manager_From': 'Is Manager - From',
    'Is_Manager_To': 'Is Manager - To',
    'Base_Pay_-_From': 'Base Pay - From',
    'Base_Pay_-_To': 'Base Pay - To',
    'Sched_Hours_-_From': 'Sched Hours - From',
    'Sched_Hours_-_To': 'Sched Hours - To',
    'Manager_-_From': 'Manager - From',
    'Manager_-_To': 'Manager - To',
    'Supervisory_Org_-_From': 'Supervisory Org - From',
    'Supervisory_Org_-_To': 'Supervisory Org - To',
    'Location_-_From': 'Location - From',
    'Location_-_To': 'Location - To',
    'Cost_Center_-_From': 'Cost Center - From',
    'Cost_Center_-_To': 'Cost Center - To',
    'Business_Area_-_From': 'Business Area - From',
    'Business_Area_-_To': 'Business Area - To',
    'Profile_Area_-_From': 'Profile Area - From',
    'Profile_Area_-_To': 'Profile Area - To',
    'Department_-_From': 'Department - From',
    'Department_-_To': 'Department - To',
    'Consolidated_Area_-_From': 'Consolidated Area - From',
    'Consolidated_Area_-_To': 'Consolidated Area - To',
    'Area_-_To': 'Area - To',
    'Sub_Area_-_To': 'Sub Area - To',
    'Potential_Rating': 'Potential Rating',
    'Rating_Status': 'Rating Status',
    'Last_Rating': 'Last Rating',
}

TERMINATION_RENAMES = {
    'primaryWorkEmail': 'Email - Primary Work',
    'Hire_Date': 'Hire Date',
    'Term_Date': 'Term Date',
    'Terminated__based_on_report_date_': 'Terminated Based on Report Date',
    'CF_Worker_Latest_Term_Date': 'CF Worker Latest Term Date',
    'Is_Term_90_Day_Hire': 'Is Term 90 Day Hire',
    'Term_Reason': 'Term Reason',
    'termination_primary': 'Termination Primary',
    'Secondary_Term_Reason': 'Secondary Term Reason',
    'Term_Category': 'Term Category',
    'Employee_has_had_Performance_Improvement_or_Reprimand_Plan': 'Employee had Performance Improvement or Reprimand Plan',
    'Eligible_for_Rehire': 'Eligible for Rehire',
    'Job_Profile': 'Job Profile',
    'Time_in_Job_Profile': 'Time in Job Profile',
    'Job_Code': 'Job Code',
    'Job_Level': 'Job Level',
    'Annual_Salary': 'Annual Salary',
    'Worker_Type': 'Worker Type',
    'Time_Type': 'Time Type',
    'Employee_Type': 'Employee Type',
    'Scheduled_Hours': 'Scheduled Hours',
    'Exempt_': 'Exempt',
    'Job_Exempt_Applies': 'Job Exempt Applies',
    'Job_Family': 'Job Family',
    'Job_Family_Group': 'Job Family Group',
    'Leadership_Role': 'Leadership Role',
    'location': 'Location',
    'Supervisory_Organization': 'Supervisory Organization',
    'Tenure_Category_-_Position': 'Tenure Category - Position',
    'Years_of_Service': 'Years of Service',
    'Race_Ethnicity': 'Race Ethnicity',
    'Hispanic_or_Latino': 'Hispanic or Latino',
    'Age_Group': 'Age Group',
    'Cost_Center': 'Cost Center',
    'Email_-_Work': 'Email - Work',
    'Profile_Area_Division': 'Profile Area Division',
    'Consolidated_Area': 'Consolidated Area',
    'Potential_-_Completed_Rating': 'Potential - Completed Rating',
    'Last_Update_-_Potential': 'Last Update - Potential',
    'effectiveDate': 'Effective Date',
    'staffingPlanTitle': 'Staffing Plan Title',
    'fieldOfficeProfileIndicator': 'Field Office Profile Indicator',
}

CANDIDATE_RENAMES = {
    'Candidate_ID': 'Candidate ID',
    'Last_Recruiting_Stage': 'Last Recruiting Stage',
    'Disposition_Reason': 'Disposition Reason',
    'Candidate_Disposition_Reason': 'Candidate Disposition Reason',
    'Internal_': 'Internal',
    'App_Created': 'App Created',
    'Employee_ID': 'Employee ID',
    'termination_date': 'Termination Date',
    'Hire_Date': 'Hire Date',
    'Do_Not_Hire': 'Do Not Hire',
    'CF_Calc_Candidate_Stage': 'CF Calc Candidate Stage',
    'App_Source': 'App Source',
    'Recruiter_s_Department': 'Recruiters Department',
    'CF_Job_Requisition_Business_Area_SI': 'Business Area',
    'Req_Location': 'Req Location',
    'Hiring_Mgr': 'Hiring Mgr',
    'Job_Profile': 'Job Profile',
    'Compensation_Grade': 'Compensation Grade',
    'Job_Level': 'Job Level',
    'Req_Created': 'Req Created',
    'CF_Job_App_Req_Cmplt_Date': 'App Created',
    'CF_Job_App_Offer_Cmplt_Date': 'Offer Completed',
}


def main():
    wd_username = os.environ['WD_USERNAME']
    wd_password = os.environ['WD_PASSWORD']
    output_dir = os.environ['OUTPUT_DIR']
    email_sender = os.environ.get('EMAIL_SENDER', 'noreply@example.com')
    email_recipients = os.environ.get('EMAIL_RECIPIENTS', '').split(',')

    today = date.today().strftime('%Y-%m-%d')

    os.makedirs(output_dir, exist_ok=True)

    # ---- 1. Hires Report ----
    if os.environ.get('WD_HIRE_REPORT_URL'):
        print('Pulling hires report...')
        hire_df = pull_workday_report(os.environ['WD_HIRE_REPORT_URL'], wd_username, wd_password)
        if HIRE_RENAMES:
            hire_df = hire_df.rename(columns=HIRE_RENAMES)
        hire_path = os.path.join(output_dir, 'hire_report.csv')
        hire_df.to_csv(hire_path, index=False)
        print(f'Hires report saved: {len(hire_df)} rows')

    # ---- 2. Job Changes Report ----
    if os.environ.get('WD_JOBCHANGE_REPORT_URL'):
        print('Pulling job changes report...')
        jc_url = os.environ['WD_JOBCHANGE_REPORT_URL'].format(start_dt='2014-01-01', end_dt=today)
        jc_df = pull_workday_report(jc_url, wd_username, wd_password)
        existing_renames = {k: v for k, v in JOBCHANGE_RENAMES.items() if k in jc_df.columns}
        jc_df = jc_df.rename(columns=existing_renames)
        jc_path = os.path.join(output_dir, 'job_changes.csv')
        jc_df.to_csv(jc_path, index=False)
        print(f'Job changes report saved: {len(jc_df)} rows')

    # ---- 3. Terminations Report ----
    if os.environ.get('WD_TERM_REPORT_URL'):
        print('Pulling terminations report...')
        term_url = os.environ['WD_TERM_REPORT_URL'].format(start_dt='2000-01-01', end_dt=today)
        term_df = pull_workday_report(term_url, wd_username, wd_password)
        existing_renames = {k: v for k, v in TERMINATION_RENAMES.items() if k in term_df.columns}
        term_df = term_df.rename(columns=existing_renames)
        term_path = os.path.join(output_dir, 'term_worker_details.csv')
        term_df.to_csv(term_path, index=False)
        print(f'Terminations report saved: {len(term_df)} rows')

    # ---- 4. Candidate Reports ----
    candidate_configs = os.environ.get('WD_CANDIDATE_URLS', '[]')
    for config in json.loads(candidate_configs):
        name = config['name']
        url = config['url']
        output_file = config['output']
        print(f'Pulling {name} candidates report...')
        cand_df = pull_workday_report(url, wd_username, wd_password)
        existing_renames = {k: v for k, v in CANDIDATE_RENAMES.items() if k in cand_df.columns}
        cand_df = cand_df.rename(columns=existing_renames)
        cand_path = os.path.join(output_dir, output_file)
        cand_df.to_csv(cand_path, index=False)
        print(f'{name} candidates saved: {len(cand_df)} rows')

    # ---- Notify ----
    send_email(email_sender, email_recipients,
               'LDP Monthly Pull Completed',
               'All LDP Workday data pulls completed successfully.')
    print('All reports complete. Notification sent.')


if __name__ == '__main__':
    main()
