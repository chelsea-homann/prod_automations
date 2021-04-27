# -*- coding: utf-8 -*-
"""
Created on Wed Apr 21 19:11:41 2021

@author: ddy17
"""

import requests
import pandas as pd
import io
import numpy as np
from io import StringIO
import UnumEmail
import os
from datetime import date, timedelta
pd.set_option("display.max_rows", 100000, "display.max_columns", 100000)

username = os.getenv('WDUSER')
password = os.getenv('WDPASSWORD')

# raas hires
hireend = '2022-12-31'
hirestart = '2000-01-01'

hire = 'https://services1.myworkday.com/ccx/service/customreport2/unum/DKJ05/RaaS_Hires?SupervisoryOrg%21WID=fad8c8a44c4510541494e34161d00311&BPStatus%21WID=b90bc51be01d4ae99b603b02b073714d&BPType%21WID=e6591cf3a39e44f0b01c711957f72e76!26627c6715f84ddba510f25c433aeb2b!bd774409e883445d8a773a92274ece71!08e574a19f6b400fac5dbe71ea854f1d!aaa046227982460f98d5a1ca14f91d2b!1758d7cf019a4c6a827fbba824a2866c!c44ef33941cf425f9d4e27e1403c7670&IncludeSubOrgs=1&EffectiveEnd=2021-12-31-08%3A00&EffectiveStart=2000-01-01-08%3A00&Organization%21WID=fad8c8a44c4510541494e34161d00311&EndDate=2022-12-31-08%3A00&StartDate=2014-01-01-08%3A00&format=csv'
with requests.Session() as s:
    download = s.get(hire, auth=(username, password))
    decoded_content = download.content.decode('utf-8')
    hire = pd.read_csv(io.StringIO(decoded_content))
    hire = hire.set_index('Emplid')
    
hire.to_csv(r'O:\people_analytics\scorecards_kpis\ldp\data_build\hire_report_updated.csv')
print('Hired dataset written to shared drive!')

# job changes
jch_startdate = '2014-01-01'
jch_enddate = (date.today()).strftime('%Y-%m-%d')

jobchanges = 'https://services1.myworkday.com/ccx/service/customreport2/unum/DKJ05/RaaS_Internal_Job_Change_Details?SupervisoryOrgFromOrTo%21WID=fad8c8a44c4510541494e34161d00311&BPStatus%21WID=b90bc51be01d4ae99b603b02b073714d&BPType%21WID=e6591cf3a39e44f0b01c711957f72e76!26627c6715f84ddba510f25c433aeb2b!bd774409e883445d8a773a92274ece71!08e574a19f6b400fac5dbe71ea854f1d!367d55bcf1ff49e4afa95b60c8531771!5598cba0054d439690bca4c2a0079eb9!aaa046227982460f98d5a1ca14f91d2b!1758d7cf019a4c6a827fbba824a2866c!c44ef33941cf425f9d4e27e1403c7670&IncludeSubOrgs=1&ChangeEnd={0}-08%3A00&ChangeStart={1}-08%3A00&Organization%21WID=fad8c8a44c4510541494e34161d00311&format=csv'.format(jch_enddate,jch_startdate)
with requests.Session() as s:
    download = s.get(jobchanges, auth=(username, password))
    decoded_content = download.content.decode('utf-8')
    jobchanges = pd.read_csv(io.StringIO(decoded_content))
    jobchanges = jobchanges.set_index('Emplid') 
    
jobchanges = jobchanges.rename(columns={'Job_Change_Date':'Job Change Date',
 'Job_Change_Reason':'Job Change Reason',
 'Job_Change_Type':'Job Change Type',
 'Years_in_Job_Profile_Before_Change':'Years in Job Profile Before Change',
 'Time_in_Job_Profile_Before_Change':'Time in Job Profile Before Change',
 'Time_in_Position_Before_Change':'Time in Position Before Change',
 'Job_Code_-_From':'Job Code - From',
 'Job_Code_-_To':'Job Code - To',
 'Job_Profile_-_From':'Job Profile - From',
 'Job_Profile_-_To':'Job Profile - To',
 'Grade_-_From': 'Grade - From',
 'Grade_-_To':'Grade - To',
 'Job_Level_From':'Job Level From',
 'Job_Level_To':'Job Level To',
 'Is_Manager_From':'Is Manager - From',
 'Is_Manager_To':'Is Manager - To',                                        
 'Base_Pay_-_From':'Base Pay - From',
 'Base_Pay_-_To':'Base Pay - To',
 'Sched_Hours_-_From':'Sched Hours - From',
 'Sched_Hours_-_To':'Sched Hours - To',
 'Manager_-_From':'Manager - From',
 'Manager_-_To':'Manager - To',
 'Supervisory_Org_-_From':'Supervisory Org - From',
 'Supervisory_Org_-_To':'Supervisory Org - To',
 'Location_-_From':'Location - From',
 'Location_-_To':'Location - To',
 'Cost_Center_-_From':'Cost Center - From',
 'Cost_Center_-_To':'Cost Center - To',
 'Business_Area_-_From':'Business Area - From',
 'Business_Area_-_To':'Business Area - To',
 'Profile_Area_-_From':'Profile Area - From',
 'Profile_Area_-_To':'Profile Area - To',
 'Department_-_From':'Department - From',
 'Department_-_To':'Department - To',
 'Consolidated_Area_-_From':'Consolidated Area - From',
 'Consolidated_Area_-_To':'Consolidated Area - To',
 'Area_-_To':'Area - To',
 'Sub_Area_-_To':'Sub Area - To',
 'Potential_Rating':'Potential Rating',
 'Rating_Status':'Rating Status',
 'Last_Rating':'Last Rating'})

