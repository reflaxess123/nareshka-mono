# Стадия сборки
FROM node:20-alpine AS builder

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей
COPY package.json package-lock.json ./

# Устанавливаем зависимости
RUN npm ci --silent

# Копируем исходный код
COPY . .

# Используем продакшен конфигурацию если нет .env
RUN if [ ! -f .env ]; then cp .env.prod .env; fi

# Показываем содержимое .env для отладки
RUN echo "=== Content of .env ===" && cat .env

# Собираем приложение
RUN npm run build

# Показываем что собралось
RUN echo "=== Built files ===" && ls -la dist/

# Стадия производства с nginx
FROM nginx:alpine

# Копируем собранное приложение
COPY --from=builder /app/dist /usr/share/nginx/html

# Удаляем дефолтную конфигурацию и копируем нашу
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/nginx.conf

# Открываем порт
EXPOSE 80

# Запускаем nginx
CMD ["nginx", "-g", "daemon off;"] 