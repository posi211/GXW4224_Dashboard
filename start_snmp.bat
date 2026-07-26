@echo off
title SNMP Monitor Launcher
cd /d %~dp0

:: 1. Clean up old processes silently
taskkill /F /IM python.exe /T >nul 2>&1

:: 2. Start the Collector — keep a visible log instead of nul
echo [*] Starting Services...
start /b "" python app.py > app_log.txt 2>&1

:: 3. Start the Dashboard in its own window
start streamlit run dashboard.py

exit