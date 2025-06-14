#!/bin/sh
set -e

# --- Динамическая настройка прав для Docker-in-Docker ---

# Получаем GID (ID группы) Docker-сокета на хосте
DOCKER_SOCKET_GID=$(stat -c '%g' /var/run/docker.sock)

# Создаем группу 'docker' с таким же GID внутри контейнера, если она еще не существует
if ! getent group $DOCKER_SOCKET_GID >/dev/null; then
    addgroup --gid $DOCKER_SOCKET_GID docker
fi

# Добавляем пользователя 'app' в группу 'docker'.
# Это даст приложению права на использование сокета.
usermod -aG $DOCKER_SOCKET_GID app

# --- Подготовка окружения приложения ---

# Меняем владельца общей директории на пользователя app,
# чтобы у приложения были права на запись.
# Это необходимо, т.к. Docker монтирует директорию от root.
chown app:app /tmp/nareshka-executions

# --- Запуск приложения ---

# Запускаем основную команду (из CMD) от имени пользователя "app"
exec runuser -u app -- "$@" 