@echo off
title SNMP Monitor Launcher
cd /d %~dp0

set PIDFILE=snmp_app.pid

:: 1. Stop ONLY our own previous instance (by exact PID) --
::    never touches any other python.exe process on the machine
if exist "%PIDFILE%" (
    for /f "usebackq" %%P in ("%PIDFILE%") do set OLDPID=%%P
    tasklist /FI "PID eq %OLDPID%" 2>NUL | find /I "%OLDPID%" >NUL
    if not errorlevel 1 (
        echo [*] Stopping previous instance ^(PID %OLDPID%^)...
        taskkill /F /PID %OLDPID% >nul 2>&1
    )
    del "%PIDFILE%" >nul 2>&1
)

:: 2. Start the Collector, capture its exact PID via PowerShell
echo [*] Starting Services...
for /f %%i in ('powershell -NoProfile -Command "(Start-Process python -ArgumentList 'app.py' -RedirectStandardOutput app_log.txt -RedirectStandardError app_log_err.txt -WindowStyle Hidden -PassThru).Id"') do set NEWPID=%%i
echo %NEWPID%>"%PIDFILE%"
echo [*] Collector started ^(PID %NEWPID%^)

:: 3. Start the Dashboard in its own window
start streamlit run dashboard.py

exit
