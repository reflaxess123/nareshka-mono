# CLAUDE.md

Меня зовут Никалай

Этот файл предоставляет руководство для Claude Code (claude.ai/code) при работе с кодом в данном репозитории.

## Обзор проекта

**Nareshka** - современная платформа для изучения программирования с полноценной full-stack архитектурой. Включает интерактивный редактор кода с выполнением в Docker, базу интервью-вопросов с AI-категоризацией, ментальные карты для обучения и систему отслеживания прогресса.

### Ключевые особенности
- 📝 **8,560 вопросов интервью** из 380+ IT компаний с ML-категоризацией
- 🖥️ **Monaco Editor** с безопасным выполнением кода в Docker
- 🗺️ **Интерактивные ментальные карты** через React Flow
- 🤖 **AI-генерация тест-кейсов** для проверки кода
- 📊 **Система аналитики** и трекинга прогресса
- 🎨 **Полная темная тема** с адаптивным дизайном

## Команды разработки

### Frontend (React + TypeScript + Vite)
```bash
cd front
npm run dev          # Сервер разработки (порт 5173)
npm run build        # Сборка для продакшена  
npm run lint         # ESLint проверка кода
npm run type-check   # TypeScript проверка типов
npm run api:generate # Генерация API клиента из OpenAPI
npm run api:watch    # Автогенерация API при изменениях
```

### Backend (FastAPI + Python + Poetry)
```bash
cd back
poetry run uvicorn main:app --host 0.0.0.0 --port 4000 --reload  # Сервер разработки
poetry run ruff check .                      # Линтинг кода
poetry run ruff format .                     # Форматирование кода  
poetry run mypy . --config-file .mypy.ini    # Проверка типов
alembic upgrade head                         # Применение миграций БД
alembic revision --autogenerate -m "описание" # Создание миграции
```

### Быстрый старт разработки
```bash
# Windows - запуск frontend + backend с hot reload
start.bat

# Docker Compose - полный стек с PostgreSQL/Redis
docker-compose -f docker-compose.dev.yml up

# Продакшн деплой через Dokploy
docker-compose up -d
```

## Архитектура проекта

### Backend: Feature-First

#### Структура приложения
- `app/features/` - **Доменные модули** (auth, code_editor, interviews, mindmap, etc.)
- `app/shared/` - **Общие компоненты** (database, dependencies, middleware, schemas)
- `app/core/` - **Ядро приложения** (logging, error handlers, settings, health, rate limiter)

#### Ключевые модули в app/features/:
- **auth** - Session аутентификация с Redis
  - api/auth_router.py - эндпоинты входа, регистрации, обновления токенов
  - dto/auth_dto.py - схемы данных для auth
  - repositories/ - интерфейс и SQLAlchemy репозиторий пользователей
  - services/auth_service.py - бизнес-логика аутентификации

- **interviews** - Система интервью (8560 вопросов, 13 категорий, 380 компаний)
  - api/ - роутеры для категорий, компаний и вопросов интервью
  - dto/ - схемы ответов для категорий и интервью
  - repositories/ - работа с базой данных интервью
  - services/ - бизнес-логика обработки интервью

- **code_editor** - Monaco Editor + Docker выполнение + AI тесты
  - api/code_editor_router.py - эндпоинты выполнения кода
  - dto/ - схемы запросов, ответов и тест-кейсов
  - services/enhanced_code_executor_service.py - улучшенное выполнение кода
  - services/ai_test_generator_service.py - AI генерация тестов

- **mindmap** - React Flow интеграция для карт знаний
  - api/mindmap_router.py - эндпоинты генерации ментальных карт
  - config/mindmap_config.py - конфигурация технологий
  - utils/ - утилиты для расчета прогресса и построения запросов

- **progress** - Трекинг прогресса и аналитика
  - api/progress_router.py - эндпоинты управления прогрессом
  - dto/ - схемы запросов и ответов прогресса
  - repositories/ - работа с данными прогресса
  - utils/ - константы и валидаторы

- **theory** - Теоретические материалы с spaced repetition
  - api/theory_router.py - эндпоинты теоретических материалов
  - dto/ - схемы теоретических карточек
  - services/theory_service.py - логика работы с теорией

- **admin** - Административная панель
  - api/admin_router.py - защищенные эндпоинты администратора
  - decorators.py - декораторы для проверки прав администратора

