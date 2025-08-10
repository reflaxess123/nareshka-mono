import React, { useState, useEffect, useCallback } from 'react';
import { useQuery, useInfiniteQuery } from '@tanstack/react-query';
import type { InfiniteData } from '@tanstack/react-query';
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

type ViewMode = 'categories' | 'category-detail' | 'cluster-questions' | 'search' | 'companies';

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
  const [viewMode, setViewMode] = useState<ViewMode>('categories');
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [selectedCluster, setSelectedCluster] = useState<number | null>(null);
  const [selectedCompany, setSelectedCompany] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [clusterQuestionsPage, setClusterQuestionsPage] = useState(1);
  const [showFilters, setShowFilters] = useState(false);

  // Загрузка категорий
  const { data: categories, isLoading: categoriesLoading } = useQuery<Category[]>({
    queryKey: ['interview-categories'],
    queryFn: async () => {
      const response = await fetch('/api/v2/interview-categories/');
      if (!response.ok) throw new Error('Failed to fetch categories');
      return response.json();
    }
  });

  // Загрузка топ компаний
  const { data: topCompanies } = useQuery<Company[]>({
    queryKey: ['top-companies'],
    queryFn: async () => {
      const response = await fetch('/api/v2/interview-categories/companies/top');
      if (!response.ok) throw new Error('Failed to fetch companies');
      return response.json();
    }
  });

  // Загрузка деталей категории
  const { data: categoryDetail, isLoading: categoryDetailLoading } = useQuery<CategoryDetail>({
    queryKey: ['category-detail', selectedCategory],
    queryFn: async () => {
      if (!selectedCategory) return null;
      const response = await fetch(`/api/v2/interview-categories/${selectedCategory}?limit_questions=20`);
      if (!response.ok) throw new Error('Failed to fetch category detail');
      return response.json();
    },
    enabled: !!selectedCategory
  });

  // Загрузка вопросов категории с infinite scroll
  const {
    data: categoryQuestionsData,
    fetchNextPage: fetchNextCategoryPage,
    hasNextPage: hasNextCategoryPage,
    isFetchingNextPage: isFetchingNextCategoryPage,
    isLoading: categoryQuestionsLoading,
  } = useInfiniteQuery<Question[], Error, InfiniteData<Question[]>, (string | null)[], number>({
    queryKey: ['category-questions', selectedCategory],
    queryFn: async (context) => {
      const { pageParam = 0 } = context;
      if (!selectedCategory) return [];
      const params = new URLSearchParams({ 
        q: '*', 
        category_id: selectedCategory, 
        limit: '100',
        offset: pageParam.toString()
      });
      
      const response = await fetch(`/api/v2/interview-categories/search/questions?${params}`);
      if (!response.ok) throw new Error('Failed to fetch category questions');
      return response.json();
    },
    initialPageParam: 0,
    getNextPageParam: (lastPage: Question[], allPages: Question[][]) => {
      if (lastPage.length < 100) return undefined;
      return allPages.length * 100;
    },
    enabled: !!selectedCategory && viewMode === 'category-detail'
  });

  // Загрузка вопросов кластера
  const { data: clusterQuestions, isLoading: clusterQuestionsLoading } = useQuery<Question[]>({
    queryKey: ['cluster-questions', selectedCluster, clusterQuestionsPage],
    queryFn: async () => {
      if (!selectedCluster) return [];
      const response = await fetch(`/api/v2/interview-categories/cluster/${selectedCluster}/questions?page=${clusterQuestionsPage}&limit=50`);
      if (!response.ok) throw new Error('Failed to fetch cluster questions');
      return response.json();
    },
    enabled: !!selectedCluster
  });

  // Поиск вопросов
  const { data: searchResults, isLoading: searchLoading } = useQuery<Question[]>({
    queryKey: ['search-questions', searchQuery, selectedCategory, selectedCompany],
    queryFn: async () => {
      if (!searchQuery || searchQuery.length < 2) return [];
      const params = new URLSearchParams({ q: searchQuery, limit: '500' });
      if (selectedCategory) params.append('category_id', selectedCategory);
      if (selectedCompany) params.append('company', selectedCompany);
      
      const response = await fetch(`/api/v2/interview-categories/search/questions?${params}`);
      if (!response.ok) throw new Error('Failed to search questions');
      return response.json();
    },
    enabled: searchQuery.length >= 2
  });

  // Вопросы по компании с infinite scroll
  const {
    data: companyQuestionsData,
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
    isLoading: companyQuestionsLoading,
  } = useInfiniteQuery<Question[], Error, InfiniteData<Question[]>, (string | null)[], number>({
    queryKey: ['company-questions', selectedCompany],
    queryFn: async (context) => {
      const { pageParam = 0 } = context;
      if (!selectedCompany) return [];
      const params = new URLSearchParams({ 
        q: '*', 
        company: selectedCompany, 
        limit: '100',
        offset: pageParam.toString()
      });
      
      const response = await fetch(`/api/v2/interview-categories/search/questions?${params}`);
      if (!response.ok) throw new Error('Failed to fetch company questions');
      return response.json();
    },
    initialPageParam: 0,
    getNextPageParam: (lastPage: Question[], allPages: Question[][]) => {
      if (lastPage.length < 100) return undefined; // No more pages
      return allPages.length * 100; // Next offset
    },
    enabled: !!selectedCompany && viewMode === 'companies'
  });

  // Flatten questions for display  
  const companyQuestions: Question[] = companyQuestionsData?.pages.flat() || [];
  const categoryQuestions: Question[] = categoryQuestionsData?.pages.flat() || [];

  // Infinite scroll handler
  const handleScroll = useCallback(() => {
    if (
      window.innerHeight + document.documentElement.scrollTop !== document.documentElement.offsetHeight
    ) {
      return;
    }

    // Handle company questions infinite scroll
    if (viewMode === 'companies' && selectedCompany && !isFetchingNextPage && hasNextPage) {
      fetchNextPage();
    }
    
    // Handle category questions infinite scroll
    if (viewMode === 'category-detail' && selectedCategory && !isFetchingNextCategoryPage && hasNextCategoryPage) {
      fetchNextCategoryPage();
    }
  }, [viewMode, selectedCompany, selectedCategory, fetchNextPage, isFetchingNextPage, hasNextPage, fetchNextCategoryPage, isFetchingNextCategoryPage, hasNextCategoryPage]);

  useEffect(() => {
    if ((viewMode === 'companies' && selectedCompany) || (viewMode === 'category-detail' && selectedCategory)) {
      window.addEventListener('scroll', handleScroll);
      return () => window.removeEventListener('scroll', handleScroll);
    }
  }, [viewMode, selectedCompany, selectedCategory, handleScroll]);

  // Навигация
  const handleCategorySelect = (categoryId: string) => {
    setSelectedCategory(categoryId);
    setSelectedCluster(null);
    setViewMode('category-detail');
    setSearchQuery('');
  };

  const handleClusterSelect = (clusterId: number) => {
    setSelectedCluster(clusterId);
    setViewMode('cluster-questions');
    setClusterQuestionsPage(1);
  };

  const handleBackToCategories = () => {
    setViewMode('categories');
    setSelectedCategory(null);
    setSelectedCluster(null);
    setSearchQuery('');
  };

  const handleBackToCategoryDetail = () => {
    setViewMode('category-detail');
    setSelectedCluster(null);
    setClusterQuestionsPage(1);
  };

  const handleSearch = (query: string) => {
    setSearchQuery(query);
    if (query.length >= 2) {
      setViewMode('search');
    } else if (query.length === 0) {
      setViewMode(selectedCategory ? 'category-detail' : 'categories');
    }
  };

  const handleCompanySelect = (company: string | null) => {
    setSelectedCompany(company);
    if (company) {
      setViewMode('companies');
      setSelectedCategory(null);
      setSelectedCluster(null);
      setSearchQuery('');
      setShowFilters(false);
    } else {
      setViewMode('categories');
      setSelectedCategory(null);
      setSelectedCluster(null);
      setSearchQuery('');
    }
  };

  // Расчет статистики
  const totalQuestions = categories?.reduce((sum, cat) => sum + cat.questions_count, 0) || 0;
  const totalClusters = categories?.reduce((sum, cat) => sum + cat.clusters_count, 0) || 0;

  // Получаем данные о текущем кластере
  const currentCluster = categoryDetail?.clusters.find(c => c.id === selectedCluster);

  return (
    <div className={styles.container}>
      {/* Навигационная панель */}
      <div className={styles.breadcrumbs}>
        <button 
          onClick={handleBackToCategories}
          className={`${styles.breadcrumb} ${viewMode === 'categories' ? styles.active : ''}`}
        >
          📊 Категории
        </button>
        {selectedCategory && (
          <>
            <span className={styles.separator}>›</span>
            <button 
              onClick={handleBackToCategoryDetail}
              className={`${styles.breadcrumb} ${viewMode === 'category-detail' ? styles.active : ''}`}
            >
              {categoryDetail?.category.name}
            </button>
          </>
        )}
        {selectedCluster && currentCluster && (
          <>
            <span className={styles.separator}>›</span>
            <span className={`${styles.breadcrumb} ${styles.active}`}>
              {currentCluster.name}
            </span>
          </>
        )}
        {viewMode === 'search' && searchQuery && (
          <>
            <span className={styles.separator}>›</span>
            <span className={`${styles.breadcrumb} ${styles.active}`}>
              Поиск: "{searchQuery}"
            </span>
          </>
        )}
        {viewMode === 'companies' && selectedCompany && (
          <>
            <span className={styles.separator}>›</span>
            <span className={`${styles.breadcrumb} ${styles.active}`}>
              🏢 {selectedCompany}
            </span>
          </>
        )}
      </div>

      {/* Заголовок и статистика */}
      <div className={styles.header}>
        <h1>
          {viewMode === 'categories' && 'Категории вопросов интервью'}
          {viewMode === 'category-detail' && categoryDetail?.category.name}
          {viewMode === 'cluster-questions' && currentCluster?.name}
          {viewMode === 'search' && `Результаты поиска: "${searchQuery}"`}
          {viewMode === 'companies' && `Вопросы ${selectedCompany}`}
        </h1>
        
        {viewMode === 'categories' && (
          <div className={styles.stats}>
            <div className={styles.stat}>
              <span className={styles.statValue}>{totalQuestions.toLocaleString()}</span>
              <span className={styles.statLabel}>вопросов</span>
            </div>
            <div className={styles.stat}>
              <span className={styles.statValue}>{categories?.length || 0}</span>
              <span className={styles.statLabel}>категорий</span>
            </div>
            {totalClusters > 0 && (
              <div className={styles.stat}>
                <span className={styles.statValue}>{totalClusters}</span>
                <span className={styles.statLabel}>топиков</span>
              </div>
            )}
          </div>
        )}

        {viewMode === 'category-detail' && categoryDetail && (
          <div className={styles.stats}>
            <div className={styles.stat}>
              <span className={styles.statValue}>{categoryDetail.category.questions_count.toLocaleString()}</span>
              <span className={styles.statLabel}>вопросов</span>
            </div>
            <div className={styles.stat}>
              <span className={styles.statValue}>{categoryDetail.category.clusters_count}</span>
              <span className={styles.statLabel}>топиков</span>
            </div>
            <div className={styles.stat}>
              <span className={styles.statValue}>{categoryDetail.category.percentage.toFixed(1)}%</span>
              <span className={styles.statLabel}>от общего числа</span>
            </div>
          </div>
        )}

        {viewMode === 'cluster-questions' && currentCluster && (
          <div className={styles.stats}>
            <div className={styles.stat}>
              <span className={styles.statValue}>{currentCluster.questions_count}</span>
              <span className={styles.statLabel}>вопросов</span>
            </div>
            <div className={styles.stat}>
              <span className={styles.statValue}>{currentCluster.keywords.length}</span>
              <span className={styles.statLabel}>ключевых слов</span>
            </div>
          </div>
        )}

        {viewMode === 'companies' && selectedCompany && companyQuestions && (
          <div className={styles.stats}>
            <div className={styles.stat}>
              <span className={styles.statValue}>{companyQuestions.length}</span>
              <span className={styles.statLabel}>вопросов</span>
            </div>
            <div className={styles.stat}>
              <span className={styles.statValue}>{topCompanies?.find(c => c.name === selectedCompany)?.count || 0}</span>
              <span className={styles.statLabel}>всего в базе</span>
            </div>
          </div>
        )}
      </div>

      {/* Поиск и фильтры */}
      <div className={styles.searchBar}>
        <input
          type="text"
          placeholder="Поиск вопросов..."
          value={searchQuery}
          onChange={(e) => handleSearch(e.target.value)}
          className={styles.searchInput}
        />
        {searchQuery && (
          <button 
            onClick={() => handleSearch('')}
            className={styles.clearButton}
          >
            ✕
          </button>
        )}
        <button 
          onClick={() => setShowFilters(!showFilters)}
          className={styles.filtersToggle}
        >
          🔍 Фильтры
        </button>
      </div>

      {/* Панель фильтров */}
      {showFilters && viewMode !== 'companies' && (
        <div className={styles.filtersPanel}>
          <div className={styles.filterGroup}>
            <label>Компания:</label>
            <select 
              value={selectedCompany || ''} 
              onChange={(e) => handleCompanySelect(e.target.value || null)}
              className={styles.companySelect}
            >
              <option value="">Все компании</option>
              {topCompanies?.map(company => (
                <option key={company.name} value={company.name}>
                  {company.name} ({company.count})
                </option>
              ))}
            </select>
          </div>
        </div>
      )}

      {/* Контент в зависимости от режима просмотра */}
      {viewMode === 'categories' && (
        <div className={styles.categoriesGrid}>
          {categoriesLoading && <div className={styles.loading}>Загрузка категорий...</div>}
          
          {categories?.map(category => (
            <div
              key={category.id}
              className={styles.categoryCard}
              onClick={() => handleCategorySelect(category.id)}
              style={{
                borderColor: CATEGORY_COLORS[category.id] || '#ddd',
                '--category-color': CATEGORY_COLORS[category.id] || '#ddd'
              } as React.CSSProperties}
            >
              <div className={styles.categoryHeader}>
                <h3>{category.name}</h3>
                <span className={styles.percentage}>{category.percentage.toFixed(1)}%</span>
              </div>
              <div className={styles.categoryStats}>
                <div className={styles.statItem}>
                  <span className={styles.count}>{category.questions_count.toLocaleString()}</span>
                  <span className={styles.label}>вопросов</span>
                </div>
                {category.clusters_count > 0 && (
                  <div className={styles.statItem}>
                    <span className={styles.count}>{category.clusters_count}</span>
                    <span className={styles.label}>топиков</span>
                  </div>
                )}
              </div>
              <div className={styles.progressBar}>
                <div 
                  className={styles.progressFill}
                  style={{ width: `${category.percentage}%` }}
                />
              </div>
              <div className={styles.cardAction}>
                <span>Изучить →</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {viewMode === 'category-detail' && categoryDetail && (
        <div className={styles.categoryDetail}>
          {categoryDetailLoading && <div className={styles.loading}>Загрузка...</div>}
          
          {/* Кластеры/Топики */}
          {categoryDetail.clusters.length > 0 && (
            <div className={styles.clusters}>
              <h2>Топики в категории</h2>
              <div className={styles.clustersList}>
                {categoryDetail.clusters.map((cluster) => (
                <div 
                  key={cluster.id} 
                  className={styles.clusterCard}
                  onClick={() => handleClusterSelect(cluster.id)}
                >
                  <div className={styles.clusterHeader}>
                    <div className={styles.clusterName}>{cluster.name}</div>
                    <span className={styles.questionsCount}>
                      {cluster.questions_count} вопросов
                    </span>
                  </div>
                  
                  <div className={styles.keywords}>
                    {cluster.keywords.slice(0, 5).map((keyword, idx) => (
                      <span key={idx} className={styles.keyword}>{keyword}</span>
                    ))}
                  </div>
                  
                  {cluster.example_question && (
                    <div className={styles.exampleQuestion}>
                      "{cluster.example_question}"
                    </div>
                  )}
                  
                  <div className={styles.cardAction}>
                    <span>Все вопросы →</span>
                  </div>
                </div>
              ))}
              </div>
            </div>
          )}

          {/* Вопросы из категории */}
          <div className={styles.sampleQuestions}>
            <h3>Вопросы из категории ({categoryQuestions.length} из {categoryDetail.category.questions_count})</h3>
            {categoryQuestionsLoading && categoryQuestions.length === 0 && (
              <div className={styles.loading}>Загрузка вопросов...</div>
            )}
            <div className={styles.questionsList}>
              {categoryQuestions.map((question, index) => (
                <div key={question.id} className={styles.questionItem}>
                  <div className={styles.questionNumber}>#{index + 1}</div>
                  <div className={styles.questionContent}>
                    <div className={styles.questionText}>{question.question_text}</div>
                    <div className={styles.questionMeta}>
                      {question.company && <span className={styles.company}>{question.company}</span>}
                      {question.topic_name && <span className={styles.topic}>{question.topic_name}</span>}
                    </div>
                  </div>
                </div>
              ))}
            </div>
            {isFetchingNextCategoryPage && (
              <div className={styles.loading}>Загрузка дополнительных вопросов...</div>
            )}
          </div>
        </div>
      )}

      {viewMode === 'cluster-questions' && currentCluster && (
        <div className={styles.clusterQuestions}>
          {clusterQuestionsLoading && <div className={styles.loading}>Загрузка вопросов...</div>}
          
          <div className={styles.clusterInfo}>
            <div className={styles.keywords}>
              {currentCluster.keywords.map((keyword, idx) => (
                <span key={idx} className={styles.keyword}>{keyword}</span>
              ))}
            </div>
          </div>

          <div className={styles.questionsList}>
            {clusterQuestions?.map((question, index) => (
              <div key={question.id} className={styles.questionItem}>
                <div className={styles.questionNumber}>#{(clusterQuestionsPage - 1) * 50 + index + 1}</div>
                <div className={styles.questionContent}>
                  <div className={styles.questionText}>{question.question_text}</div>
                  <div className={styles.questionMeta}>
                    {question.company && <span className={styles.company}>{question.company}</span>}
                    {question.topic_name && <span className={styles.topic}>{question.topic_name}</span>}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Пагинация */}
          {currentCluster.questions_count > 50 && (
            <div className={styles.pagination}>
              <button 
                onClick={() => setClusterQuestionsPage(prev => Math.max(1, prev - 1))}
                disabled={clusterQuestionsPage === 1}
                className={styles.paginationButton}
              >
                ← Предыдущая
              </button>
              <span className={styles.pageInfo}>
                Страница {clusterQuestionsPage} из {Math.ceil(currentCluster.questions_count / 50)}
              </span>
              <button 
                onClick={() => setClusterQuestionsPage(prev => prev + 1)}
                disabled={clusterQuestionsPage * 50 >= currentCluster.questions_count}
                className={styles.paginationButton}
              >
                Следующая →
              </button>
            </div>
          )}
        </div>
      )}

      {viewMode === 'search' && searchQuery && (
        <div className={styles.searchResults}>
          {searchLoading && <div className={styles.loading}>Поиск...</div>}
          
          {searchResults && searchResults.length > 0 && (
            <>
              <div className={styles.searchStats}>
                <span>Найдено: <strong>{searchResults.length}</strong> вопросов</span>
              </div>
              
              <div className={styles.questionsList}>
                {searchResults.map((question, index) => (
                  <div key={question.id} className={styles.questionItem}>
                    <div className={styles.questionNumber}>#{index + 1}</div>
                    <div className={styles.questionContent}>
                      <div className={styles.questionText}>{question.question_text}</div>
                      <div className={styles.questionMeta}>
                        {question.company && <span className={styles.company}>{question.company}</span>}
                        {question.topic_name && <span className={styles.topic}>{question.topic_name}</span>}
                        {question.category_id && <span className={styles.category}>{question.category_id}</span>}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}

          {searchResults && searchResults.length === 0 && !searchLoading && (
            <div className={styles.noResults}>
              <span>По запросу "{searchQuery}" ничего не найдено</span>
            </div>
          )}
        </div>
      )}

      {viewMode === 'companies' && selectedCompany && (
        <div className={styles.companyQuestions}>
          {companyQuestionsLoading && <div className={styles.loading}>Загрузка вопросов...</div>}
          
          {companyQuestions && companyQuestions.length > 0 && (
            <>
              <div className={styles.companyStats}>
                <span>Найдено: <strong>{companyQuestions.length}</strong> вопросов от {selectedCompany}</span>
              </div>
              
              <div className={styles.questionsList}>
                {companyQuestions.map((question, index) => (
                  <div key={question.id} className={styles.questionItem}>
                    <div className={styles.questionNumber}>#{index + 1}</div>
                    <div className={styles.questionContent}>
                      <div className={styles.questionText}>{question.question_text}</div>
                      <div className={styles.questionMeta}>
                        {question.topic_name && <span className={styles.topic}>{question.topic_name}</span>}
                        {question.category_id && <span className={styles.category}>{question.category_id}</span>}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}

          {/* Loading indicator for infinite scroll */}
          {isFetchingNextPage && (
            <div className={styles.loading}>Загрузка дополнительных вопросов...</div>
          )}

          {companyQuestions && companyQuestions.length === 0 && !companyQuestionsLoading && (
            <div className={styles.noResults}>
              <span>У компании {selectedCompany} нет вопросов в базе</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
};