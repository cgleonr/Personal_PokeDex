@echo off
title Personal Pokédex Launcher
color 0A

echo ========================================
echo    Personal Pokédex - Starting...
echo ========================================
echo.

REM Change to the script's directory
cd /d "%~dp0"

REM Check if Python is available (try both 'python' and 'py')
set PYTHON_CMD=
python --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python
) else (
    py --version >nul 2>&1
    if not errorlevel 1 (
        set PYTHON_CMD=py
    ) else (
        echo ERROR: Python is not installed or not in PATH
        echo Please install Python 3.7 or higher
        pause
        exit /b 1
    )
)

REM Check if required packages are installed
%PYTHON_CMD% -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    %PYTHON_CMD% -m pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install required packages
        pause
        exit /b 1
    )
)

REM Start the Flask server
echo Starting Pokédex server...
echo Browser will open automatically...
echo.
echo Press Ctrl+C to stop the server
echo.

%PYTHON_CMD% run.py

pause

