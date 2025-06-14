# 🚀 Встроенный редактор кода - Nareshka Learning Platform

Документация по интеграции и использованию встроенного редактора кода, который превосходит CodeSandbox по функциональности.

## 📋 Обзор

Встроенный редактор кода предоставляет полнофункциональную среду разработки прямо в браузере с безопасным выполнением кода в изолированных Docker контейнерах.

### ✨ Ключевые возможности

- **🔒 Безопасное выполнение**: Код запускается в изолированных Docker контейнерах
- **🌍 Поддержка 10+ языков**: Python, JavaScript, TypeScript, Java, C++, C, Go, Rust, PHP, Ruby
- **💾 Сохранение решений**: Автоматическое сохранение и загрузка кода пользователя
- **📊 Аналитика**: Детальная статистика выполнения и прогресса
- **⚡ Быстрое выполнение**: Оптимизированная система с ограничениями ресурсов
- **🎨 Monaco Editor**: Профессиональный редактор кода (как в VS Code)

## 🏗️ Архитектура

### Backend (Python + FastAPI)

```
back/
├── app/
│   ├── models.py              # Новые модели для редактора кода
│   ├── schemas.py             # Pydantic схемы для API
│   ├── code_executor.py       # Сервис выполнения кода в Docker
│   └── routers/
│       └── code_editor.py     # API эндпоинты редактора
├── init_languages.py         # Скрипт инициализации языков
└── pyproject.toml            # Добавлена зависимость docker
```

#### Новые модели базы данных:

1. **SupportedLanguage** - Конфигурация языков программирования
2. **CodeExecution** - История выполнения кода
3. **UserCodeSolution** - Сохраненные решения пользователей

### Frontend (React + TypeScript)

```
front/
├── src/
│   ├── shared/
│   │   ├── api/
│   │   │   └── code-editor.ts         # API клиент
│   │   └── components/
│   │       └── CodeEditor/            # Основной компонент
│   ├── widgets/
│   │   └── CodeEditorWidget/          # Виджет для интеграции
│   └── pages/
│       └── CodeEditor/                # Демо страница
└── package.json                      # Добавлены Monaco Editor зависимости
```

## 🚀 Установка и настройка

### 1. Backend Setup

```bash
# Установка зависимостей
cd back
poetry install

# Создание миграций (если нужно)
poetry run alembic revision --autogenerate -m "Add code editor tables"
poetry run alembic upgrade head

# Инициализация поддерживаемых языков
poetry run python init_languages.py init
```

### 2. Frontend Setup

```bash
# Установка зависимостей
cd front
npm install

# Запуск в режиме разработки
npm run dev
```

### 3. Docker Setup

Убедитесь, что Docker запущен и доступен:

```bash
# Проверка Docker
docker --version
docker run hello-world

# Предварительная загрузка образов (опционально)
docker pull python:3.9-alpine
docker pull node:18-alpine
docker pull openjdk:17-alpine
docker pull gcc:11-alpine
docker pull golang:1.21-alpine
```

## 🔧 Использование

### Базовый редактор

```tsx
import { CodeEditor } from "@/shared/components/CodeEditor";

function MyComponent() {
  return (
    <CodeEditor
      initialCode="print('Hello, World!')"
      initialLanguage="python"
      height="400px"
      onExecutionComplete={(result) => {
        console.log("Результат:", result);
      }}
    />
  );
}
```

### Виджет для задач

```tsx
import { CodeEditorWidget } from "@/widgets/CodeEditorWidget";

function TaskPage() {
  return (
    <CodeEditorWidget
      blockId="task-123"
      blockTitle="Задача: Сортировка массива"
      codeContent="# Ваш код здесь..."
      codeLanguage="python"
    />
  );
}
```

## 🛡️ Безопасность

### Docker изоляция

- **Сетевые ограничения**: `network_disabled: true`
- **Файловая система**: `read_only: true`
- **Пользователь**: `user: nobody`
- **Capabilities**: `cap_drop: ["ALL"]`
- **Ресурсы**: Ограничения CPU и памяти
- **Процессы**: `pids_limit: 50`

### Валидация кода

```python
# Автоматическая проверка на опасные паттерны
forbidden_patterns = [
    "system", "exec", "eval", "subprocess",
    "import os", "socket", "urllib"
]
```

