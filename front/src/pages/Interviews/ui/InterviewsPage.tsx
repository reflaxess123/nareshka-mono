import React, { useState, useCallback, useEffect } from 'react';
import { Search, X } from 'lucide-react';
import { PageWrapper } from '@/shared/components/PageWrapper/ui/PageWrapper';
import { Text, TextAlign, TextSize, TextWeight } from '@/shared/components/Text';
import { InterviewsList } from '../../../widgets/InterviewsList';
import { UnifiedFilters, type UnifiedFilterState } from '../../../features/UnifiedFilters';
import { List } from 'lucide-react';
import styles from './InterviewsPage.module.scss';

export const InterviewsPage: React.FC = () => {
  const [filters, setFilters] = useState<UnifiedFilterState>({
    search: undefined,
    companies: undefined,
    has_audio: undefined,
  });

  // Keyboard navigation для поиска
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.ctrlKey && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.querySelector('#interviews-search') as HTMLInputElement;
        searchInput?.focus();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);

  const handleFiltersChange = useCallback((newFilters: UnifiedFilterState) => {
    setFilters(newFilters);
  }, []);

  const handleSearchChange = useCallback((value: string) => {
    setFilters(prev => ({
      ...prev,
      search: value || undefined,
    }));
  }, []);


  return (
    <PageWrapper>
      <div className={styles.page}>
        <header className={styles.header}>
          <div className={styles.headerContent}>
            <div className={styles.iconWrapper}>
              <List size={32} className={styles.pageIcon} />
            </div>
            <div className={styles.headerText}>
              <Text
                text="Интервью"
                size={TextSize.XXL}
                weight={TextWeight.BOLD}
                align={TextAlign.LEFT}
                className={styles.title}
              />
              <Text
                text="База интервью для изучения реального опыта собеседований"
                size={TextSize.MD}
                align={TextAlign.LEFT}
                className={styles.description}
              />
            </div>
          </div>
        </header>

        {/* Search Bar */}
        <div className={styles.searchSection}>
          <div className={styles.searchInputWrapper}>
            <Search size={20} className={styles.searchIcon} />
            <input
              id="interviews-search"
              type="text"
              placeholder="Поиск интервью... (Ctrl+K)"
              value={filters.search || ''}
              onChange={(e) => handleSearchChange(e.target.value)}
              className={styles.searchInput}
            />
            {filters.search && (
              <button
                onClick={() => handleSearchChange('')}
                className={styles.clearSearchButton}
              >
                <X size={16} />
              </button>
            )}
          </div>
        </div>


        {/* Main Content - Two Columns */}
        <div className={styles.mainContent}>
          <div className={styles.interviewsSection}>
            <InterviewsList
              filters={filters}
              onFiltersChange={handleFiltersChange}
              className={styles.interviewsList}
            />
          </div>

          {/* Filters Sidebar */}
          <aside className={styles.filtersSection}>
            <div className={styles.filtersContainer}>
              <UnifiedFilters
                type="interviews"
                filters={filters}
                onFiltersChange={handleFiltersChange}
                className={styles.filters}
              />
            </div>
          </aside>
        </div>
      </div>
    </PageWrapper>
  );
};