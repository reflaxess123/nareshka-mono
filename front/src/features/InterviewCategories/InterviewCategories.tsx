import React, { useEffect, useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Search, X } from 'lucide-react';
import { QuestionFilters } from '@/features/InterviewFilters';
import { useUrlState, type FilterState } from '@/shared/hooks';
import styles from './InterviewCategories.module.scss';

interface Question {
  id: string;
  question_text: string;
  company?: string;
  topic_name?: string;
  cluster_id?: number;
  category_id?: string;
  interview_id?: string;
}



export const InterviewCategories: React.FC = () => {
  const { filters, currentPage, updateFilters, updatePage, resetFilters } = useUrlState();
  const [totalPages, setTotalPages] = React.useState(1);
  const ITEMS_PER_PAGE = 50;

  // Helper functions
  const handleFiltersChange = useCallback((newFilters: FilterState) => {
    updateFilters(newFilters);
  }, [updateFilters]);

  const clearAllFilters = useCallback(() => {
    resetFilters();
  }, [resetFilters]);
  

  // Always fetch questions - всегда показываем вопросы
  const shouldFetchQuestions = true;
  
  const buildQuestionsQuery = () => {
    const params = new URLSearchParams();
    
    // Поисковый запрос
    const searchTerm = filters.search;
    if (searchTerm.length >= 2) {
      params.append('q', searchTerm);
    } else {
      params.append('q', '*'); // Показываем все вопросы
    }
    
    // Множественные категории
    filters.categories.forEach(categoryId => {
      params.append('category_ids', categoryId);
    });
    
    // Множественные кластеры
    filters.clusters.forEach(clusterId => {
      params.append('cluster_ids', clusterId.toString());
    });
    
    // Множественные компании
    filters.companies.forEach(company => {
      params.append('companies', company);
    });
    
    params.append('limit', ITEMS_PER_PAGE.toString());
    params.append('offset', ((currentPage - 1) * ITEMS_PER_PAGE).toString());
    return params.toString();
  };

  // Unified questions query with pagination
  const { data: questionsData, isLoading: questionsLoading } = useQuery<{questions: Question[], total: number}>({
    queryKey: ['questions', filters, currentPage],
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
  const handleSearchChange = useCallback((value: string) => {
    updateFilters({
      ...filters,
      search: value
    });
  }, [filters, updateFilters]);

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

  // Filter by same interview
  const handleShowSameInterview = useCallback((interviewId: string) => {
    updateFilters({
      categories: [],
      clusters: [],
      companies: [],
      search: `interview:${interviewId}`
    });
  }, [updateFilters]);

  // Memoized interview counts for performance
  const interviewCounts = React.useMemo(() => {
    const counts: Record<string, number> = {};
    questions.forEach(q => {
      if (q.interview_id) {
        counts[q.interview_id] = (counts[q.interview_id] || 0) + 1;
      }
    });
    return counts;
  }, [questions]);

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

  
  // Helper to generate filter tags for display (memoized)
  const activeFilterTags = React.useMemo(() => {
    const tags = [];
    
    if (filters.search) {
      tags.push({ type: 'search', label: `"🔍 ${filters.search}"`, value: filters.search });
    }
    
    filters.categories.forEach(categoryId => {
      tags.push({ type: 'category', label: `📁 ${categoryId}`, value: categoryId });
    });
    
    filters.clusters.forEach(clusterId => {
      tags.push({ type: 'cluster', label: `🏷️ Cluster ${clusterId}`, value: clusterId.toString() });
    });
    
    filters.companies.forEach(company => {
      tags.push({ type: 'company', label: `🏢 ${company}`, value: company });
    });
    
    return tags;
  }, [filters]);
  
  const removeFilterTag = useCallback((tag: { type: string; value: string }) => {
    const newFilters = { ...filters };
    
    switch (tag.type) {
      case 'search':
        newFilters.search = '';
        break;
      case 'category':
        newFilters.categories = newFilters.categories.filter(id => id !== tag.value);
        break;
      case 'cluster':
        newFilters.clusters = newFilters.clusters.filter(id => id.toString() !== tag.value);
        break;
      case 'company':
        newFilters.companies = newFilters.companies.filter(name => name !== tag.value);
        break;
    }
    
    updateFilters(newFilters);
  }, [filters, updateFilters]);

  return (
    <div className={styles.container}>
      {/* Search Bar */}
      <div className={styles.searchSection}>
        <div className={styles.searchInputWrapper}>
          <Search size={20} className={styles.searchIcon} />
          <input
            id="question-search"
            type="text"
            placeholder="Поиск вопросов... (Ctrl+K)"
            value={filters.search}
            onChange={(e) => handleSearchChange(e.target.value)}
            className={styles.searchInput}
          />
          {filters.search && (
            <button
              onClick={() => handleSearchChange('')}
              className={styles.clearSearchButton}
            >
              <X size={16} />
            </button>
          )}
        </div>
      </div>
      
      {/* Active Filters Tags */}
      {activeFilterTags.length > 0 && (
        <div className={styles.activeFiltersSection}>
          <div className={styles.activeFilters}>
            {activeFilterTags.map((tag, index) => (
              <span key={`${tag.type}-${tag.value}-${index}`} className={styles.filterTag}>
                {tag.label}
                <button
                  onClick={() => removeFilterTag(tag)}
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
            <>
              <table className={styles.dataTable}>
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Вопрос</th>
                    <th>Компания</th>
                    <th>Категория</th>
                    <th>Интервью</th>
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
                      <td className={styles.interviewCell}>
                        {question.interview_id ? (
                          <button
                            className={styles.interviewButton}
                            onClick={(e) => {
                              e.stopPropagation();
                              handleShowSameInterview(question.interview_id!);
                            }}
                            title={`${question.interview_id.replace('interview_', '').replace(/_(\d+)$/, (match, num) => ` - интервью ${parseInt(num) + 1}`).replace(/_/g, ' ')} (${interviewCounts[question.interview_id] || 1} вопросов)`}
                          >
                            <span className={styles.interviewName}>
                              {question.interview_id
                                .replace('interview_', '')
                                .replace(/_(\d+)$/, (match, num) => ` - интервью ${parseInt(num) + 1}`)
                                .replace(/_/g, ' ')
                              }
                            </span>
                            <span className={styles.interviewCount}>
                              {interviewCounts[question.interview_id] || 1} вопр.
                            </span>
                          </button>
                        ) : '-'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              
              {/* Pagination */}
              {questions.length > 0 && (
                <div className={styles.pagination}>
                  <div className={styles.paginationControls}>
                    <button
                      className={styles.paginationButton}
                      onClick={() => updatePage(Math.max(1, currentPage - 1))}
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
                            onClick={() => updatePage(pageNum)}
                          >
                            {pageNum}
                          </button>
                        );
                      })}
                    </div>
                    
                    <button
                      className={styles.paginationButton}
                      onClick={() => updatePage(Math.min(totalPages || 1, currentPage + 1))}
                      disabled={currentPage === totalPages}
                    >
                      Следующая →
                    </button>
                  </div>
                  
                  <div className={styles.paginationInfo}>
                    Страница {currentPage} из {totalPages} • Всего: {totalQuestions.toLocaleString()} вопросов
                  </div>
                </div>
              )}
            </>
          )}
        </div>
        
        {/* Filters Sidebar */}
        <aside className={styles.filtersSection}>
          <div className={styles.filtersContainer}>
            <h3 className={styles.filtersTitle}>🔧 Фильтры</h3>
            <QuestionFilters 
              filters={filters}
              onFiltersChange={handleFiltersChange}
              onReset={clearAllFilters}
              className={styles.filters}
            />
          </div>
        </aside>
      </div>
    </div>
  );
};