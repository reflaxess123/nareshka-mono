// API константы
export const API_ENDPOINTS = {
  BASE_URL: '/api',
  AUTH: '/auth',
  USERS: '/users',
  CONTENT: '/content',
  THEORY: '/theory',
} as const;

// Пагинация
export const PAGINATION = {
  DEFAULT_PAGE: 1,
  DEFAULT_LIMIT: 20,
  MAX_LIMIT: 100,
} as const;

// Роли пользователей
export const USER_ROLES = {
  GUEST: 'guest',
  USER: 'user',
  ADMIN: 'admin',
} as const;

// Времена задержки
export const DELAYS = {
  DEBOUNCE: 300,
  THROTTLE: 1000,
  TOAST_DURATION: 3000,
} as const;

// Размеры экрана
export const BREAKPOINTS = {
  MOBILE: 768,
  TABLET: 1024,
  DESKTOP: 1200,
} as const;

// Z-индексы
export const Z_INDEX = {
  DROPDOWN: 1000,
  STICKY: 1020,
  FIXED: 1030,
  MODAL_BACKDROP: 1040,
  MODAL: 1050,
  POPOVER: 1060,
  TOOLTIP: 1070,
  TOAST: 1080,
} as const;
