@echo off
setlocal enabledelayedexpansion
title Nareshka Development Servers (Current Architecture)

echo ==========================================
echo NARESHKA DEVELOPMENT SERVERS STARTUP
echo *** CURRENT FEATURE-BASED ARCHITECTURE ***
echo ==========================================
echo.

REM Kill processes on development ports
echo -> Cleaning up existing processes...
for %%p in (4000 5173) do (
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr /i ":%%p" 2^>nul') do (
        if not "%%a"=="" if not "%%a"=="0" (
            echo Killing process PID %%a on port %%p
            taskkill /PID %%a /F >nul 2>&1
        )
    )
)

echo Process cleanup completed.
timeout /t 2 /nobreak >nul
echo.

REM Directory checks
if not exist "back" (
    echo ❌ ERROR: 'back' directory not found. 
    echo    Make sure you're running this from the project root.
    pause
    exit /b 1
)

if not exist "front" (
    echo ❌ ERROR: 'front' directory not found. 
    echo    Make sure you're running this from the project root.
    pause
    exit /b 1
)

if not exist "back/main.py" (
    echo ❌ ERROR: 'back/main.py' not found.
    pause
    exit /b 1
)

if not exist "back/.env" (
    echo ❌ ERROR: 'back/.env' file not found.
    echo    Please create and configure your backend .env file.
    pause
    exit /b 1
)

echo ✓ Basic files verified

REM Check Poetry
echo -> Checking Poetry installation...
poetry --version >nul 2>&1
if !errorlevel! neq 0 (
    echo ❌ ERROR: Poetry not found. Please install Poetry.
    pause
    exit /b 1
) else (
    echo ✓ Poetry found
)

REM Check Node.js
echo -> Checking Node.js installation...
node --version >nul 2>&1
if !errorlevel! neq 0 (
    echo ❌ ERROR: Node.js not found. Please install Node.js.
    pause
    exit /b 1
) else (
    echo ✓ Node.js found
)

echo.
echo ==========================================
echo STARTING SERVERS (Hot Reload ENABLED)
echo ==========================================
echo Backend will auto-restart on code changes (Uvicorn --reload)

REM Start backend
echo -> Starting Python backend server...
start "Nareshka Backend (Port 4000)" cmd /k "cd /d %~dp0back && echo Starting backend... && poetry run uvicorn main:app --host 0.0.0.0 --port 4000 --reload --reload-exclude logs/* --reload-exclude *.log || (echo Backend failed to start! && pause)"

REM Wait for backend
echo Waiting for backend to initialize...
timeout /t 5 /nobreak >nul

REM Start frontend
echo -> Starting frontend server...
start "Nareshka Frontend (Port 5173)" cmd /k "cd /d %~dp0front && echo Starting frontend... && npm run dev || (echo Frontend failed to start! && pause)"

echo.
echo ==========================================
echo SERVERS STARTUP COMPLETED
echo ==========================================
echo.
echo 🌐 Backend:     http://localhost:4000
echo 🎨 Frontend:    http://localhost:5173
echo 📚 API Docs:    http://localhost:4000/docs
echo 🔧 Health:      http://localhost:4000/api/health
echo.

set /p "open_browser=Open browser automatically? (y/n): "
if /i "!open_browser!"=="y" (
    echo Opening browser...
    timeout /t 2 >nul
    start http://localhost:5173
    timeout /t 2 >nul
    start http://localhost:4000/docs
)

echo.
echo 🚀 Development environment is ready!
echo This window can be safely closed.
echo.
pause 