@echo off
title iVolunteer Manager Tool - Setup
cd /d "%~dp0"

echo ============================================
echo   iVolunteer Manager Tool - Setup
echo   Checking Python environment...
echo ============================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo Please install Python 3.10+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo [1/2] Creating virtual environment...
if not exist venv (
    python -m venv venv
) else (
    echo       Virtual environment already exists, skip
)

echo [2/2] Installing dependencies (needs internet, 2-3 min)...
venv\Scripts\python.exe -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple
venv\Scripts\python.exe -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

echo.
echo ============================================
echo   Setup complete! Run start.bat to launch.
echo ============================================
pause
