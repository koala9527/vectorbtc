@echo off
chcp 65001 >nul
title VectorBTC Backend
cd /d "%~dp0backend"
echo [VectorBTC] Activating virtual environment...
call venv\Scripts\activate.bat
echo [VectorBTC] Starting FastAPI server on http://localhost:8000 ...
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
pause
