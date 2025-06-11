import { authApi } from '@/shared/api/auth';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

// Ключи для кэширования
export const adminQueryKeys = {
  all: ['admin'] as const,
  stats: () => [...adminQueryKeys.all, 'stats'] as const,
  users: () => [...adminQueryKeys.all, 'users'] as const,
  overview: () => [...adminQueryKeys.all, 'overview'] as const,
  contentStats: (params?: { category?: string; includeBlocks?: boolean }) =>
    [...adminQueryKeys.all, 'content-stats', params] as const,
  theoryStats: (params?: { category?: string; includeCards?: boolean }) =>
    [...adminQueryKeys.all, 'theory-stats', params] as const,
};

// Хук для получения основной статистики для админ-дашборда
export const useAdminStats = () => {
  return useQuery({
    queryKey: adminQueryKeys.stats(),
    queryFn: () => authApi.admin.getStats(),
    staleTime: 2 * 60 * 1000, // 2 минуты
    retry: 3,
  });
};

// Хук для получения списка пользователей
export const useUsers = () => {
  return useQuery({
    queryKey: adminQueryKeys.users(),
    queryFn: async () => {
      const response = await authApi.admin.getUsers();
      // Адаптируем ответ API к нашему интерфейсу
      if (response.users) {
        return response.users;
      } else if (Array.isArray(response)) {
        return response;
      } else {
        return [];
      }
    },
    staleTime: 1 * 60 * 1000, // 1 минута
    retry: 3,
  });
};

// Хук для получения детальной статистики
export const useDetailedStats = () => {
  return useQuery({
    queryKey: [...adminQueryKeys.stats(), 'detailed'],
    queryFn: async () => {
      // Пока нет метода getDetailedStats, используем обычную статистику
      const response = await authApi.admin.getStats();
      // Дополняем базовую статистику до детальной
      return {
        users: {
          ...response.users,
          activeThisMonth: response.users.total || 0,
          newThisWeek: 0,
          avgSessionTime: 0,
        },
        content: {
          ...response.content,
          categoriesCount: 0,
          avgBlocksPerFile:
            response.content.totalFiles > 0
              ? response.content.totalBlocks / response.content.totalFiles
              : 0,
          recentlyAdded: 0,
        },
        progress: {
          ...response.progress,
          avgProgressPerUser: 0,
          mostActiveUsers: [] as Array<{
            email: string;
            progressCount: number;
          }>,
          topCategories: [] as Array<{
            category: string;
            progressCount: number;
          }>,
        },
        system: {
          uptime: 0,
          responseTime: 0,
          errorRate: 0,
          apiCalls24h: 0,
        },
      };
    },
    staleTime: 2 * 60 * 1000, // 2 минуты
    retry: 3,
  });
};

// Хук для получения статистики обзора
export const useOverviewStats = () => {
  return useQuery({
    queryKey: adminQueryKeys.overview(),
    queryFn: async () => {
      const response = await fetch('/api/stats/overview', {
        credentials: 'include',
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return response.json();
    },
    staleTime: 5 * 60 * 1000, // 5 минут
    retry: 3,
  });
};

// Хук для получения статистики контента
export const useContentStats = (
  params: {
    category?: string;
    includeBlocks?: boolean;
  } = {}
) => {
  return useQuery({
    queryKey: adminQueryKeys.contentStats(params),
    queryFn: async () => {
      const searchParams = new URLSearchParams();
      if (params.category) searchParams.append('category', params.category);
      if (params.includeBlocks) searchParams.append('includeBlocks', 'true');

      const response = await fetch(`/api/stats/content?${searchParams}`, {
        credentials: 'include',
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return response.json();
    },
    enabled: Object.keys(params).length > 0,
    staleTime: 5 * 60 * 1000, // 5 минут
    retry: 3,
  });
};

// Хук для получения статистики теории
export const useTheoryStats = (
  params: {
    category?: string;
    includeCards?: boolean;
  } = {}
) => {
  return useQuery({
    queryKey: adminQueryKeys.theoryStats(params),
    queryFn: async () => {
      const searchParams = new URLSearchParams();
      if (params.category) searchParams.append('category', params.category);
      if (params.includeCards) searchParams.append('includeCards', 'true');

      const response = await fetch(`/api/stats/theory?${searchParams}`, {
        credentials: 'include',
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return response.json();
    },
    enabled: Object.keys(params).length > 0,
    staleTime: 5 * 60 * 1000, // 5 минут
    retry: 3,
  });
};

// Хук для изменения роли пользователя
export const useChangeUserRole = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      userId,
      newRole,
    }: {
      userId: number;
      newRole: 'USER' | 'ADMIN';
    }) => {
      return authApi.admin.updateUser(userId, { role: newRole });
    },
    onSuccess: () => {
      // Инвалидируем кэш пользователей для обновления списка
      queryClient.invalidateQueries({ queryKey: adminQueryKeys.users() });
    },
    onError: (error) => {
      console.error('Ошибка изменения роли:', error);
    },
  });
};

// Хук для удаления пользователя
export const useDeleteUser = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (userId: number) => {
      return authApi.admin.deleteUser(userId);
    },
    onSuccess: () => {
      // Инвалидируем кэш пользователей для обновления списка
      queryClient.invalidateQueries({ queryKey: adminQueryKeys.users() });
      // Также обновляем статистику
      queryClient.invalidateQueries({ queryKey: adminQueryKeys.stats() });
    },
    onError: (error) => {
      console.error('Ошибка удаления пользователя:', error);
    },
  });
};
