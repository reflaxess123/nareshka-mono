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
COPY <<EOF /etc/nginx/conf.d/default.conf
server {
    listen 80;
    root /usr/share/nginx/html;
    index index.html;
    
    # Проксирование API запросов на бэкенд (приоритет 1)
    location /api {
        proxy_pass http://backend:4000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
    }
    
    # Статические ресурсы (приоритет 2)
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)\$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        try_files \$uri =404;
    }
    
    # SPA маршрутизация - все остальные запросы на index.html (приоритет 3)
    location / {
        try_files \$uri \$uri/ /index.html;
    }
    
    # Gzip сжатие
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied expired no-cache no-store private auth;
    gzip_types text/plain text/css text/xml text/javascript application/x-javascript application/javascript application/xml+rss;
}
EOF

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"] 