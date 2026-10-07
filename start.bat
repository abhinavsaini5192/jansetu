@echo off
setlocal enabledelayedexpansion
title JanSetu Platform Launcher

echo ===================================================
echo             JanSetu Platform Launcher              
echo ===================================================
echo.

set "ROOT_DIR=%~dp0"
set "BACKEND_DIR=%ROOT_DIR%jansetu-backend"

:: Detect Python environment
set "PY_CMD=python"
if exist "%BACKEND_DIR%\.venv\Scripts\python.exe" (
    set "PY_CMD=%BACKEND_DIR%\.venv\Scripts\python.exe"
    echo [*] Found virtualenv at: jansetu-backend\.venv
) else if exist "%BACKEND_DIR%\venv\Scripts\python.exe" (
    set "PY_CMD=%BACKEND_DIR%\venv\Scripts\python.exe"
    echo [*] Found virtualenv at: jansetu-backend\venv
) else (
    echo [*] Using system Python
)

echo.
echo [1/2] Launching Backend (FastAPI on http://localhost:8000)...
start "JanSetu Backend (FastAPI)" cmd /k "cd /d "%BACKEND_DIR%" && "%PY_CMD%" run.py"

echo [2/2] Launching Frontend (Vite on http://localhost:3000)...
start "JanSetu Frontend (React + Vite)" cmd /k "cd /d "%ROOT_DIR%" && npm run dev"

echo.
echo ===================================================
echo   JanSetu is running!
echo.
echo   - Frontend Portal  : http://localhost:3000
echo   - Backend API      : http://localhost:8000
echo   - API Swagger Docs : http://localhost:8000/docs
echo ===================================================
echo.
echo Leave the opened terminal windows running while using the app.
echo.
pause
