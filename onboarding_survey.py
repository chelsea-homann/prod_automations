# -*- coding: utf-8 -*-
"""
Created on Thu Sep  3 11:04:24 2020

@author: buf20
"""
import warnings
import sys
import requests
import os
import pandas as pd
from pandas.core.common import SettingWithCopyWarning
import io
import UnumEmail
import paramiko
from datetime import date, timedelta, datetime
import dateutil.relativedelta

warnings.simplefilter(action = 'ignore', category=SettingWithCopyWarning)

def Qualtrics_url_generator():
    
    url = 'https://services1.myworkday.com/ccx/service/customreport2/unum/C2HXT/Qualtrics_Survey_Data_File?Supervisory_Organization%21WID=fad8c8a44c4510541494e34161d00311&Include_Subordinate_Organizations=1&format=csv'
    
    return url

def wd_report_pull(url, username, password):
    
    with requests.Session() as s:
        download = s.get(url, auth=(username, password))
        decoded_content = download.content.decode('utf-8')
        
    return pd.read_csv(io.StringIO(decoded_content))

def sftp_transfer(username, password, myHostname, filename):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(myHostname, username = username, password = password)
    sftp = ssh.open_sftp()
    sftp.chdir('/Home/unumqualtrics/PeopleAnalytics/Workday/Out')
    
    try:
        sftp.remove('/Home/unumqualtrics/PeopleAnalytics/Workday/Out/' + filename)
        sftp.put('C:\\Users\\hr_automations\\UUS_PC_PeopleAnalytics_Automation\\Python_Jobs\\onboarding_survey_automation\\' + filename, "/Home/unumqualtrics/PeopleAnalytics/Workday/Out/" + filename)
        sftp.close()
        
    except Exception:
        sftp.put('C:\\Users\\hr_automations\\UUS_PC_PeopleAnalytics_Automation\\Python_Jobs\\onboarding_survey_automation\\' + filename, "/Home/unumqualtrics/PeopleAnalytics/Workday/Out/" + filename)
        sftp.close()
    
    return ssh.close()

