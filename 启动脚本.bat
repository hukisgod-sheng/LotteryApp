@echo off
chcp 65001 >nul
title 炸裂双色球数据沙盘
color 0A

cd /d "%~dp0"

echo ========================================
echo   炸裂双色球数据沙盘 - 启动中...
echo ========================================
echo.

:: 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.10 或更高版本
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version 2^>^&1') do echo [OK] %%i

:: 检查 Streamlit（未安装则自动装依赖）
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo [提示] 首次运行，正在安装依赖，请稍候...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [错误] 依赖安装失败
        pause
        exit /b 1
    )
)

echo [OK] 依赖就绪
echo [OK] 服务地址: http://localhost:8501
echo.
echo 提示: 保持本窗口打开；关闭窗口即停止服务
echo ========================================
echo.

:: 延迟 4 秒后自动打开浏览器（等服务起来）
start "" cmd /c "ping 127.0.0.1 -n 5 >nul && start http://localhost:8501"

:: 启动 Streamlit（headless 避免重复弹窗，由上面脚本打开浏览器）
python -m streamlit run app.py --server.port 8501 --server.headless true --browser.gatherUsageStats false

if errorlevel 1 (
    echo.
    echo [错误] 启动失败，请检查上方报错信息
    pause
    exit /b 1
)

pause
