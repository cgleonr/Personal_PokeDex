@echo off
title Personal Pokédex - Standalone Application
color 0A

echo ========================================
echo  Personal Pokédex - Standalone App
echo ========================================
echo.

REM Change to the script's directory
cd /d "%~dp0"

REM Check if Python is available (try both 'python' and 'py')
set PYTHON_CMD=
echo Checking for Python...
python --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python
    python --version
) else (
    py --version >nul 2>&1
    if not errorlevel 1 (
        set PYTHON_CMD=py
        py --version
    ) else (
        echo.
        echo ERROR: Python is not installed or not in PATH
        echo Please install Python 3.7 or higher
        echo.
        echo You can download Python from: https://www.python.org/downloads/
        echo.
        pause
        exit /b 1
    )
)
echo.

REM Check if pokedex_standalone.py exists
if not exist "pokedex_standalone.py" (
    echo ERROR: pokedex_standalone.py not found!
    echo Current directory: %CD%
    echo.
    pause
    exit /b 1
)

REM Check if data directory exists
if not exist "data" (
    echo ERROR: data directory not found!
    echo Please make sure you're running this from the project directory.
    echo.
    pause
    exit /b 1
)

REM Check if required packages are installed
echo Checking dependencies...
%PYTHON_CMD% -c "import flask, webview" 2>nul
if errorlevel 1 (
    echo.
    echo Some required packages are missing. Installing...
    echo This may take a few minutes...
    echo.
    %PYTHON_CMD% -m pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to install required packages
        echo Please check your internet connection and try again.
        echo.
        pause
        exit /b 1
    )
    echo.
    echo Dependencies installed successfully!
    echo.
) else (
    echo Dependencies OK!
    echo.
)

REM Start the standalone application
echo ========================================
echo Starting Pokédex standalone application...
echo ========================================
echo.
echo A window will open automatically.
echo Keep this window open while using the Pokédex.
echo Close the window to exit.
echo.
echo If you see any errors below, please report them.
echo.

REM Run the Python script and capture output
%PYTHON_CMD% pokedex_standalone.py

REM Check exit code
set EXIT_CODE=%ERRORLEVEL%

if %EXIT_CODE% neq 0 (
    echo.
    echo ========================================
    echo ERROR: Application failed to start
    echo Exit code: %EXIT_CODE%
    echo ========================================
    echo.
    echo Common issues:
    echo - Make sure Python 3.7+ is installed
    echo - Check that all dependencies are installed
    echo - Verify data files exist in the data\ directory
    echo - Try running: python pokedex_standalone.py
    echo.
)

echo.
echo Application closed.
pause

