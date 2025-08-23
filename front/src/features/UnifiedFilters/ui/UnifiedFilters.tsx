import React, { useState, useEffect, useCallback } from 'react';
import { X } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { useGetTopCompaniesApiV2InterviewsTopCompaniesGet } from '@/shared/api/generated/api';
import { FilterSection } from './FilterSection';
import { CompanyFilter } from './CompanyFilter';
import { AdditionalFilter } from './AdditionalFilter';
import { ContentFilters } from '@/features/ContentFilters';
import { useContentCategories, useCompanies } from '@/shared/hooks/useContentBlocks';
import { translateMainCategory, translateSubCategory } from '@/shared/constants/categoryTranslations';
import { useRole } from '@/shared/hooks/useRole';
import { Modal } from '@/shared/components/Modal';
import { SubscriptionPrompt } from '@/shared/components/SubscriptionPrompt';
import type { UnifiedFiltersProps } from '../model/types';
import { hasActiveFilters } from '../model/utils';
import styles from './UnifiedFilters.module.scss';

// Интерфейсы для API данных
interface Category {
  id: string;
  name: string;
  questions_count: number;
  percentage: number;
}

interface Cluster {
  id: number;
  name: string;
  category_id: string;
  keywords: string[];
  questions_count: number;
}

interface PracticeCategory {
  name: string;
  subCategories: string[];
  totalCount: number;
  contentBlockCount: number;
  theoryQuizCount: number;
}

