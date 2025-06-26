// Конфигурация API

// Функция для получения переменной окружения, совместимая с orval
const getEnvVar = (key: string, defaultValue: string): string => {
  // В Node.js используем process.env
  if (typeof process !== 'undefined' && process.env) {
    return process.env[key] || defaultValue;
  }

  return defaultValue;
};

export const API_CONFIG = {
  BASE_URL: getEnvVar('VITE_API_BASE_URL', '/api'),
  TIMEOUT: 20000,
  WITH_CREDENTIALS: true,
} as const;
