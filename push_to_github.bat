@echo off
title Push to GitHub - ticket-management
cd /d "%~dp0"
echo ========================================================
echo   Pushing Ticket Management to GitHub
echo   Target: https://github.com/Shyamprasadpatnaik/ticket-management
echo ========================================================
echo.
echo Make sure you have created the empty repository on GitHub:
echo https://github.com/new (Repository name: ticket-management)
echo.
"%LOCALAPPDATA%\Programs\Git\cmd\git.exe" push -u origin main
echo.
if %ERRORLEVEL% equ 0 (
    echo ========================================================
    echo   SUCCESS! Pushed to GitHub.
    echo   Now go to https://vercel.com/new to deploy!
    echo ========================================================
) else (
    echo ========================================================
    echo   Push failed. Please ensure:
    echo   1. The repo 'ticket-management' is created at https://github.com/new
    echo   2. You have logged in when GitHub prompts.
    echo ========================================================
)
pause
