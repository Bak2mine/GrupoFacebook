@echo off
REM Leiloaria Smart - One-Click Setup Script for Windows

echo.
echo ========================================
echo Leiloaria Smart - Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

echo [1/3] Python found:
python --version
echo.

REM Install dependencies
echo [2/3] Installing Python packages from requirements.txt...
cd Grupo
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install packages
    pause
    exit /b 1
)
echo.

REM Install Playwright browsers
echo [3/3] Installing Playwright browsers (this may take a few minutes)...
playwright install
if errorlevel 1 (
    echo ERROR: Failed to install Playwright browsers
    echo Try running: playwright install
    pause
    exit /b 1
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To start the pipeline, run:
echo   cd Grupo
echo   python main.py
echo.
pause
