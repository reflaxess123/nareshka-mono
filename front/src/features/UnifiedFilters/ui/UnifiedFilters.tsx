import React, { useState, useEffect, useCallback } from 'react';
import { X } from 'lucide-react';
import { useGetTopCompaniesApiV2InterviewsTopCompaniesGet } from '@/shared/api/generated/api';
import { FilterSection } from './FilterSection';
import { CompanyFilter } from './CompanyFilter';
import { AdditionalFilter } from './AdditionalFilter';
import type { UnifiedFiltersProps } from '../model/types';
import { hasActiveFilters } from '../model/utils';
import styles from './UnifiedFilters.module.scss';

export const UnifiedFilters: React.FC<UnifiedFiltersProps> = ({
  type,
  filters,
  onFiltersChange,
  resultsCount,
  className,
}) => {
  const [expandedSections, setExpandedSections] = useState({
    companies: true,
    additional: true,
  });

  const [isMobile, setIsMobile] = useState(false);

  // Проверка размера экрана
  useEffect(() => {
    const checkScreenSize = () => {
      setIsMobile(window.innerWidth <= 768);
    };

    checkScreenSize();
    window.addEventListener('resize', checkScreenSize);
    return () => window.removeEventListener('resize', checkScreenSize);
  }, []);

  // На мобильных устройствах сворачиваем секции по умолчанию
  useEffect(() => {
    if (isMobile) {
      setExpandedSections((prev) => ({
        ...prev,
        additional: false,
      }));
    } else {
      setExpandedSections({
        companies: true,
        additional: true,
      });
    }
  }, [isMobile]);

  // Загрузка данных компаний для интервью с количеством вопросов
  const { data: companiesData, isLoading: companiesLoading } = 
    useGetTopCompaniesApiV2InterviewsTopCompaniesGet(
      { limit: 100 },
      {
        query: {
          enabled: type === 'interviews',
        },
      }
    );

  const handleCompaniesChange = useCallback((companies: string[]) => {
    onFiltersChange({
      ...filters,
      companies: companies.length > 0 ? companies : undefined,
    });
  }, [filters, onFiltersChange]);

  const handleHasAudioChange = useCallback((hasAudio: boolean) => {
    onFiltersChange({
      ...filters,
      has_audio: hasAudio || undefined,
    });
  }, [filters, onFiltersChange]);

  const handleReset = useCallback(() => {
    onFiltersChange({
      search: undefined,
      companies: undefined,
      has_audio: undefined,
      categories: undefined,
      clusters: undefined,
    });
  }, [onFiltersChange]);

  const toggleSection = (section: keyof typeof expandedSections) => {
    setExpandedSections((prev) => ({
      ...prev,
      [section]: !prev[section],
    }));
  };

  const activeFilters = hasActiveFilters(filters);
  const companiesList = companiesData || [];

  return (
    <div className={`${styles.unifiedFilters} ${className || ''}`}>

      {/* Фильтр по компаниям */}
      {type === 'interviews' && (
        <FilterSection
          title="Компании"
          icon="🏢"
          isExpanded={expandedSections.companies}
          onToggle={() => toggleSection('companies')}
        >
          <CompanyFilter
            companies={companiesList}
            selectedCompanies={filters.companies || []}
            onSelectionChange={handleCompaniesChange}
            isLoading={companiesLoading}
          />
        </FilterSection>
      )}

      {/* Дополнительные фильтры */}
      {type === 'interviews' && (
        <FilterSection
          title="Дополнительно"
          icon="⚙️"
          isExpanded={expandedSections.additional}
          onToggle={() => toggleSection('additional')}
        >
          <AdditionalFilter
            hasAudio={filters.has_audio}
            onHasAudioChange={handleHasAudioChange}
          />
        </FilterSection>
      )}

      {/* Кнопка сброса внизу */}
      {activeFilters && (
        <div className={styles.resetSection}>
          <button
            onClick={handleReset}
            className={styles.resetButton}
          >
            <X size={16} />
            Сбросить фильтры
          </button>
        </div>
      )}
    </div>
  );
};