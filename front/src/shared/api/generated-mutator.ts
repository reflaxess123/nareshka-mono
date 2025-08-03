import axios from 'axios';

// Создаем отдельный экземпляр axios для generated API
// Не используем базовый URL, так как пути в OpenAPI уже содержат /api/v2
export const generatedApiInstance = axios.create({
  withCredentials: true,
  timeout: 20000,
  headers: {
    'Content-Type': 'application/json',
  },
  // Настройка сериализации параметров для массивов
  paramsSerializer: {
    serialize: (params) => {
      const searchParams = new URLSearchParams();
      
      Object.entries(params).forEach(([key, value]) => {
        if (Array.isArray(value)) {
          // Для массивов повторяем ключ для каждого значения
          value.forEach(item => {
            if (item !== null && item !== undefined) {
              searchParams.append(key, String(item));
            }
          });
        } else if (value !== null && value !== undefined) {
          searchParams.append(key, String(value));
        }
      });
      
      return searchParams.toString();
    }
  }
});

generatedApiInstance.interceptors.response.use(
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

// Функция для Orval mutator - для generated API
export const generatedApiClient = <T = unknown>(
  config: import('axios').AxiosRequestConfig
): Promise<T> => {
  const source = axios.CancelToken.source();
  const promise = generatedApiInstance({
    ...config,
    cancelToken: source.token,
  }).then(({ data }) => data);

  // @ts-expect-error добавляем метод cancel к promise
  promise.cancel = () => {
    source.cancel('Query was cancelled');
  };

  return promise;
};

// Экспорт для Orval mutator (именованный)
export default generatedApiClient;
