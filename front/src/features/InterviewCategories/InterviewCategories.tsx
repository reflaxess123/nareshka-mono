import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { useQuery, useInfiniteQuery } from '@tanstack/react-query';
import type { InfiniteData } from '@tanstack/react-query';
import { Search, Filter, X, Eye, Copy, Heart, ChevronRight, Grid, List, Table } from 'lucide-react';
import styles from './InterviewCategories.module.scss';

interface Category {
  id: string;
  name: string;
  questions_count: number;
  clusters_count: number;
  percentage: number;
  color?: string;
  icon?: string;
}

interface Cluster {
  id: number;
  name: string;
  category_id: string;
  keywords: string[];
  questions_count: number;
  example_question?: string;
}

interface Question {
  id: string;
  question_text: string;
  company?: string;
  topic_name?: string;
  cluster_id?: number;
  category_id?: string;
}

interface CategoryDetail {
  category: Category;
  clusters: Cluster[];
  sample_questions: Question[];
}

interface Company {
  name: string;
  count: number;
}

type ViewMode = 'categories' | 'questions' | 'search';
type DisplayMode = 'table' | 'cards' | 'compact';
type FilterTag = {
  type: 'category' | 'company' | 'search';
  value: string;
  label: string;
};

// Цвета для категорий
const CATEGORY_COLORS: Record<string, string> = {
  'javascript_core': '#f7df1e',
  'react': '#61dafb',
  'typescript': '#3178c6',
  'soft_skills': '#9b59b6',
  'сеть': '#e74c3c',
  'алгоритмы': '#2ecc71',
  'верстка': '#e67e22',
  'инструменты': '#95a5a6',
  'производительность': '#f39c12',
  'тестирование': '#27ae60',
  'архитектура': '#8e44ad',
  'браузеры': '#3498db',
  'другое': '#7f8c8d'
};

