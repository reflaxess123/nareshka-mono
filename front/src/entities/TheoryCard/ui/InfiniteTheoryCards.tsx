import { useCallback, useEffect, useRef } from 'react';
import { useInfiniteTheoryCards } from '../model/queries';
import type { TheoryFilters } from '../model/types';
import styles from './InfiniteTheoryCards.module.scss';
import { TheoryCard } from './TheoryCard';

interface InfiniteTheoryCardsProps {
  filters: TheoryFilters;
}

export const InfiniteTheoryCards = ({ filters }: InfiniteTheoryCardsProps) => {
  const observerRef = useRef<IntersectionObserver | null>(null);
  const loadMoreRef = useRef<HTMLDivElement | null>(null);

  const {
    data,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    isLoading,
    error,
  } = useInfiniteTheoryCards({
    limit: 10,
    category: filters.category,
    subCategory: filters.subCategory,
    sortBy: filters.sortBy,
    sortOrder: filters.sortOrder,
    q: filters.searchQuery,
    onlyUnstudied: filters.onlyUnstudied,
  });

  const handleObserver = useCallback(
    (entries: IntersectionObserverEntry[]) => {
      const [target] = entries;
      if (target.isIntersecting && hasNextPage && !isFetchingNextPage) {
        const lastPage = data?.pages?.[data.pages.length - 1];
        if (lastPage && lastPage.cards?.length === 0) {
          return;
        }
        fetchNextPage();
      }
    },
    [fetchNextPage, hasNextPage, isFetchingNextPage, data?.pages]
  );

  useEffect(() => {
    const element = loadMoreRef.current;
    if (!element) return;

    observerRef.current = new IntersectionObserver(handleObserver, {
      threshold: 0.1,
    });

    observerRef.current.observe(element);

    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
    };
  }, [handleObserver]);

  if (isLoading) {
    return (
      <div className={styles.loadingState}>
        <div className={styles.spinner}></div>
        <span>Загружаем карточки...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.errorState}>
        <span className={styles.errorIcon}>⚠️</span>
        <span>Ошибка загрузки: {error.message}</span>
      </div>
    );
  }

  const allCards = data?.pages.flatMap((page) => page.cards) || [];
  const totalItems = data?.pages[0]?.pagination.totalItems || 0;

  if (allCards.length === 0) {
    return (
      <div className={styles.emptyState}>
        <span className={styles.emptyIcon}>📚</span>
        <h3>Карточки не найдены</h3>
        <p>Попробуйте изменить фильтры или поисковый запрос</p>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.statsBar}>
        <span className={styles.statsText}>
          Показано {allCards.length} из {totalItems} карточек
        </span>
        {filters.onlyUnstudied && (
          <span className={styles.filterBadge}>🔴 Только неизученные</span>
        )}
        {filters.category && (
          <span className={styles.filterBadge}>📂 {filters.category}</span>
        )}
        {filters.subCategory && (
          <span className={styles.filterBadge}>📁 {filters.subCategory}</span>
        )}
      </div>

      <div className={styles.cardsGrid}>
        {allCards
          .filter((card) => {
            const hasCard = card && card.id;
            return hasCard;
          })
          .map((card) => (
            <TheoryCard key={card.id} card={card} />
          ))}
      </div>

      {hasNextPage && (
        <div ref={loadMoreRef} className={styles.loadMore}>
          {isFetchingNextPage ? (
            <div className={styles.loadingMore}>
              <div className={styles.spinner}></div>
              <span>Загружаем ещё...</span>
            </div>
          ) : (
            <div className={styles.loadMoreTrigger}>
              Прокрутите для загрузки ещё
            </div>
          )}
        </div>
      )}

      {!hasNextPage && allCards.length > 0 && (
        <div className={styles.endMessage}>
          <span>🎉 Все карточки загружены!</span>
        </div>
      )}
    </div>
  );
};