jobchanges.to_csv(r'O:\people_analytics\scorecards_kpis\ldp\data_build\job_changes_2017_now.csv')
print('Job Changes dataset written to shared drive!')

# term report
termstart = '2000-01-01'
termend = (date.today()).strftime('%Y-%m-%d')

terminations = 'https://services1.myworkday.com/ccx/service/customreport2/unum/DKJ05/RaaS_Terminated_Worker_Details__2014__?Term_Start_Date={0}-08%3A00&Term_End_Date={1}-08%3A00&Supervisory_Organization%21WID=fad8c8a44c4510541494e34161d00311&Employee_Type%21WID=c4ed1a5d88a41050a1f47a5de48823db!c4ed1a5d88a41050a1f47c52de8823dc&format=csv'.format(termstart,termend)
with requests.Session() as s:
    download = s.get(terminations, auth=(username, password))
    decoded_content = download.content.decode('utf-8')
    terminations = pd.read_csv(io.StringIO(decoded_content))
    terminations = terminations.set_index('Employee_ID') 
    
terminations = terminations.rename(columns={'Employee_ID':'Employee ID',
  'primaryWorkEmail':'Email - Primary Work',
 'Hire_Date':'Hire Date',
 'Term_Date':'Term Date',
 'Terminated__based_on_report_date_':'Terminated Based on Report Date',
 'CF_Worker_Latest_Term_Date':'CF Worker Lastest Term Date',
 'Is_Term_90_Day_Hire':'Is Term 90 Day Hire',
 'Term_Reason':"Term Reason",
 'termination_primary':'Termination Primary',
 'Secondary_Term_Reason':'Secondary Term Reason',
 'Term_Category':'Term Category',
 'Employee_has_had_Performance_Improvement_or_Reprimand_Plan':'Employee had has Performance Improvement or Reprimand Plan',
 'Eligible_for_Rehire':'Eligible for Rehire',
 'Job_Profile':'Job Profile',
 'Time_in_Job_Profile':'Time in Job Profile',
 'Job_Code':'Job Code',
 'Job_Level':'Job Level',
 'Annual_Salary':'Annual Salary',
 'Worker_Type':'Worker Type',
 'Time_Type':'Time Type',
 'Employee_Type':'Employee Type',
 'Scheduled_Hours':'Scheduled Hours',
 'Exempt_':'Exempt',
 'Job_Exempt_Applies':'Job Exempt Applies',
 'Job_Family':'Job Family',
 'Job_Family_Group':'Job Family Group',
 'Leadership_Role':'Leadership Role',
 'location':'Location',
 'Supervisory_Organization':'Supervisory Organization',
 'Tenure_Category_-_Position':'Tenure Category - Position',
 'Years_of_Service':'Years of Service',
 'Race_Ethnicity':'Race Ethnicity',
 'Hispanic_or_Latino':'Hispanic or Latino',
 'Age_Group':'Age Group',
 'Cost_Center':'Cost Center',
 'Email_-_Work':'Email - Work',
 'Profile_Area_Division':'Profile Area Division',
 'Consolidated_Area':'Consolidated Area',
 'Potential_-_Completed_Rating':'Potential - Completed Rating',
 'Last_Update_-_Potential':'Last Update - Potential',
 'effectiveDate':'Effective Date',
 'staffingPlanTitle':'Staffing Plan Title',
 'fieldOfficeProfileIndicator':'Field Office Profile Indicator'})

terminations.to_csv(r'O:\people_analytics\scorecards_kpis\ldp\data_build\term_worker_details.csv')
print('Terminations dataset written to shared drive!')

