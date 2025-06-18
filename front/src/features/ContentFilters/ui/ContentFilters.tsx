import {
  selectContentBlocksFilters,
  setFilters,
  type ContentBlocksFilters,
} from '@/entities/ContentBlock';
import { ButtonVariant } from '@/shared/components/Button/model/types';
import { Button } from '@/shared/components/Button/ui/Button';
import { Input } from '@/shared/components/Input';
import {
  findOriginalCategory,
  translateMainCategory,
  translateSubCategory,
} from '@/shared/constants/categoryTranslations';
import { useAppDispatch, useAppSelector } from '@/shared/hooks/redux';
import {
  useCompanies,
  useContentCategories,
} from '@/shared/hooks/useContentBlocks';
import { Search, X } from 'lucide-react';
import { useCallback } from 'react';
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

  // Получаем компании с учетом текущих фильтров по категориям
  const { data: companies } = useCompanies({
    mainCategory: filters.mainCategory,
    subCategory: filters.subCategory,
  });

  const handleFilterChange = useCallback(
    (
      key: keyof ContentBlocksFilters,
      value: string | number | boolean | undefined
    ) => {
      const newFilters = { ...filters, [key]: value };
      dispatch(setFilters(newFilters));
      onFiltersChange?.(newFilters);
    },
    [dispatch, filters, onFiltersChange]
  );

  const handleMainCategoryChange = useCallback(
    (mainCategory: string) => {
      // Если выбрана переведенная категория, конвертируем обратно в оригинальное название для API
      const originalMainCategory = mainCategory
        ? findOriginalCategory(mainCategory, true)
        : undefined;

      const newFilters = {
        ...filters,
        mainCategory: originalMainCategory,
        subCategory: undefined, // Сбрасываем подкатегорию при изменении основной категории
        companies: undefined, // Сбрасываем компанию при изменении основной категории
      };
      dispatch(setFilters(newFilters));
      onFiltersChange?.(newFilters);
    },
    [dispatch, filters, onFiltersChange]
  );

  const handleSubCategoryChange = useCallback(
    (subCategory: string) => {
      // Если выбрана переведенная подкатегория, конвертируем обратно в оригинальное название для API
      const originalSubCategory = subCategory
        ? findOriginalCategory(subCategory, false)
        : undefined;

      const newFilters = {
        ...filters,
        subCategory: originalSubCategory,
        companies: undefined, // Сбрасываем компанию при изменении подкатегории
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
      mainCategory: undefined,
      subCategory: undefined,
      onlyUnsolved: undefined,
      companies: undefined,
    };
    dispatch(setFilters(resetFilters));
    onFiltersChange?.(resetFilters);
  }, [dispatch, onFiltersChange]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Поиск уже применяется автоматически при изменении
  };

  const getSubCategories = (mainCategory: string) => {
    // Находим оригинальное название категории для поиска
    const originalCategory = findOriginalCategory(mainCategory, true);
    return (
      categories?.find((cat: Category) => cat.name === originalCategory)
        ?.subCategories || []
    );
  };

  const hasActiveFilters = () => {
    return !!(
      filters.q ||
      filters.onlyUnsolved ||
      filters.mainCategory ||
      filters.subCategory ||
      filters.companies
    );
  };

  // Получаем переведенное название выбранной категории для отображения
  const displayMainCategory = filters.mainCategory
    ? translateMainCategory(filters.mainCategory)
    : '';

  const displaySubCategory = filters.subCategory
    ? translateSubCategory(filters.subCategory)
    : '';

  return (
    <div className={`${styles.contentFilters} ${className || ''}`}>
      {/* Поиск */}
      <form onSubmit={handleSearchSubmit} className={styles.searchForm}>
        <div className={styles.searchContainer}>
          <Search size={20} className={styles.searchIcon} />
          <Input
            type="text"
            placeholder="Поиск по контенту..."
            value={filters.q || ''}
            onChange={(e) => handleFilterChange('q', e.target.value)}
            className={styles.searchInput}
          />
          {filters.q && (
            <button
              type="button"
              onClick={() => handleFilterChange('q', '')}
              className={styles.clearSearch}
              aria-label="Очистить поиск"
            >
              <X size={16} />
            </button>
          )}
        </div>
      </form>

      {/* Фильтры */}
      <div className={styles.filtersRow}>
        {/* Основная категория */}
        <div className={styles.filterGroup}>
          <select
            value={displayMainCategory}
            onChange={(e) => handleMainCategoryChange(e.target.value || '')}
            className={styles.filterSelect}
          >
            <option value="">Все категории</option>
            {categories?.map((category: Category) => (
              <option
                key={category.name}
                value={translateMainCategory(category.name)}
              >
                {translateMainCategory(category.name)}
              </option>
            ))}
          </select>
        </div>

        {/* Подкатегория */}
        {displayMainCategory && (
          <div className={styles.filterGroup}>
            <select
              value={displaySubCategory}
              onChange={(e) => handleSubCategoryChange(e.target.value || '')}
              className={styles.filterSelect}
            >
              <option value="">Все подкатегории</option>
              {getSubCategories(displayMainCategory).map(
                (subCategory: string) => (
                  <option
                    key={subCategory}
                    value={translateSubCategory(subCategory)}
                  >
                    {translateSubCategory(subCategory)}
                  </option>
                )
              )}
            </select>
          </div>
        )}

        {/* Фильтр по компаниям */}
        <div className={styles.filterGroup}>
          <select
            value={filters.companies || ''}
            onChange={(e) =>
              handleFilterChange('companies', e.target.value || undefined)
            }
            className={styles.filterSelect}
          >
            <option value="">Все компании</option>
            {companies?.companies?.map((company: string) => (
              <option key={company} value={company}>
                {company}
              </option>
            ))}
          </select>
        </div>

        {/* Фильтр "Только нерешенные" */}
        <label className={styles.checkboxFilter}>
          <input
            type="checkbox"
            checked={filters.onlyUnsolved || false}
            onChange={(e) =>
              handleFilterChange('onlyUnsolved', e.target.checked)
            }
            className={styles.checkbox}
          />
          <span className={styles.checkboxLabel}>Только нерешенные</span>
        </label>

        {/* Кнопка сброса фильтров */}
        {hasActiveFilters() && (
          <Button
            type="button"
            variant={ButtonVariant.GHOST}
            onClick={handleReset}
            className={styles.resetButton}
          >
            Сбросить
          </Button>
        )}
      </div>
    </div>
  );
};
