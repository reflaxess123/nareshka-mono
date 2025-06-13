# Этап сборки
FROM node:20-alpine as build

WORKDIR /app

# Копируем package.json и package-lock.json
COPY package*.json ./

# Устанавливаем все зависимости (включая dev для сборки)
RUN npm ci

# Копируем исходный код
COPY . .

# Создаем продакшн сборку
RUN npm run build

# Продакшн этап с nginx
FROM nginx:alpine

# Копируем собранное приложение
COPY --from=build /app/dist /usr/share/nginx/html

# Копируем кастомную конфигурацию nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"] 