import React, { useState, useEffect } from 'react';
import { 
  useGetCompaniesListApiV2InterviewsCompaniesListGet
} from '../../../shared/api/generated/api';
import styles from './InterviewFilters.module.scss';

export interface InterviewFiltersType {
  company?: string;
  search?: string;
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
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [localFilters, onFiltersChange]);

  const handleFilterChange = (key: keyof InterviewFiltersType, value: string | number | undefined) => {
    setLocalFilters(prev => ({
      ...prev,
      [key]: value || undefined
    }));
  };

  const clearFilters = () => {
    const emptyFilters = {};
    setLocalFilters(emptyFilters);
    onFiltersChange(emptyFilters);
  };

  const hasActiveFilters = Object.values(localFilters).some(value => value !== undefined && value !== '');

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
              <label className={styles.label}>Компания</label>
              <select
                className={styles.select}
                value={localFilters.company || ''}
                onChange={(e) => handleFilterChange('company', e.target.value)}
              >
                <option value="">Все компании</option>
                {companiesData?.companies?.map(company => (
                  <option key={company} value={company}>
                    {company}
                  </option>
                ))}
              </select>
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