import axios from 'axios';
import { API_CONFIG } from '../config/api.config';

export const apiInstance = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  withCredentials: API_CONFIG.WITH_CREDENTIALS,
  timeout: API_CONFIG.TIMEOUT,
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

export const apiClient = <T = unknown>(
  config: import('axios').AxiosRequestConfig
): Promise<T> => {
  const source = axios.CancelToken.source();
  const promise = apiInstance({
    ...config,
    cancelToken: source.token,
  }).then(({ data }) => data);

  // @ts-expect-error добавляем метод cancel к promise
  promise.cancel = () => {
    source.cancel('Query was cancelled');
  };

  return promise;
};

export default apiClient;