export const UnifiedFilters: React.FC<UnifiedFiltersProps> = ({
  type,
  filters,
  onFiltersChange,
  resultsCount,
  className,
}) => {
  const [expandedSections, setExpandedSections] = useState({
    categories: true,
    clusters: true,
    companies: true,
    additional: true,
  });

  const [isMobile, setIsMobile] = useState(false);
  const [showSubscriptionModal, setShowSubscriptionModal] = useState(false);

  // Хуки для practice фильтров
  const { data: practiceCategories } = useContentCategories();
  const { data: practiceCompanies } = useCompanies({
    mainCategories: filters.categories,
    subCategories: filters.subCategories,
  });
  const { canUseFilters } = useRole();

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
        clusters: false,
        additional: false,
      }));
    } else {
      setExpandedSections({
        categories: true,
        clusters: true,
        companies: true,
        additional: true,
      });
    }
  }, [isMobile]);

  // Загрузка данных компаний для интервью и вопросов с количеством вопросов
  const { data: companiesData, isLoading: companiesLoading } = 
    useGetTopCompaniesApiV2InterviewsTopCompaniesGet(
      { limit: 100 },
      {
        query: {
          enabled: type === 'interviews' || type === 'questions',
        },
      }
    );

  // Загрузка категорий для вопросов
  const { data: categories } = useQuery<Category[]>({
    queryKey: ['interview-categories'],
    queryFn: async () => {
      const response = await fetch('/api/v2/interview-categories/');
      if (!response.ok) throw new Error('Failed to fetch categories');
      return response.json();
    },
    enabled: type === 'questions'
  });

  // Загрузка кластеров для вопросов
  const { data: clusters } = useQuery<Cluster[]>({
    queryKey: ['interview-clusters', filters.categories],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (filters.categories?.length) {
        filters.categories.forEach(catId => params.append('category_id', catId));
      }
      params.append('limit', '200');
      
      const response = await fetch(`/api/v2/interview-categories/clusters/all?${params}`);
      if (!response.ok) throw new Error('Failed to fetch clusters');
      return response.json();
    },
    enabled: type === 'questions'
  });

  const handleCompaniesChange = useCallback((companies: string[]) => {
    onFiltersChange({
      ...filters,
      companies: companies.length > 0 ? companies : undefined,
    });
  }, [filters, onFiltersChange]);

  const handleCategoriesChange = useCallback((categories: string[]) => {
    onFiltersChange({
      ...filters,
      categories: categories.length > 0 ? categories : undefined,
      clusters: undefined, // Сброс кластеров при изменении категорий
    });
  }, [filters, onFiltersChange]);

  const handleClustersChange = useCallback((clusters: number[]) => {
    onFiltersChange({
      ...filters,
      clusters: clusters.length > 0 ? clusters : undefined,
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

  // Обработчики для practice фильтров
  const handlePracticeMainCategoryToggle = useCallback((categoryName: string, checked: boolean) => {
    const currentCategories = filters.categories || [];
    let newCategories: string[];
    
    if (checked) {
      newCategories = [...currentCategories, categoryName];
    } else {
      newCategories = currentCategories.filter((cat) => cat !== categoryName);
    }

    onFiltersChange({
      ...filters,
      categories: newCategories.length > 0 ? newCategories : undefined,
      subCategories: undefined, // Сброс подкатегорий при изменении категорий
    });
  }, [filters, onFiltersChange]);

  const handlePracticeSubCategoryToggle = useCallback((subCategoryName: string, checked: boolean) => {
    const currentSubCategories = filters.subCategories || [];
    let newSubCategories: string[];
    
    if (checked) {
      newSubCategories = [...currentSubCategories, subCategoryName];
    } else {
      newSubCategories = currentSubCategories.filter((cat) => cat !== subCategoryName);
    }

    onFiltersChange({
      ...filters,
      subCategories: newSubCategories.length > 0 ? newSubCategories : undefined,
    });
  }, [filters, onFiltersChange]);

  const handlePracticeCompanyToggle = useCallback((companyName: string, checked: boolean) => {
    if (!canUseFilters) {
      setShowSubscriptionModal(true);
      return;
    }

    const currentCompanies = filters.companies || [];
    let newCompanies: string[];
    
    if (checked) {
      newCompanies = [...currentCompanies, companyName];
    } else {
      newCompanies = currentCompanies.filter((company) => company !== companyName);
    }

    onFiltersChange({
      ...filters,
      companies: newCompanies.length > 0 ? newCompanies : undefined,
    });
  }, [filters, onFiltersChange, canUseFilters]);

  const handlePracticeProgressToggle = useCallback((progress: 'completed' | 'not_completed', checked: boolean) => {
    onFiltersChange({
      ...filters,
      onlyCompleted: progress === 'completed' ? (checked || undefined) : filters.onlyCompleted,
    });
  }, [filters, onFiltersChange]);

  const toggleSection = (section: keyof typeof expandedSections) => {
    setExpandedSections((prev) => ({
      ...prev,
      [section]: !prev[section],
    }));
  };

  const getAvailableSubCategories = () => {
    if (!filters.categories?.length || !practiceCategories?.categories) return [];

    const allSubCategories = new Set<string>();
    filters.categories.forEach((mainCategory) => {
      const category = practiceCategories.categories.find(
        (cat: PracticeCategory) => cat.name === mainCategory
      );
      if (category) {
        category.subCategories.forEach((sub: string) =>
          allSubCategories.add(sub)
        );
      }
    });

    return Array.from(allSubCategories);
  };

  const activeFilters = hasActiveFilters(filters);
  const companiesList = companiesData || [];

  return (
    <div className={`${styles.unifiedFilters} ${className || ''}`}>

      {/* Фильтр по категориям - только для вопросов */}
      {type === 'questions' && (
        <FilterSection
          title="Категории"
          icon="📁"
          isExpanded={expandedSections.categories}
          onToggle={() => toggleSection('categories')}
        >
          <div className={styles.checkboxGroup}>
            {categories?.map((category) => (
              <label key={category.id} className={styles.checkboxLabel}>
                <input
                  type="checkbox"
                  checked={filters.categories?.includes(category.id) || false}
                  onChange={(e) => {
                    const newCategories = e.target.checked
                      ? [...(filters.categories || []), category.id]
                      : (filters.categories || []).filter(id => id !== category.id);
                    handleCategoriesChange(newCategories);
                  }}
                  className={styles.checkbox}
                />
                <span className={styles.labelText}>
                  {category.name} ({category.questions_count})
                </span>
              </label>
            ))}
          </div>
        </FilterSection>
      )}

      {/* Фильтр по кластерам - только для вопросов */}
      {type === 'questions' && (
        <FilterSection
          title="Кластеры"
          icon="🏷️"
          isExpanded={expandedSections.clusters}
          onToggle={() => toggleSection('clusters')}
        >
          <div className={styles.checkboxGroup}>
            {clusters?.map((cluster) => (
              <label key={cluster.id} className={styles.checkboxLabel}>
                <input
                  type="checkbox"
                  checked={filters.clusters?.includes(cluster.id) || false}
                  onChange={(e) => {
                    const newClusters = e.target.checked
                      ? [...(filters.clusters || []), cluster.id]
                      : (filters.clusters || []).filter(id => id !== cluster.id);
                    handleClustersChange(newClusters);
                  }}
                  className={styles.checkbox}
                />
                <span className={styles.labelText}>
                  {cluster.name} ({cluster.questions_count})
                </span>
              </label>
            ))}
          </div>
        </FilterSection>
      )}

      {/* Фильтр по компаниям */}
      {(type === 'interviews' || type === 'questions') && (
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

      {/* Фильтры для practice - структурированные секции */}
      {type === 'practice' && (
        <>
          {/* Основные категории */}
          <FilterSection
            title="Темы"
            icon="📁"
            isExpanded={expandedSections.categories}
            onToggle={() => toggleSection('categories')}
          >
            <div className={styles.checkboxGroup}>
              <div className={styles.filterLabel}>Основные категории</div>
              {practiceCategories?.categories?.map((category: PracticeCategory) => {
                const translatedName = translateMainCategory(category.name);
                const isChecked = filters.categories?.includes(category.name) || false;

                return (
                  <label key={category.name} className={styles.checkboxLabel}>
                    <input
                      type="checkbox"
                      checked={isChecked}
                      onChange={(e) => handlePracticeMainCategoryToggle(category.name, e.target.checked)}
                      className={styles.checkbox}
                    />
                    <span className={styles.labelText}>{translatedName}</span>
                  </label>
                );
              })}

              {/* Подкатегории */}
              {filters.categories?.length && filters.categories.length > 0 && (
                <div style={{ marginTop: '1rem' }}>
                  <div className={styles.filterLabel}>Подкатегории</div>
                  {getAvailableSubCategories().map((subCategory: string) => {
                    const translatedName = translateSubCategory(subCategory);
                    const isChecked = filters.subCategories?.includes(subCategory) || false;

                    return (
                      <label key={subCategory} className={styles.checkboxLabel}>
                        <input
                          type="checkbox"
                          checked={isChecked}
                          onChange={(e) => handlePracticeSubCategoryToggle(subCategory, e.target.checked)}
                          className={styles.checkbox}
                        />
                        <span className={styles.labelText}>{translatedName}</span>
                      </label>
                    );
                  })}
                </div>
              )}
            </div>
          </FilterSection>

          {/* Компании */}
          <FilterSection
            title="Компании"
            icon="🏢"
            isExpanded={expandedSections.companies}
            onToggle={() => toggleSection('companies')}
          >
            <div className={styles.checkboxGroup}>
              {practiceCompanies?.companies?.map((company: { name: string; count: number }) => {
                const isChecked = filters.companies?.includes(company.name) || false;

                return (
                  <label key={company.name} className={styles.checkboxLabel}>
                    <input
                      type="checkbox"
                      checked={isChecked}
                      onChange={(e) => handlePracticeCompanyToggle(company.name, e.target.checked)}
                      className={styles.checkbox}
                    />
                    <span className={styles.labelText}>
                      {company.name} ({company.count})
                    </span>
                  </label>
                );
              })}
            </div>
          </FilterSection>

          {/* Прогресс */}
          <FilterSection
            title="Прогресс"
            icon="📊"
            isExpanded={expandedSections.additional}
            onToggle={() => toggleSection('additional')}
          >
            <div className={styles.checkboxGroup}>
              <label className={styles.checkboxLabel}>
                <input
                  type="checkbox"
                  checked={filters.onlyCompleted || false}
                  onChange={(e) => handlePracticeProgressToggle('completed', e.target.checked)}
                  className={styles.checkbox}
                />
                <span className={styles.labelText}>Решенные</span>
              </label>
              <label className={styles.checkboxLabel}>
                <input
                  type="checkbox"
                  checked={filters.onlyCompleted === false}
                  onChange={(e) => handlePracticeProgressToggle('not_completed', e.target.checked)}
                  className={styles.checkbox}
                />
                <span className={styles.labelText}>Нерешенные</span>
              </label>
            </div>
          </FilterSection>
        </>
      )}

      {/* Фильтры для theory */}
      {type === 'theory' && (
        <FilterSection
          title="Статус"
          icon="📊"
          isExpanded={expandedSections.additional}
          onToggle={() => toggleSection('additional')}
        >
          <div className={styles.checkboxGroup}>
            <label className={styles.checkboxLabel}>
              <input
                type="checkbox"
                checked={filters.onlyUnstudied || false}
                onChange={(e) => onFiltersChange({ ...filters, onlyUnstudied: e.target.checked || undefined })}
                className={styles.checkbox}
              />
              <span className={styles.labelText}>Только неизученные</span>
            </label>
          </div>
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

      {/* Модал подписки */}
      <Modal
        isOpen={showSubscriptionModal}
        onClose={() => setShowSubscriptionModal(false)}
        closeOnOverlay={true}
        closeOnEsc={true}
      >
        <SubscriptionPrompt
          feature="Фильтр по компаниям"
          description="Фильтрация задач по компаниям доступна только пользователям с подпиской Нарешка+ или администраторам"
        />
      </Modal>
    </div>
  );
};