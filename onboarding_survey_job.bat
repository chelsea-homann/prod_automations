@echo off
rem ---------------------------------
rem build log for leave survey
rem ---------------------------------

CALL C:\ProgramData\Miniconda3\condabin\conda.bat activate py37
CALL python C:\Users\hr_automations\UUS_PC_PeopleAnalytics_Automation\Python_Jobs\onboarding_survey_automation\onboarding_survey.py > C:\Users\hr_automations\UUS_PC_PeopleAnalytics_Automation\Python_Jobs\onboarding_survey_automation\onboarding_survey_log.txt