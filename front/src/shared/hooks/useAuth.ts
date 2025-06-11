import type {
  LoginRequest,
  RegisterRequest,
} from '@/entities/User/model/types';
import { authApi } from '@/shared/api/auth';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

// Ключи для запросов
export const authKeys = {
  profile: ['auth', 'profile'] as const,
};

// Хук для получения профиля
export const useProfile = () => {
  return useQuery({
    queryKey: authKeys.profile,
    queryFn: async () => {
      try {
        return await authApi.getProfile();
      } catch (error) {
        // 401 - это нормально, пользователь просто не авторизован
        if (error instanceof Error && error.message.includes('401')) {
          return null;
        }

        // Network/CORS ошибки в preview режиме - считаем как неавторизованного пользователя
        if (
          error instanceof Error &&
          (error.message.includes('CORS') ||
            error.message.includes('Network Error') ||
            error.message.includes('ERR_FAILED') ||
            error.message.includes('fetch'))
        ) {
          console.warn(
            'API недоступен (preview режим?), пользователь считается неавторизованным'
          );
          return null;
        }

        throw error;
      }
    },
    retry: false, // Не повторяем при ошибках
    retryOnMount: false, // Не повторяем при монтировании
    refetchOnWindowFocus: false, // Не перезапрашиваем при фокусе окна
    refetchOnReconnect: false, // Не перезапрашиваем при переподключении
    staleTime: Infinity, // Данные никогда не устаревают автоматически
    gcTime: 30 * 60 * 1000, // 30 минут в памяти
  });
};

// Хук для входа
export const useLogin = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (credentials: LoginRequest) => authApi.login(credentials),
    onSuccess: async () => {
      // Обновляем профиль после успешного входа
      await queryClient.invalidateQueries({ queryKey: authKeys.profile });
    },
  });
};

// Хук для регистрации
export const useRegister = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (credentials: RegisterRequest) => authApi.register(credentials),
    onSuccess: () => {
      // Очищаем кэш профиля после регистрации
      queryClient.removeQueries({ queryKey: authKeys.profile });
      window.location.href = '/';
    },
  });
};

// Хук для выхода
export const useLogout = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => authApi.logout(),
    onSuccess: () => {
      // Очищаем весь кэш после выхода
      queryClient.clear();
      window.location.href = '/';
    },
  });
};

// Основной хук для авторизации
export const useAuth = () => {
  const { data: user, isLoading, error, isSuccess, isFetched } = useProfile();

  return {
    user,
    isAuthenticated: isSuccess && !!user,
    isInitialized: isFetched, // Инициализированы когда запрос завершен (успешно или с ошибкой)
    isLoading,
    error: error?.message || null,
  };
};