- **logs** - Система логирования и мониторинга
  - api/logs_router.py - эндпоинты просмотра логов и websocket streaming
  
- **stats** - Статистика и аналитика
  - api/stats_router.py - эндпоинты получения статистических данных
  
- **task** - Управление заданиями и квизами
  - api/task_router.py - эндпоинты работы с заданиями
  - repositories/ - репозитории заданий, попыток, квизов

- **content** - Управление контентом платформы
  - api/content_router.py - эндпоинты контента
  - repositories/content_repository.py - работа с блоками контента

- **visualization** - Визуализация данных
  - api/cluster_visualization_router.py - эндпоинты визуализации кластеров
  - services/universe_calculator.py - расчет 3D координат для визуализации

#### Архитектурные паттерны
- **Dependency Injection** - собственный DI контейнер в shared/di/
- **Repository Pattern** - абстракция доступа к данным
- **Service Layer** - бизнес-логика
- **Feature-First** - модульная организация по доменам
- **DTO Pattern** - отдельные схемы для запросов/ответов

### Frontend: Feature-Sliced Design (FSD)

- `src/app/` - **Конфигурация приложения**
  - providers/ - глобальные провайдеры (auth, modal, notification, query, redux, router)
  - styles/ - глобальные стили с темами (base, light, dark)
  
- `src/pages/` - **Страницы** и роутинг
  - Home/ - главная страница
  - Landing/ - лендинг
  - Learning/ - страница обучения с Redux store
  - CodeEditor/ - редактор кода
  - MindMap/ - ментальные карты
  - InterviewDetail/ - детальный просмотр интервью
  - Admin/ - административные страницы (DetailedStats, UserManagement)
  - Profile/, Settings/, Adminka/ - профиль и настройки

- `src/widgets/` - **Композитные UI блоки**
  - AdminDashboard/ - административная панель
  - CodeEditorWidget/ - виджет редактора кода
  - InterviewAnalyticsDashboard/ - аналитика интервью
  - InterviewCategorySidebar/ - сайдбар категорий
  - MindMapProgressSidebar/ - прогресс ментальных карт
  - ProgressAnalyticsDashboard/ - аналитика прогресса
  - UniversalContentList/ - универсальный список контента
  - UserProgressDashboard/ - дашборд прогресса пользователя
  - Sidebar/ - основной сайдбар с Redux slice

- `src/features/` - **Бизнес-функции**
  - LoginForm/, RegisterForm/ - формы авторизации с валидацией
  - InterviewSearch/ - поиск по интервью
  - ContentProgress/ - отображение прогресса контента
  - TechnologySwitcher/ - переключатель технологий
  - UnifiedFilters/ - унифицированная система фильтров
  - visualizations/ - визуализации (InterviewMapNodes, MindMapNodes)

- `src/entities/` - **Бизнес-сущности**
  - User/ - модель пользователя
  - ContentBlock/ - блоки контента с Redux slice
  - TheoryCard/ - теоретические карточки с React Query и Redux

- `src/shared/` - **Переиспользуемый код**
  - api/ - API клиенты и генерированный код (generated/api.ts)
  - components/ - UI компоненты (Button, Input, Modal, Loading, etc.)
  - hooks/ - переиспользуемые хуки
  - config/ - конфигурация API
  - constants/ - константы и переводы категорий
  - context/ - контексты (Theme)
  - lib/ - адаптеры и утилиты
  - utils/ - генераторы шаблонов кода
  - types/ - типы TypeScript

#### Технологический стек
- **React 19.1** с TypeScript и Vite 6.3
- **Redux Toolkit** для глобального состояния
- **React Query v5** для серверного состояния
- **React Router v7** с ленивой загрузкой
- **Monaco Editor** для редактирования кода
- **React Flow (XYFlow)** для ментальных карт
- **React Hook Form + Zod** для форм и валидации
- **SCSS модули** с темной/светлой темой
- **Framer Motion** для анимаций
- **Axios** для HTTP запросов
- **D3.js + ECharts** для визуализаций

## Система собеседований и ML-анализ

### Архитектура обработки данных
```
8,560 вопросов из 380 компаний
    ↓
BERTopic + HDBSCAN кластеризация
    ↓  
GPT-4 постобработка и категоризация
    ↓
13 категорий, 150+ кластеров
    ↓
PostgreSQL + полнотекстовый поиск
    ↓
React frontend с фильтрацией
```