def main():
    
    day1 = (date.today()) #Monday run date
    week1 = datetime.strptime((date.today().strftime('%Y-%m-%d')), '%Y-%m-%d') #Week 1 and run date (Friday)
    month1 = week1 - dateutil.relativedelta.relativedelta(months = 1)
    month3 = week1 - dateutil.relativedelta.relativedelta(months = 3)
    month6 = week1 - dateutil.relativedelta.relativedelta(months = 6)
    year1 = week1 - dateutil.relativedelta.relativedelta(months = 12)
    

    username = os.environ.get('WDUSER') 
    password = os.environ.get('WDPASSWORD')
    
    myHostname = os.environ.get('SFTP_HOST') 
    myUsername = os.environ.get('SFTP_USER') 
    myPassword = os.environ.get('SFTP_PASSWORD')
    
    sender = 'do_not_reply@estevan.com'
    recipients = ['elara@unum.com', 'rstoner@unum.com']
    subject = 'Job Completed'
    body = 'Job # Onboarding Survey Completed!'
    
    
    try:
        print('pulling report now....')
        qual_df = wd_report_pull(Qualtrics_url_generator(), username, password)
        print('Report Pulled!')
 
    except Exception as e:
        print('\nWD Report pull failed!')
        subject = 'Onboarding Job Failed!'
        body = print('Job Failed!')
        UnumEmail.send_email(sender, recipients, subject, body, file_attached = False)
        print(str(e))
        sys.exit()

    try:
        
        if date.today().strftime('%A') == 'Monday' : 
        
            day1_df = qual_df[qual_df['Hire_Date'] == (day1.strftime('%Y-%m-%d'))]
            day1_df['Day1_Launch_Date'] = day1.strftime('%m-%d-%Y')
                                         
            day1_df.to_csv('C:\\Users\\hr_automations\\UUS_PC_PeopleAnalytics_Automation\\Python_Jobs\\onboarding_survey_automation\\DAY1_Onboarding.csv', index = False)
                                         
        else:
            week1_df = qual_df[(qual_df['Hire_Date'] <= (week1.strftime('%Y-%m-%d'))) & (qual_df['Hire_Date'] >= ((week1 - timedelta(4)).strftime('%Y-%m-%d')))]
            week1_df['Week1_Launch_Date'] = week1.strftime('%m-%d-%Y')
            week1_df.to_csv('C:\\Users\\hr_automations\\UUS_PC_PeopleAnalytics_Automation\\Python_Jobs\\onboarding_survey_automation\\WEEK1_Onboarding.csv', index = False)
        
            month1_df = qual_df[(qual_df['Hire_Date'] >= ((month1 - timedelta(4)).strftime('%Y-%m-%d'))) & (qual_df['Hire_Date'] <= (month1.strftime('%Y-%m-%d')))]
            month1_df['Month1_Launch_Date'] = month1.strftime('%m-%d-%Y')
            month1_df.to_csv('C:\\Users\\hr_automations\\UUS_PC_PeopleAnalytics_Automation\\Python_Jobs\\onboarding_survey_automation\\MONTH1_Onboarding.csv', index = False)
        
            month3_df = qual_df[(qual_df['Hire_Date'] >= ((month3 - timedelta(4)).strftime('%Y-%m-%d'))) & (qual_df['Hire_Date'] <= (month3.strftime('%Y-%m-%d')))]
            month3_df['Month3_Launch_Date'] = month3.strftime('%m-%d-%Y')
            month3_df.to_csv('C:\\Users\\hr_automations\\UUS_PC_PeopleAnalytics_Automation\\Python_Jobs\\onboarding_survey_automation\\MONTH3_Onboarding.csv', index = False)
        
            month6_df = qual_df[(qual_df['Hire_Date'] >= ((month6 - timedelta(4)).strftime('%Y-%m-%d'))) & (qual_df['Hire_Date'] <= (month6.strftime('%Y-%m-%d')))]
            month6_df['Month6_Launch_Date'] = month6.strftime('%m-%d-%Y')
            month6_df.to_csv('C:\\Users\\hr_automations\\UUS_PC_PeopleAnalytics_Automation\\Python_Jobs\\onboarding_survey_automation\\MONTH6_Onboarding.csv', index = False)
        
            year1_df = qual_df[(qual_df['Hire_Date'] >= ((year1 - timedelta(4)).strftime('%Y-%m-%d'))) & (qual_df['Hire_Date'] <= (year1.strftime('%Y-%m-%d')))]
            year1_df['Year1_Launch_Date'] = year1.strftime('%m-%d-%Y')
            year1_df.to_csv('C:\\Users\\hr_automations\\UUS_PC_PeopleAnalytics_Automation\\Python_Jobs\\onboarding_survey_automation\\YEAR1_Onboarding.csv', index = False)
            
    except Exception as e:
        
        print('\nCSV Creation Failed!')
        subject = 'Onboarding Job Failed!'
        body = print('Job Failed!')
        UnumEmail.send_email(sender, recipients, subject, body, file_attached = False)
        print(str(e))
        sys.exit()

    files = ['WEEK1_Onboarding.csv', 'MONTH1_Onboarding.csv', 'MONTH3_Onboarding.csv', 'MONTH6_Onboarding.csv', 'YEAR1_Onboarding.csv']
    
    try:
        
        if date.today().strftime('%A') == 'Monday' :
        
            print('Begin File Transfer!')
            sftp_transfer(myUsername, myPassword, myHostname, 'DAY1_Onboarding.csv')
        else:
            
            for i in files:
                sftp_transfer(myUsername, myPassword, myHostname, i)
            for i in files:    
                os.remove('C:\\Users\\hr_automations\\UUS_PC_PeopleAnalytics_Automation\\Python_Jobs\\onboarding_survey_automation\\' + i)
            
    except Exception as e:
        print('\nFile transfer incomplete')
        print(str(e))
        subject = 'Onboarding Job Failed!'
        body = 'Job Failed!'
        UnumEmail.send_email(sender, recipients, subject, body, file_attached = False)
        sys.exit()
    
    print('file transfer complete!')

    UnumEmail.send_email(sender, recipients, subject, body, file_attached = False)
    print('email sent!')
    ()

if __name__ == '__main__':
    main()
