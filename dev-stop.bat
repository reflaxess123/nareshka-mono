@echo off
echo ⏹️ Останавливаю Nareshka...
docker-compose -f docker-compose.dev.yml down

echo.
echo ✅ Остановлено!
pause 