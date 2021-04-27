#!/usr/bin/env python
# coding: utf-8

# In[10]:


import sys
import requests
import pandas as pd
import io
import UnumEmail
import re
import zipfile
import json
from datetime import date


# In[12]:


def exportSurvey(apiToken,surveyId, dataCenter, fileFormat):
    
    surveyId = surveyId
    fileFormat = fileFormat 
    dataCenter = dataCenter #organization ID

    # Setting static parameters
    requestCheckProgress = 0.0
    progressStatus = "inProgress"
    baseUrl = "https://{0}.az1.qualtrics.com/API/v3/surveys/{1}/export-responses/".format(dataCenter, surveyId)
    headers = {
    "content-type": "application/json",
    "x-api-token": apiToken,
    "proxies" : '10.8.109.16:8080'
    }
    
    proxies = {
      'http': 'http://10.8.109.16:8080',
      'https': 'http://10.8.109.16:8080',
    }
    # Step 1: Creating Data Export
    useLabels = True
    downloadRequestUrl = baseUrl
    dictionaryPayload = {'format': fileFormat, 'useLabels': useLabels}
    downloadRequestPayload = json.dumps(dictionaryPayload)
    downloadRequestResponse = requests.request("POST", downloadRequestUrl, data=downloadRequestPayload, headers=headers,
                                               proxies=proxies)
    progressId = downloadRequestResponse.json()["result"]["progressId"]
    print(downloadRequestResponse.text)

    # Step 2: Checking on Data Export Progress and waiting until export is ready
    while progressStatus != "complete" and progressStatus != "failed":
        print ("progressStatus=", progressStatus)
        requestCheckUrl = baseUrl + progressId
        requestCheckResponse = requests.request("GET", requestCheckUrl, headers=headers, proxies=proxies)
        requestCheckProgress = requestCheckResponse.json()["result"]["percentComplete"]
        print("Download is " + str(requestCheckProgress) + " complete")
        progressStatus = requestCheckResponse.json()["result"]["status"]

    #step 2.1: Check for error
    if progressStatus == "failed":
        raise Exception("export failed")

    fileId = requestCheckResponse.json()["result"]["fileId"]

    # Step 3: Downloading file
    requestDownloadUrl = baseUrl + fileId + '/file'
    requestDownload = requests.request("GET", requestDownloadUrl, headers=headers, proxies = proxies, stream=True)

    # Step 4: Unzipping the file
    zipfile.ZipFile(io.BytesIO(requestDownload.content)).extractall()
    print('Complete')

    
def main():
    
    apiToken = 'oDIeIeHRieqLqI3fe26wvAGe2oEGTM1sZw433nK1'
    surveyId = 'SV_3dAVD7hE5Oz1sXj'
    dataCenter = 'unumhr'
    fileFormat = 'csv'

    if fileFormat not in ["csv", "tsv", "spss"]:
        print ('fileFormat must be either csv, tsv, or spss')
        sys.exit(2)
        
    r = re.compile('^SV_.*')
    m = r.match(surveyId)
    if not m:
        print ("survey Id must match ^SV_.*")
        sys.exit(2)

    exportSurvey(apiToken, surveyId,dataCenter, fileFormat)
    
if __name__ == "__main__":
    main()


# In[13]:



import numpy as np

df = pd.read_csv(r'C:\Users\hr_automations\UUS_PC_PeopleAnalytics_Automation\Python_Jobs\leave_data_monthly_pull\Employee Leave Experience Lifecycle.csv', header = 0,  skiprows=lambda x: x in [0, 2])


# In[14]:


