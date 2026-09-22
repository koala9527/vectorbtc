@echo off
chcp 65001 >nul
title VectorBTC Frontend
cd /d "%~dp0frontend"
echo [VectorBTC] Starting Vite dev server on http://localhost:5173 ...
npm run dev
pause
