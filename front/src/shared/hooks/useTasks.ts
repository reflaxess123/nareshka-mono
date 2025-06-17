import { tasksApi, type TaskItemsFilters } from '@/shared/api/tasks';
import {
  useInfiniteQuery,
  useMutation,
  useQuery,
  useQueryClient,
} from '@tanstack/react-query';

export const taskQueryKeys = {
  all: ['tasks'] as const,
  items: () => [...taskQueryKeys.all, 'items'] as const,
  item: (id: string) => [...taskQueryKeys.all, 'item', id] as const,
  categories: () => [...taskQueryKeys.all, 'categories'] as const,
  filteredItems: (filters: TaskItemsFilters) =>
    [...taskQueryKeys.items(), 'filtered', filters] as const,
};

export const useTasks = (filters: TaskItemsFilters = {}) => {
  return useQuery({
    queryKey: taskQueryKeys.filteredItems(filters),
    queryFn: () => tasksApi.getTaskItems(filters),
    staleTime: 5 * 60 * 1000,
    retry: false,
    retryOnMount: false,
  });
};

export const useInfiniteTasks = (params: Omit<TaskItemsFilters, 'page'>) => {
  return useInfiniteQuery({
    queryKey: ['tasks-infinite', params],
    queryFn: async ({ pageParam = 1 }) => {
      try {
        return await tasksApi.getTaskItems({
          ...params,
          page: pageParam,
        });
      } catch (error) {
        if (
          error instanceof Error &&
          (error.message.includes('CORS') ||
            error.message.includes('Network Error') ||
            error.message.includes('ERR_FAILED') ||
            error.message.includes('fetch'))
        ) {
          console.warn('Tasks API недоступен (preview режим?)');
          return {
            items: [],
            pagination: {
              page: pageParam,
              limit: 10,
              total: 0,
              totalPages: 0,
              hasNext: false,
              hasPrev: false,
            },
          };
        }
        throw error;
      }
    },
    getNextPageParam: (lastPage) => {
      const { page, totalPages } = lastPage.pagination;
      return page < totalPages ? page + 1 : undefined;
    },
    initialPageParam: 1,
    retry: false,
    retryOnMount: false,
  });
};

export const useTaskCategories = () => {
  return useQuery({
    queryKey: taskQueryKeys.categories(),
    queryFn: () => tasksApi.getTaskCategories(),
    staleTime: 10 * 60 * 1000,
    retry: false,
    retryOnMount: false,
  });
};

export const useTasksByCategory = (
  category: string,
  subCategory?: string,
  additionalFilters: TaskItemsFilters = {}
) => {
  return useQuery({
    queryKey: [
      ...taskQueryKeys.items(),
      'category',
      category,
      subCategory,
      additionalFilters,
    ],
    queryFn: () =>
      tasksApi.getTasksByCategory(category, subCategory, additionalFilters),
    enabled: !!category,
    staleTime: 5 * 60 * 1000,
    retry: false,
    retryOnMount: false,
  });
};

export const useSearchTasks = (
  query: string,
  additionalFilters: TaskItemsFilters = {}
) => {
  return useQuery({
    queryKey: [...taskQueryKeys.items(), 'search', query, additionalFilters],
    queryFn: () => tasksApi.searchTasks(query, additionalFilters),
    enabled: !!query && query.length > 2,
    staleTime: 5 * 60 * 1000,
    retry: false,
    retryOnMount: false,
  });
};

export const useContentBlocksOnly = (
  filters: Omit<TaskItemsFilters, 'itemType'> = {}
) => {
  return useQuery({
    queryKey: [...taskQueryKeys.items(), 'content-blocks', filters],
    queryFn: () => tasksApi.getContentBlocks(filters),
    staleTime: 5 * 60 * 1000,
    retry: false,
    retryOnMount: false,
  });
};

export const useQuizCardsOnly = (
  filters: Omit<TaskItemsFilters, 'itemType'> = {}
) => {
  return useQuery({
    queryKey: [...taskQueryKeys.items(), 'quiz-cards', filters],
    queryFn: () => tasksApi.getQuizCards(filters),
    staleTime: 5 * 60 * 1000,
    retry: false,
    retryOnMount: false,
  });
};

export const usePrefetchTasks = () => {
  const queryClient = useQueryClient();

  return (filters: TaskItemsFilters) => {
    queryClient.prefetchQuery({
      queryKey: taskQueryKeys.filteredItems(filters),
      queryFn: () => tasksApi.getTaskItems(filters),
      staleTime: 5 * 60 * 1000,
    });
  };
};

export const useUpdateTaskProgress = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async ({
      itemId,
      type,
      action,
    }: {
      itemId: string;
      type: 'content_block' | 'theory_quiz';
      action: 'increment' | 'decrement';
    }) => {
      if (type === 'content_block') {
        const response = await fetch(`/api/content/blocks/${itemId}/progress`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({ action }),
        });
        return response.json();
      } else {
        const response = await fetch(`/api/theory/cards/${itemId}/progress`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({ action }),
        });
        return response.json();
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: taskQueryKeys.all });
    },
  });
};
