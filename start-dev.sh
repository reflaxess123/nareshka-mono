#!/bin/bash

ports=(4000 5173 5174 5175 5176)
for port in "${ports[@]}"; do
  echo "Ищем процессы на порту $port..."
  pids=$(sudo lsof -t -i :$port)
  if [ -n "$pids" ]; then
    echo "Убиваем PID: $pids"
    sudo kill -9 $pids
  fi
done

# Скрипт для одновременного запуска бэкенд и фронтенд серверов для разработки


# Выходить немедленно, если команда завершается с ошибкой
set -e

# Функция для остановки всех дочерних процессов при выходе
cleanup() {
    echo ""
    echo "Stopping development servers..."
    # Убиваем все дочерние процессы этого скрипта
    pkill -P $$
    echo "Servers stopped."
}

# Перехватываем сигналы прерывания (Ctrl+C) и завершения, чтобы вызвать функцию очистки
trap cleanup INT TERM

# --- Запуск Бэкенда ---
echo "-> Starting Python backend server..."
# Переходим в директорию back и запускаем сервер в фоновом режиме
(cd back && poetry run uvicorn main:app --host 0.0.0.0 --port 4000 --reload) &
BACK_PID=$!
echo "   Backend server started with PID $BACK_PID"

# --- Запуск Фронтенда ---
echo "-> Starting Node.js frontend server..."
# Переходим в директорию front и запускаем сервер в фоновом режиме
(cd front && npm run dev) &
FRONT_PID=$!
echo "   Frontend server started with PID $FRONT_PID"

echo ""
echo "=========================================="
echo "All development servers are running."
echo "Backend should be available at http://localhost:4000 (or check console output)"
echo "Frontend should be available at http://localhost:5173 (or check console output)"
echo ""
echo "Press Ctrl+C to stop all servers."
echo "=========================================="
echo ""

# Ожидаем завершения любого из фоновых процессов
# Это позволяет скрипту оставаться активным, пока дочерние процессы работают
wait -n

# Выполняем очистку, если один из серверов упал, чтобы остановить и второй
cleanup 