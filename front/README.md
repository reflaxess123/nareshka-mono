# 🧠 NSFN - Образовательная платформа

Современная образовательная платформа, построенная на React + TypeScript с использованием архитектуры Feature-Sliced Design.

## 🚀 Технологический стек

### Frontend

- **React 19** - библиотека пользовательского интерфейса
- **TypeScript** - типизированный JavaScript
- **Vite** - быстрый сборщик проектов
- **SCSS** - препроцессор CSS
- **Feature-Sliced Design** - архитектурная методология

### Управление состоянием

- **Redux Toolkit** - управление глобальным состоянием
- **React Query (TanStack)** - кэширование серверного состояния
- **React Hook Form** - управление формами

### Дополнительные библиотеки

- **Framer Motion** - анимации
- **Zod** - валидация схем
- **Axios** - HTTP клиент
- **Lucide React** - иконки
- **Date-fns** - работа с датами

## 📁 Структура проекта (FSD)

```
src/
├── app/                    # Инициализация приложения
│   ├── providers/         # Провайдеры (Router, Store, etc)
│   ├── styles/           # Глобальные стили
│   └── main.tsx          # Точка входа
├── pages/                 # Страницы приложения
│   ├── Tasks/            # Страница задач
│   ├── Theory/           # Страница теории
│   ├── Profile/          # Профиль пользователя
│   └── Admin/            # Админ панель
├── widgets/              # Виджеты страниц
│   ├── Sidebar/          # Боковая панель
│   ├── ContentBlocksList/ # Список контентных блоков
│   └── AdminDashboard/   # Админ дашборд
├── features/             # Функциональность
│   ├── LoginForm/        # Форма входа
│   ├── RegisterForm/     # Форма регистрации
│   └── ContentFilters/   # Фильтры контента
├── entities/             # Бизнес-сущности
│   ├── User/             # Пользователь
│   ├── ContentBlock/     # Контентный блок
│   └── TheoryCard/       # Карточка теории
└── shared/               # Переиспользуемые ресурсы
    ├── components/       # UI компоненты
    ├── hooks/           # Хуки
    ├── api/             # API методы
    ├── lib/             # Утилиты
    ├── types/           # Типы
    └── constants/       # Константы
```

## 🛠️ Установка и запуск

### Предварительные требования

- Node.js 18+
- npm или yarn

### Установка зависимостей

```bash
npm install
```

### Команды разработки

```bash
# Запуск в режиме разработки
npm run dev

# Сборка для production
npm run build

# Проверка кода линтером
npm run lint

# Предварительный просмотр production сборки
npm run preview
```

## 🎨 Система дизайна

### Цветовая схема

Проект поддерживает темную и светлую темы через CSS custom properties:

```scss
// Использование цветов
.component {
  background: var(--bg-primary);
  color: var(--text-primary);
  border: 1px solid var(--border-primary);
}
```

### Компоненты

- **Button** - настраиваемые кнопки с различными вариантами
- **Input** - поля ввода с валидацией
- **Text** - типографика с различными размерами и весами
- **Modal** - модальные окна
- **Loading** - индикаторы загрузки

## 🔧 Конфигурация

### Алиасы путей

```typescript
"paths": {
  "@/*": ["src/*"],
  "@/shared/*": ["src/shared/*"],
  "@/app/*": ["src/app/*"],
  "@/pages/*": ["src/pages/*"],
  "@/widgets/*": ["src/widgets/*"],
  "@/features/*": ["src/features/*"],
  "@/entities/*": ["src/entities/*"]
}
```

### ESLint правила

- Type-aware правила TypeScript
- React Hooks правила
- Consistent type imports
- Prefer nullish coalescing

## 📦 API

### Конфигурация

API настроено через Axios с interceptors для обработки ошибок:

```typescript
const apiInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  withCredentials: true,
});
```

### Эндпоинты

- `/api/auth` - аутентификация
- `/api/users` - пользователи
- `/api/content` - контент
- `/api/theory` - теория

## 🔐 Аутентификация

Система поддерживает роли:

- **Guest** - гостевой доступ
- **User** - обычный пользователь
- **Admin** - администратор

## 📱 Адаптивность

Проект адаптирован под различные устройства:

- **Mobile**: < 768px
- **Tablet**: 768px - 1024px
- **Desktop**: > 1024px

## 🧪 Валидация

Используется Zod для валидации:

```typescript
const loginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(6),
});
```

## 📈 Производительность

### Оптимизации

- Lazy loading компонентов
- Мемоизация с React.memo
- Виртуализация списков
- Оптимизация изображений

### Сборка

- Tree shaking
- Code splitting
- Минификация
- Gzip сжатие

## 🐛 Обработка ошибок

- **ErrorBoundary** для React ошибок
- **Global error handler** для API
- **Graceful degradation** для недоступных функций

## 📚 Дополнительная документация

- [Архитектура FSD](src/app/styles/README.md)
- [Система тем](src/app/styles/themes/)
- [API документация](src/shared/api/)

## 🤝 Контрибьюция

1. Форкните репозиторий
2. Создайте feature branch (`git checkout -b feature/amazing-feature`)
3. Закоммитьте изменения (`git commit -m 'Add amazing feature'`)
4. Запушьте в branch (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📝 Лицензия

Этот проект лицензирован под MIT License.

## 👥 Команда

- Разработка: [Ваше имя]
- Дизайн: [Имя дизайнера]
- Тестирование: [Имя тестировщика]
