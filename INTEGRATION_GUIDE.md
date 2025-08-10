# 📚 Руководство по интеграции категоризированных вопросов интервью

## 🎯 Что мы интегрируем

У нас есть **8,532 вопроса интервью**, категоризированных на:
- **13 категорий** (JavaScript Core, React, TypeScript и т.д.)
- **182 кластера/топика** 
- **77.9% покрытие категоризацией**
- Только **1.5% в категории "Другое"**

## 🚀 Шаги интеграции

### 1. Backend - Миграция базы данных

```bash
cd back

# Применяем миграцию для создания новых таблиц
alembic upgrade head
```

Это создаст 3 новые таблицы:
- `InterviewCategory` - категории вопросов
- `InterviewCluster` - кластеры/топики внутри категорий  
- `InterviewQuestion` - все вопросы с категоризацией

### 2. Импорт данных в БД

```bash
cd back

# Запускаем скрипт импорта
python scripts/import_categorized_questions.py
```

Скрипт импортирует:
- 13 категорий
- 182 кластера
- 8,532 вопроса

### 3. Регистрация новых роутеров в Backend

В файле `back/main.py` добавь:

```python
from app.features.interviews.api.categories_router import router as categories_router

# В секцию роутеров добавь:
app.include_router(categories_router, prefix="/api")
```

### 4. Frontend - Добавление компонента категорий

Компонент уже создан в `front/src/features/InterviewCategories/`

Добавь его на страницу интервью:

```tsx
// В файле front/src/pages/Interviews/ui/InterviewsPage.tsx
import { InterviewCategories } from '@/features/InterviewCategories/InterviewCategories';

// Добавь вкладку или секцию:
<InterviewCategories />
```

### 5. Обновление навигации

В навигацию добавь новый пункт:

```tsx
// В Sidebar или Header
<Link to="/interviews/categories">Категории вопросов</Link>
```

## 📊 API Endpoints

### Новые endpoints для категорий:

- `GET /api/interviews/categories/` - список всех категорий
- `GET /api/interviews/categories/{category_id}` - детали категории с кластерами
- `GET /api/interviews/categories/cluster/{cluster_id}/questions` - вопросы кластера
- `GET /api/interviews/categories/search?q=react` - поиск вопросов

## 🎨 Frontend компоненты

### InterviewCategories
Главный компонент отображения категорий с функциями:
- Сетка категорий с статистикой
- Детальный просмотр категории
- Список топиков/кластеров
- Поиск по вопросам
- Примеры вопросов

## 📁 Структура данных

```typescript
interface Category {
  id: string;           // 'javascript_core'
  name: string;         // 'JavaScript Core'
  questions_count: number;  // 2082
  clusters_count: number;   // 60
  percentage: number;       // 24.4
}

interface Cluster {
  id: number;              // 25
  name: string;            // 'Замыкания и область видимости'
  category_id: string;     
  keywords: string[];      // ['closure', 'scope', 'замыкание']
  questions_count: number; // 38
  example_question: string;
}

interface Question {
  id: string;
  question_text: string;
  company?: string;
  cluster_id?: number;
  category_id?: string;
  topic_name?: string;
}
```

## 🔧 Дополнительные настройки

### Переменные окружения

В `.env` файле frontend добавь:
```
VITE_API_URL=http://localhost:8000
```

### CORS настройки

Убедись что в backend разрешены CORS запросы с frontend:

```python
# back/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## ✅ Проверка интеграции

1. Запусти backend: `cd back && python main.py`
2. Запусти frontend: `cd front && npm run dev`
3. Открой http://localhost:5173/interviews/categories
4. Должны отобразиться:
   - 13 категорий с процентами
   - При клике - детали категории
   - Поиск по вопросам

## 🎯 Что дальше?

1. **Фильтры на странице интервью** - добавить фильтр по категориям
2. **Статистика в профиле** - показывать прогресс по категориям
3. **Рекомендации** - предлагать вопросы из слабых категорий
4. **Тренажер** - режим подготовки по выбранным категориям
5. **Аналитика компаний** - какие категории спрашивает каждая компания

## 📈 Статистика категорий

| Категория | Вопросов | % от общего |
|-----------|----------|-------------|
| JavaScript Core | 2,082 | 24.4% |
| React | 1,407 | 16.5% |
| Soft Skills | 823 | 9.6% |
| TypeScript | 672 | 7.9% |
| Сеть | 410 | 4.8% |
| Алгоритмы | 314 | 3.7% |
| Верстка | 278 | 3.3% |
| Инструменты | 218 | 2.6% |
| Производительность | 136 | 1.6% |
| Тестирование | 102 | 1.2% |
| Архитектура | 59 | 0.7% |
| Браузеры | 48 | 0.6% |
| Другое | 100 | 1.2% |

## 🐛 Troubleshooting

**Проблема**: Ошибка при миграции
**Решение**: Проверь последнюю миграцию в `alembic/versions/` и обнови `down_revision`

**Проблема**: Данные не импортируются
**Решение**: Убедись что файлы данных есть в `sobes-data/analysis/outputs_api_ready/`

**Проблема**: CORS ошибки
**Решение**: Проверь настройки CORS в `back/main.py`

---

**Готово!** Теперь у тебя есть полноценная система категоризации вопросов интервью 🎉