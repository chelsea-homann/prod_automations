#!/usr/bin/env python
# coding: utf-8


import sys
import requests
import os
import pandas as pd
import io
import paramiko
import UnumEmail
from datetime import date, timedelta




def us_exit_url_generator(start_dt, end_dt):
    
    url = 'https://services1.myworkday.com/ccx/service/customreport2/unum/C2HXT/Terminated_Worker_Details_for_Exit_Survey?Term_Date_On_After={0}-08%3A00&Term_Date_On_Before={1}-08%3A00&Supervisory_Organization%21WID=fad8c8a44c4510541494e34161d00311&Country%21WID=bc33aa3152ec42d4995f4791a106ed09&format=csv'.format(start_dt, end_dt)    
    return url


def wd_report_pull(url, username, password):
    
    with requests.Session() as s:
        download = s.get(url, auth=(username, password))
        decoded_content = download.content.decode('utf-8')
        
    return pd.read_csv(io.StringIO(decoded_content))

def sftp_transfer(username, password, myHostname):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(myHostname, username = username, password = password)
    sftp = ssh.open_sftp()
    sftp.chdir('/Home/unumqualtrics/PeopleAnalytics/Workday/Out/')  # updated with new account
    
    try:
        sftp.put('C:\\Users\\hr_automations\\UUS_PC_PeopleAnalytics_Automation\\Python_Jobs\\exit_survey_participants.csv', "/Home/unumqualtrics/PeopleAnalytics/Workday/Out/exit_survey_participants.csv")

    except Exception:
        sftp.put('C:\\Users\\hr_automations\\UUS_PC_PeopleAnalytics_Automation\\Python_Jobs\\exit_survey_participants.csv', "/Home/unumqualtrics/PeopleAnalytics/Workday/Out/exit_survey_participants.csv")
    
    return sftp.close()


def main():
    
    start_dt = (date.today() - timedelta(4)).strftime('%Y-%m-%d')
    end_dt = (date.today()).strftime('%Y-%m-%d')
    username = os.environ.get('WDUSER')
    password = os.environ.get('WDPASSWORD')
    # updated to get start date as a Monday and end date as a Friday (will set up this script to run weekly on Fridays)
    
    myHostname = os.environ.get('SFTP_HOST')
    myUsername = os.environ.get('SFTP_USER')
    myPassword = os.environ.get('SFTP_PASSWORD')
    
    sender = 'do_not_reply@chelsea.com'
    recipients = ['cwymer@unum.com']
    subject = 'Exit Survey Job Completed'
    body = 'Job # Exit Survey Completed!'
    # updated sender section for exit survey
    
    try:
        print('pulling reports now....')
        exit_df = wd_report_pull(us_exit_url_generator(start_dt, end_dt), username, password)
        print('exit report pulled...')

        exit_df['Exit Survey Launch Date'] = (date.today()).strftime('%m-%d-%Y')
        exit_df = exit_df.drop(columns=['Survey_Launch_Date'])
        exit_df = exit_df.rename(columns={"FirstName": "First Name", "LastName": "Last Name", "Unique_Identifier":"Unique Identifier","Employee_ID":"Employee ID", "UserName":"User Name",
                              "Supervisory_Organization":"Supervisory Organization", "Business_Area":"Business Area", "Profile_Area_Division":"Profile Area Division",
                              "Consolidated_Area":"Consolidated Area","Hire_Date":"Hire Date","termination_date":"Termination Date","Termination_Reason":"Termination Reason",
                              "Job_Profile":"Job Profile", "Time_in_Job_Profile":"Time in Job Profile", "Job_Level":"Job Level", "Ethnicity_Generic":"Ethnicity Generic", 
                              "Worker_has_a_Disability":"Worker has a Disability", "Worker_is_a_Veteran":"Worker is a Veteran","Potential_Rating":"Potential Rating",
                              })
        exit_df = exit_df.set_index('First Name')
        exit_df.head()
        exit_df.to_csv('C:\\Users\\hr_automations\\UUS_PC_PeopleAnalytics_Automation\\Python_Jobs\\exit_survey_participants.csv')
        print('CSV Created!')
        
    except Exception as e:
        print('\nWD Report pull failed!')
        subject = 'Job Failed!'
        body = print('Job Failed!')
        UnumEmail.send_email(sender, recipients, subject, body, file_attached = False)
        print(str(e))
        sys.exit()
    
    try:
        print('Begin File Transfer...')
        sftp_transfer(myUsername, myPassword, myHostname)
        
    except Exception as e:
        print('\nFile transfer incomplete!')
        print(str(e))
        subject = 'Job Failed!'
        body = 'Job Failed!'
        UnumEmail.send_email(sender, recipients, subject, body, file_attached = True, attachment = 'exit_survey_participants.csv', attach_path = './exit_survey_participants.csv')
        sys.exit()
        
    os.remove('C:\\Users\\hr_automations\\UUS_PC_PeopleAnalytics_Automation\\Python_Jobs\\exit_survey_participants.csv')
    print('file transfer complete!')

    UnumEmail.send_email(sender, recipients, subject, body, file_attached = False)
    print('email sent!')
    ()

if __name__ == '__main__':
    main()



