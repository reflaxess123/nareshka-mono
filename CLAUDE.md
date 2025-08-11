# CLAUDE.md

Этот файл предоставляет руководство для Claude Code (claude.ai/code) при работе с кодом в данном репозитории.

## Обзор проекта

**Nareshka** - это современная платформа для изучения программирования с полноценной full-stack архитектурой. Включает интерактивный редактор кода с выполнением в Docker, базу интервью-вопросов с AI-категоризацией, ментальные карты для обучения и систему отслеживания прогресса.

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
start-dev-simple.bat

# Docker Compose - полный стек с PostgreSQL/Redis
docker-compose -f docker-compose.dev.yml up

# Продакшн деплой через Dokploy
docker-compose up -d
```

## Архитектура проекта

### Backend: Feature-First + Clean Architecture

#### Структура приложения
- `app/features/` - **Доменные модули** (auth, code_editor, interviews, mindmap, etc.)
- `app/shared/` - **Общие компоненты** (database, dependencies, middleware)
- `app/core/` - **Ядро приложения** (logging, error handlers, settings)

#### Ключевые модули в app/features/:
- **auth** - JWT + Session аутентификация с Redis
- **interviews** - Система интервью (8560 вопросов, 13 категорий, 380 компаний)
- **code_editor** - Monaco Editor + Docker выполнение + AI тесты
- **mindmap** - React Flow интеграция для карт знаний
- **progress** - Трекинг прогресса и аналитика
- **theory** - Теоретические материалы с spaced repetition
- **admin** - Административная панель

#### Архитектурные паттерны
- **Dependency Injection** - собственный DI контейнер
- **Repository Pattern** - абстракция доступа к данным
- **Service Layer** - бизнес-логика
- **Feature-First** - модульная организация по доменам

### Frontend: Feature-Sliced Design (FSD)

#### Слоистая архитектура
- `src/app/` - **Конфигурация приложения** (providers, глобальные стили)
- `src/pages/` - **Страницы** и роутинг
- `src/widgets/` - **Композитные UI блоки**
- `src/features/` - **Бизнес-функции** (формы, фильтры)
- `src/entities/` - **Бизнес-сущности** (User, Interview, ContentBlock)
- `src/shared/` - **Переиспользуемый код** (UI компоненты, API, хуки)

#### Технологический стек
- **React 19.1** с TypeScript и Vite 6.3
- **Redux Toolkit** + **React Query v5** для состояния
- **React Router v7** с ленивой загрузкой
- **Monaco Editor** для редактирования кода
- **React Flow** для ментальных карт
- **SCSS модули** с темной темой

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

### Judge0 интеграция
- **Fallback система** при недоступности Docker
- **60+ языков программирования**
- **Sandboxed выполнение** через внешний API
- **Base64 кодирование** данных

## База данных и API

### PostgreSQL схема
```sql
InterviewCategory (id, name, questions_count, percentage)
InterviewCluster (id, name, category_id, keywords[], example_question)
InterviewQuestion (id, question_text, company, category_id, cluster_id)
```

### API Endpoints
```
/api/v2/interview-categories/     # Категории с процентным распределением
/api/v2/interview-categories/search/questions  # Полнотекстовый поиск
/api/v2/interviews/companies/list # Список компаний
/api/v2/code-editor/execute       # Выполнение кода
/api/v2/mindmap/generate          # Генерация ментальных карт
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
- **Structured logging** с JSON форматом
- **Correlation ID** для трассировки запросов
- **Фильтрация чувствительных данных** (пароли, токены)
- **Контекстная информация** (user_id, request_id)

### Chrome Monitor Plugin
Уникальная возможность отладки - автоматический мониторинг:
```javascript
window.chromeMonitor = {
  requests: [], // HTTP запросы
  logs: [],     // Console логи  
  errors: [],   // JS ошибки
  getStats(),   # Статистика
  export()      # Экспорт данных
};
```

## Среда разработки

### Требования
- **Node.js 20+** и **npm 10+**
- **Python 3.8+** с Poetry
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
- **Качество кластеризации**: 82% полезных кластеров (vs 7% в старом алгоритме)
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

### При работе с frontend
1. **Следовать FSD архитектуре** с правильными импортами (сверху вниз)
2. **Регенерировать API клиент** после изменений backend
3. **Использовать TypeScript strict mode** для типобезопасности
4. **Применять CSS модули** для изоляции стилей
5. **Оптимизировать компоненты** с React.memo и useMemo

### При работе с данными интервью
1. **Использовать готовые скрипты** из sobes-data/analysis/
2. **Проверять качество кластеризации** перед импортом
3. **Бэкапить данные** перед большими изменениями
4. **Тестировать поиск и фильтрацию** на больших наборах данных

## Мониторинг и отладка

### Логи и метрики
- Backend логи: `back/logs/` или Docker logs
- Frontend ошибки: Chrome DevTools + Chrome Monitor
- API метрики: FastAPI automatic metrics at `/metrics`
- Здоровье системы: `/api/health` endpoint

### Типичные проблемы
1. **Docker socket permissions** - проверить `entrypoint.sh`
2. **API CORS errors** - настроить `ALLOWED_ORIGINS`
3. **Database connection** - проверить `DATABASE_URL`
4. **Redis unavailable** - система работает с graceful degradation

## 🔧 Конфигурационные файлы Claude Code

### Дополнительные файлы конфигурации
В корне проекта созданы дополнительные файлы для оптимизации работы с Claude Code:

- **`.claude_settings.json`** - Конфигурация проекта, команды, пути, API endpoints
- **`.claude_hooks.json`** - Автоматические хуки для pre-commit, post-deploy проверок
- **`.claude_prompts.md`** - Контекстные промпты для разных типов задач
- **`.claude_workflows.json`** - Готовые workflow для типичных задач разработки
- **`.mcp.json`** - MCP серверы (postgres, git, chrome, filesystem, ide)

### Использование конфигураций
```bash
# Быстрые команды из .claude_settings.json
"dev_start": "start-dev-simple.bat"
"lint_backend": "cd back && poetry run ruff check ."
"api_generate": "cd front && npm run api:generate"

# Workflows из .claude_workflows.json
- new_feature: Пошаговое добавление новой функциональности  
- bug_fix: Систематическое исправление ошибок
- performance_optimization: Оптимизация производительности
- security_review: Аудит безопасности
- ml_pipeline_update: Обновление ML обработки данных
```

### MCP серверы
- **postgres** - Прямой доступ к БД разработки
- **git** - Git операции через MCP
- **chrome** - Браузер автоматизация
- **filesystem** - Расширенная работа с файлами
- **sequential-thinking** - Пошаговое мышление
- **puppeteer** - Веб автоматизация

---

*Этот файл регулярно обновляется. При добавлении новых фич или изменении архитектуры, обязательно обновите соответствующие разделы и конфигурационные файлы.*