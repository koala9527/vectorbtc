@echo off
chcp 65001 >nul
title VectorBTC Launcher

echo ===================================================
echo             VectorBTC System Launcher
echo ===================================================
echo [1/2] Starting Backend service...
start "VectorBTC_Backend" cmd.exe /k "call \"%~dp0start_backend.bat\""

timeout /t 2 >nul

echo [2/2] Starting Frontend service...
start "VectorBTC_Frontend" cmd.exe /k "call \"%~dp0start_frontend.bat\""

echo.
echo ===================================================
echo  Services started successfully!
echo  - Backend Docs: http://localhost:8000/docs
echo  - Frontend UI:  http://localhost:5173
echo ===================================================
echo.
pause
