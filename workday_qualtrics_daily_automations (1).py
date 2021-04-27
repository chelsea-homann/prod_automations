#!/usr/bin/env python
# coding: utf-8

# In[1]:


# -*- coding: utf-8 -*-

"""
Created on Tue Apr 6 2021

@author: ddy17
"""

import sys
import requests
import os
import pandas as pd
import io
import UnumEmail
import paramiko
from datetime import date, timedelta


# In[ ]:


def Term_url_generator(termdate1, termdate2):
    
    url = 'https://services1.myworkday.com/ccx/service/customreport2/unum/INT0078+ISU/INT0078_Workday_to_Qualtrics_Terminated_Workers?Prompt_-_Date_and_Time_2={0}T20%3A59%3A00.000-07%3A00&Prompt_-_Date_and_Time_1={1}T21%3A00%3A00.000-07%3A00&format=csv'.format(termdate2, termdate1)
    
    return url

def Employee_url_generator():
    
    url = 'https://services1.myworkday.com/ccx/service/customreport2/unum/INT0079+ISU/INT0079_Workday_to_Qualtrics_Employees?format=csv'
    
    return url

def wd_report_pull(url, username, password):
    
    with requests.Session() as s:
        download = s.get(url, auth=(username, password))
        decoded_content = download.content.decode('utf-8')
        
    return pd.read_csv(io.StringIO(decoded_content))


# In[ ]:


def sftp_transfer(username, password, myHostname):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(myHostname, username = username, password = password)
    sftp = ssh.open_sftp()
    sftp.chdir('/Home/unumqualtrics/PeopleAnalytics/Workday/Out')
    
    try:
        sftp.remove('/Home/unumqualtrics/PeopleAnalytics/Workday/Out/term_df.csv')
        sftp.put('C:\\Users\\hr_automations\\UUS_PC_PeopleAnalytics_Automation\\Python_Jobs\\wd_qualtrics_daily_automation\\term_df.csv', "/Home/unumqualtrics/PeopleAnalytics/Workday/Out/term_df.csv")

    except Exception:
        sftp.put('C:\\Users\\hr_automations\\UUS_PC_PeopleAnalytics_Automation\\Python_Jobs\\wd_qualtrics_daily_automation\\term_df.csv', "/Home/unumqualtrics/PeopleAnalytics/Workday/Out/term_df.csv")
    
    return sftp.close()


# In[ ]:


def main():
    
    termdate1 = (date.today() - timedelta(1)).strftime('%Y-%m-%d')
    termdate2 = (date.today()).strftime('%Y-%m-%d')
    username = os.environ.get('WDUSER') 
    password = os.environ.get('WDPASSWORD') 
    
    myHostname = os.environ.get('SFTP_HOST') 
    myUsername = os.environ.get('SFTP_USER') 
    myPassword = os.environ.get('SFTP_PASSWORD') 
    
    sender = 'do_not_reply@automation.com'
    recipients = ['lgmontez@unum.com', 'elara@unum.com']
    subject = 'Workday to Qualtrics Automation (Terms) Successfully Completed'
    body = 'Workday to Qualtrics Automation (Terms) Successfully Completed'
    
    try:
        print('Pulling Term Report Now')
        term_df = wd_report_pull(Term_url_generator(termdate1, termdate2), username, password)
        print('Report Pulled!')

    
        term_df.to_csv('C:\\Users\\hr_automations\\UUS_PC_PeopleAnalytics_Automation\\Python_Jobs\\wd_qualtrics_daily_automation\\term_df.csv', index=False)
        print('CSV Created and Sent to Notebook Directory!')
        
    except Exception as e:
        print('\nWD Term Report pull failed!')
        subject = 'Term Job Failed!'
        body = print('Daily Term Job Failed!')
        UnumEmail.send_email(sender, recipients, subject, body, file_attached = False)
        print(str(e))
        sys.exit()
    
    try:
        print('Beginning Term File Transfer')
        sftp_transfer(myUsername, myPassword, myHostname)
    except Exception as e:
        print('\n Term File Transfer Incomplete')
        print(str(e))
        subject = 'Term Job Failed!'
        body = 'Daily Term Job Failed!'
        UnumEmail.send_email(sender, recipients, subject, body, file_attached = True, attachment = ['term_df.csv', ], attach_path = './term_df.csv')
        sys.exit()
        
    os.remove('C:\\Users\\hr_automations\\UUS_PC_PeopleAnalytics_Automation\\Python_Jobs\\wd_qualtrics_daily_automation\\term_df.csv')
    print('File Transfer Successful!')

    UnumEmail.send_email(sender, recipients, subject, body, file_attached = False)
    print('Email Has Been Sent')
    ()

