@echo off
rem ---------------------------------
rem build log for daily workday-qualtrics automations
rem ---------------------------------

CALL C:\ProgramData\Miniconda3\condabin\conda.bat activate py37
CALL python C:\Users\hr_automations\UUS_PC_PeopleAnalytics_Automation\Python_Jobs\wd_qualtrics_daily_automation\workday_qualtrics_daily_automations.py > C:\Users\hr_automations\UUS_PC_PeopleAnalytics_Automation\Python_Jobs\wd_qualtrics_daily_automation\wd_qualtrics_daily_automations_log.txt