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

export const contentQueryKeys = {
  all: ['content'] as const,
  blocks: () => [...contentQueryKeys.all, 'blocks'] as const,
  block: (id: string) => [...contentQueryKeys.all, 'block', id] as const,
  categories: () => [...contentQueryKeys.all, 'categories'] as const,
  companies: () => [...contentQueryKeys.all, 'companies'] as const,
  filteredBlocks: (filters: ContentBlocksFilters) =>
    [...contentQueryKeys.blocks(), 'filtered', filters] as const,
};

export const useContentBlocks = (filters: ContentBlocksFilters = {}) => {
  const dispatch = useAppDispatch();

  const query = useQuery({
    queryKey: contentQueryKeys.filteredBlocks(filters),
    queryFn: () => {
      const params = new URLSearchParams();
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') {
          if (Array.isArray(value)) {
            let paramName = key;
            if (key === 'mainCategories') {
              paramName = 'mainCategories';
            } else if (key === 'subCategories') {
              paramName = 'subCategories';
            } else if (key === 'companies') {
              paramName = 'companiesList';
            }

            value.forEach((item) => {
              if (item !== undefined && item !== null && item !== '') {
                params.append(paramName, item.toString());
              }
            });
          } else {
            params.append(key, value.toString());
          }
        }
      });

      return fetch(`/api/tasks/items?${params.toString()}`, {
        credentials: 'include',
      }).then((res) => res.json());
    },
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
            : 'Ошибка загрузки блоков'
        )
      );
    }
  }, [query.error, dispatch]);

  return query;
};

