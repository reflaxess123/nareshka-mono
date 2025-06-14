FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    procps \
    passwd \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Poetry
RUN pip install poetry

# Копируем файлы зависимостей
COPY pyproject.toml poetry.lock ./

# Конфигурируем Poetry
RUN poetry config virtualenvs.create false \
    && poetry install --without dev --no-interaction --no-ansi

# Копируем исходный код приложения
COPY . .

# Копируем и настраиваем entrypoint
COPY entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh

# Создаем непривилегированного пользователя
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app

# Устанавливаем entrypoint. Он будет запущен от root.
ENTRYPOINT ["entrypoint.sh"]

# Открываем порт
EXPOSE 4000

# Команда запуска, которая будет передана в entrypoint
# Она будет выполнена от пользователя app, как указано в entrypoint.sh
CMD ["python", "main.py"] 