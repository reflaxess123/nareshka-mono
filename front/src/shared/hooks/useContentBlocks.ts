import {
  type ContentBlock,
  type ContentBlocksFilters,
  type ContentProgressUpdate,
  setCategories,
  setError,
  updateBlockProgress,
} from '@/entities/ContentBlock';
import { contentApi } from '@/shared/api/content';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useEffect } from 'react';
import { useAppDispatch } from './redux';

interface InfiniteQueryData {
  pages: { data: ContentBlock[] }[];
  pageParams: unknown[];
}

export const contentQueryKeys = {
  all: ['content'] as const,
  blocks: () => [...contentQueryKeys.all, 'blocks'] as const,
  block: (id: string) => [...contentQueryKeys.all, 'block', id] as const,
  categories: () => [...contentQueryKeys.all, 'categories'] as const,
  companies: () => [...contentQueryKeys.all, 'companies'] as const,
  filteredBlocks: (filters: ContentBlocksFilters) =>
    [...contentQueryKeys.blocks(), 'filtered', filters] as const,
};

export const useContentCategories = () => {
  const dispatch = useAppDispatch();

  const query = useQuery({
    queryKey: contentQueryKeys.categories(),
    queryFn: () => {
      return fetch('/api/v2/tasks/categories', {
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

          const data = oldData as InfiniteQueryData;
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

          const dataObj = oldData as InfiniteQueryData;
          return {
            ...dataObj,
            pages: dataObj.pages.map((page: { data: ContentBlock[] }) => ({
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

      // ИСПРАВЛЕНИЕ: Инвалидируем кэш прогресса для обновления профиля
      queryClient.invalidateQueries({ queryKey: ['progress'] });
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

export const useCompanies = (filters?: {
  mainCategories?: string[];
  subCategories?: string[];
}) => {
  return useQuery({
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

      return fetch(`/api/v2/tasks/companies?${params.toString()}`, {
        credentials: 'include',
      }).then((res) => res.json());
    },
    staleTime: 30 * 60 * 1000,
  });
};
