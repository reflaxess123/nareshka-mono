import React, { useState, useCallback } from 'react';
import { InterviewCard } from '../../../entities/Interview';
import { InterviewFilters, type InterviewFiltersType } from '../../../features/InterviewFilters';
import { useGetInterviewsApiV2InterviewsGet } from '../../../shared/api/generated/api';
import styles from './InterviewsList.module.scss';

export const InterviewsList: React.FC = () => {
  const [filters, setFilters] = useState<InterviewFiltersType>({});
  const [page, setPage] = useState(1);
  const limit = 20;

  const { data, isLoading, error } = useGetInterviewsApiV2InterviewsGet(
    {
      page,
      limit,
      company: filters.company,
      search: filters.search,
    }
  );

  const handleFiltersChange = useCallback((newFilters: InterviewFiltersType) => {
    setFilters(prevFilters => {
      const filtersChanged = JSON.stringify(prevFilters) !== JSON.stringify(newFilters);
      if (filtersChanged) {
        setPage(1);
      }
      return newFilters;
    });
  }, []);

  const handlePageChange = useCallback((newPage: number) => {
    setPage(newPage);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, []);

  const renderPagination = () => {
    if (!data || data.total <= limit) return null;

    const totalPages = Math.ceil(data.total / limit);
    const pages = [];

    // Show max 7 pages around current page
    const startPage = Math.max(1, page - 3);
    const endPage = Math.min(totalPages, page + 3);

    if (startPage > 1) {
      pages.push(1);
      if (startPage > 2) pages.push('...');
    }

    for (let i = startPage; i <= endPage; i++) {
      pages.push(i);
    }

    if (endPage < totalPages) {
      if (endPage < totalPages - 1) pages.push('...');
      pages.push(totalPages);
    }

    return (
      <div className={styles.pagination}>
        <button
          className={styles.pageButton}
          onClick={() => handlePageChange(page - 1)}
          disabled={!data.has_prev}
        >
          ←
        </button>

        {pages.map((pageNum, index) => {
          if (pageNum === '...') {
            return (
              <span key={`ellipsis-${index}`} className={styles.ellipsis}>
                ...
              </span>
            );
          }

          const pageNumber = pageNum as number;
          return (
            <button
              key={pageNumber}
              className={`${styles.pageButton} ${
                pageNumber === page ? styles.active : ''
              }`}
              onClick={() => handlePageChange(pageNumber)}
            >
              {pageNumber}
            </button>
          );
        })}

        <button
          className={styles.pageButton}
          onClick={() => handlePageChange(page + 1)}
          disabled={!data.has_next}
        >
          →
        </button>
      </div>
    );
  };

  if (error) {
    return (
      <div className={styles.container}>
        <div className={styles.error}>
          <h2>Ошибка загрузки данных</h2>
          <p>Не удалось загрузить список интервью. Попробуйте обновить страницу.</p>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className={styles.container}>
        <InterviewFilters
          filters={filters}
          onFiltersChange={handleFiltersChange}
        />
        <div className={styles.loading}>
          <div className={styles.spinner}></div>
          <p>Загрузка интервью...</p>
        </div>
      </div>
    );
  }

  if (!data || data.interviews.length === 0) {
    return (
      <div className={styles.container}>
        <InterviewFilters
          filters={filters}
          onFiltersChange={handleFiltersChange}
          resultsCount={0}
        />
        <div className={styles.empty}>
          <h2>Интервью не найдены</h2>
          <p>Попробуйте изменить параметры поиска или очистить фильтры.</p>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <InterviewFilters
        filters={filters}
        onFiltersChange={handleFiltersChange}
        resultsCount={data.total}
      />

      <div className={styles.resultsInfo}>
        Показано {data.interviews.length} из {data.total} интервью
      </div>

      <div className={styles.grid}>
        {data.interviews.map(interview => (
          <InterviewCard
            key={interview.id}
            interview={interview}
          />
        ))}
      </div>

      {renderPagination()}
    </div>
  );
};