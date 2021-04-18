@echo off
rem ---------------------------------
rem build log for leave survey
rem ---------------------------------

CALL C:\ProgramData\Miniconda3\condabin\conda.bat activate py37
CALL python C:\Users\hr_automations\UUS_PC_PeopleAnalytics_Automation\Python_Jobs\leave_survey_automation\exit_survey_automation.py > C:\Users\hr_automations\UUS_PC_PeopleAnalytics_Automation\Python_Jobs\leave_survey_automation\exit_survey_log.txt