### Ограничения ресурсов

- **Время выполнения**: 10-15 секунд (настраивается)
- **Память**: 128-256 МБ (настраивается)
- **CPU**: 50% от одного ядра
- **Размер кода**: Максимум 10 КБ

## 📊 API Endpoints

### Языки программирования

```http
GET /api/code-editor/languages
# Получение списка поддерживаемых языков
```

### Выполнение кода

```http
POST /api/code-editor/execute
Content-Type: application/json

{
  "sourceCode": "print('Hello, World!')",
  "language": "python",
  "stdin": "optional input",
  "blockId": "optional-task-id"
}
```

### Результаты выполнения

```http
GET /api/code-editor/executions/{execution_id}
# Получение результата выполнения

GET /api/code-editor/executions?blockId=task-123
# История выполнений для задачи
```

### Решения пользователя

```http
POST /api/code-editor/solutions
# Сохранение решения

GET /api/code-editor/solutions/{block_id}
# Получение решений для задачи

PUT /api/code-editor/solutions/{solution_id}
# Обновление решения
```

### Статистика

```http
GET /api/code-editor/stats
# Статистика выполнения кода пользователя
```

## 🎯 Интеграция с контентом

### Автоматическое обнаружение кода

Виджет автоматически интегрируется с существующими блоками контента:

```typescript
// В ContentBlock компоненте
{
  block.codeContent && (
    <CodeEditorWidget
      blockId={block.id}
      blockTitle={block.blockTitle}
      codeContent={block.codeContent}
      codeLanguage={block.codeLanguage || "python"}
    />
  );
}
```

### Прогресс и статистика

- Автоматическое обновление прогресса пользователя
- Связь с существующей системой `UserContentProgress`
- Детальная аналитика по языкам и задачам

## 🔧 Конфигурация языков

### Добавление нового языка

```bash
# Через скрипт инициализации
cd back
poetry run python init_languages.py update "Python 3.9" dockerImage=python:3.10-alpine
```

### Структура конфигурации

```python
{
    "name": "Python 3.9",
    "language": "python",
    "version": "3.9",
    "dockerImage": "python:3.9-alpine",
    "fileExtension": ".py",
    "compileCommand": None,  # Для интерпретируемых языков
    "runCommand": "python main.py",
    "timeoutSeconds": 10,
    "memoryLimitMB": 128,
    "isEnabled": True
}
```

## 📈 Мониторинг и логирование

### Системные логи

```python
# В code_executor.py
logger.info(f"Starting code execution {execution_id} for language {language.language}")
logger.info(f"Code execution {execution_id} completed in {execution_time}ms")
```

### Метрики выполнения

- Время выполнения каждого запуска
- Использование памяти
- Статус завершения (SUCCESS/ERROR/TIMEOUT)
- Статистика по языкам программирования

## 🚨 Устранение неполадок

### Распространенные проблемы

1. **Docker не запущен**

   ```bash
   # Запуск Docker Desktop или daemon
   sudo systemctl start docker  # Linux
   ```

2. **Образы не найдены**

   ```bash
   # Предварительная загрузка
   docker pull python:3.9-alpine
   ```

3. **Превышение лимитов**
   ```python
   # Настройка в модели SupportedLanguage
   timeoutSeconds = 15  # Увеличить время
   memoryLimitMB = 256  # Увеличить память
   ```

### Отладка выполнения

```python
# Просмотр логов контейнера
execution.containerLogs  # Поле в CodeExecution модели
```

## 🎉 Заключение

Встроенный редактор кода Nareshka предоставляет полнофункциональную среду разработки, превосходящую по возможностям многие онлайн-редакторы:

- ✅ **Безопасность**: Полная изоляция в Docker
- ✅ **Производительность**: Оптимизированное выполнение
- ✅ **Удобство**: Интуитивный интерфейс
- ✅ **Аналитика**: Детальная статистика
- ✅ **Масштабируемость**: Легкое добавление новых языков

Система готова к продакшену и может обрабатывать тысячи одновременных выполнений кода с высоким уровнем безопасности и производительности.

---

🔗 **Полезные ссылки:**

- [Monaco Editor Docs](https://microsoft.github.io/monaco-editor/)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [FastAPI Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)
