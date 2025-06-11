import axios from 'axios';

export const apiInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  withCredentials: true,
  timeout: 5000, // 5 секунд таймаут
  headers: {
    'Content-Type': 'application/json',
  },
});

apiInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status;
    const message =
      error.response?.data?.message || 'An unknown error occurred';

    // Обрабатываем различные типы ошибок
    if (error.code === 'ERR_NETWORK') {
      return Promise.reject(new Error('Network Error: API недоступен'));
    }

    if (error.code === 'ECONNABORTED') {
      return Promise.reject(new Error('Network Error: Таймаут запроса'));
    }

    // Включаем статус код в сообщение для правильной обработки 401
    const errorMessage = status ? `${status}: ${message}` : message;

    return Promise.reject(new Error(errorMessage));
  }
);
