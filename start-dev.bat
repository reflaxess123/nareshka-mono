@echo off
setlocal enabledelayedexpansion
title Nareshka Development Servers

echo ==========================================
echo NARESHKA DEVELOPMENT SERVERS STARTUP
echo ==========================================
echo.

REM Safer process killing - only specific processes
echo -> Cleaning up existing development processes...

REM Kill only processes running on our specific ports (more targeted)
echo Checking for processes on development ports...
for %%p in (4000 5173 5174 5175 5176) do (
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr /i ":%%p" 2^>nul') do (
        if not "%%a"=="" if not "%%a"=="0" (
            echo Killing process PID %%a on port %%p
            taskkill /PID %%a /F >nul 2>&1
            if !errorlevel! equ 0 (
                echo   ✓ Successfully killed PID %%a
            ) else (
                echo   ✗ Failed to kill PID %%a
            )
        )
    )
)

REM More targeted killing - only uvicorn processes (not all Python)
echo Killing existing uvicorn processes...
for /f "tokens=2" %%a in ('tasklist /fi "imagename eq python.exe" /fo csv ^| findstr uvicorn 2^>nul') do (
    if not "%%a"=="" (
        echo Killing uvicorn process %%a
        taskkill /PID %%a /F >nul 2>&1
    )
)

REM Kill Node processes only if they're running on our ports
echo Checking for Node.js processes on our ports...
for /f "tokens=2,5" %%a in ('netstat -ano ^| findstr ":5173\|:5174\|:5175" 2^>nul') do (
    if not "%%b"=="" (
        tasklist /fi "pid eq %%b" /fi "imagename eq node.exe" >nul 2>&1
        if !errorlevel! equ 0 (
            echo Killing Node.js process PID %%b
            taskkill /PID %%b /F >nul 2>&1
        )
    )
)

echo Process cleanup completed.
echo.

REM Wait for processes to fully terminate
echo Waiting for processes to terminate...
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

REM Check Poetry availability
echo -> Checking Poetry installation...
poetry --version >nul 2>&1
if !errorlevel! neq 0 (
    echo ❌ ERROR: Poetry not found or not in PATH.
    echo    Please install Poetry: https://python-poetry.org/docs/#installation
    pause
    exit /b 1
) else (
    echo ✓ Poetry found
)

REM Check if Poetry project is set up
cd back
poetry env info >nul 2>&1
if !errorlevel! neq 0 (
    echo ⚠️  WARNING: Poetry environment not found. Installing dependencies...
    poetry install
    if !errorlevel! neq 0 (
        echo ❌ ERROR: Failed to install Poetry dependencies
        cd..
        pause
        exit /b 1
    )
) else (
    echo ✓ Poetry environment ready
)
cd..

REM Check Node.js and npm
echo -> Checking Node.js installation...
node --version >nul 2>&1
if !errorlevel! neq 0 (
    echo ❌ ERROR: Node.js not found. Please install Node.js.
    pause
    exit /b 1
) else (
    echo ✓ Node.js found
)

REM Check if npm dependencies are installed
cd front
if not exist "node_modules" (
    echo ⚠️  WARNING: Node modules not found. Installing dependencies...
    npm install
    if !errorlevel! neq 0 (
        echo ❌ ERROR: Failed to install npm dependencies
        cd..
        pause
        exit /b 1
    )
) else (
    echo ✓ Node modules ready
)
cd..

echo.
echo ==========================================
echo STARTING SERVERS
echo ==========================================

REM Start backend with error checking
echo -> Starting Python backend server...
echo   Command: poetry run uvicorn main:app --host 0.0.0.0 --port 4000 --reload
start "Nareshka Backend (Port 4000)" cmd /k "cd /d %~dp0back && echo Starting backend... && poetry run uvicorn main:app --host 0.0.0.0 --port 4000 --reload || (echo Backend failed to start! && pause)"

REM Wait and check if backend started
echo Waiting for backend to initialize...
timeout /t 3 /nobreak >nul

REM Quick backend health check
for /L %%i in (1,1,10) do (
    curl -s http://localhost:4000/docs >nul 2>&1
    if !errorlevel! equ 0 (
        echo ✓ Backend is responding
        goto backend_ready
    )
    timeout /t 1 /nobreak >nul
)
echo ⚠️  Backend might not be ready yet (will continue anyway)

:backend_ready

REM Start frontend
echo.
echo -> Starting Node.js frontend server...
echo   Command: npm run dev
start "Nareshka Frontend (Port 5173)" cmd /k "cd /d %~dp0front && echo Starting frontend... && npm run dev || (echo Frontend failed to start! && pause)"

echo.
echo ==========================================
echo SERVERS STARTUP COMPLETED
echo ==========================================
echo.
echo 🌐 Backend:  http://localhost:4000
echo 🎨 Frontend: http://localhost:5173
echo 📚 API Docs: http://localhost:4000/docs
echo.
echo Check the separate windows for server logs and status.
echo.
echo 💡 To stop servers: Close the backend and frontend windows
echo    or use Ctrl+C in each window
echo.

REM Ask user if they want to open browser
set /p "open_browser=Open browser automatically? (y/n): "
if /i "!open_browser!"=="y" (
    echo Opening browser...
    timeout /t 2 >nul
    start http://localhost:5173
)

echo.
echo 🚀 Development environment is ready!
echo This window can be safely closed.
pause 