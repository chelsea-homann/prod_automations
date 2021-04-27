@echo off
rem ---------------------------------
rem build log for monthly ldp worday data pull
rem ---------------------------------

CALL C:\ProgramData\Miniconda3\condabin\conda.bat activate py37
CALL python C:\Users\hr_automations\UUS_PC_PeopleAnalytics_Automation\Python_Jobs\ldp_workday_monthly_pull_automation\ldp_workday_data_monthly_pull.py > C:\Users\hr_automations\UUS_PC_PeopleAnalytics_Automation\Python_Jobs\ldp_workday_monthly_pull_automation\ldp_workday_data_monthly_pull_log.txt
pause >nul