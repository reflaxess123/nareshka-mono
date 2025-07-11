@echo off
setlocal enabledelayedexpansion
title Nareshka Development Servers (NEW ARCHITECTURE)

echo ==========================================
echo NARESHKA DEVELOPMENT SERVERS STARTUP
echo *** NEW ARCHITECTURE v2.0 ***
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

REM Check NEW ARCHITECTURE FILES
echo -> Checking NEW ARCHITECTURE files...
if not exist "back/main.py" (
    echo ❌ ERROR: 'back/main.py' not found.
    echo    NEW ARCHITECTURE requires main.py file.
    pause
    exit /b 1
)

if not exist "back/main_old.py" (
    echo ⚠️  WARNING: 'back/main_old.py' not found.
    echo    No rollback file available.
)

if not exist "back/app/config/new_settings.py" (
    echo ❌ ERROR: 'back/app/config/new_settings.py' not found.
    echo    NEW ARCHITECTURE requires new_settings.py file.
    pause
    exit /b 1
)

if not exist "back/app/presentation/api" (
    echo ❌ ERROR: 'back/app/presentation/api' directory not found.
    echo    NEW ARCHITECTURE requires presentation layer.
    pause
    exit /b 1
)

echo ✓ NEW ARCHITECTURE files verified

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

REM Verify NEW ARCHITECTURE can be imported
echo -> Testing NEW ARCHITECTURE import...
poetry run python -c "import main; print('NEW ARCHITECTURE verified')" >nul 2>&1
if !errorlevel! neq 0 (
    echo ❌ ERROR: NEW ARCHITECTURE import failed.
    echo    Please check main.py and dependencies.
    cd..
    pause
    exit /b 1
) else (
    echo ✓ NEW ARCHITECTURE import successful
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

REM Check for .env file and show DB/Redis config
if not exist "back/.env" (
    echo ❌ ERROR: 'back/.env' file not found.
    echo    Please create and configure your backend .env file.
    pause
    exit /b 1
) else (
    echo ✓ Found back/.env
    echo Current DATABASE_URL and REDIS_URL:
    for /f "usebackq tokens=*" %%a in (`findstr /b /c:"DATABASE_URL=" back/.env`) do echo   %%a
    for /f "usebackq tokens=*" %%a in (`findstr /b /c:"REDIS_URL=" back/.env`) do echo   %%a
)

REM === Auto-update DATABASE_URL and REDIS_URL in .env ===
set NEW_DATABASE_URL=DATABASE_URL=postgresql://postgres:nbmbovmpeoz9pyjw@103.74.93.55:8001/postgres
set NEW_REDIS_URL=REDIS_URL=redis://default:qe1yqfyuv0oo0ysg@103.74.93.55:6384
powershell -Command "(Get-Content back/.env) -replace '^DATABASE_URL=.*', '%NEW_DATABASE_URL%' | Set-Content back/.env"
powershell -Command "(Get-Content back/.env) -replace '^REDIS_URL=.*', '%NEW_REDIS_URL%' | Set-Content back/.env"

echo.
echo ==========================================
echo STARTING SERVERS (NEW ARCHITECTURE)
echo ==========================================

REM Start backend with error checking
echo -> Starting Python backend server (NEW ARCHITECTURE)...
echo   Command: poetry run uvicorn main:app --host 0.0.0.0 --port 4000 --reload --reload-exclude logs/* --reload-exclude *.log
echo   Architecture: Clean Architecture with DI, UnitOfWork, v2 APIs
start "Nareshka Backend NEW ARCH (Port 4000)" cmd /k "cd /d %~dp0back && echo Starting NEW ARCHITECTURE backend... && echo Available endpoints: /api/v2/auth, /api/v2/content, /api/v2/theory, etc. && poetry run uvicorn main:app --host 0.0.0.0 --port 4000 --reload --reload-exclude logs/* --reload-exclude *.log || (echo NEW ARCHITECTURE backend failed to start! && pause)"

REM Wait and check if backend started
echo Waiting for NEW ARCHITECTURE backend to initialize...
timeout /t 5 /nobreak >nul

REM Quick backend health check
for /L %%i in (1,1,15) do (
    curl -s http://localhost:4000/api/health >nul 2>&1
    if !errorlevel! equ 0 (
        echo ✓ NEW ARCHITECTURE backend is responding
        goto backend_ready
    )
    timeout /t 1 /nobreak >nul
)
echo ⚠️  NEW ARCHITECTURE backend might not be ready yet (will continue anyway)

:backend_ready

REM Start frontend
echo.
echo -> Starting Node.js frontend server...
echo   Command: npm run dev
echo   Note: Frontend will connect to NEW ARCHITECTURE endpoints /api/v2/*
start "Nareshka Frontend (Port 5173)" cmd /k "cd /d %~dp0front && echo Starting frontend for NEW ARCHITECTURE... && echo Backend endpoints: /api/v2/auth, /api/v2/content, etc. && npm run dev || (echo Frontend failed to start! && pause)"

echo.
echo ==========================================
echo NEW ARCHITECTURE SERVERS STARTUP COMPLETED
echo ==========================================
echo.
echo 🌐 Backend:     http://localhost:4000
echo 🎨 Frontend:    http://localhost:5173
echo 📚 API Docs:    http://localhost:4000/docs
echo 🔧 Health:      http://localhost:4000/api/health
echo 🔑 Auth v2:     http://localhost:4000/api/v2/auth
echo 📄 Content v2:  http://localhost:4000/api/v2/content
echo 🎓 Theory v2:   http://localhost:4000/api/v2/theory
echo 📝 Tasks v2:    http://localhost:4000/api/v2/tasks
echo 📊 Progress v2: http://localhost:4000/api/v2/progress
echo 🛠️  Admin v2:    http://localhost:4000/api/v2/admin
echo.
echo 🏗️  Architecture: Clean Architecture with DI, UnitOfWork, Services
echo 🔧 Features: JWT Auth, Redis Sessions, Async Operations
echo.
echo Check the separate windows for server logs and status.
echo.
echo 💡 To stop servers: Close the backend and frontend windows
echo    or use Ctrl+C in each window
echo.
echo 🔄 To rollback to OLD ARCHITECTURE: run start-dev.bat
echo    (requires main_old.py to be present)
echo.

REM Ask user if they want to open browser
set /p "open_browser=Open browser automatically? (y/n): "
if /i "!open_browser!"=="y" (
    echo Opening browser...
    timeout /t 2 >nul
    start http://localhost:5173
    timeout /t 2 >nul
    start http://localhost:4000/docs
)

echo.
echo 🚀 NEW ARCHITECTURE development environment is ready!
echo This window can be safely closed.
echo.
echo Architecture Details:
echo - Domain Layer: Entities, Repositories, Services
echo - Application Layer: DTOs, Services, Use Cases  
echo - Infrastructure Layer: Database, External APIs
echo - Presentation Layer: API Controllers (v2)
echo.
pause 