export const useInfiniteContentBlocks = (
  filters: ContentBlocksFilters = {}
) => {
  const dispatch = useAppDispatch();

  const query = useInfiniteQuery({
    queryKey: contentQueryKeys.filteredBlocks(filters),
    queryFn: ({ pageParam = 1 }) => {
      const params = new URLSearchParams();
      Object.entries({ ...filters, page: pageParam }).forEach(
        ([key, value]) => {
          if (value !== undefined && value !== null && value !== '') {
            if (Array.isArray(value)) {
              let paramName = key;
              if (key === 'mainCategories') {
                paramName = 'mainCategories';
              } else if (key === 'subCategories') {
                paramName = 'subCategories';
              } else if (key === 'companies') {
                paramName = 'companiesList';
              }

              value.forEach((item) => {
                if (item !== undefined && item !== null && item !== '') {
                  params.append(paramName, item.toString());
                }
              });
            } else {
              params.append(key, value.toString());
            }
          }
        }
      );

      return fetch(`/api/tasks/items?${params.toString()}`, {
        credentials: 'include',
      }).then((res) => res.json());
    },
    getNextPageParam: (lastPage: ContentBlocksResponse) => {
      const { page, totalPages } = lastPage.pagination;
      return page < totalPages ? page + 1 : undefined;
    },
    staleTime: 5 * 60 * 1000,
    initialPageParam: 1,
  });

  useEffect(() => {
    if (query.data) {
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

export const useContentBlock = (blockId: string) => {
  const dispatch = useAppDispatch();

  const query = useQuery({
    queryKey: contentQueryKeys.block(blockId),
    queryFn: () => contentApi.getBlock(blockId),
    enabled: !!blockId,
    staleTime: 10 * 60 * 1000,
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

export const useContentCategories = () => {
  const dispatch = useAppDispatch();

  const query = useQuery({
    queryKey: contentQueryKeys.categories(),
    queryFn: () => {
      return fetch('/api/tasks/categories', {
        credentials: 'include',
      }).then((res) => res.json());
    },
    staleTime: 30 * 60 * 1000,
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

    onMutate: async ({ blockId, action }) => {
      await queryClient.cancelQueries({ queryKey: ['content'] });

      const currentBlocks = queryClient.getQueryData([
        'content',
        'blocks',
        'filtered',
      ]);

      let newCount = 0;
      if (
        currentBlocks &&
        typeof currentBlocks === 'object' &&
        'pages' in currentBlocks
      ) {
        const pages = (currentBlocks as { pages: { data: ContentBlock[] }[] })
          .pages;
        for (const page of pages) {
          const block = page.data.find((b: ContentBlock) => b.id === blockId);
          if (block) {
            newCount =
              action === 'increment'
                ? (block.currentUserSolvedCount || 0) + 1
                : Math.max(0, (block.currentUserSolvedCount || 0) - 1);
            break;
          }
        }
      }

      dispatch(
        updateBlockProgress({
          blockId,
          solvedCount: newCount,
        })
      );

      queryClient.setQueriesData(
        { queryKey: ['content', 'blocks', 'filtered'] },
        (oldData: unknown) => {
          if (!oldData || typeof oldData !== 'object' || !('pages' in oldData))
            return oldData;

          const data = oldData as { pages: { data: ContentBlock[] }[] };
          return {
            ...data,
            pages: data.pages.map((page) => ({
              ...page,
              data: page.data.map((block: ContentBlock) =>
                block.id === blockId
                  ? { ...block, currentUserSolvedCount: newCount }
                  : block
              ),
            })),
          };
        }
      );

      // Оптимистично обновляем кэш для конкретного блока
      queryClient.setQueryData<ContentBlock>(
        contentQueryKeys.block(blockId),
        (oldBlock) => {
          if (!oldBlock) return oldBlock;
          return { ...oldBlock, currentUserSolvedCount: newCount };
        }
      );

      // Обновляем также старый query key на всякий случай
      queryClient.setQueryData<ContentBlock>(
        ['content-block', blockId],
        (oldBlock) => {
          if (!oldBlock) return oldBlock;
          return { ...oldBlock, currentUserSolvedCount: newCount };
        }
      );

      return { previousData: currentBlocks, newCount };
    },

    onSuccess: (data, variables) => {
      dispatch(
        updateBlockProgress({
          blockId: variables.blockId,
          solvedCount: data.solvedCount,
        })
      );

      queryClient.setQueriesData(
        { queryKey: ['content', 'blocks', 'filtered'] },
        (oldData: unknown) => {
          if (!oldData || typeof oldData !== 'object' || !('pages' in oldData))
            return oldData;

          const dataObj = oldData as { pages: { data: ContentBlock[] }[] };
          return {
            ...dataObj,
            pages: dataObj.pages.map((page) => ({
              ...page,
              data: page.data.map((block: ContentBlock) =>
                block.id === variables.blockId
                  ? { ...block, currentUserSolvedCount: data.solvedCount }
                  : block
              ),
            })),
          };
        }
      );

      queryClient.setQueryData<ContentBlock>(
        contentQueryKeys.block(variables.blockId),
        (oldBlock) => {
          if (!oldBlock) return oldBlock;
          return { ...oldBlock, currentUserSolvedCount: data.solvedCount };
        }
      );

      // Обновляем также старый query key на всякий случай
      queryClient.setQueryData<ContentBlock>(
        ['content-block', variables.blockId],
        (oldBlock) => {
          if (!oldBlock) return oldBlock;
          return { ...oldBlock, currentUserSolvedCount: data.solvedCount };
        }
      );
    },

    onError: (error, _variables, context) => {
      if (context?.previousData) {
        queryClient.setQueryData(
          ['content', 'blocks', 'filtered'],
          context.previousData
        );
      }

      dispatch(
        setError(
          error instanceof Error ? error.message : 'Ошибка обновления прогресса'
        )
      );
    },
  });
};

export const useSearchContentBlocks = (
  query: string,
  filters: ContentBlocksFilters = {}
) => {
  const dispatch = useAppDispatch();

  const queryResult = useQuery({
    queryKey: [...contentQueryKeys.blocks(), 'search', query, filters],
    queryFn: () => contentApi.searchBlocks(query, filters),
    enabled: query.length >= 2,
    staleTime: 2 * 60 * 1000,
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

export const useContentBlocksByCategories = (
  mainCategories?: string[],
  subCategories?: string[],
  additionalFilters: ContentBlocksFilters = {}
) => {
  const dispatch = useAppDispatch();

  const query = useQuery({
    queryKey: [
      ...contentQueryKeys.blocks(),
      'categories',
      mainCategories,
      subCategories,
      additionalFilters,
    ],
    queryFn: () =>
      contentApi.getBlocksByCategories(
        mainCategories,
        subCategories,
        additionalFilters
      ),
    enabled: !!(mainCategories && mainCategories.length > 0),
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
            : 'Ошибка загрузки блоков категорий'
        )
      );
    }
  }, [query.error, dispatch]);

  return query;
};

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

export const useCompanies = (filters?: {
  mainCategories?: string[];
  subCategories?: string[];
}) => {
  const query = useQuery({
    queryKey: [...contentQueryKeys.companies(), filters],
    queryFn: () => {
      const params = new URLSearchParams();
      if (filters?.mainCategories && filters.mainCategories.length > 0) {
        filters.mainCategories.forEach((category) => {
          params.append('mainCategories', category);
        });
      }
      if (filters?.subCategories && filters.subCategories.length > 0) {
        filters.subCategories.forEach((category) => {
          params.append('subCategories', category);
        });
      }

      return fetch(`/api/tasks/companies?${params.toString()}`, {
        credentials: 'include',
      }).then((res) => res.json());
    },
    staleTime: 30 * 60 * 1000,
  });

  return query;
};
