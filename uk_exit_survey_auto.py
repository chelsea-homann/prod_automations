#!/usr/bin/env python
# coding: utf-8

# In[2]:


import sys
import requests
import os
import pandas as pd
import io
import paramiko
import UnumEmail
from datetime import date, timedelta


# In[3]:


def uk_exit_url_generator(start_dt, end_dt):
    
    url = 'https://services1.myworkday.com/ccx/service/customreport2/unum/C2HXT/UK_Terminated_Worker_Details_for_Exit_Survey?Organization%21WID=fad8c8a44c4510541494e34161d00311&End_Date={0}-08%3A00&Start_Date={1}-08%3A00&Include_Subordinate_Organizations=1&Country%21WID=29247e57dbaf46fb855b224e03170bc7&format=csv'.format(end_dt,start_dt)    
    return url

# def Qualtrics_url_generator():
    
    # url = 'https://services1.myworkday.com/ccx/service/customreport2/unum/C2HXT/Qualtrics_Survey_Data_File?Supervisory_Organization%21WID=fad8c8a44c4510541494e34161d00311&Include_Subordinate_Organizations=1&format=csv'
    
    # return url

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
        # sftp.remove('/Home/unumqualtrics/peopleanalytics/workday/out/leave_survey_participants.csv')
        sftp.put('C:\\Users\\hr_automations\\UUS_PC_PeopleAnalytics_Automation\\Python_Jobs\\uk_exit_survey_participants.csv', "/Home/unumqualtrics/PeopleAnalytics/Workday/Out/uk_exit_survey_participants.csv")

    except Exception:
        sftp.put('C:\\Users\\hr_automations\\UUS_PC_PeopleAnalytics_Automation\\Python_Jobs\\uk_exit_survey_participants.csv', "/Home/unumqualtrics/PeopleAnalytics/Workday/Out/uk_exit_survey_participants.csv")
    
    return sftp.close()


def main():
    
    end_dt = (date.today() + timedelta(4)).strftime('%Y-%m-%d')
    start_dt = (date.today()).strftime('%Y-%m-%d')
    username = os.environ.get('WDUSER')
    password = os.environ.get('WDPASSWORD')
    
    myHostname = os.environ.get('SFTP_HOST')
    myUsername = os.environ.get('SFTP_USER')
    myPassword = os.environ.get('SFTP_PASSWORD')
    
    sender = 'do_not_reply@chelsea.com'
    recipients = ['cwymer@unum.com', 'elara@unum.com']
    subject = 'Job Completed'
    body = 'Job # UK Exit Survey Completed!'
    # updated sender section for exit survey
    
    try:
        print('pulling reports now....')
        exit_df = wd_report_pull(uk_exit_url_generator(start_dt, end_dt), username, password)
        print('exit report pulled...')
        #qual_df = wd_report_pull(Qualtrics_url_generator(), username, password)
        #print('Reports Pulled!')
        
        #merged_df = qual_df.merge(leave_df[['Unique_Identifier','First_Day_Back']], left_on = 'Employee_ID', right_on = 'Unique_Identifier')
        #deduped = merged_df.drop_duplicates()
        exit_df['Exit Survey Launch Date'] = (date.today()).strftime('%m-%d-%Y')
        #exit_df = exit_df.drop(columns=['Survey_Launch_Date'])
        exit_df = exit_df.rename(columns={"FirstName": "First Name", "LastName": "Last Name", "Unique_Identifier":"Unique Identifier","Employee_ID":"Employee ID", "UserName":"User Name",
                              "Supervisory_Organization":"Supervisory Organization", "Business_Area":"Business Area", "Profile_Area_Division":"Profile Area Division",
                              "Consolidated_Area":"Consolidated Area","Hire_Date":"Hire Date","termination_date":"Termination Date","Termination_Reason":"Termination Reason",
                              "Job_Profile":"Job Profile", "Time_in_Job_Profile":"Time in Job Profile", "Job_Level":"Job Level", "Ethnicity_Generic":"Ethnicity Generic", 
                              "Worker_has_a_Disability":"Worker has a Disability", "Worker_is_a_Veteran":"Worker is a Veteran","Potential_Rating":"Potential Rating",
                              })
        exit_df = exit_df.set_index('First Name')
        exit_df.to_csv('C:\\Users\\hr_automations\\UUS_PC_PeopleAnalytics_Automation\\Python_Jobs\\uk_exit_survey_participants.csv')
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
        UnumEmail.send_email(sender, recipients, subject, body, file_attached = True, attachment = 'uk_exit_survey_participants.csv', attach_path = './uk_exit_survey_participants.csv')
        sys.exit()
        
    os.remove('C:\\Users\\hr_automations\\UUS_PC_PeopleAnalytics_Automation\\Python_Jobs\\uk_exit_survey_participants.csv')
    print('file transfer complete!')

    UnumEmail.send_email(sender, recipients, subject, body, file_attached = False)
    print('email sent!')
    ()

if __name__ == '__main__':
    main()


# In[ ]:





# In[ ]:




