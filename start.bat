@echo off
title iVolunteer Manager Tool
cd /d "%~dp0"

if not exist venv\Scripts\python.exe (
    echo [INFO] First time? Run setup.bat first to install dependencies.
    pause
    exit /b 1
)

echo ============================================
echo    iVolunteer Manager Tool
echo    Browser will open: http://localhost:8000
echo    Press Ctrl+C to stop
echo ============================================
echo.

start "" http://localhost:8000

venv\Scripts\python.exe app.py

pause
