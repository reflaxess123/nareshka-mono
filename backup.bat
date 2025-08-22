@echo off
setlocal
title Database Backup Tool

echo ==========================================
echo NARESHKA DATABASE BACKUP
echo ==========================================
echo.

REM Получаем текущую дату и время для имени файла
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YY=%dt:~2,2%" & set "YYYY=%dt:~0,4%" & set "MM=%dt:~4,2%" & set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%" & set "MIN=%dt:~10,2%" & set "SS=%dt:~12,2%"
set "datestamp=%YYYY%-%MM%-%DD_%HH-%MIN-%SS%"

REM Имя файла бэкапа
set "backup_file=backup_%datestamp%.sql"

echo [INFO] Создание бэкапа: %backup_file%
echo [INFO] Время: %DD%.%MM%.%YYYY% %HH%:%MIN%:%SS%
echo.

REM Проверяем, что Docker контейнер запущен
echo [1/3] Проверка Docker контейнера...
docker ps --filter "name=nareshka-postgres-dev" --format "table {{.Names}}\t{{.Status}}" | findstr "nareshka-postgres-dev" >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] PostgreSQL контейнер не запущен!
    echo Запустите: docker-compose up -d
    pause
    exit /b 1
)
echo [OK] PostgreSQL контейнер найден

REM Создаем директорию для бэкапов если её нет
echo [2/3] Подготовка директории...
if not exist "backups" (
    mkdir backups
    echo [OK] Создана папка backups
) else (
    echo [OK] Папка backups существует
)

REM Создаем бэкап
echo [3/3] Создание бэкапа базы данных...
docker exec nareshka-postgres-dev pg_dump -U postgres nareshka_dev > "backups\%backup_file%"

if %errorlevel% neq 0 (
    echo [ERROR] Ошибка создания бэкапа!
    pause
    exit /b 1
)

REM Проверяем размер файла
for %%F in ("backups\%backup_file%") do set "size=%%~zF"
set /a "size_mb=%size% / 1024 / 1024"

echo.
echo ==========================================
echo BACKUP COMPLETED
echo ==========================================
echo [OK] Файл: backups\%backup_file%
echo [OK] Размер: %size_mb% MB
echo [OK] Время: %HH%:%MIN%:%SS%
echo.

REM Показываем список последних бэкапов
echo [INFO] Последние 5 бэкапов:
dir /b /o-d "backups\backup_*.sql" 2>nul | head -5 2>nul || (
    for /f %%i in ('dir /b /o-d "backups\backup_*.sql" 2^>nul') do (
        set /a count+=1
        if !count! leq 5 echo   - %%i
    )
)

echo.
echo [INFO] Для восстановления используйте: restore.bat %backup_file%
echo [INFO] Готово! Можно безопасно закрыть окно.
echo.
pause