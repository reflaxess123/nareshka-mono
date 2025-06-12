@echo off
echo 🚀 Запускаю Nareshka для разработки...
docker-compose -f docker-compose.dev.yml up -d

echo.
echo ✅ Готово! Доступно по адресам:
echo 🎨 Фронтенд: http://localhost:3001
echo ⚙️ Бэкенд: http://localhost:4000
echo 📚 API документация: http://localhost:4000/api-docs
echo.
echo 📋 Для просмотра логов: docker-compose -f docker-compose.dev.yml logs -f
echo ⏹️ Для остановки: docker-compose -f docker-compose.dev.yml down
pause 