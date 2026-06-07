@echo off
chcp 65001 >nul
cd /d "%~dp0.."
powershell -NoProfile -ExecutionPolicy Bypass -File "scripts\push_and_deploy.ps1"
pause
