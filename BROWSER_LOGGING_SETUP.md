# 🔧 Настройка автоматического сбора логов браузера

## ✅ Что уже настроено

1. **Browser Tools MCP Server** установлен и добавлен в Claude
2. **Browser Tools Server** интегрирован в `start-dev-simple.bat`
3. **Backend endpoint** `/api/browser-logs` создан для приема логов
4. **Конфигурация** `browser-logging-config.json` готова

## 🚀 Следующие шаги для полной настройки

### 1. Установка Chrome расширения

**Скачать расширение:**
```bash
# Клонировать репозиторий
git clone https://github.com/AgentDeskAI/browser-tools-mcp.git
cd browser-tools-mcp/chrome-extension
```

**Установить в Chrome:**
1. Открыть Chrome → `chrome://extensions/`
2. Включить "Режим разработчика" (Developer mode)
3. Нажать "Загрузить распакованное расширение" (Load unpacked)
4. Выбрать папку `chrome-extension` из склонированного репозитория

### 2. Настройка расширения

После установки расширения:
1. Кликнуть на иконку расширения в Chrome
2. Ввести URL сервера: `http://localhost:3001`
3. Нажать "Connect"

### 3. Запуск dev окружения

Теперь просто запусти:
```bash
./start-dev-simple.bat
```

Автоматически поднимутся:
- ✅ Backend (порт 4000)
- ✅ Browser Tools Server (порт 3001) 
- ✅ Frontend (порт 5173)

### 4. Проверка работы

1. **Открой фронтенд:** http://localhost:5173
2. **Открой DevTools** в браузере (F12)
3. **В консоли напиши:** `console.log('Test browser logging')`
4. **Проверь backend логи** - должно появиться сообщение о получении лога

### 5. Автоматический мониторинг

После настройки Browser Tools будет автоматически собирать:

**🖥️ Console логи:**
- `console.log()`, `console.error()`, `console.warn()`
- JavaScript ошибки и исключения
- Пользовательские логи из кода студентов

**🌐 Network активность:**
- Все HTTP запросы/ответы
- Ошибки сети (404, 500, timeout)
- API вызовы к твоему бэкенду

**⚡ Performance метрики:**
- Время загрузки страниц
- Memory usage
- JavaScript выполнение

**📸 Screenshots:**
- Автоматические скриншоты при ошибках
- Визуальные состояния интерфейса

## 🔗 Интеграция с Claude

После настройки ты сможешь через Claude:

```
# Получить логи консоли
claude: "Покажи последние console логи с фронтенда"

# Проанализировать ошибки
claude: "Найди все JavaScript ошибки за последний час"

# Мониторинг network запросов
claude: "Проанализируй неудачные API запросы"

# Debugging студенческого кода
claude: "Собери логи выполнения кода студента ID 123"
```

## 📊 Endpoints для мониторинга

- **Receive logs:** `POST /api/browser-logs`
- **Health check:** `GET /api/browser-logs/health`  
- **Statistics:** `GET /api/browser-logs/stats`
- **Browser Tools Server:** `http://localhost:3001`

## 🛠️ Troubleshooting

**Проблема:** Browser Tools Server не подключается
**Решение:** 
```bash
# Проверь что сервер запущен
netstat -ano | findstr :3001

# Перезапусти вручную
npx @agentdeskai/browser-tools-server
```

**Проблема:** Chrome расширение не видит сервер
**Решение:**
1. Проверь что сервер на порту 3001
2. Убедись что в расширении указан правильный URL
3. Перезагрузи расширение в `chrome://extensions/`

**Проблема:** Логи не приходят в backend
**Решение:**
1. Проверь endpoint `GET /api/browser-logs/health`
2. Посмотри логи в консоли Backend сервера
3. Убедись что CORS настроен правильно

Теперь у тебя будет полноценная система автоматического сбора логов браузера для отладки кода студентов! 🎉