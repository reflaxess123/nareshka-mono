@echo off
title Development Servers

REM Kill processes on specified ports
echo Checking for and killing processes on ports 4000, 5173, 5174, 5175, 5176...
for %%p in (4000 5173 5174 5175 5176) do (
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr /i ":%%p"') do (
        echo Attempting to kill PID: %%a on port %%p
        taskkill /PID %%a /F >nul 2>&1
    )
)
echo.

REM Start Python backend server
echo -> Starting Python backend server...
start "Python Backend" cmd /c "cd back && poetry run uvicorn main:app --host 0.0.0.0 --port 4000 --reload"
echo Backend server started.
echo.

REM Start Node.js frontend server
echo -> Starting Node.js frontend server...
start "Node.js Frontend" cmd /c "cd front && npm run dev"
echo Frontend server started.
echo.

echo ==========================================
echo All development servers are running.
echo Backend should be available at http://localhost:4000 (or check console output in the new backend window)
echo Frontend should be available at http://localhost:5173 (or check console output in the new frontend window)
echo.
echo To stop all servers, close the separate backend and frontend windows.
echo Press Ctrl+C in this window to stop this script, but the servers will continue running in their own windows.
echo ==========================================
echo.

pause 