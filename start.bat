@echo off
chcp 936 >nul
title i志愿 考勤比对工具
cd /d "%~dp0"

if not exist venv\Scripts\python.exe (
    echo [提示] 首次使用请先双击 setup.bat 安装环境！
    pause
    exit /b 1
)

echo ============================================
echo    i志愿 考勤比对工具
echo    浏览器将自动打开: http://localhost:8000
echo    按 Ctrl+C 停止服务
echo ============================================
echo.

start "" http://localhost:8000

venv\Scripts\python.exe app.py

pause
