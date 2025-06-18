/**
 * Централизованные переводы категорий и подкатегорий
 * Все английские названия должны быть переведены на русский язык
 */

// Переводы основных категорий
export const MAIN_CATEGORY_TRANSLATIONS: Record<string, string> = {
  JS: 'JavaScript',
  REACT: 'React',
  'NODE.JS': 'Node.js',
  CSS: 'CSS',
  HTML: 'HTML',
  TYPESCRIPT: 'TypeScript',
  'JS QUIZ': 'JS-Квиз',
  'REACT QUIZ': 'React-Квиз',
  'JS ТЕОРИЯ': 'JS Теория',
  ПРАКТИКА: 'Практика',
};

// Переводы подкатегорий
export const SUB_CATEGORY_TRANSLATIONS: Record<string, string> = {
  // JavaScript подкатегории
  Array: 'Массивы',
  Classes: 'Классы',
  'Custom method and function': 'Кастомные методы и функции',
  Zamiki: 'Замыкания',
  Promise: 'Промисы',
  Objects: 'Объекты',
  Strings: 'Строки',
  Numbers: 'Числа',
  QUIZ: 'Квиз',

  // React подкатегории
  Hooks: 'Хуки',
  Components: 'Компоненты',
  'State Management': 'Управление состоянием',
  Props: 'Пропсы',
  Context: 'Контекст',
  Routing: 'Маршрутизация',
  Testing: 'Тестирование',
  Performance: 'Производительность',
  Lifecycle: 'Жизненный цикл',

  // Node.js подкатегории
  Express: 'Express',
  Database: 'База данных',
  Authentication: 'Аутентификация',
  'File System': 'Файловая система',
  HTTP: 'HTTP',
  Middleware: 'Промежуточное ПО',
  Security: 'Безопасность',
  API: 'API',

  // CSS подкатегории
  Flexbox: 'Флексбокс',
  Grid: 'Грид',
  Animations: 'Анимации',
  Responsive: 'Адаптивность',
  Selectors: 'Селекторы',
  Properties: 'Свойства',
  Layout: 'Макет',
  Typography: 'Типографика',

  // HTML подкатегории
  Elements: 'Элементы',
  Attributes: 'Атрибуты',
  Forms: 'Формы',
  Semantic: 'Семантика',
  Accessibility: 'Доступность',
  Meta: 'Мета-теги',

  // TypeScript подкатегории
  Types: 'Типы',
  Interfaces: 'Интерфейсы',
  Generics: 'Дженерики',
  Modules: 'Модули',
  Decorators: 'Декораторы',
  Configuration: 'Конфигурация',

  // Общие подкатегории
  Basics: 'Основы',
  Advanced: 'Продвинутый',
  Patterns: 'Паттерны',
  'Best Practices': 'Лучшие практики',
  Debugging: 'Отладка',
  Tools: 'Инструменты',
  Documentation: 'Документация',
  Examples: 'Примеры',
};

/**
 * Функция для получения перевода основной категории
 * @param category - английское название категории
 * @returns русское название или оригинальное, если перевод не найден
 */
export const translateMainCategory = (category: string): string => {
  return MAIN_CATEGORY_TRANSLATIONS[category] || category;
};

/**
 * Функция для получения перевода подкатегории
 * @param subCategory - английское название подкатегории
 * @returns русское название или оригинальное, если перевод не найден
 */
export const translateSubCategory = (subCategory: string): string => {
  return SUB_CATEGORY_TRANSLATIONS[subCategory] || subCategory;
};

/**
 * Функция для получения полного перевода категории и подкатегории
 * @param mainCategory - основная категория
 * @param subCategory - подкатегория
 * @returns объект с переведенными названиями
 */
export const translateCategory = (
  mainCategory: string,
  subCategory?: string
) => {
  return {
    mainCategory: translateMainCategory(mainCategory),
    subCategory: subCategory ? translateSubCategory(subCategory) : undefined,
  };
};

/**
 * Функция для поиска оригинального названия по переводу
 * @param translatedCategory - переведенное название
 * @param isMainCategory - является ли основной категорией
 * @returns оригинальное английское название
 */
export const findOriginalCategory = (
  translatedCategory: string,
  isMainCategory: boolean = false
): string => {
  const translations = isMainCategory
    ? MAIN_CATEGORY_TRANSLATIONS
    : SUB_CATEGORY_TRANSLATIONS;

  const entry = Object.entries(translations).find(
    ([, translation]) => translation === translatedCategory
  );

  return entry ? entry[0] : translatedCategory;
};

/**
 * Проверяет, есть ли перевод для категории
 * @param category - название категории
 * @param isMainCategory - является ли основной категорией
 * @returns true, если перевод существует
 */
export const hasTranslation = (
  category: string,
  isMainCategory: boolean = false
): boolean => {
  const translations = isMainCategory
    ? MAIN_CATEGORY_TRANSLATIONS
    : SUB_CATEGORY_TRANSLATIONS;

  return category in translations;
};
