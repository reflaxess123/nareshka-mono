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
    onFiltersChange({
      ...filters,
      category: category === 'all' ? undefined : category,
      subCategory: undefined, // Сбрасываем подкатегорию при смене категории
    });
  };

  const handleSubCategoryChange = (subCategory: string) => {
    onFiltersChange({
      ...filters,
      subCategory: subCategory === 'all' ? undefined : subCategory,
    });
  };

  const handleOnlyUnstudiedChange = (checked: boolean) => {
    onFiltersChange({ ...filters, onlyUnstudied: checked });
  };

  const selectedCategory = categories?.find(
    (cat) => cat.name === filters.category
  );

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
            value={filters.category || 'all'}
            onChange={(e) => handleCategoryChange(e.target.value)}
            className={styles.filterSelect}
            disabled={categoriesLoading}
          >
            <option value="all">Все категории</option>
            {categories?.map((category) => (
              <option key={category.name} value={category.name}>
                {category.name} ({category.totalCards})
              </option>
            ))}
          </select>
        </div>

        {/* Подкатегории */}
        {selectedCategory && selectedCategory.subCategories.length > 0 && (
          <div className={styles.filterGroup}>
            <select
              value={filters.subCategory || 'all'}
              onChange={(e) => handleSubCategoryChange(e.target.value)}
              className={styles.filterSelect}
            >
              <option value="all">Все подкатегории</option>
              {selectedCategory.subCategories.map((subCategory) => (
                <option key={subCategory.name} value={subCategory.name}>
                  {subCategory.name} ({subCategory.cardCount})
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
