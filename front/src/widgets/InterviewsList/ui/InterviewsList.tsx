import React, { useState, useCallback, useEffect } from 'react';
import { InterviewCard, InterviewSkeletonList } from '../../../entities/Interview';
import { getInterviewsApiV2InterviewsGet } from '../../../shared/api/generated/api';
import { useInfiniteScroll } from '../../../shared/hooks/useInfiniteScroll';
import type { InterviewRecordResponseType } from '../../../shared/api/generated/api';
import type { UnifiedFilterState } from '../../../features/UnifiedFilters';
import { adaptToInterviewFilters } from '../../../features/UnifiedFilters';
import styles from './InterviewsList.module.scss';

interface InterviewsListProps {
  filters: UnifiedFilterState;
  onFiltersChange?: (filters: UnifiedFilterState) => void;
  className?: string;
}

export const InterviewsList: React.FC<InterviewsListProps> = ({
  filters,
  onFiltersChange,
  className,
}) => {
  const [page, setPage] = useState(1);
  const [allInterviews, setAllInterviews] = useState<InterviewRecordResponseType[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingMore, setIsLoadingMore] = useState(false);
  const [isInitialLoad, setIsInitialLoad] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);
  const [hasNextPage, setHasNextPage] = useState(false);
  const limit = 20;

  // Load interviews function
  const loadInterviews = useCallback(async (pageNum: number, isLoadMore: boolean = false) => {
    try {
      if (pageNum === 1 && !isLoadMore) {
        setIsLoading(true);
        setError(null);
      } else {
        setIsLoadingMore(true);
      }

      const adaptedFilters = adaptToInterviewFilters(filters);
      const response = await getInterviewsApiV2InterviewsGet({
        page: pageNum,
        limit,
        ...adaptedFilters,
      });

      if (response && response.interviews) {
        if (pageNum === 1 && !isLoadMore) {
          // Reset list for new search/filters
          setAllInterviews(response.interviews);
        } else {
          // Append new interviews
          setAllInterviews(prev => [...prev, ...response.interviews]);
        }
        
        setTotal(response.total);
        setHasNextPage(response.has_next);
        setError(null);
        
        // После первой успешной загрузки убираем флаг инициальной загрузки
        if (isInitialLoad) {
          setIsInitialLoad(false);
        }
      }
    } catch (err) {
      console.error('Error loading interviews:', err);
      setError('Не удалось загрузить интервью');
    } finally {
      setIsLoading(false);
      setIsLoadingMore(false);
    }
  }, [filters, limit, isInitialLoad]);

  // Initial load and filters change
  useEffect(() => {
    setPage(1);
    // НЕ очищаем allInterviews здесь, чтобы избежать мигания
    loadInterviews(1, false);
  }, [loadInterviews]);

  const handleLoadMore = useCallback(async () => {
    if (!isLoadingMore && hasNextPage && !isLoading) {
      const nextPage = page + 1;
      setPage(nextPage);
      await loadInterviews(nextPage, true);
    }
  }, [isLoadingMore, hasNextPage, isLoading, page, loadInterviews]);

  const { sentinelRef } = useInfiniteScroll({
    hasNextPage,
    isLoading: isLoading || isLoadingMore,
    onLoadMore: handleLoadMore,
    threshold: 200
  });



  if (error) {
    return (
      <div className={`${styles.container} ${className || ''}`}>
        <div className={styles.error}>
          <h2>Ошибка загрузки данных</h2>
          <p>Не удалось загрузить список интервью. Попробуйте обновить страницу.</p>
        </div>
      </div>
    );
  }

  // Initial loading with skeleton (только при самой первой загрузке)
  if (isInitialLoad && isLoading) {
    return (
      <div className={`${styles.container} ${className || ''}`}>
        <div className={styles.grid}>
          <InterviewSkeletonList count={8} />
        </div>
      </div>
    );
  }

  if (allInterviews.length === 0 && !isLoading && !isInitialLoad) {
    return (
      <div className={`${styles.container} ${className || ''}`}>
        <div className={styles.empty}>
          <h2>Интервью не найдены</h2>
          <p>Попробуйте изменить параметры поиска или очистить фильтры.</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`${styles.container} ${className || ''}`}>
      <div className={styles.resultsInfo}>
        <span>📊 Показано {allInterviews.length} из {total.toLocaleString()} интервью</span>
        {isLoading && !isInitialLoad && (
          <span className={styles.filterLoadingText}>• Обновление...</span>
        )}
        {hasNextPage && !isLoading && (
          <span style={{ color: 'var(--text-tertiary)', fontSize: '0.8rem' }}>
            • Прокрутите для загрузки ещё
          </span>
        )}
      </div>

      {/* Показываем полупрозрачный оверлей при загрузке фильтров */}
      <div className={`${styles.grid} ${isLoading && !isInitialLoad ? styles.gridLoading : ''}`}>
        {allInterviews.map(interview => (
          <InterviewCard
            key={interview.id}
            interview={interview}
          />
        ))}
        
        {/* Loading more indicator */}
        {isLoadingMore && (
          <InterviewSkeletonList count={3} />
        )}
        
        {/* Intersection Observer sentinel */}
        <div ref={sentinelRef} className={styles.sentinel} />
      </div>

      {/* Show "end of list" indicator when no more pages */}
      {!hasNextPage && allInterviews.length > 0 && (
        <div className={styles.endOfList}>
          <p>✅ Все интервью загружены ({total.toLocaleString()} всего)</p>
        </div>
      )}
    </div>
  );
};