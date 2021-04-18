@echo off
rem ---------------------------------
rem build log for leave survey data pull automation
rem ---------------------------------

CALL "C:\Users\ddy17\Anaconda3\condabin\conda.bat" activate base
CALL python "C:\Users\hr_automations\UUS_PC_PeopleAnalytics_Automation\Python_Jobs\leave_survey_qualtrics_data_pull.py" > "C:\Users\hr_automations\UUS_PC_PeopleAnalytics_Automation\Python_Jobs\leave_data_pull_log.txt"