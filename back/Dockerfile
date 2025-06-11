FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Poetry
RUN pip install poetry

# Копируем файлы зависимостей
COPY pyproject.toml poetry.lock ./

# Конфигурируем Poetry
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

# Копируем исходный код приложения
COPY . .

# Создаем непривилегированного пользователя
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Открываем порт
EXPOSE 4000

# Команда запуска
CMD ["python", "main.py"] 