# raas candidate data
adp_afdp_candidates = 'https://services1.myworkday.com/ccx/service/customreport2/unum/DKJ05/RaaS_Candidate_Data?Internal=0&Job_Profile%21WID=2a18aa346de810528f0098df37904f81!2a18aa346de810528f00a35f6b404f8d!2a18aa346de810528f00a72729704f91!a9ad2a8b8c5301f3e4df754e01507b93!3abe0b922fa00106d93d2c50fd014412!c6c651ae891c0198ea8c87fd580186de!c6c651ae891c0128a399508759013ae1!c6c651ae891c0172f54591c7580181dc&format=csv'
with requests.Session() as s:
    download = s.get(adp_afdp_candidates, auth=(username, password))
    decoded_content = download.content.decode('utf-8')
    adp_afdp_candidates = pd.read_csv(io.StringIO(decoded_content))
    adp_afdp_candidates = adp_afdp_candidates.set_index('Candidate') 
    
adp_afdp_candidates = adp_afdp_candidates.rename(columns={'Candidate_ID':'Candidate ID',
 'Last_Recruiting_Stage':'Last Recruiting Stage',
 'Disposition_Reason':'Disposition Reason',
 'Candidate_Disposition_Reason':'Candidate Disposition Reason',
 'Internal_':'Internal',
 'App_Created':'App Created',
 'Employee_ID':'Employee ID',
 'termination_date':'Termination Date',
 'Hire_Date':'Hire Date',
 'JKCF_-_Format_App_Created_Date__MM-YYYY_':'App Created (Quarter-Year)',
 'Do_Not_Hire':'Do Not Hire',
 'CF_Calc_Candidate_Stage':'CF Calc Candidate Stage',
 'App_Source':'App Source',
 'Recruiter_s_Department':'Recruiters Department',
 'CF_Job_Requisition_Business_Area_SI':'Business Area',
 'LDCF_EE_SLC_Member':'SLC Member',
 'Req_Location':'Req Location',
 'Hiring_Mgr':'Hiring Mgr',
 'Job_Profile':'Job Profile',
 'Compensation_Grade':'Compensation Grade',
 'Job_Level':'Job Level',
 'Req_Created':'Req Created',
 'CF_Job_App_Req_Cmplt_Date':'App Created',
 'CF_Job_App_Offer_Cmplt_Date':'Offer Completed',
 'JKCF_-_Job_Offer_Complete_Date__Format_Y-Q_':'Offer Completed (Y-Q)',
 'JKCF_-_Return_1_for_In_Thru_Review_Stage':'In/Thru Review',
 'JKCF_-_Return_1_for_In_Thru_Assessment_Stage':'In/Thru Assessment',
 'JKCF_-_Return_1_for_In_Thru_Screen_Stage':'In/Thru Screen',
 'JKCF_-_Return_1_for_In_Thru_Interview_Stage':'In/Thru Interview',
 'JKCF_-_Return_1_for_In_Thru_Offer_Stage':'In/Thru Offer',
 'JKCF_-_Return_1_for_In_Thru_Background_Check_Stage':'In/Thru Background Check',
 'JKCF_-_Return_1_for_In_Thru_Ready_for_Hire_Stage':'In/Thru Ready for Hire'})

adp_afdp_candidates.to_csv(r'O:\people_analytics\scorecards_kpis\ldp\data_build\adp_afdp_candidates_export.csv')
print('ADP AFDP Candidates dataset written to shared drive!')


pdp_candidates = 'https://services1.myworkday.com/ccx/service/customreport2/unum/DKJ05/RaaS_Candidate_Data?Internal=0&JKCF_-_LRV_Primary_Recruiter_s_Department%21WID=1dd9ce98a6940104889a0b5381d7f3f1&Job_Profile%21WID=2a18aa346de810528f404b23be287596&format=csv'
with requests.Session() as s:
    download = s.get(pdp_candidates, auth=(username, password))
    decoded_content = download.content.decode('utf-8')
    pdp_candidates = pd.read_csv(io.StringIO(decoded_content))
    pdp_candidates = pdp_candidates.set_index('Candidate') 
    