df_subset = df[['Recorded Date',
 'Response ID', 
 'Thinking about your experience to date, how satisfied were you with the overall handling of your leave of absence or claim?\n\n\n0 = Extremely Unsatisfied, 10 = Extremely Satisfied',
 'Please elaborate on your answer below, any positive and/or constructive feedback you can share is helpful.',
 'Were you on a paid or unpaid leave of absence?', 
 'Did you receive your pay and benefit deductions accurately and in a timely manner?', 
 'Were your benefits handled as you expected them to be?',
 'Please describe either what went wrong or what did not go as expected with your pay and benefit deductions:',
 'For planning and filing your leave of absence or claim, did you primarily call in to the Absence Management Center (AMC) or use the Online Portal?',
 'How would you rate your interaction(s) with the Absence Management Center?',
 'How would you rate your experience using the online portal?',
 'Are there any details you would like to share regarding your experience?',
 'Leading up to your return to work, who did you speak with? Please select all that apply: - Absence Management Center (AMC)',
 'Leading up to your return to work, who did you speak with? Please select all that apply: - My Manager ',
 'Leading up to your return to work, who did you speak with? Please select all that apply: - HR / Payroll',
 'Leading up to your return to work, who did you speak with? Please select all that apply: - None of the above',
 'To the best of your knowledge, please rate your experience with the HR team(s) that you interacted with before, during, or after your return to work experience (if applicable): - HR Leave and Disability Consultant (formerly known as Health and Wellbeing Consultant)',
 'To the best of your knowledge, please rate your experience with the HR team(s) that you interacted with before, during, or after your return to work experience (if applicable): - HR Response Team or HR Leave Administration',
 'To the best of your knowledge, please rate your experience with the HR team(s) that you interacted with before, during, or after your return to work experience (if applicable): - Payroll',
 'Is there anything regarding your experience and interaction(s) with the previously selected team(s) or individual(s) that you would like to share?',
 'How was your experience when you returned to work?',
 'Please tell us about your overall return to work experience including the days leading up to your return and the time that followed:',
 'If you have any feedback, suggestions, or comments relating to your leave of absence or claim that were not addressed in this survey, please feel free to share with us below:',
 'The HR Leave Transformation Team holds focus groups throughout the year to get our employees opinions on a variety of leave/absence related topics. If you would be interested in participating in a focus group, please provide your name and email to be contacted when future focus groups are planned. \n\n \n\nIf you would not like to participate, please leave the fields blank. Thank you! - Name',
 'The HR Leave Transformation Team holds focus groups throughout the year to get our employees opinions on a variety of leave/absence related topics. If you would be interested in participating in a focus group, please provide your name and email to be contacted when future focus groups are planned. \n\n \n\nIf you would not like to participate, please leave the fields blank. Thank you! - Email',
 'Age Group','Business Area', 'Campus', 'Country', 'Department','First Day Back', 'Return To Work Date', 'Survey Launch Date', 'Leave Launch Date']].copy()




# In[15]:


df_subset['Leave Launch Date'] = pd.to_datetime(df_subset['Leave Launch Date'])
df_subset['Leave Launch Date'] = df_subset['Leave Launch Date'].dt.strftime('%m/%d/%Y')
df_subset['Return To Work Date'] = pd.to_datetime(df_subset['Return To Work Date'])
df_subset['Return To Work Date'] = df_subset['Return To Work Date'].dt.strftime('%m/%d/%Y')
df_subset['First Day Back'] = pd.to_datetime(df_subset['First Day Back'])
df_subset['First Day Back'] = df_subset['First Day Back'].dt.strftime('%m/%d/%Y')
df_subset['Survey Launch Date'] = pd.to_datetime(df_subset['Survey Launch Date'])
df_subset['Survey Launch Date'] = df_subset['Survey Launch Date'].dt.strftime('%m/%d/%Y')


# In[16]:

df_subset['Return To Work Date Combined'] = np.where(df_subset['Return To Work Date'].isnull(),
                                              df_subset['First Day Back'],df_subset['Return To Work Date'])


# In[17]:

df_subset['Combined Launch Dates'] = np.where(df_subset['Leave Launch Date'].isnull(),
                                              df_subset['Survey Launch Date'],
                                              (np.where(df_subset['Leave Launch Date'] > df_subset['Survey Launch Date'], 
                                                        df_subset['Leave Launch Date'],df_subset['Leave Launch Date'])))


# In[18]:


df_subset['Quarter'] = pd.DatetimeIndex(df_subset['Combined Launch Dates']).quarter
df_subset['Year'] = pd.DatetimeIndex(df_subset['Combined Launch Dates']).year
df_subset['Quarter - Year'] = "Q" + df_subset['Quarter'].astype(str) +"-"+ df_subset['Year'].astype(str)


# ## Exporting Data to Jupyter WD (.csv)

# In[19]:


date = (date.today()).strftime('%m-%Y')


# In[20]:


df_subset.to_csv(r'C:\Users\hr_automations\UUS_PC_PeopleAnalytics_Automation\Python_Jobs\leave_data_monthly_pull\leave_experience_deidentified_data_{0}.csv'.format(date), na_rep='')


# ## Sending Datafile to Leave team

# In[ ]:


sender = 'leaveautomation@estevan.com'
recipients = ['rstoner@unum.com','KPreble@UNUM.COM', 'elara@unum.com']
subject = (date + " " + 'Leave Experience Data Export' )
body = 'Leave data export from Qualtrics is attached to this email'
attach_path = (r'C:\Users\hr_automations\UUS_PC_PeopleAnalytics_Automation\Python_Jobs\leave_data_monthly_pull\leave_experience_deidentified_data_{0}.csv'.format(date))
UnumEmail.send_email(sender, recipients, subject, body, file_attached = True, 
                     attachment = 'leave_experience_deidentified_data_{0}.csv'.format(date),
                     attach_path = attach_path)


