import {
  selectContentBlocksError,
  selectContentBlocksFilters,
  type ContentBlock,
  type ContentBlocksResponse,
} from '@/entities/ContentBlock';
import { ButtonVariant } from '@/shared/components/Button/model/types';
import { Button } from '@/shared/components/Button/ui/Button';
import { useAppSelector } from '@/shared/hooks/redux';
import { useInfiniteContentBlocks } from '@/shared/hooks/useContentBlocks';
import { ContentBlockCard } from '@/widgets/ContentBlockCard';
import { AlertCircle, Loader2 } from 'lucide-react';
import { useEffect, useMemo, useRef } from 'react';
import styles from './ContentBlocksList.module.scss';

interface ContentBlocksListProps {
  className?: string;
  variant?: 'default' | 'compact';
}

export const ContentBlocksList = ({
  className,
  variant = 'default',
}: ContentBlocksListProps) => {
  const filters = useAppSelector(selectContentBlocksFilters);
  const error = useAppSelector(selectContentBlocksError);
  const loadMoreRef = useRef<HTMLDivElement>(null);

  const {
    data,
    error: queryError,
    fetchNextPage,
    hasNextPage,
    isFetching,
    isFetchingNextPage,
    isLoading,
  } = useInfiniteContentBlocks(filters);

  // Автоматическая загрузка при прокручивании
  useEffect(() => {
    const loadMoreElement = loadMoreRef.current;
    if (!loadMoreElement || !hasNextPage || isFetchingNextPage) return;

    const observer = new IntersectionObserver(
      (entries) => {
        const [entry] = entries;
        if (entry.isIntersecting) {
          fetchNextPage();
        }
      },
      {
        threshold: 0.1, // Загружаем когда элемент на 10% виден
        rootMargin: '100px', // Начинаем загрузку за 100px до появления элемента
      }
    );

    observer.observe(loadMoreElement);

    return () => {
      observer.unobserve(loadMoreElement);
    };
  }, [fetchNextPage, hasNextPage, isFetchingNextPage]);

  // Объединяем все блоки со всех страниц
  const allBlocks = useMemo(() => {
    if (!data?.pages) return [];

    return data.pages.flatMap((page) => {
      // Проверяем структуру каждой страницы
      if (!page) {
        return [];
      }

      // Возможно API возвращает данные в другом поле - проверяем все возможные варианты
      const pageWithBlocks = page as ContentBlocksResponse & {
        blocks?: ContentBlock[];
      };
      const blocks = page.data || pageWithBlocks.blocks || [];

      if (!Array.isArray(blocks)) {
        return [];
      }

      return blocks.filter((block) => block && block.id);
    });
  }, [data]);

  // Получаем информацию о пагинации с последней страницы
  const lastPage = data?.pages[data.pages.length - 1];
  const pagination = lastPage?.pagination;

  const displayError = error || queryError;

  if (isLoading) {
    return (
      <div
        className={`${styles.contentBlocksList} ${styles.loading} ${className || ''}`}
      >
        <div className={styles.loadingContainer}>
          <Loader2 size={32} className={styles.spinner} />
          <p>Загрузка контент-блоков...</p>
        </div>
      </div>
    );
  }

  if (displayError) {
    return (
      <div
        className={`${styles.contentBlocksList} ${styles.error} ${className || ''}`}
      >
        <div className={styles.errorContainer}>
          <AlertCircle size={32} className={styles.errorIcon} />
          <h3>Ошибка загрузки</h3>
          <p>
            {displayError instanceof Error
              ? displayError.message
              : 'Произошла ошибка при загрузке данных'}
          </p>
          <Button
            onClick={() => window.location.reload()}
            variant={ButtonVariant.PRIMARY}
          >
            Обновить страницу
          </Button>
        </div>
      </div>
    );
  }

  if (allBlocks.length === 0) {
    return (
      <div
        className={`${styles.contentBlocksList} ${styles.empty} ${className || ''}`}
      >
        <div className={styles.emptyContainer}>
          <h3>Контент-блоки не найдены</h3>
          <p>Попробуйте изменить фильтры поиска или создать новый контент.</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`${styles.contentBlocksList} ${className || ''}`}>
      {/* Информация о результатах */}
      <div className={styles.resultsInfo}>
        <p>
          Показано {allBlocks.length}
          {pagination && <span> из {pagination.totalItems} блоков</span>}
        </p>
      </div>

      {/* Список блоков */}
      <div
        className={`${styles.blocksList} ${variant === 'compact' ? styles.compact : ''}`}
      >
        {allBlocks.map((block) => (
          <ContentBlockCard
            key={block.id}
            block={block}
            variant={variant}
            className={styles.blockCard}
          />
        ))}
      </div>

      {/* Элемент-триггер для автоматической загрузки */}
      {hasNextPage && (
        <div ref={loadMoreRef} className={styles.loadMoreTrigger}>
          {isFetchingNextPage && (
            <div className={styles.loadingMore}>
              <Loader2 size={24} className={styles.spinner} />
              <span>Загрузка дополнительных блоков...</span>
            </div>
          )}
        </div>
      )}

      {/* Индикатор загрузки для дополнительных данных */}
      {isFetching && !isLoading && !isFetchingNextPage && (
        <div className={styles.additionalLoading}>
          <Loader2 size={24} className={styles.spinner} />
          <span>Обновление данных...</span>
        </div>
      )}
    </div>
  );
};
