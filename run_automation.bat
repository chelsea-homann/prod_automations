@echo off
rem =========================================================
rem  Generic Automation Runner
rem =========================================================
rem  Usage:  run_automation.bat <script_name.py>
rem
rem  Example:
rem    run_automation.bat exit_survey_automation.py
rem    run_automation.bat workday_qualtrics_daily_sync.py
rem
rem  Prerequisites:
rem    1. Set environment variables (see config.env.example)
rem    2. Activate the correct Python/conda environment
rem =========================================================

rem --- Activate conda environment (adjust path and env name as needed) ---
CALL "%CONDA_PATH%\condabin\conda.bat" activate %CONDA_ENV%

rem --- Set the script directory to the location of this batch file ---
SET SCRIPT_DIR=%~dp0

rem --- Run the Python script and log output ---
SET SCRIPT_NAME=%~1
SET LOG_NAME=%SCRIPT_NAME:.py=_log.txt%

echo Running %SCRIPT_NAME%...
CALL python "%SCRIPT_DIR%%SCRIPT_NAME%" > "%SCRIPT_DIR%logs\%LOG_NAME%" 2>&1

IF %ERRORLEVEL% NEQ 0 (
    echo [FAILED] %SCRIPT_NAME% exited with error code %ERRORLEVEL%
) ELSE (
    echo [SUCCESS] %SCRIPT_NAME% completed
)
