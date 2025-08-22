@echo off
setlocal enabledelayedexpansion
title Database Restore Tool

echo ==========================================
echo NARESHKA DATABASE RESTORE
echo ==========================================
echo.

REM Проверяем аргумент - имя файла для восстановления
if "%1"=="" (
    echo [INFO] Использование: restore.bat [имя_файла]
    echo [INFO] Доступные бэкапы:
    echo.
    if exist "backups\*.sql" (
        for %%f in (backups\backup_*.sql) do (
            echo   - %%~nxf
        )
    ) else (
        echo   [WARN] Бэкапы не найдены в папке backups\
    )
    echo.
    set /p "backup_file=Введите имя файла бэкапа: "
    if "!backup_file!"=="" (
        echo [ERROR] Имя файла не указано
        pause
        exit /b 1
    )
) else (
    set "backup_file=%1"
)

REM Добавляем путь к папке backups если нужно
if not exist "%backup_file%" (
    if exist "backups\%backup_file%" (
        set "backup_file=backups\%backup_file%"
    ) else (
        echo [ERROR] Файл %backup_file% не найден!
        pause
        exit /b 1
    )
)

echo [INFO] Восстановление из: %backup_file%
echo.

REM Предупреждение
echo [WARNING] Это действие ПОЛНОСТЬЮ ЗАМЕНИТ текущую базу данных!
echo [WARNING] Все текущие данные будут потеряны!
echo.
set /p "confirm=Продолжить? (y/N): "
if /i not "%confirm%"=="y" (
    echo [INFO] Операция отменена
    pause
    exit /b 0
)

echo.

REM Проверяем, что Docker контейнер запущен
echo [1/4] Проверка Docker контейнера...
docker ps --filter "name=nareshka-postgres-dev" --format "table {{.Names}}\t{{.Status}}" | findstr "nareshka-postgres-dev" >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] PostgreSQL контейнер не запущен!
    echo Запустите: docker-compose up -d
    pause
    exit /b 1
)
echo [OK] PostgreSQL контейнер найден

REM Останавливаем приложение если запущено
echo [2/4] Остановка приложения...
echo [INFO] Убиваем процессы Python (если есть)
taskkill /f /im python.exe >nul 2>&1
echo [OK] Приложение остановлено

REM Дропаем и создаем базу данных
echo [3/4] Пересоздание базы данных...
docker exec nareshka-postgres-dev psql -U postgres -c "DROP DATABASE IF EXISTS nareshka_dev;" >nul 2>&1
docker exec nareshka-postgres-dev psql -U postgres -c "CREATE DATABASE nareshka_dev;" >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Ошибка пересоздания БД!
    pause
    exit /b 1
)
echo [OK] База данных пересоздана

REM Восстанавливаем данные
echo [4/4] Восстановление данных...
type "%backup_file%" | docker exec -i nareshka-postgres-dev psql -U postgres -d nareshka_dev >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Ошибка восстановления данных!
    pause
    exit /b 1
)

echo.
echo ==========================================
echo RESTORE COMPLETED
echo ==========================================
echo [OK] База данных успешно восстановлена из %backup_file%
echo [OK] Можно запускать приложение
echo.
echo [INFO] Для запуска используйте: start.bat
echo.
pause