### Категории интервью (по количеству вопросов)
1. **JavaScript Core** - 2,364 (27.71%) - Event Loop, Promise, замыкания
2. **React** - 1,775 (20.8%) - Хуки, состояние, жизненный цикл
3. **Soft Skills** - 932 (10.92%) - Опыт, команда, проекты
4. **TypeScript** - 769 (9.01%) - Типы, интерфейсы, дженерики
5. **Сеть** - 486 (5.7%) - HTTP, CORS, API, WebSocket
6. **Алгоритмы** - 452 (5.3%) - Структуры данных, сложность
7. **Верстка** - 339 (3.97%) - CSS, HTML, Flexbox
8. **Инструменты** - 250 (2.93%) - Git, Webpack, build tools
9. **Производительность** - 149 (1.75%) - Оптимизация
10. **Браузеры** - 114 (1.34%) - DOM, рендеринг
11. **Тестирование** - 104 (1.22%) - Unit/Integration тесты
12. **Архитектура** - 98 (1.15%) - Паттерны, SOLID
13. **Другое** - 700+ (8.2%) - Некатегоризированные

### Топ-компании по вопросам
1. **Сбер** - 723 вопроса (8.47%)
2. **Яндекс** - 602 вопроса (7.05%)
3. **Альфа-Банк** - 214 вопросов (2.51%)
4. **Т-Банк** - 180 вопросов (2.11%)
5. **Иннотех** - 179 вопросов (2.10%)

## Безопасность и выполнение кода

### Docker-in-Docker архитектура
- **Полная изоляция** - отдельный контейнер для каждого выполнения
- **Ограничения ресурсов** - CPU, память, время выполнения
- **Сетевая изоляция** - `network_disabled: True`
- **Файловая система** - read-only с временными директориями
- **Безопасность** - непривилегированный пользователь, удаление capabilities

### Многоуровневая валидация кода
```python
# Опасные паттерны по языкам
Python: ["__import__", "exec", "eval", "os.", "sys.", "subprocess"]
JavaScript: ["require", "fetch", "document", "window", "eval"]
Java: ["System.exit", "Runtime", "ProcessBuilder", "File"]
```

## База данных и API

### PostgreSQL схема
```sql
InterviewCategory (id, name, questions_count, percentage)
InterviewCluster (id, name, category_id, keywords[], example_question)
InterviewQuestion (id, question_text, company, category_id, cluster_id)
User (id, email, hashed_password, role, created_at, updated_at)
ContentBlock (id, title, content, technology, difficulty, type)
Task (id, title, description, test_cases, difficulty)
Progress (id, user_id, content_id, status, started_at, completed_at)
```

### API Endpoints
```
# Auth
POST   /api/v2/auth/register        # Регистрация
POST   /api/v2/auth/login           # Вход
POST   /api/v2/auth/refresh         # Обновление токена
GET    /api/v2/auth/me              # Текущий пользователь

# Interviews
GET    /api/v2/interview-categories/                    # Категории интервью
GET    /api/v2/interview-categories/search/questions    # Поиск вопросов
GET    /api/v2/interviews/companies/list               # Список компаний
GET    /api/v2/interviews/                             # Список интервью

# Code Editor
POST   /api/v2/code-editor/execute       # Выполнение кода
POST   /api/v2/code-editor/validate      # Валидация кода
POST   /api/v2/code-editor/generate-tests # AI генерация тестов

# Mindmap
POST   /api/v2/mindmap/generate          # Генерация ментальной карты
GET    /api/v2/mindmap/progress          # Прогресс по карте

# Progress
GET    /api/v2/progress/                 # Прогресс пользователя
POST   /api/v2/progress/update           # Обновление прогресса
GET    /api/v2/progress/analytics        # Аналитика прогресса

# Theory
GET    /api/v2/theory/cards              # Теоретические карточки
GET    /api/v2/theory/quiz               # Квизы по теории

# Stats
GET    /api/v2/stats/dashboard           # Статистика дашборда
GET    /api/v2/stats/user/{id}           # Статистика пользователя

# Admin
GET    /api/v2/admin/users               # Список пользователей
GET    /api/v2/admin/stats               # Административная статистика

# Logs
GET    /api/logs/viewer                  # HTML интерфейс просмотра логов
GET    /api/logs/recent                  # Последние логи
POST   /api/logs/external               # Прием внешних логов
WS     /api/logs/stream                 # WebSocket стриминг логов
```

