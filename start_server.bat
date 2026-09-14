@echo off
title JK Paper Mill - Helpdesk Server
cd /d "%~dp0"
echo ========================================================
echo   Starting JK Paper Mill Helpdesk Server (MySQL)
echo   Local URL: http://127.0.0.1:8000/
echo ========================================================
if exist "..\venv\Scripts\activate.bat" (
    call "..\venv\Scripts\activate.bat"
) else if exist "venv\Scripts\activate.bat" (
    call "venv\Scripts\activate.bat"
)
python manage.py runserver 127.0.0.1:8000
pause
