import React, { useState, useEffect } from 'react';
import { 
  useGetCompaniesListApiV2InterviewsCompaniesListGet
} from '../../../shared/api/generated/api';
import { CompanySelector } from './CompanySelector';
import styles from './InterviewFilters.module.scss';

export interface InterviewFiltersType {
  companies?: string[];
  search?: string;
  has_audio?: boolean;
}

interface InterviewFiltersProps {
  filters: InterviewFiltersType;
  onFiltersChange: (filters: InterviewFiltersType) => void;
  resultsCount?: number;
}


export const InterviewFilters: React.FC<InterviewFiltersProps> = ({
  filters,
  onFiltersChange,
  resultsCount
}) => {
  const [localFilters, setLocalFilters] = useState(filters);
  const [isCollapsed, setIsCollapsed] = useState(false);

  const { data: companiesData } = useGetCompaniesListApiV2InterviewsCompaniesListGet();

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      onFiltersChange(localFilters);
    }, 150);

    return () => clearTimeout(timeoutId);
  }, [localFilters, onFiltersChange]);

  const handleFilterChange = (key: keyof InterviewFiltersType, value: string | string[] | boolean | undefined) => {
    setLocalFilters(prev => ({
      ...prev,
      [key]: value || undefined
    }));
  };

  const handleCompaniesChange = (companies: string[]) => {
    handleFilterChange('companies', companies.length > 0 ? companies : undefined);
  };

  const clearFilters = () => {
    const emptyFilters = {};
    setLocalFilters(emptyFilters);
    onFiltersChange(emptyFilters);
  };

  const hasActiveFilters = Object.values(localFilters).some(value => {
    if (Array.isArray(value)) {
      return value.length > 0;
    }
    return value !== undefined && value !== '';
  });

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h3 className={styles.title}>Фильтры интервью</h3>
        <div className={styles.headerActions}>
          {resultsCount !== undefined && (
            <span className={styles.count}>Найдено: {resultsCount}</span>
          )}
          <button
            className={styles.toggleButton}
            onClick={() => setIsCollapsed(!isCollapsed)}
          >
            {isCollapsed ? '▼' : '▲'}
          </button>
        </div>
      </div>

      {!isCollapsed && (
        <div className={styles.content}>
          <div className={styles.row}>
            <div className={styles.field}>
              <label className={styles.label}>Поиск</label>
              <input
                type="text"
                className={styles.input}
                placeholder="Поиск по содержимому..."
                value={localFilters.search || ''}
                onChange={(e) => handleFilterChange('search', e.target.value)}
              />
            </div>
          </div>

          <div className={styles.row}>
            <div className={styles.field}>
              <label className={styles.label}>Компании</label>
              <CompanySelector
                companies={companiesData?.companies || []}
                selectedCompanies={localFilters.companies || []}
                onSelectionChange={handleCompaniesChange}
              />
            </div>
          </div>

          <div className={styles.row}>
            <div className={styles.field}>
              <label className={styles.checkboxLabel}>
                <input
                  type="checkbox"
                  className={styles.checkbox}
                  checked={localFilters.has_audio || false}
                  onChange={(e) => handleFilterChange('has_audio', e.target.checked ? true : undefined)}
                />
                Только с аудио/видео записью
              </label>
            </div>
          </div>


          {hasActiveFilters && (
            <div className={styles.actions}>
              <button className={styles.clearButton} onClick={clearFilters}>
                Очистить фильтры
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};