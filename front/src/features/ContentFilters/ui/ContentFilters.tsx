import {
  selectContentBlocksFilters,
  setFilters,
  type ContentBlocksFilters,
} from '@/entities/ContentBlock';
import { ButtonVariant } from '@/shared/components/Button/model/types';
import { Button } from '@/shared/components/Button/ui/Button';
import {
  translateMainCategory,
  translateSubCategory,
} from '@/shared/constants/categoryTranslations';
import { useAppDispatch, useAppSelector } from '@/shared/hooks/redux';
import {
  useCompanies,
  useContentCategories,
} from '@/shared/hooks/useContentBlocks';
import { ChevronDown, ChevronUp, X } from 'lucide-react';
import { useCallback, useEffect, useState } from 'react';
import styles from './ContentFilters.module.scss';

interface Category {
  name: string;
  subCategories: string[];
}

interface ContentFiltersProps {
  onFiltersChange?: (filters: ContentBlocksFilters) => void;
  className?: string;
}

export const ContentFilters = ({
  onFiltersChange,
  className,
}: ContentFiltersProps) => {
  const dispatch = useAppDispatch();
  const filters = useAppSelector(selectContentBlocksFilters);
  const { data: categories } = useContentCategories();

  // Состояние для развертывания секций фильтров
  const [expandedSections, setExpandedSections] = useState({
    topics: true,
    companies: true,
    difficulty: true,
    importance: true,
    progress: true,
  });

  // Hook для отслеживания размера экрана
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const checkScreenSize = () => {
      setIsMobile(window.innerWidth <= 768);
    };

    checkScreenSize();
    window.addEventListener('resize', checkScreenSize);

    return () => window.removeEventListener('resize', checkScreenSize);
  }, []);

  // Автоматически сворачиваем некоторые секции на мобильных для экономии места
  useEffect(() => {
    if (isMobile) {
      setExpandedSections((prev) => ({
        ...prev,
        companies: false,
        importance: false,
      }));
    } else {
      setExpandedSections({
        topics: true,
        companies: true,
        difficulty: true,
        importance: true,
        progress: true,
      });
    }
  }, [isMobile]);

  // Получаем компании с учетом текущих фильтров по категориям
  const { data: companies } = useCompanies({
    mainCategories: filters.mainCategories,
    subCategories: filters.subCategories,
  });

  // Обработка множественного выбора категорий
  const handleMainCategoryToggle = useCallback(
    (categoryName: string, checked: boolean) => {
      const currentCategories = filters.mainCategories || [];

      let newCategories: string[];
      if (checked) {
        newCategories = [...currentCategories, categoryName];
      } else {
        newCategories = currentCategories.filter((cat) => cat !== categoryName);
      }

      const newFilters = {
        ...filters,
        mainCategories: newCategories.length > 0 ? newCategories : undefined,
        subCategories: undefined, // Сбрасываем подкатегории при изменении основных
        page: 1, // Сбрасываем страницу
      };

      dispatch(setFilters(newFilters));
      onFiltersChange?.(newFilters);
    },
    [dispatch, filters, onFiltersChange]
  );

  // Обработка множественного выбора подкатегорий
  const handleSubCategoryToggle = useCallback(
    (subCategoryName: string, checked: boolean) => {
      const currentSubCategories = filters.subCategories || [];

      let newSubCategories: string[];
      if (checked) {
        newSubCategories = [...currentSubCategories, subCategoryName];
      } else {
        newSubCategories = currentSubCategories.filter(
          (cat) => cat !== subCategoryName
        );
      }

      const newFilters = {
        ...filters,
        subCategories:
          newSubCategories.length > 0 ? newSubCategories : undefined,
        page: 1, // Сбрасываем страницу
      };

      dispatch(setFilters(newFilters));
      onFiltersChange?.(newFilters);
    },
    [dispatch, filters, onFiltersChange]
  );

  // Обработка множественного выбора компаний
  const handleCompanyToggle = useCallback(
    (companyName: string, checked: boolean) => {
      const currentCompanies = filters.companies || [];

      let newCompanies: string[];
      if (checked) {
        newCompanies = [...currentCompanies, companyName];
      } else {
        newCompanies = currentCompanies.filter(
          (company) => company !== companyName
        );
      }

      const newFilters = {
        ...filters,
        companies: newCompanies.length > 0 ? newCompanies : undefined,
        page: 1,
      };

      dispatch(setFilters(newFilters));
      onFiltersChange?.(newFilters);
    },
    [dispatch, filters, onFiltersChange]
  );

  // Обработка фильтра сложности
  const handleDifficultyToggle = useCallback(
    (difficulty: 'easy' | 'medium' | 'hard', checked: boolean) => {
      const currentDifficulties = filters.difficulties || [];

      let newDifficulties: ('easy' | 'medium' | 'hard')[];
      if (checked) {
        newDifficulties = [...currentDifficulties, difficulty];
      } else {
        newDifficulties = currentDifficulties.filter((d) => d !== difficulty);
      }

      const newFilters = {
        ...filters,
        difficulties: newDifficulties.length > 0 ? newDifficulties : undefined,
        page: 1,
      };

      dispatch(setFilters(newFilters));
      onFiltersChange?.(newFilters);
    },
    [dispatch, filters, onFiltersChange]
  );

  // Обработка фильтра важности
  const handleImportanceToggle = useCallback(
    (importance: 'low' | 'medium' | 'high', checked: boolean) => {
      const currentImportance = filters.importance || [];

      let newImportance: ('low' | 'medium' | 'high')[];
      if (checked) {
        newImportance = [...currentImportance, importance];
      } else {
        newImportance = currentImportance.filter((i) => i !== importance);
      }

      const newFilters = {
        ...filters,
        importance: newImportance.length > 0 ? newImportance : undefined,
        page: 1,
      };

      dispatch(setFilters(newFilters));
      onFiltersChange?.(newFilters);
    },
    [dispatch, filters, onFiltersChange]
  );

  // Обработка фильтра прогресса
  const handleProgressToggle = useCallback(
    (progress: 'completed' | 'not_completed', checked: boolean) => {
      const currentProgress = filters.progress || [];

      let newProgress: ('completed' | 'not_completed')[];
      if (checked) {
        newProgress = [...currentProgress, progress];
      } else {
        newProgress = currentProgress.filter((p) => p !== progress);
      }

      const newFilters = {
        ...filters,
        progress: newProgress.length > 0 ? newProgress : undefined,
        page: 1,
      };

      dispatch(setFilters(newFilters));
      onFiltersChange?.(newFilters);
    },
    [dispatch, filters, onFiltersChange]
  );

  const handleReset = useCallback(() => {
    const resetFilters: ContentBlocksFilters = {
      page: 1,
      limit: 20,
      sortBy: 'orderInFile' as const,
      sortOrder: 'asc' as const,
      q: undefined,
      mainCategories: undefined,
      subCategories: undefined,
      onlyUnsolved: undefined,
      companies: undefined,
      difficulties: undefined,
      importance: undefined,
      progress: undefined,
    };
    dispatch(setFilters(resetFilters));
    onFiltersChange?.(resetFilters);
  }, [dispatch, onFiltersChange]);

  const hasActiveFilters = () => {
    return !!(
      filters.q ||
      filters.onlyUnsolved ||
      filters.mainCategories?.length ||
      filters.subCategories?.length ||
      filters.companies?.length ||
      filters.difficulties?.length ||
      filters.importance?.length ||
      filters.progress?.length
    );
  };

  const toggleSection = (section: keyof typeof expandedSections) => {
    setExpandedSections((prev) => ({
      ...prev,
      [section]: !prev[section],
    }));
  };

  // Получаем все доступные подкатегории на основе выбранных основных категорий
  const getAvailableSubCategories = () => {
    if (!filters.mainCategories?.length || !categories) return [];

    const allSubCategories = new Set<string>();
    filters.mainCategories.forEach((mainCategory) => {
      const category = categories.find(
        (cat: Category) => cat.name === mainCategory
      );
      if (category) {
        category.subCategories.forEach((sub: string) =>
          allSubCategories.add(sub)
        );
      }
    });

    return Array.from(allSubCategories);
  };

  return (
    <div className={`${styles.contentFilters} ${className || ''}`}>
      {/* Reset button */}
      {hasActiveFilters() && (
        <div className={styles.resetSection}>
          <Button
            onClick={handleReset}
            variant={ButtonVariant.SECONDARY}
            className={styles.resetButton}
          >
            <X size={16} />
            Сбросить фильтры
          </Button>
        </div>
      )}

      {/* Topics Filter */}
      <div className={styles.filterSection}>
        <button
          className={styles.sectionHeader}
          onClick={() => toggleSection('topics')}
        >
          <span>Темы</span>
          {expandedSections.topics ? (
            <ChevronUp size={16} />
          ) : (
            <ChevronDown size={16} />
          )}
        </button>

        {expandedSections.topics && (
          <div className={styles.sectionContent}>
            {/* Main Categories */}
            <div className={styles.filterGroup}>
              <label className={styles.filterLabel}>Основные категории</label>
              <div className={styles.checkboxGroup}>
                {categories?.map((category: Category) => {
                  const translatedName = translateMainCategory(category.name);
                  const isChecked =
                    filters.mainCategories?.includes(category.name) || false;

                  return (
                    <label key={category.name} className={styles.checkboxLabel}>
                      <input
                        type="checkbox"
                        checked={isChecked}
                        onChange={(e) =>
                          handleMainCategoryToggle(
                            category.name,
                            e.target.checked
                          )
                        }
                      />
                      <span>{translatedName}</span>
                    </label>
                  );
                })}
              </div>
            </div>

            {/* Sub Categories */}
            {filters.mainCategories?.length &&
              filters.mainCategories.length > 0 && (
                <div className={styles.filterGroup}>
                  <label className={styles.filterLabel}>Подкатегории</label>
                  <div className={styles.checkboxGroup}>
                    {getAvailableSubCategories().map((subCategory: string) => {
                      const translatedName = translateSubCategory(subCategory);
                      const isChecked =
                        filters.subCategories?.includes(subCategory) || false;

                      return (
                        <label
                          key={subCategory}
                          className={styles.checkboxLabel}
                        >
                          <input
                            type="checkbox"
                            checked={isChecked}
                            onChange={(e) =>
                              handleSubCategoryToggle(
                                subCategory,
                                e.target.checked
                              )
                            }
                          />
                          <span>{translatedName}</span>
                        </label>
                      );
                    })}
                  </div>
                </div>
              )}
          </div>
        )}
      </div>

      {/* Company Filter */}
      <div className={styles.filterSection}>
        <button
          className={styles.sectionHeader}
          onClick={() => toggleSection('companies')}
        >
          <span>Компании</span>
          {expandedSections.companies ? (
            <ChevronUp size={16} />
          ) : (
            <ChevronDown size={16} />
          )}
        </button>

        {expandedSections.companies && (
          <div className={styles.sectionContent}>
            <div className={styles.checkboxGroup}>
              {companies?.companies?.map((company: string) => {
                const isChecked = filters.companies?.includes(company) || false;

                return (
                  <label key={company} className={styles.checkboxLabel}>
                    <input
                      type="checkbox"
                      checked={isChecked}
                      onChange={(e) =>
                        handleCompanyToggle(company, e.target.checked)
                      }
                    />
                    <span>{company}</span>
                  </label>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* Difficulty Filter */}
      <div className={styles.filterSection}>
        <button
          className={styles.sectionHeader}
          onClick={() => toggleSection('difficulty')}
        >
          <span>Сложность</span>
          {expandedSections.difficulty ? (
            <ChevronUp size={16} />
          ) : (
            <ChevronDown size={16} />
          )}
        </button>

        {expandedSections.difficulty && (
          <div className={styles.sectionContent}>
            <div className={styles.checkboxGroupHorizontal}>
              <label className={styles.checkboxLabel}>
                <input
                  type="checkbox"
                  checked={filters.difficulties?.includes('easy') || false}
                  onChange={(e) =>
                    handleDifficultyToggle('easy', e.target.checked)
                  }
                />
                <span>Легкая</span>
              </label>
              <label className={styles.checkboxLabel}>
                <input
                  type="checkbox"
                  checked={filters.difficulties?.includes('medium') || false}
                  onChange={(e) =>
                    handleDifficultyToggle('medium', e.target.checked)
                  }
                />
                <span>Средняя</span>
              </label>
              <label className={styles.checkboxLabel}>
                <input
                  type="checkbox"
                  checked={filters.difficulties?.includes('hard') || false}
                  onChange={(e) =>
                    handleDifficultyToggle('hard', e.target.checked)
                  }
                />
                <span>Сложная</span>
              </label>
            </div>
          </div>
        )}
      </div>

      {/* Importance Filter */}
      <div className={styles.filterSection}>
        <button
          className={styles.sectionHeader}
          onClick={() => toggleSection('importance')}
        >
          <span>Важность</span>
          {expandedSections.importance ? (
            <ChevronUp size={16} />
          ) : (
            <ChevronDown size={16} />
          )}
        </button>

        {expandedSections.importance && (
          <div className={styles.sectionContent}>
            <div className={styles.checkboxGroupHorizontal}>
              <label className={styles.checkboxLabel}>
                <input
                  type="checkbox"
                  checked={filters.importance?.includes('high') || false}
                  onChange={(e) =>
                    handleImportanceToggle('high', e.target.checked)
                  }
                />
                <span>Высокая</span>
              </label>
              <label className={styles.checkboxLabel}>
                <input
                  type="checkbox"
                  checked={filters.importance?.includes('medium') || false}
                  onChange={(e) =>
                    handleImportanceToggle('medium', e.target.checked)
                  }
                />
                <span>Средняя</span>
              </label>
              <label className={styles.checkboxLabel}>
                <input
                  type="checkbox"
                  checked={filters.importance?.includes('low') || false}
                  onChange={(e) =>
                    handleImportanceToggle('low', e.target.checked)
                  }
                />
                <span>Низкая</span>
              </label>
            </div>
          </div>
        )}
      </div>

      {/* Progress Filter */}
      <div className={styles.filterSection}>
        <button
          className={styles.sectionHeader}
          onClick={() => toggleSection('progress')}
        >
          <span>Прогресс</span>
          {expandedSections.progress ? (
            <ChevronUp size={16} />
          ) : (
            <ChevronDown size={16} />
          )}
        </button>

        {expandedSections.progress && (
          <div className={styles.sectionContent}>
            <div className={styles.checkboxGroupHorizontal}>
              <label className={styles.checkboxLabel}>
                <input
                  type="checkbox"
                  checked={filters.progress?.includes('completed') || false}
                  onChange={(e) =>
                    handleProgressToggle('completed', e.target.checked)
                  }
                />
                <span>Решенные</span>
              </label>
              <label className={styles.checkboxLabel}>
                <input
                  type="checkbox"
                  checked={filters.progress?.includes('not_completed') || false}
                  onChange={(e) =>
                    handleProgressToggle('not_completed', e.target.checked)
                  }
                />
                <span>Нерешенные</span>
              </label>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
