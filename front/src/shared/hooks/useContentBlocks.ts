import {
  setBlocks,
  setCategories,
  setCurrentBlock,
  setError,
  updateBlockProgress,
  type ContentBlock,
  type ContentBlocksFilters,
  type ContentBlocksResponse,
  type ContentProgressUpdate,
} from '@/entities/ContentBlock';
import { contentApi } from '@/shared/api/content';
import {
  useInfiniteQuery,
  useMutation,
  useQuery,
  useQueryClient,
} from '@tanstack/react-query';
import { useEffect } from 'react';
import { useAppDispatch } from './redux';

// Ключи для кэширования
export const contentQueryKeys = {
  all: ['content'] as const,
  blocks: () => [...contentQueryKeys.all, 'blocks'] as const,
  block: (id: string) => [...contentQueryKeys.all, 'block', id] as const,
  categories: () => [...contentQueryKeys.all, 'categories'] as const,
  filteredBlocks: (filters: ContentBlocksFilters) =>
    [...contentQueryKeys.blocks(), 'filtered', filters] as const,
};

// Хук для получения списка блоков с фильтрацией
export const useContentBlocks = (filters: ContentBlocksFilters = {}) => {
  const dispatch = useAppDispatch();

  const query = useQuery({
    queryKey: contentQueryKeys.filteredBlocks(filters),
    queryFn: () => contentApi.getBlocks(filters),
    staleTime: 5 * 60 * 1000, // 5 минут
  });

  useEffect(() => {
    if (query.data) {
      dispatch(setBlocks(query.data));
    }
  }, [query.data, dispatch]);

  useEffect(() => {
    if (query.error) {
      dispatch(
        setError(
          query.error instanceof Error
            ? query.error.message
            : 'Ошибка загрузки блоков'
        )
      );
    }
  }, [query.error, dispatch]);

  return query;
};

// Хук для бесконечного скролла блоков
export const useInfiniteContentBlocks = (
  filters: ContentBlocksFilters = {}
) => {
  const dispatch = useAppDispatch();

  const query = useInfiniteQuery({
    queryKey: contentQueryKeys.filteredBlocks(filters),
    queryFn: ({ pageParam = 1 }) =>
      contentApi.getBlocks({ ...filters, page: pageParam as number }),
    getNextPageParam: (lastPage: ContentBlocksResponse) => {
      const { page, totalPages } = lastPage.pagination;
      return page < totalPages ? page + 1 : undefined;
    },
    staleTime: 5 * 60 * 1000,
    initialPageParam: 1,
  });

  useEffect(() => {
    if (query.data) {
      // Объединяем все страницы в один массив
      const allBlocks = query.data.pages.flatMap((page) => page.data);
      const lastPage = query.data.pages[query.data.pages.length - 1];

      dispatch(
        setBlocks({
          data: allBlocks,
          pagination: lastPage.pagination,
        })
      );
    }
  }, [query.data, dispatch]);

  useEffect(() => {
    if (query.error) {
      dispatch(
        setError(
          query.error instanceof Error
            ? query.error.message
            : 'Ошибка загрузки блоков'
        )
      );
    }
  }, [query.error, dispatch]);

  return query;
};

// Хук для получения конкретного блока
export const useContentBlock = (blockId: string) => {
  const dispatch = useAppDispatch();

  const query = useQuery({
    queryKey: contentQueryKeys.block(blockId),
    queryFn: () => contentApi.getBlock(blockId),
    enabled: !!blockId,
    staleTime: 10 * 60 * 1000, // 10 минут
  });

  useEffect(() => {
    if (query.data) {
      dispatch(setCurrentBlock(query.data));
    }
  }, [query.data, dispatch]);

  useEffect(() => {
    if (query.error) {
      dispatch(
        setError(
          query.error instanceof Error
            ? query.error.message
            : 'Ошибка загрузки блока'
        )
      );
    }
  }, [query.error, dispatch]);

  return query;
};