## Важные технические детали

### Автогенерация API клиента
Frontend API клиент генерируется из OpenAPI схемы через Orval:
```bash
npm run api:generate  # После изменений backend схемы
```

### Миграции базы данных
```bash
cd back
alembic revision --autogenerate -m "описание изменений"
alembic upgrade head
```

### Система логирования
- **Structured logging** с JSON форматом через structlog
- **Correlation ID** для трассировки запросов
- **Фильтрация чувствительных данных** (пароли, токены)
- **Контекстная информация** (user_id, request_id)
- **WebSocket streaming** для real-time логов
- **Интеграция с Chrome MCP** для браузерных логов

### Chrome Monitor Plugin
Уникальная возможность отладки - автоматический мониторинг:
```javascript
window.chromeMonitor = {
  requests: [], // HTTP запросы
  logs: [],     // Console логи  
  errors: [],   // JS ошибки
  getStats(),   // Статистика
  sendToBackend(), // Отправка на backend
  clearMonitor()   // Очистка буфера
};
```

## Среда разработки

### Требования
- **Node.js 20+** и **npm 10+**
- **Python 3.9+** с Poetry
- **Docker** и Docker Compose
- **PostgreSQL 15+** и **Redis 7+** (или через Docker)

### Настройка окружения
1. Backend: Создать `back/.env` с настройками БД и аутентификации
2. Frontend: Vite автоматически подхватывает `.env` файлы
3. Использовать `docker-compose.dev.yml` для полного стека

### Конфигурация портов
- **Frontend**: 5173 (Vite dev server)
- **Backend**: 4000 (FastAPI с hot reload)
- **PostgreSQL**: 5432
- **Redis**: 6379

## Обработка данных интервью

### Ключевые скрипты в sobes-data/analysis/
- `bertopic_analysis.py` - ML анализ и кластеризация
- `postprocess_with_gpt.py` - GPT обогащение данных
- `generate_final_api_data.py` - Подготовка данных для API
- `import_final_categorized_data.py` - Загрузка в PostgreSQL

### ML Pipeline производительность
- **Время обработки**: 5-10 минут для 8.5k вопросов
- **Качество кластеризации**: 82% полезных кластеров
- **Покрытие данных**: 100% вопросов имеют категорию
- **Модель эмбеддингов**: paraphrase-multilingual-mpnet-base-v2

## Деплой и инфраструктура

### Docker Compose конфигурация
- **Multi-stage builds** для оптимизации размера образов
- **Health checks** для мониторинга состояния
- **Volume mapping** для персистентности данных
- **Nginx reverse proxy** с gzip сжатием

### Dokploy интеграция
- **Автоматический деплой** через git push
- **Environment variables** управление
- **SSL/TLS** автонастройка через Traefik
- **Backup система** для данных

### Производственные настройки
```bash
# Переменные окружения для продакшена
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
SECRET_KEY=... # Минимум 32 символа
DEBUG=false
ALLOWED_ORIGINS=https://domain.com
```

## Рекомендации по разработке

### При работе с backend
1. **Всегда использовать DI контейнер** для получения сервисов
2. **Создавать миграции** для любых изменений схемы БД
3. **Следовать Feature-First** архитектуре при добавлении новых модулей
4. **Использовать structured logging** с контекстной информацией
5. **Валидировать входные данные** через Pydantic схемы
6. **Разделять DTO** для запросов и ответов

### При работе с frontend
1. **Следовать FSD архитектуре** с правильными импортами (сверху вниз)
2. **Регенерировать API клиент** после изменений backend
3. **Использовать TypeScript strict mode** для типобезопасности
4. **Применять CSS модули** для изоляции стилей
5. **Оптимизировать компоненты** с React.memo и useMemo
6. **Использовать React Query** для серверного состояния

### При работе с данными интервью
1. **Использовать готовые скрипты** из sobes-data/analysis/
2. **Проверять качество кластеризации** перед импортом
3. **Бэкапить данные** перед большими изменениями
4. **Тестировать поиск и фильтрацию** на больших наборах данных

## Мониторинг и отладка

### 🚀 Единая система логирования

