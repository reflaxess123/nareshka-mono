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
