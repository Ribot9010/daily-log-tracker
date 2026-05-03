@echo off
REM Double-click this file to see your Daily Log stats.
REM The console window stays open until you press a key.

cd /d "%~dp0"
python analytics.py
echo.
pause