#### Архитектура логирования
```
Chrome браузер → Chrome Monitor → Chrome MCP → /api/logs/external → Единая система
       ↓               ↓              ↓               ↓                    ↓
   JS события     Сбор логов    Автоотправка    Backend API       Все логи в одном месте:
   XHR запросы    Console API    каждые 60 сек   Парсинг          • /api/logs/viewer (UI)
   JS ошибки      Автозапуск                     Логирование      • /api/logs/recent (API)
                                                                   • WebSocket streaming
```

#### Endpoints системы логирования

**Backend логи (внутренние):**
- `GET /api/logs/viewer` - HTML интерфейс для просмотра логов в реальном времени
- `GET /api/logs/recent?seconds=30` - Последние логи (для Claude Code)
- `GET /api/logs/tail?lines=50` - Аналог `tail -f` для логов
- `GET /api/logs/buffer?limit=100` - Буфер последних логов
- `WS /api/logs/stream` - WebSocket для real-time streaming

**Внешние логи (Chrome MCP, Frontend):**
- `POST /api/logs/external` - Прием логов от внешних источников
  ```json
  {
    "logs": [{
      "level": "ERROR",
      "message": "JavaScript error",
      "source": "chrome_mcp",
      "url": "http://localhost:5173/page",
      "metadata": {}
    }],
    "source_info": {"name": "Chrome Monitor", "version": "1.0"}
  }
  ```

#### Chrome MCP интеграция
Chrome MCP автоматически собирает и отправляет в backend:
- Console.log/error/warn из браузера
- XHR/Fetch запросы и их статусы
- JavaScript исключения со stack trace
- Performance метрики

**Команды Chrome Monitor в браузере:**
```javascript
chromeMonitor.getStats()        // Посмотреть собранные логи
chromeMonitor.sendToBackend()   // Отправить логи в backend вручную
chromeMonitor.clearMonitor()    // Очистить буфер логов
```

**Автоотправка:** Каждые 60 секунд Chrome Monitor автоматически отправляет накопленные логи в backend.

### Логи и метрики
- Backend логи: Единая система `/api/logs/` + `back/logs/` файлы
- Frontend логи: Автоматически через Chrome MCP → `/api/logs/external`
- Просмотр всех логов: http://localhost:4000/api/logs/viewer
- API метрики: FastAPI automatic metrics at `/metrics`
- Здоровье системы: `/api/health` endpoint

### Типичные проблемы
1. **Docker socket permissions** - проверить `entrypoint.sh`
2. **API CORS errors** - настроить `ALLOWED_ORIGINS`
3. **Database connection** - проверить `DATABASE_URL`
4. **Redis unavailable** - система работает с graceful degradation
5. **Chrome MCP не отправляет логи** - проверить что страница открыта и Chrome Monitor активен

## 🔧 Конфигурационные файлы

### Основные конфигурационные файлы

**Backend:**
- `back/pyproject.toml` - зависимости Python и настройки инструментов
- `back/alembic.ini` - конфигурация миграций
- `back/.env` - переменные окружения (не в git)
- `back/app/core/settings.py` - настройки приложения

**Frontend:**
- `front/package.json` - зависимости и скрипты npm
- `front/vite.config.ts` - конфигурация Vite
- `front/tsconfig.json` - настройки TypeScript
- `front/orval.config.ts` - генерация API клиента
- `front/eslint.config.js` - правила линтинга

**Корневые файлы:**
- `.claude_settings.json` - настройки проекта для Claude Code
- `docker-compose.yml` - продакшн конфигурация
- `docker-compose.dev.yml` - конфигурация для разработки
- `start.bat` - быстрый старт разработки (Windows)

### MCP серверы
Проект интегрирован с MCP (Model Context Protocol) серверами:
- **postgres** - прямой доступ к БД разработки
- **git** - Git операции через MCP
- **chrome** - браузер автоматизация и мониторинг
- **filesystem** - расширенная работа с файлами
- **github** - работа с GitHub API
- **ide** - интеграция с IDE

### Переменные окружения

**Backend (.env):**
```env
DATABASE_URL=postgresql://postgres:dev_password@localhost:5432/nareshka_dev
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key-at-least-32-chars
DEBUG=true
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:4000
```

**Frontend (.env):**
```env
VITE_API_URL=http://localhost:4000
VITE_APP_ENV=development
```

---

*Этот файл регулярно обновляется. При добавлении новых фич или изменении архитектуры, обязательно обновите соответствующие разделы.*
