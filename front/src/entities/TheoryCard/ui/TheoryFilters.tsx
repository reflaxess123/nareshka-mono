import {
  findOriginalCategory,
  translateMainCategory,
  translateSubCategory,
} from '@/shared/constants/categoryTranslations';
import { useEffect, useState } from 'react';
import { useCategories } from '../model/queries';
import type { TheoryFilters } from '../model/types';
import styles from './TheoryFilters.module.scss';

interface TheoryFiltersComponentProps {
  filters: TheoryFilters;
  onFiltersChange: (filters: TheoryFilters) => void;
}

export const TheoryFiltersComponent = ({
  filters,
  onFiltersChange,
}: TheoryFiltersComponentProps) => {
  const { data: categories, isLoading: categoriesLoading } = useCategories();
  const [searchInput, setSearchInput] = useState(filters.searchQuery || '');

  // Дебаунс для поиска
  useEffect(() => {
    const timer = setTimeout(() => {
      onFiltersChange({ ...filters, searchQuery: searchInput || undefined });
    }, 500);

    return () => clearTimeout(timer);
  }, [searchInput, filters, onFiltersChange]);

  const handleCategoryChange = (category: string) => {
    // Если выбрана переведенная категория, конвертируем обратно в оригинальное название для API
    const originalCategory =
      category === 'all' ? undefined : findOriginalCategory(category, true);

    onFiltersChange({
      ...filters,
      category: originalCategory,
      subCategory: undefined, // Сбрасываем подкатегорию при смене категории
    });
  };

  const handleSubCategoryChange = (subCategory: string) => {
    // Если выбрана переведенная подкатегория, конвертируем обратно в оригинальное название для API
    const originalSubCategory =
      subCategory === 'all'
        ? undefined
        : findOriginalCategory(subCategory, false);

    onFiltersChange({
      ...filters,
      subCategory: originalSubCategory,
    });
  };

  const handleOnlyUnstudiedChange = (checked: boolean) => {
    onFiltersChange({ ...filters, onlyUnstudied: checked });
  };

  const selectedCategory = categories?.categories?.find(
    (cat) => cat.name === filters.category
  );

  // Получаем переведенные названия для отображения
  const displayCategory = filters.category
    ? translateMainCategory(filters.category)
    : 'all';

  const displaySubCategory = filters.subCategory
    ? translateSubCategory(filters.subCategory)
    : 'all';

  return (
    <div className={styles.filters}>
      <div className={styles.filtersRow}>
        {/* Поиск */}
        <div className={styles.searchGroup}>
          <input
            type="text"
            placeholder="Поиск по вопросам и ответам..."
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            className={styles.searchInput}
          />
          <span className={styles.searchIcon}>🔍</span>
        </div>

        {/* Категории */}
        <div className={styles.filterGroup}>
          <select
            value={displayCategory}
            onChange={(e) => handleCategoryChange(e.target.value)}
            className={styles.filterSelect}
            disabled={categoriesLoading}
          >
            <option value="all">Все категории</option>
            {categories?.categories?.map((category) => (
              <option
                key={category.name}
                value={translateMainCategory(category.name)}
              >
                {translateMainCategory(category.name)} ({category.totalCards})
              </option>
            ))}
          </select>
        </div>

        {/* Подкатегории */}
        {selectedCategory && selectedCategory.subCategories.length > 0 && (
          <div className={styles.filterGroup}>
            <select
              value={displaySubCategory}
              onChange={(e) => handleSubCategoryChange(e.target.value)}
              className={styles.filterSelect}
            >
              <option value="all">Все подкатегории</option>
              {selectedCategory.subCategories.map((subCategory) => (
                <option
                  key={subCategory.name}
                  value={translateSubCategory(subCategory.name)}
                >
                  {translateSubCategory(subCategory.name)} (
                  {subCategory.cardCount})
                </option>
              ))}
            </select>
          </div>
        )}

        {/* Только неизученные */}
        <div className={styles.checkboxGroup}>
          <label className={styles.checkboxLabel}>
            <input
              type="checkbox"
              checked={filters.onlyUnstudied || false}
              onChange={(e) => handleOnlyUnstudiedChange(e.target.checked)}
              className={styles.checkbox}
            />
            Только неизученные
          </label>
        </div>
      </div>
    </div>
  );
};
