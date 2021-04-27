@echo off
rem ---------------------------------
rem build log for leave survey data pull automation
rem ---------------------------------

CALL C:\ProgramData\Miniconda3\condabin\conda.bat activate py37
CALL python C:\Users\hr_automations\UUS_PC_PeopleAnalytics_Automation\Python_Jobs\leave_data_monthly_pull\leave_survey_qualtrics_data_pull.py > C:\Users\hr_automations\UUS_PC_PeopleAnalytics_Automation\Python_Jobs\leave_data_monthly_pull\leave_data_pull_log.txt