if __name__ == '__main__':
        main()


# In[ ]:


def sftp_transfer(username, password, myHostname):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(myHostname, username = username, password = password)
    sftp = ssh.open_sftp()
    sftp.chdir('/Home/unumqualtrics/PeopleAnalytics/Workday/Out')
    
    try:
        sftp.remove('/Home/unumqualtrics/PeopleAnalytics/Workday/Out/employee_df.csv')
        sftp.put('C:\\Users\\hr_automations\\UUS_PC_PeopleAnalytics_Automation\\Python_Jobs\\wd_qualtrics_daily_automation\\employee_df.csv', "/Home/unumqualtrics/PeopleAnalytics/Workday/Out/employee_df.csv")

    except Exception:
        sftp.put('C:\\Users\\hr_automations\\UUS_PC_PeopleAnalytics_Automation\\Python_Jobs\\wd_qualtrics_daily_automation\\employee_df.csv', "/Home/unumqualtrics/PeopleAnalytics/Workday/Out/employee_df.csv")
    
    return sftp.close()


# In[ ]:


def main():
    
    username = os.environ.get('WDUSER') 
    password = os.environ.get('WDPASSWORD') 
    
    myHostname = os.environ.get('SFTP_HOST') 
    myUsername = os.environ.get('SFTP_USER') 
    myPassword = os.environ.get('SFTP_PASSWORD') 
    
    sender = 'do_not_reply@automation.com'
    recipients = ['lgmontez@unum.com', 'elara@unum.com']
    subject = 'Workday to Qualtrics Automation (Employees) Successfully Completed'
    body = 'Workday to Qualtrics Automation (Employees) Successfully Completed'
    
    try:
        print('Pulling Employee Report Now')
        employee_df = wd_report_pull(Employee_url_generator(), username, password)
        print('Employee Report Pulled!')

        employee_df.to_csv('C:\\Users\\hr_automations\\UUS_PC_PeopleAnalytics_Automation\\Python_Jobs\\wd_qualtrics_daily_automation\\employee_df.csv', index=False)
        print('CSV Created and Sent to Notebook Directory!')
        
    except Exception as e:
        print('\nWD Employee Report pull failed!')
        subject = 'Employee Job Failed!'
        body = print('Daily Employee Job Failed!')
        UnumEmail.send_email(sender, recipients, subject, body, file_attached = False)
        print(str(e))
        sys.exit()
    
    try:
        print('Beginning Employee File Transfer')
        sftp_transfer(myUsername, myPassword, myHostname)
    except Exception as e:
        print('\nEmployee File Transfer Incomplete')
        print(str(e))
        subject = 'Employee Job Failed!'
        body = 'Daily Employee Job Failed!'
        UnumEmail.send_email(sender, recipients, subject, body, file_attached = True, attachment = ['employee_df.csv', ], attach_path = './term_df.csv')
        sys.exit()
        
    os.remove('C:\\Users\\hr_automations\\UUS_PC_PeopleAnalytics_Automation\\Python_Jobs\\wd_qualtrics_daily_automation\\employee_df.csv')
    print('File Transfer Successful!')

    UnumEmail.send_email(sender, recipients, subject, body, file_attached = False)
    print('Email Has Been Sent')
    ()

if __name__ == '__main__':
        main()



