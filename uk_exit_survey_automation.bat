@echo off
rem ---------------------------------
rem build log for leave survey
rem ---------------------------------

CALL "C:\Users\ddy17\Anaconda3\condabin\conda.bat" activate base
CALL python "C:\Users\hr_automations\UUS_PC_PeopleAnalytics_Automation\Python_Jobs\uk_exit_survey_auto.py" > "C:\Users\hr_automations\UUS_PC_PeopleAnalytics_Automation\Python_Jobs\uk_exit_survey_log.txt"