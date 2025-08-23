import React, { useState, useCallback, useEffect } from 'react';
import { 
  getInterviewsApiV2InterviewsGet
} from '@/shared/api/generated/api';
import { ContentAdapter } from '@/shared/lib/contentAdapters';
import { useInfiniteScroll } from '@/shared/hooks/useInfiniteScroll';
import { useLearningStore } from '@/pages/Learning/model/learningStore';
import { UniversalContentCard } from './UniversalContentCard';
import { ContentSkeletonList } from './ContentSkeletonList';
import type { ContentType, UniversalContentItem, LearningFilters } from '@/shared/types/learning';
import styles from './UniversalContentList.module.scss';

interface UniversalContentListProps {
  contentType: ContentType;
  filters: LearningFilters;
  viewMode: 'cards' | 'list' | 'compact';
  className?: string;
}

export const UniversalContentList: React.FC<UniversalContentListProps> = ({
  contentType,
  filters,
  viewMode,
  className
}) => {
  const {
    items,
    isLoading,
    error,
    page,
    limit,
    total,
    hasNextPage,
    sortBy,
    sortOrder,
    setItems,
    appendItems,
    setLoading,
    setError,
    setPaginationData,
    nextPage
  } = useLearningStore();

  const [isInitialLoad, setIsInitialLoad] = useState(true);

  // Функция загрузки данных в зависимости от типа контента
  const fetchContent = useCallback(async (pageNum: number) => {
    setLoading(true);
    setError(null);

    try {
      let response: any;
      let adaptedItems: UniversalContentItem[] = [];
      let totalCount = 0;
      let hasMore = false;

      switch (contentType) {
        case 'interviews':
          response = await getInterviewsApiV2InterviewsGet({
            page: pageNum,
            limit,
            companies: filters.companies,
            search: filters.search,
            has_audio: filters.hasAudio
          });
          
          if (response && response.interviews) {
            adaptedItems = ContentAdapter.adaptArray(response.interviews, 'interviews');
            totalCount = response.total;
            hasMore = response.has_next;
          }
          break;

        case 'questions':
          // Используем fetch напрямую для questions API
          const queryParams = new URLSearchParams();
          queryParams.append('q', filters.search || '*');
          queryParams.append('limit', limit.toString());
          queryParams.append('offset', ((pageNum - 1) * limit).toString());
          
          filters.categories?.forEach(cat => queryParams.append('category_ids', cat));
          filters.clusters?.forEach(cluster => queryParams.append('cluster_ids', cluster.toString()));
          filters.companies?.forEach(comp => queryParams.append('companies', comp));
          
          const questionsResponse = await fetch(
            `/api/v2/interview-categories/search/questions?${queryParams}`
          );
          const questionsData = await questionsResponse.json();
          
          if (questionsData.questions) {
            adaptedItems = ContentAdapter.adaptArray(questionsData.questions, 'questions');
            totalCount = questionsData.total || 0;
            hasMore = questionsData.has_next || false;
          }
          break;

        case 'practice':
          // Используем правильный API endpoint как в /tasks
          const contentParams = new URLSearchParams({
            page: pageNum.toString(),
            limit: limit.toString(),
            sortBy: sortBy || 'orderInFile',
            sortOrder: sortOrder || 'asc'
          });
          
          if (filters.search) contentParams.append('q', filters.search);
          
          // Исправляем формат фильтров как в useInfiniteContentBlocks
          if (filters.categories?.length) {
            filters.categories.forEach(cat => contentParams.append('mainCategories', cat));
          }
          if (filters.subCategories?.length) {
            filters.subCategories.forEach(subCat => contentParams.append('subCategories', subCat));
          }
          if (filters.companies?.length) {
            filters.companies.forEach(comp => contentParams.append('companiesList', comp));
          }
          
          const practiceResponse = await fetch(
            `/api/v2/tasks/items?${contentParams}`,
            { credentials: 'include' }
          );
          const practiceData = await practiceResponse.json();
          
          if (practiceData.data) {
            adaptedItems = ContentAdapter.adaptArray(practiceData.data, 'practice');
            totalCount = practiceData.pagination?.total || 0;
            hasMore = practiceData.pagination?.page < practiceData.pagination?.totalPages;
          }
          break;

        case 'theory':
          // Используем fetch для theory cards
          const theoryParams = new URLSearchParams({
            page: pageNum.toString(),
            limit: limit.toString(),
            sortBy: sortBy || 'orderIndex',
            sortOrder: sortOrder || 'asc'
          });
          
          if (filters.search) theoryParams.append('q', filters.search);
          if (filters.categories?.[0]) theoryParams.append('category', filters.categories[0]);
          if (filters.subCategories?.[0]) theoryParams.append('subCategory', filters.subCategories[0]);
          if (filters.onlyUnstudied) theoryParams.append('onlyUnstudied', 'true');
          
          const theoryResponse = await fetch(
            `/api/v2/theory/cards?${theoryParams}`
          );
          const theoryData = await theoryResponse.json();
          
          if (theoryData.cards) {
            adaptedItems = ContentAdapter.adaptArray(theoryData.cards, 'theory');
            totalCount = theoryData.pagination?.total || 0;
            hasMore = theoryData.pagination?.hasNext || false;
          }
          break;
      }

      // Обновляем store
      if (pageNum === 1) {
        setItems(adaptedItems);
      } else {
        appendItems(adaptedItems);
      }

      setPaginationData({ total: totalCount, hasNextPage: hasMore });

      if (isInitialLoad) {
        setIsInitialLoad(false);
      }

    } catch (err) {
      console.error('Error loading content:', err);
      setError(err instanceof Error ? err.message : 'Не удалось загрузить данные');
    } finally {
      setLoading(false);
    }
  }, [
    contentType, 
    filters, 
    limit, 
    sortBy, 
    sortOrder,
    setItems,
    appendItems,
    setLoading,
    setError,
    setPaginationData,
    isInitialLoad
  ]);

  // Загрузка при изменении фильтров или типа контента
  useEffect(() => {
    fetchContent(1);
  }, [contentType, filters, sortBy, sortOrder]);

  // Обработчик подгрузки следующей страницы
  const handleLoadMore = useCallback(async () => {
    if (!isLoading && hasNextPage) {
      nextPage();
      await fetchContent(page + 1);
    }
  }, [isLoading, hasNextPage, page, nextPage, fetchContent]);

  // Инфинитный скролл
  const { sentinelRef } = useInfiniteScroll({
    hasNextPage,
    isLoading,
    onLoadMore: handleLoadMore,
    threshold: 200
  });

  // Подсчет количества вопросов по интервью для questions
  const interviewCounts = React.useMemo(() => {
    if (contentType !== 'questions') return {};
    const counts: Record<string, number> = {};
    items.forEach(item => {
      const interviewId = item.metadata?.interviewId;
      if (interviewId) {
        counts[interviewId] = (counts[interviewId] || 0) + 1;
      }
    });
    return counts;
  }, [contentType, items]);

  // Рендер в зависимости от состояния
  if (error) {
    return (
      <div className={`${styles.container} ${className || ''}`}>
        <div className={styles.error}>
          <h2>Ошибка загрузки</h2>
          <p>{error}</p>
          <button 
            className={styles.retryButton}
            onClick={() => fetchContent(1)}
          >
            Попробовать снова
          </button>
        </div>
      </div>
    );
  }

  if (isInitialLoad && isLoading) {
    return (
      <div className={`${styles.container} ${className || ''}`}>
        <div className={`${styles.grid} ${styles[viewMode]}`}>
          <ContentSkeletonList count={8} viewMode={viewMode} />
        </div>
      </div>
    );
  }

  if (items.length === 0 && !isLoading && !isInitialLoad) {
    // Специализированные сообщения для каждого типа контента
    const emptyMessages = {
      interviews: {
        icon: '🎤',
        title: 'Интервью не найдены',
        description: 'Попробуйте изменить компании в фильтрах или очистить поиск'
      },
      questions: {
        icon: '❓',
        title: 'Вопросы не найдены',
        description: 'Попробуйте другие ключевые слова или очистите фильтры'
      },
      practice: {
        icon: '💻',
        title: 'Задачи для практики не найдены',
        description: 'Попробуйте изменить категорию или сбросить фильтры'
      },
      theory: {
        icon: '📚',
        title: 'Теоретические материалы не найдены',
        description: 'Попробуйте другие категории или очистите фильтры'
      }
    };
    
    const message = emptyMessages[contentType];
    
    return (
      <div className={`${styles.container} ${className || ''}`}>
        <div className={styles.empty}>
          <div className={styles.emptyIcon}>{message.icon}</div>
          <h2>{message.title}</h2>
          <p>{message.description}</p>
          <button 
            className={styles.clearFiltersButton}
            onClick={() => {
              // TODO: реализовать очистку фильтров
              console.log('Clear filters');
            }}
          >
            Очистить фильтры
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={`${styles.container} ${className || ''}`}>
      {/* Results info */}
      <div className={styles.resultsInfo}>
        <span>📊 Показано {items.length} из {total.toLocaleString()}</span>
        {isLoading && !isInitialLoad && (
          <span className={styles.loadingText}>• Обновление...</span>
        )}
        {hasNextPage && !isLoading && (
          <span className={styles.moreText}>• Прокрутите для загрузки ещё</span>
        )}
      </div>

      {/* Content grid */}
      <div className={`${styles.grid} ${styles[viewMode]} ${isLoading && !isInitialLoad ? styles.gridLoading : ''}`}>
        {items.map(item => (
          <UniversalContentCard
            key={`${item.type}-${item.id}`}
            item={item}
            viewMode={viewMode}
            interviewCounts={interviewCounts}
          />
        ))}

        {/* Loading more indicator */}
        {isLoading && !isInitialLoad && (
          <ContentSkeletonList count={3} viewMode={viewMode} />
        )}

        {/* Intersection Observer sentinel */}
        <div ref={sentinelRef} className={styles.sentinel} />
      </div>

      {/* End of list indicator */}
      {!hasNextPage && items.length > 0 && (
        <div className={styles.endOfList}>
          <p>✅ Весь контент загружен ({total.toLocaleString()} всего)</p>
        </div>
      )}
    </div>
  );
};