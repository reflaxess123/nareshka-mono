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

# Собираем приложение
RUN npm run build

# Стадия производства с nginx
FROM nginx:alpine

# Копируем собранное приложение
COPY --from=builder /app/dist /usr/share/nginx/html

# Копируем конфигурацию nginx
COPY nginx.conf /etc/nginx/nginx.conf

# Открываем порт
EXPOSE 80

# Запускаем nginx
CMD ["nginx", "-g", "daemon off;"] 