// Хук для получения категорий
export const useContentCategories = () => {
  const dispatch = useAppDispatch();

  const query = useQuery({
    queryKey: contentQueryKeys.categories(),
    queryFn: () => contentApi.getCategories(),
    staleTime: 30 * 60 * 1000, // 30 минут (категории редко меняются)
  });

  useEffect(() => {
    if (query.data) {
      dispatch(setCategories(query.data));
    }
  }, [query.data, dispatch]);

  useEffect(() => {
    if (query.error) {
      dispatch(
        setError(
          query.error instanceof Error
            ? query.error.message
            : 'Ошибка загрузки категорий'
        )
      );
    }
  }, [query.error, dispatch]);

  return query;
};

// Хук для обновления прогресса
export const useUpdateProgress = () => {
  const queryClient = useQueryClient();
  const dispatch = useAppDispatch();

  return useMutation({
    mutationFn: ({
      blockId,
      action,
    }: {
      blockId: string;
      action: ContentProgressUpdate['action'];
    }) => contentApi.updateProgress(blockId, { action }),
    onSuccess: (data, variables) => {
      // Обновляем Redux состояние
      dispatch(
        updateBlockProgress({
          blockId: variables.blockId,
          solvedCount: data.solvedCount,
        })
      );

      // Обновляем конкретный блок в кеше
      queryClient.setQueryData<ContentBlock>(
        contentQueryKeys.block(variables.blockId),
        (oldBlock) => {
          if (!oldBlock) return oldBlock;
          return { ...oldBlock, currentUserSolvedCount: data.solvedCount };
        }
      );

      // Инвалидируем кэш для обновления UI
      queryClient.invalidateQueries({ queryKey: contentQueryKeys.blocks() });
      queryClient.invalidateQueries({
        queryKey: contentQueryKeys.block(variables.blockId),
      });
    },
    onError: (error) => {
      dispatch(
        setError(
          error instanceof Error ? error.message : 'Ошибка обновления прогресса'
        )
      );
    },
  });
};

// Хук для поиска блоков
export const useSearchContentBlocks = (
  query: string,
  filters: ContentBlocksFilters = {}
) => {
  const dispatch = useAppDispatch();

  const queryResult = useQuery({
    queryKey: [...contentQueryKeys.blocks(), 'search', query, filters],
    queryFn: () => contentApi.searchBlocks(query, filters),
    enabled: query.length >= 2, // Поиск только при длине запроса >= 2 символов
    staleTime: 2 * 60 * 1000, // 2 минуты
  });

  useEffect(() => {
    if (queryResult.data) {
      dispatch(setBlocks(queryResult.data));
    }
  }, [queryResult.data, dispatch]);

  useEffect(() => {
    if (queryResult.error) {
      dispatch(
        setError(
          queryResult.error instanceof Error
            ? queryResult.error.message
            : 'Ошибка поиска'
        )
      );
    }
  }, [queryResult.error, dispatch]);

  return queryResult;
};

// Хук для получения блоков по категории
export const useContentBlocksByCategory = (
  mainCategory: string,
  subCategory?: string,
  additionalFilters: ContentBlocksFilters = {}
) => {
  const dispatch = useAppDispatch();

  const query = useQuery({
    queryKey: [
      ...contentQueryKeys.blocks(),
      'category',
      mainCategory,
      subCategory,
      additionalFilters,
    ],
    queryFn: () =>
      contentApi.getBlocksByCategory(
        mainCategory,
        subCategory,
        additionalFilters
      ),
    enabled: !!mainCategory,
    staleTime: 5 * 60 * 1000,
  });

  useEffect(() => {
    if (query.data) {
      dispatch(setBlocks(query.data));
    }
  }, [query.data, dispatch]);

  useEffect(() => {
    if (query.error) {
      dispatch(
        setError(
          query.error instanceof Error
            ? query.error.message
            : 'Ошибка загрузки блоков категории'
        )
      );
    }
  }, [query.error, dispatch]);

  return query;
};

// Хук для предзагрузки блока
export const usePrefetchContentBlock = () => {
  const queryClient = useQueryClient();

  return (blockId: string) => {
    queryClient.prefetchQuery({
      queryKey: contentQueryKeys.block(blockId),
      queryFn: () => contentApi.getBlock(blockId),
      staleTime: 10 * 60 * 1000,
    });
  };
};
