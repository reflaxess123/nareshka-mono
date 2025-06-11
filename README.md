# Nareshka - Деплой через Dokploy

## Описание

Проект Nareshka состоит из:

- **Backend**: FastAPI приложение с PostgreSQL и Redis
- **Frontend**: React + Vite приложение с Nginx

## Структура

```
nareshka/
├── back/                 # Backend (FastAPI)
│   ├── app/             # Исходный код приложения
│   ├── alembic/         # Миграции базы данных
│   ├── Dockerfile       # Docker образ для бэкенда
│   └── main.py          # Точка входа
├── front/               # Frontend (React + Vite)
│   ├── src/            # Исходный код фронтенда
│   ├── Dockerfile      # Docker образ для фронтенда
│   └── package.json    # Зависимости Node.js
├── docker-compose.yml   # Конфигурация Docker Compose
└── .env                # Переменные окружения
```

## Деплой через Dokploy

### 1. Подготовка

1. Убедитесь, что у вас настроен Dokploy на сервере
2. Клонируйте репозиторий на свой Dokploy сервер
3. Настройте переменные окружения в файле `.env`

### 2. Конфигурация Dokploy

1. В Dokploy создайте новое приложение типа **Docker Compose**
2. Укажите путь к файлу `docker-compose.yml`
3. Настройте переменные окружения в разделе **Environment**

### 3. Переменные окружения

Настройте следующие переменные в Dokploy:

```env
# База данных
DATABASE_URL=postgresql://user:password@host:5432/database

# Redis
REDIS_URL=redis://user:password@host:6379/0

# JWT
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Режим
DEBUG=false

# WebDAV (опционально)
WEBDAV_URL=your-webdav-url
WEBDAV_USERNAME=your-username
WEBDAV_PASSWORD=your-password

# Домен
DOKPLOY_DOMAIN=your-domain.com
```

### 4. Volumes

Проект использует следующие volumes для персистентности данных:

- `../files/backend-logs` - логи бэкенда
- `../files/backend-uploads` - загруженные файлы

Эти папки создадутся автоматически в директории Dokploy согласно рекомендациям.

### 5. Сеть

Приложения работают в одной Docker сети `nareshka-network`:

- **Backend**: доступен на порту 4000
- **Frontend**: доступен на порту 80, проксирует API запросы на бэкенд

### 6. Health Checks

Настроены проверки здоровья для обоих сервисов:

- Backend: `GET /health`
- Frontend: `GET /`

### 7. Запуск

После настройки в Dokploy нажмите кнопку **Deploy** для запуска приложения.

## Архитектура

- **Frontend** (Nginx) принимает все запросы на порту 80
- Статические файлы обслуживаются напрямую
- API запросы (пути начинающиеся с `/api`) проксируются на **Backend**
- **Backend** работает на внутреннем порту 4000
- Оба сервиса в одной Docker сети для безопасной коммуникации

## Мониторинг

Используйте встроенные возможности Dokploy для:

- Просмотра логов каждого сервиса
- Мониторинга ресурсов
- Управления деплоями
- Отслеживания health checks