pdp_candidates = pdp_candidates.rename(columns={'Candidate_ID':'Candidate ID',
 'Last_Recruiting_Stage':'Last Recruiting Stage',
 'Disposition_Reason':'Disposition Reason',
 'Candidate_Disposition_Reason':'Candidate Disposition Reason',
 'Internal_':'Internal',
 'App_Created':'App Created',
 'Employee_ID':'Employee ID',
 'termination_date':'Termination Date',
 'Hire_Date':'Hire Date',
 'JKCF_-_Format_App_Created_Date__MM-YYYY_':'App Created (Quarter-Year)',
 'Do_Not_Hire':'Do Not Hire',
 'CF_Calc_Candidate_Stage':'CF Calc Candidate Stage',
 'App_Source':'App Source',
 'Recruiter_s_Department':'Recruiters Department',
 'CF_Job_Requisition_Business_Area_SI':'Business Area',
 'LDCF_EE_SLC_Member':'SLC Member',
 'Req_Location':'Req Location',
 'Hiring_Mgr':'Hiring Mgr',
 'Job_Profile':'Job Profile',
 'Compensation_Grade':'Compensation Grade',
 'Job_Level':'Job Level',
 'Req_Created':'Req Created',
 'CF_Job_App_Req_Cmplt_Date':'App Created',
 'CF_Job_App_Offer_Cmplt_Date':'Offer Completed',
 'JKCF_-_Job_Offer_Complete_Date__Format_Y-Q_':'Offer Completed (Y-Q)',
 'JKCF_-_Return_1_for_In_Thru_Review_Stage':'In/Thru Review',
 'JKCF_-_Return_1_for_In_Thru_Assessment_Stage':'In/Thru Assessment',
 'JKCF_-_Return_1_for_In_Thru_Screen_Stage':'In/Thru Screen',
 'JKCF_-_Return_1_for_In_Thru_Interview_Stage':'In/Thru Interview',
 'JKCF_-_Return_1_for_In_Thru_Offer_Stage':'In/Thru Offer',
 'JKCF_-_Return_1_for_In_Thru_Background_Check_Stage':'In/Thru Background Check',
 'JKCF_-_Return_1_for_In_Thru_Ready_for_Hire_Stage':'In/Thru Ready for Hire'})

pdp_candidates.to_csv(r'O:\people_analytics\scorecards_kpis\ldp\data_build\pdp_candidates_export.csv')
print('PDP Candidates dataset written to shared drive!')


alp_candidates = 'https://services1.myworkday.com/ccx/service/customreport2/unum/DKJ05/RaaS_Candidate_Data?Internal=0&Job_Profile%21WID=a04c256469720175e4e817c392839858&format=csv'
with requests.Session() as s:
    download = s.get(alp_candidates, auth=(username, password))
    decoded_content = download.content.decode('utf-8')
    alp_candidates = pd.read_csv(io.StringIO(decoded_content))
    alp_candidates = alp_candidates.set_index('Candidate') 
    
alp_candidates = alp_candidates.rename(columns={'Candidate_ID':'Candidate ID',
 'Last_Recruiting_Stage':'Last Recruiting Stage',
 'Disposition_Reason':'Disposition Reason',
 'Candidate_Disposition_Reason':'Candidate Disposition Reason',
 'Internal_':'Internal',
 'App_Created':'App Created',
 'Employee_ID':'Employee ID',
 'termination_date':'Termination Date',
 'Hire_Date':'Hire Date',
 'JKCF_-_Format_App_Created_Date__MM-YYYY_':'App Created (Quarter-Year)',
 'Do_Not_Hire':'Do Not Hire',
 'CF_Calc_Candidate_Stage':'CF Calc Candidate Stage',
 'App_Source':'App Source',
 'Recruiter_s_Department':'Recruiters Department',
 'CF_Job_Requisition_Business_Area_SI':'Business Area',
 'LDCF_EE_SLC_Member':'SLC Member',
 'Req_Location':'Req Location',
 'Hiring_Mgr':'Hiring Mgr',
 'Job_Profile':'Job Profile',
 'Compensation_Grade':'Compensation Grade',
 'Job_Level':'Job Level',
 'Req_Created':'Req Created',
 'CF_Job_App_Req_Cmplt_Date':'App Created',
 'CF_Job_App_Offer_Cmplt_Date':'Offer Completed',
 'JKCF_-_Job_Offer_Complete_Date__Format_Y-Q_':'Offer Completed (Y-Q)',
 'JKCF_-_Return_1_for_In_Thru_Review_Stage':'In/Thru Review',
 'JKCF_-_Return_1_for_In_Thru_Assessment_Stage':'In/Thru Assessment',
 'JKCF_-_Return_1_for_In_Thru_Screen_Stage':'In/Thru Screen',
 'JKCF_-_Return_1_for_In_Thru_Interview_Stage':'In/Thru Interview',
 'JKCF_-_Return_1_for_In_Thru_Offer_Stage':'In/Thru Offer',
 'JKCF_-_Return_1_for_In_Thru_Background_Check_Stage':'In/Thru Background Check',
 'JKCF_-_Return_1_for_In_Thru_Ready_for_Hire_Stage':'In/Thru Ready for Hire'})

alp_candidates.to_csv(r'O:\people_analytics\scorecards_kpis\ldp\data_build\alp_candidates_export.csv')
print('ALP Candidates dataset written to shared drive!')

sender = 'do_not_reply@estevan.com'
recipients = ['elara@unum.com', 'rstoner@unum.com']
subject = 'LDP Job Completed'
body = 'Job LDP Survey Completed!'

UnumEmail.send_email(sender, recipients, subject, body, file_attached = False)
print('email sent!')