# -*- coding: utf-8 -*-
"""
Created on Thu Sep  3 11:04:24 2020

@author: buf20
"""
import sys
import requests
import os
import pandas as pd
import io
import UnumEmail
import paramiko
from datetime import date, timedelta



def LeaveReturn_url_generator(start_dt, end_dt):
    
    url = 'https://services1.myworkday.com/ccx/service/customreport2/unum/G3006/WS_Leave_Return_Completed_in_Range?Return_Completed_End={0}%3A00&Return_Completed_Start={1}%3A00&format=csv'.format(end_dt, start_dt)
    
    return url

def Qualtrics_url_generator():
    
    url = 'https://services1.myworkday.com/ccx/service/customreport2/unum/C2HXT/Qualtrics_Survey_Data_File?Supervisory_Organization%21WID=fad8c8a44c4510541494e34161d00311&Include_Subordinate_Organizations=1&format=csv'
    
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
    sftp.chdir('/Home/unumqualtrics/PeopleAnalytics/Workday/Out')
    
    try:
        sftp.remove('/Home/unumqualtrics/PeopleAnalytics/Workday/Out/LEAVE.csv')
        sftp.put('C:\\Users\\hr_automations\\UUS_PC_PeopleAnalytics_Automation\\Python_Jobs\\LEAVE.csv', \
                 "/Home/unumqualtrics/PeopleAnalytics/Workday/Out/LEAVE.csv")

    except Exception:
        sftp.put('C:\\Users\\hr_automations\\UUS_PC_PeopleAnalytics_Automation\\Python_Jobs\\LEAVE.csv', \
                 "/Home/unumqualtrics/PeopleAnalytics/Workday/Out/LEAVE.csv")

    sftp.close()


def main():
   

    start_dt = (date.today() - timedelta(6)).strftime('%Y-%m-%d') + '-08'
    end_dt = (date.today()).strftime('%Y-%m-%d') + '-07'
        
    #end_dt = '2021-01-28-07'
    #start_dt = '2021-02-03-07'
    username = os.environ.get('WDUSER')
    password =  'Dina4166!@'
    
    myHostname = os.environ.get('SFTP_HOST')
    myUsername = os.environ.get('SFTP_USER')
    myPassword = os.environ.get('SFTP_PASSWORD')
    
    sender = 'do_not_reply@estevan.com'
    recipients = ['elara@unum.com', 'cwymer@unum.com']
    subject = 'Job Completed'
    body = 'Job # Leave Survey Completed!'
    
    
    try:
        print('pulling reports now....')
        leave_df = wd_report_pull(LeaveReturn_url_generator(start_dt, end_dt), username, password)
        print('leave report pulled...')
        qual_df = wd_report_pull(Qualtrics_url_generator(), username, password)
        print('Reports Pulled!')
        
        merged_df = qual_df.merge(leave_df[['Unique_Identifier','First_Day_Back']], left_on = 'Employee_ID', right_on = 'Unique_Identifier')
        deduped = merged_df.drop_duplicates()
        deduped['Leave_Launch_Date'] = (date.today()).strftime('%m-%d-%Y')
        deduped.to_csv('C:\\Users\\hr_automations\\UUS_PC_PeopleAnalytics_Automation\\Python_Jobs\\LEAVE.csv', index=False)
        print('CSV Created!')
        
    except Exception as e:
        print('\nWD Report pull failed!')
        subject = 'Job Failed!'
        body = 'Job Failed!'
        UnumEmail.send_email(sender, recipients, subject, body, file_attached = False)
        print(str(e))
        sys.exit()
    
    try:
        print('Begin File Transfer!')
        sftp_transfer(myUsername, myPassword, myHostname)
    except Exception as e:
        print('\nFile transfer incomplete')
        print(str(e))
        subject = 'Job Failed!'
        body = 'Job Failed!'
        UnumEmail.send_email(sender, recipients, subject, body, file_attached = True, attachment = 'LEAVE.csv', attach_path = 'C:\\Users\\hr_automations\\UUS_PC_PeopleAnalytics_Automation\\Python_Jobs\\LEAVE.csv')
        sys.exit()
        
    os.remove('C:\\Users\\hr_automations\\UUS_PC_PeopleAnalytics_Automation\\Python_Jobs\\LEAVE.csv')
    print('file transfer complete!')

    UnumEmail.send_email(sender, recipients, subject, body, file_attached = False)
    print('email sent!')
    ()

if __name__ == '__main__':
    main()
