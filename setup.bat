@echo off
chcp 936 >nul
title i志愿 考勤比对工具 - 环境安装
cd /d "%~dp0"

echo ============================================
echo   i志愿 考勤比对工具 - 环境安装
echo   正在检查 Python 环境...
echo ============================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python！
    echo 请先到 https://www.python.org/downloads/ 下载安装 Python 3.10 或更高版本
    echo 安装时务必勾选 "Add Python to PATH"，然后重新运行本脚本。
    pause
    exit /b 1
)

echo [1/2] 创建虚拟环境...
if not exist venv (
    python -m venv venv
) else (
    echo       虚拟环境已存在，跳过
)

echo [2/2] 安装依赖（需联网，约 2-3 分钟）...
venv\Scripts\python.exe -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple
venv\Scripts\python.exe -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

echo.
echo ============================================
echo   环境安装完成！请双击 start.bat 启动工具
echo ============================================
pause