export const InterviewCategories: React.FC = () => {
  const [viewMode, setViewMode] = useState<ViewMode>('questions'); // По умолчанию показываем вопросы
  const [displayMode, setDisplayMode] = useState<DisplayMode>('table');
  const [searchQuery, setSearchQuery] = useState('');
  const [activeFilters, setActiveFilters] = useState<FilterTag[]>([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const ITEMS_PER_PAGE = 50;

  // Helper functions
  const addFilter = (filter: FilterTag) => {
    setActiveFilters(prev => {
      const exists = prev.find(f => f.type === filter.type && f.value === filter.value);
      if (exists) return prev;
      
      // Remove existing filter of same type for categories/companies
      if (filter.type === 'category' || filter.type === 'company') {
        const filtered = prev.filter(f => f.type !== filter.type);
        return [...filtered, filter];
      }
      
      return [...prev, filter];
    });
    setCurrentPage(1); // Сброс на первую страницу при фильтрации
  };

  const removeFilter = (filter: FilterTag) => {
    setActiveFilters(prev => prev.filter(f => !(f.type === filter.type && f.value === filter.value)));
    setCurrentPage(1);
  };

  const clearAllFilters = () => {
    setActiveFilters([]);
    setSearchQuery('');
    setCurrentPage(1);
  };

  // Derived state
  const currentCategory = activeFilters.find(f => f.type === 'category')?.value || null;
  const currentCompany = activeFilters.find(f => f.type === 'company')?.value || null;
  
  // Загрузка категорий
  const { data: categories, isLoading: categoriesLoading } = useQuery<Category[]>({
    queryKey: ['interview-categories'],
    queryFn: async () => {
      const response = await fetch('/api/v2/interview-categories/');
      if (!response.ok) throw new Error('Failed to fetch categories');
      return response.json();
    }
  });

  // Загрузка топ компаний (для фильтров)
  const { data: topCompanies } = useQuery<Company[]>({
    queryKey: ['top-companies'],
    queryFn: async () => {
      const response = await fetch('/api/v2/interview-categories/companies/top');
      if (!response.ok) throw new Error('Failed to fetch companies');
      return response.json();
    }
  });

  // Загрузка общего количества компаний (для статистики)
  const { data: totalCompaniesCount } = useQuery<number>({
    queryKey: ['total-companies-count'],
    queryFn: async () => {
      const response = await fetch('/api/v2/interview-categories/companies/count');
      if (!response.ok) throw new Error('Failed to fetch companies count');
      return response.json();
    }
  });

  // Always fetch questions - всегда показываем вопросы
  const shouldFetchQuestions = true;
  
  const buildQuestionsQuery = () => {
    const params = new URLSearchParams();
    
    if (searchQuery.length >= 2) {
      params.append('q', searchQuery);
    } else {
      params.append('q', '*'); // Показываем все вопросы
    }
    
    if (currentCategory) {
      params.append('category_id', currentCategory);
    }
    
    if (currentCompany) {
      params.append('company', currentCompany);
    }
    
    params.append('limit', ITEMS_PER_PAGE.toString());
    params.append('offset', ((currentPage - 1) * ITEMS_PER_PAGE).toString());
    return params.toString();
  };

  // Unified questions query with pagination
  const { data: questionsData, isLoading: questionsLoading } = useQuery<{questions: Question[], total: number}>({
    queryKey: ['questions', currentCategory, currentCompany, searchQuery, currentPage],
    queryFn: async () => {
      const queryString = buildQuestionsQuery();
      const response = await fetch(`/api/v2/interview-categories/search/questions?${queryString}`);
      if (!response.ok) throw new Error('Failed to fetch questions');
      const data = await response.json();
      
      // API теперь возвращает QuestionsListResponse с пагинацией
      return {
        questions: data.questions || [],
        total: data.total || 0
      };
    },
    enabled: shouldFetchQuestions
  });

  const questions = questionsData?.questions || [];
  const totalQuestions = questionsData?.total || 0;
  
  // Update total pages when data changes
  useEffect(() => {
    setTotalPages(Math.ceil(totalQuestions / ITEMS_PER_PAGE));
  }, [totalQuestions]);




  // Handle search input
  const handleSearchChange = (value: string) => {
    setSearchQuery(value);
    setCurrentPage(1); // Сброс на первую страницу при поиске
    if (value.length >= 2) {
      const searchFilter: FilterTag = {
        type: 'search',
        value: value,
        label: `"${value}"`
      };
      setActiveFilters(prev => {
        const withoutSearch = prev.filter(f => f.type !== 'search');
        return [...withoutSearch, searchFilter];
      });
    } else {
      setActiveFilters(prev => prev.filter(f => f.type !== 'search'));
    }
  };

  // Handle question click - copy to clipboard
  const handleQuestionSelect = async (question: Question) => {
    try {
      await navigator.clipboard.writeText(question.question_text);
      // TODO: Add toast notification here
      console.log('Вопрос скопирован в буфер обмена');
    } catch (err) {
      console.error('Ошибка копирования:', err);
    }
  };

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.ctrlKey && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.querySelector('#question-search') as HTMLInputElement;
        searchInput?.focus();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Statistics
  const totalQuestionsInDB = categories?.reduce((sum, cat) => sum + cat.questions_count, 0) || 0;
  const totalClusters = categories?.reduce((sum, cat) => sum + cat.clusters_count, 0) || 0;
  const totalCompanies = totalCompaniesCount || 0;
  
  // All categories for filtering
  const topCategories = useMemo(() => {
    if (!categories) return [];
    return categories; // Show all categories
  }, [categories]);

  // Navigation handlers
  const handleCategorySelect = (category: Category) => {
    const filter: FilterTag = {
      type: 'category',
      value: category.id,
      label: category.name
    };
    addFilter(filter);
  };

  const handleCompanySelect = (company: Company) => {
    const filter: FilterTag = {
      type: 'company',
      value: company.name,
      label: company.name
    };
    addFilter(filter);
  };

  return (
    <div className={styles.container}>
      {/* Sticky Toolbar */}
      <div className={styles.stickyToolbar}>
        {/* Search Bar */}
        <div className={styles.searchSection}>
          <div className={styles.searchInputWrapper}>
            <Search size={20} className={styles.searchIcon} />
            <input
              id="question-search"
              type="text"
              placeholder="Поиск вопросов... (Ctrl+K)"
              value={searchQuery}
              onChange={(e) => handleSearchChange(e.target.value)}
              className={styles.searchInput}
            />
            {searchQuery && (
              <button
                onClick={() => handleSearchChange('')}
                className={styles.clearSearchButton}
              >
                <X size={16} />
              </button>
            )}
          </div>
        </div>
        
        {/* Quick Category Filters */}
        <div className={styles.toolbarActions}>
          <div className={styles.quickCategories}>
            {topCategories.map((category) => (
              <button
                key={category.id}
                onClick={() => handleCategorySelect(category)}
                className={styles.categoryChip}
                style={{
                  '--category-color': CATEGORY_COLORS[category.id] || '#ddd'
                } as React.CSSProperties}
              >
                <span className={styles.chipLabel}>{category.name}</span>
                <span className={styles.chipCount}>{category.questions_count}</span>
              </button>
            ))}
          </div>
        </div>
      </div>
      
      {/* Active Filters Tags */}
      {activeFilters.length > 0 && (
        <div className={styles.activeFiltersSection}>
          <div className={styles.activeFilters}>
            {activeFilters.map((filter, index) => (
              <span key={`${filter.type}-${filter.value}-${index}`} className={styles.filterTag}>
                {filter.type === 'category' && '📁'}
                {filter.type === 'company' && '🏢'}
                {filter.type === 'search' && '🔍'}
                {filter.label}
                <button
                  onClick={() => removeFilter(filter)}
                  className={styles.removeFilterButton}
                >
                  <X size={12} />
                </button>
              </span>
            ))}
            <button onClick={clearAllFilters} className={styles.clearAllFilters}>
              Очистить всё
            </button>
          </div>
        </div>
      )}
      
      {/* Statistics Bar */}
      <div className={styles.statisticsBar}>
        <div className={styles.statItem}>
          <span className={styles.statValue}>
            {totalQuestions.toLocaleString()}
          </span>
          <span className={styles.statLabel}>
            {activeFilters.length > 0 || searchQuery ? 'найдено вопросов' : 'всего вопросов'}
          </span>
        </div>
        {totalQuestions > 0 && (
          <>
            <div className={styles.statSeparator}>•</div>
            <div className={styles.statItem}>
              <span className={styles.statValue}>{currentPage}</span>
              <span className={styles.statLabel}>из {totalPages}</span>
            </div>
          </>
        )}
        <div className={styles.statSeparator}>•</div>
        <div className={styles.statItem}>
          <span className={styles.statValue}>{categories?.length || 0}</span>
          <span className={styles.statLabel}>категорий</span>
        </div>
        <div className={styles.statSeparator}>•</div>
        <div className={styles.statItem}>
          <span className={styles.statValue}>{totalCompanies}</span>
          <span className={styles.statLabel}>компаний</span>
        </div>
      </div>

      


      {/* Main Content Area */}
      <div className={styles.mainContent}>
        <div className={styles.questionsSection}>
          {questionsLoading && <div className={styles.loading}>Загрузка вопросов...</div>}
          
          {!questionsLoading && questions.length === 0 && (
            <div className={styles.noResults}>
              <span>Вопросы не найдены</span>
            </div>
          )}
          
          {questions.length > 0 && (
            <table className={styles.dataTable}>
              <thead>
                <tr>
                  <th>#</th>
                  <th>Вопрос</th>
                  <th>Компания</th>
                  <th>Категория</th>
                </tr>
              </thead>
              <tbody>
                {questions.map((question, index) => (
                  <tr 
                    key={question.id}
                    className={styles.tableRow}
                    onClick={() => handleQuestionSelect(question)}
                  >
                    <td className={styles.numberCell}>#{((currentPage - 1) * ITEMS_PER_PAGE) + index + 1}</td>
                    <td className={styles.questionCell}>
                      <div className={styles.questionText}>{question.question_text}</div>
                    </td>
                    <td className={styles.companyCell}>{question.company || '-'}</td>
                    <td className={styles.categoryCell}>{question.category_id || '-'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
        
        {/* Pagination */}
        {/* Отладка: показываем всегда для тестирования */}
        <div style={{ padding: '1rem', background: '#f0f0f0', color: '#000' }}>
          Отладка: totalQuestions={totalQuestions}, totalPages={totalPages}, currentPage={currentPage}
        </div>
        
        <div className={styles.pagination}>
          <button
            className={styles.paginationButton}
            onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
            disabled={currentPage === 1}
          >
            ← Предыдущая
          </button>
          
          <div className={styles.paginationNumbers}>
            {Array.from({ length: Math.max(1, Math.min(5, totalPages)) }, (_, i) => {
              let pageNum: number;
              if (totalPages <= 5) {
                pageNum = i + 1;
              } else if (currentPage <= 3) {
                pageNum = i + 1;
              } else if (currentPage >= totalPages - 2) {
                pageNum = totalPages - 4 + i;
              } else {
                pageNum = currentPage - 2 + i;
              }
              
              return (
                <button
                  key={pageNum}
                  className={`${styles.paginationButton} ${currentPage === pageNum ? styles.active : ''}`}
                  onClick={() => setCurrentPage(pageNum)}
                >
                  {pageNum}
                </button>
              );
            })}
          </div>
          
          <button
            className={styles.paginationButton}
            onClick={() => setCurrentPage(prev => Math.min(totalPages || 1, prev + 1))}
            disabled={currentPage === totalPages}
          >
            Следующая →
          </button>
        </div>
      </div>
      

    </div>
  );
};