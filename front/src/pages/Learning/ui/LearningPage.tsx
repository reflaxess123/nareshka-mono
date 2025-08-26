import React, { useState, useCallback, useEffect } from 'react';
import { Search, X, BookOpen, HelpCircle, Briefcase, GraduationCap, ArrowUpDown } from 'lucide-react';
import { PageWrapper } from '@/shared/components/PageWrapper/ui/PageWrapper';
import { Text, TextAlign, TextSize, TextWeight } from '@/shared/components/Text';
import { UnifiedFilters } from '@/features/UnifiedFilters';
import { useLearningStore } from '../model/learningStore';
import { UniversalContentList } from '@/widgets/UniversalContentList';
import { CONTENT_TYPE_CONFIG, type ContentType } from '@/shared/types/learning';
import styles from './LearningPage.module.scss';

const TAB_ICONS: Record<ContentType, React.ReactNode> = {
  interviews: <Briefcase size={18} />,
  questions: <HelpCircle size={18} />,
  practice: <BookOpen size={18} />,
  theory: <GraduationCap size={18} />
};

export const LearningPage: React.FC = () => {
  const {
    activeTab,
    filters,
    searchHistory,
    sortBy,
    sortOrder,
    setActiveTab,
    updateFilters,
    addToSearchHistory,
    setSorting
  } = useLearningStore();

  // Фиксированный режим отображения - только список
  const viewMode = 'list';

  const [showFilters, setShowFilters] = useState(true);
  const [searchValue, setSearchValue] = useState(filters.search || '');
  const [showSortOptions, setShowSortOptions] = useState(false);

  // Закрытие dropdown при клике вне
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (showSortOptions) {
        const target = event.target as Element;
        if (!target.closest(`.${styles.sortContainer}`)) {
          setShowSortOptions(false);
        }
      }
    };

    if (showSortOptions) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showSortOptions]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ctrl+K для фокуса на поиск
      if (e.ctrlKey && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.querySelector('#learning-search') as HTMLInputElement;
        searchInput?.focus();
      }
      // Ctrl+F для toggle фильтров
      if (e.ctrlKey && e.key === 'f' && !e.shiftKey) {
        e.preventDefault();
        setShowFilters(prev => !prev);
      }
      // Alt+1,2,3,4 для переключения табов
      if (e.altKey) {
        const tabIndex = parseInt(e.key) - 1;
        const tabs: ContentType[] = ['interviews', 'questions', 'practice', 'theory'];
        if (tabIndex >= 0 && tabIndex < tabs.length) {
          e.preventDefault();
          setActiveTab(tabs[tabIndex]);
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [setActiveTab]);

  // Обработка поиска - теперь автоматический при вводе

  const handleSearchChange = useCallback((value: string) => {
    setSearchValue(value);
    // Debounced search можно добавить здесь
  }, []);

  const handleClearSearch = useCallback(() => {
    setSearchValue('');
    updateFilters({ search: undefined });
  }, [updateFilters]);

  // Обработка сортировки
  const handleSortChange = useCallback((newSortBy: string, newSortOrder?: 'asc' | 'desc') => {
    setSorting(newSortBy, newSortOrder || 'desc');
    setShowSortOptions(false);
  }, [setSorting]);

  // Опции сортировки в зависимости от типа контента
  const getSortOptions = () => {
    switch (activeTab) {
      case 'interviews':
        return [
          { value: 'created_at', label: 'По дате создания' },
          { value: 'company_name', label: 'По компании' },
          { value: 'title', label: 'По названию' }
        ];
      case 'questions':
        return [
          { value: 'created_at', label: 'По дате' },
          { value: 'company', label: 'По компании' },
          { value: 'category_id', label: 'По категории' }
        ];
      case 'practice':
        return [
          { value: 'orderInFile', label: 'По порядку в файле' },
          { value: 'createdAt', label: 'По дате создания' },
          { value: 'blockLevel', label: 'По сложности' }
        ];
      case 'theory':
        return [
          { value: 'orderIndex', label: 'По порядку' },
          { value: 'createdAt', label: 'По дате создания' },
          { value: 'category', label: 'По категории' }
        ];
      default:
        return [{ value: 'created_at', label: 'По дате создания' }];
    }
  };

  // Получаем конфигурацию текущего таба
  const currentConfig = CONTENT_TYPE_CONFIG[activeTab];

  return (
    <PageWrapper>
      <div className={styles.page}>
        {/* Header */}
        <header className={styles.header}>
          <div className={styles.headerContent}>
            <div className={styles.iconWrapper}>
              <BookOpen size={40} className={styles.pageIcon} />
            </div>
            <div className={styles.headerText}>
              <Text
                text="Центр обучения"
                size={TextSize.XXL}
                weight={TextWeight.BOLD}
                align={TextAlign.LEFT}
                className={styles.title}
              />
              <Text
                text="Все материалы для подготовки к собеседованиям в одном месте"
                size={TextSize.MD}
                align={TextAlign.LEFT}
                className={styles.description}
              />
            </div>

            {/* Режим отображения зафиксирован на "Список" */}
          </div>
        </header>

        {/* Content Type Tabs */}
        <div className={styles.tabsSection}>
          <div className={styles.tabs}>
            {(Object.keys(CONTENT_TYPE_CONFIG) as ContentType[]).map((type) => {
              const config = CONTENT_TYPE_CONFIG[type];
              return (
                <button
                  key={type}
                  className={`${styles.tab} ${activeTab === type ? styles.active : ''}`}
                  onClick={() => setActiveTab(type)}
                  style={{
                    '--tab-color': config.color
                  } as React.CSSProperties}
                >
                  <span className={styles.tabIcon}>{TAB_ICONS[type]}</span>
                  <span className={styles.tabLabel}>{config.label}</span>
                </button>
              );
            })}
          </div>

          {/* Tab Description */}
          <div className={styles.tabDescription}>
            <span className={styles.tabDescIcon}>{currentConfig.icon}</span>
            <Text
              text={currentConfig.description}
              size={TextSize.SM}
              className={styles.tabDescText}
            />
          </div>
        </div>

        {/* Search Bar */}
        <div className={styles.searchSection}>
          <div className={styles.searchInputWrapper}>
            <Search size={20} className={styles.searchIcon} />
            <input
              id="learning-search"
              type="text"
              placeholder={`Поиск ${currentConfig.label.toLowerCase()}... (Ctrl+K)`}
              value={searchValue}
              onChange={(e) => {
                handleSearchChange(e.target.value);
                // Автоматически применяем поиск при изменении
                if (e.target.value.trim()) {
                  updateFilters({ search: e.target.value });
                  addToSearchHistory(e.target.value);
                } else {
                  updateFilters({ search: undefined });
                }
              }}
              className={styles.searchInput}
              list="search-history"
            />
            {searchValue && (
              <button
                type="button"
                onClick={handleClearSearch}
                className={styles.clearSearchButton}
              >
                <X size={16} />
              </button>
            )}
            {/* Search history datalist */}
            <datalist id="search-history">
              {searchHistory.map((query, index) => (
                <option key={index} value={query} />
              ))}
            </datalist>
          </div>

          {/* Sort Dropdown */}
          <div className={styles.sortContainer}>
            <button
              className={`${styles.sortButton} ${showSortOptions ? styles.active : ''}`}
              onClick={() => setShowSortOptions(!showSortOptions)}
              title="Сортировка"
            >
              <ArrowUpDown size={20} />
              <span>Сортировка</span>
            </button>

            {showSortOptions && (
              <div className={styles.sortDropdown}>
                {getSortOptions().map(option => (
                  <button
                    key={option.value}
                    className={`${styles.sortOption} ${sortBy === option.value ? styles.active : ''}`}
                    onClick={() => handleSortChange(option.value)}
                  >
                    {option.label}
                    {sortBy === option.value && (
                      <span className={styles.sortDirection}>
                        {sortOrder === 'asc' ? '↑' : '↓'}
                      </span>
                    )}
                  </button>
                ))}
                <div className={styles.sortDivider} />
                <button
                  className={styles.sortOption}
                  onClick={() => handleSortChange(sortBy, sortOrder === 'asc' ? 'desc' : 'asc')}
                >
                  {sortOrder === 'asc' ? 'По убыванию' : 'По возрастанию'}
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Main Content Area */}
        <div className={styles.mainContent}>
          {/* Content List */}
          <div className={styles.contentSection}>
            <UniversalContentList
              contentType={activeTab}
              filters={filters}
              viewMode={viewMode}
              className={styles.contentList}
            />
          </div>

          {/* Filters Sidebar */}
          {showFilters && (
            <aside className={styles.filtersSection}>
              <div className={styles.filtersContainer}>
                <UnifiedFilters
                  type={activeTab}
                  filters={filters}
                  onFiltersChange={updateFilters}
                  className={styles.filters}
                />
              </div>
            </aside>
          )}
        </div>
      </div>
    </PageWrapper>
  );
};
