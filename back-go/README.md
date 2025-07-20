# Nareshka Go Backend

Бэкенд для образовательной платформы Nareshka, переписанный с Python FastAPI на Go с использованием адаптированной FSD архитектуры.

## Архитектура

Проект использует адаптированную FSD (Feature-Sliced Design) архитектуру:

```
back-go/
├── app/           # Инициализация приложения и провайдеры
├── shared/        # Общие утилиты, конфиг, типы, подключения к БД
├── entities/      # Бизнес-сущности (User, Task, Content, Progress)
├── features/      # Бизнес-фичи (Auth, TaskExecution, ContentManagement)
├── widgets/       # Композитные блоки (API Router)
└── pages/         # Точки входа (HTTP handlers)
```

## Технологии

- **Go 1.21+**
- **Gin** - HTTP router
- **GORM** - ORM для PostgreSQL
- **Redis** - кеширование и сессии
- **JWT** - аутентификация
- **bcrypt** - хеширование паролей
- **Docker** - для баз данных

## Быстрый старт

### 1. Установка зависимостей

```bash
# Установите Go 1.21+
# Установите Docker для баз данных

# Скачайте зависимости
make deps
```

### 2. Настройка окружения

```bash
# Скопируйте файл конфигурации
cp .env.example .env

# Отредактируйте .env под ваши настройки
```

### 3. Запуск баз данных

```bash
# Запустите PostgreSQL и Redis в Docker
make db-up
```

### 4. Запуск сервера

```bash
# Запустите Go сервер
make run

# Или напрямую
go run main.go
```

Сервер запустится на `http://localhost:8000`

## API Endpoints

### Аутентификация
- `POST /api/v1/auth/register` - Регистрация пользователя
- `POST /api/v1/auth/login` - Вход в систему
- `POST /api/v1/auth/logout` - Выход из системы
- `GET /api/v1/auth/me` - Текущий пользователь

### Пользователи
- `GET /api/v1/users/profile` - Профиль пользователя
- `PUT /api/v1/users/profile` - Обновление профиля

### Задачи (в разработке)
- `GET /api/v1/tasks/` - Список задач

### Контент (в разработке)  
- `GET /api/v1/content/` - Список контента

### Служебные
- `GET /health` - Health check

## Тестирование

```bash
# Запустите тесты
make test

# Протестируйте API endpoints
make test-api

# Или используйте curl
./test_server.sh
```

### Пример регистрации:

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com", 
    "password": "testpass123"
  }'
```

### Пример входа:

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "login": "testuser",
    "password": "testpass123"
  }'
```

## Структура базы данных

### Основные модели:

**User** - пользователи с ролями, прогрессом обучения
**Task** - задачи программирования с тест-кейсами  
**Content** - образовательный контент (теория, статьи)
**Progress** - отслеживание прогресса пользователей

## Команды Makefile

```bash
make run        # Запустить сервер
make build      # Собрать бинарник
make test       # Запустить тесты
make deps       # Скачать зависимости
make db-up      # Запустить базы данных
make db-down    # Остановить базы данных
make test-api   # Протестировать API
```

## Переменные окружения

```env
# Сервер
PORT=8000
HOST=0.0.0.0
ENV=development

# База данных PostgreSQL
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=nareshka

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Аутентификация
JWT_SECRET=your-super-secret-jwt-key
SESSION_SECRET=your-session-secret-key

# OpenAI (для AI генерации тестов)
OPENAI_API_KEY=your-openai-api-key
OPENAI_BASE_URL=https://api.proxyapi.ru/openai/v1
```

## Статус разработки

✅ **Базовая архитектура FSD**  
✅ **Модели данных**  
✅ **Аутентификация JWT**  
✅ **HTTP сервер и роутинг**  
✅ **Подключение к PostgreSQL/Redis**  

🔄 **В разработке:**
- Система выполнения кода
- AI генерация тестов  
- Управление контентом
- Отслеживание прогресса
- Админ панель

## Миграция с Python

Проект является переписанной версией Python FastAPI бэкенда. Основные изменения:

- **FastAPI → Gin** - HTTP framework
- **SQLAlchemy → GORM** - ORM
- **Pydantic → встроенная валидация Go** 
- **Async/await → горутины** для конкурентности
- **Clean Architecture → FSD** для лучшей структуры