@echo off
setlocal
echo Updating OpenAPI schema and frontend client...

echo [1/2] Generating OpenAPI schema on backend...
pushd back >nul 2>&1
python scripts/generate_openapi.py
if %errorlevel% neq 0 (
    echo ERROR: Failed to generate OpenAPI schema
    popd >nul 2>&1
    pause
    exit /b 1
)
popd >nul 2>&1

echo [2/2] Updating frontend API client...
pushd front >nul 2>&1
npm run api:generate
if %errorlevel% neq 0 (
    echo ERROR: Failed to generate frontend client
    popd >nul 2>&1
    pause
    exit /b 1
)
popd >nul 2>&1

echo [OK] API updated successfully!
pause