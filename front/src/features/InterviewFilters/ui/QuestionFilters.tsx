import React, { useState, useEffect, useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import { ChevronDown, ChevronUp, X, Search } from 'lucide-react';
import styles from './QuestionFilters.module.scss';

// Интерфейсы
export interface FilterState {
  categories: string[];
  clusters: number[];
  companies: string[];
  search: string;
}

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

interface Company {
  name: string;
  count: number;
}

interface QuestionFiltersProps {
  filters: FilterState;
  onFiltersChange: (filters: FilterState) => void;
  className?: string;
}

export const QuestionFilters: React.FC<QuestionFiltersProps> = ({
  filters,
  onFiltersChange,
  className,
}) => {
  const [expandedSections, setExpandedSections] = useState({
    categories: true,
    clusters: true,
    companies: true,
  });

  const [clusterSearch, setClusterSearch] = useState('');
  const [companySearch, setCompanySearch] = useState('');
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const checkScreenSize = () => {
      setIsMobile(window.innerWidth <= 768);
    };

    checkScreenSize();
    window.addEventListener('resize', checkScreenSize);
    return () => window.removeEventListener('resize', checkScreenSize);
  }, []);

  useEffect(() => {
    if (isMobile) {
      setExpandedSections((prev) => ({
        ...prev,
        clusters: false,
        companies: false,
      }));
    } else {
      setExpandedSections({
        categories: true,
        clusters: true,
        companies: true,
      });
    }
  }, [isMobile]);

  // Загрузка категорий
  const { data: categories } = useQuery<Category[]>({
    queryKey: ['interview-categories'],
    queryFn: async () => {
      const response = await fetch('/api/v2/interview-categories/');
      if (!response.ok) throw new Error('Failed to fetch categories');
      return response.json();
    }
  });

  // Загрузка кластеров
  const { data: clusters } = useQuery<Cluster[]>({
    queryKey: ['interview-clusters', filters.categories, clusterSearch],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (filters.categories.length > 0) {
        filters.categories.forEach(catId => params.append('category_id', catId));
      }
      if (clusterSearch.length >= 2) {
        params.append('search', clusterSearch);
      }
      params.append('limit', '200');
      
      const response = await fetch(`/api/v2/interview-categories/clusters/all?${params}`);
      if (!response.ok) throw new Error('Failed to fetch clusters');
      return response.json();
    }
  });

  // Загрузка компаний
  const { data: companies } = useQuery<Company[]>({
    queryKey: ['interview-companies'],
    queryFn: async () => {
      const response = await fetch('/api/v2/interview-categories/companies/top?limit=50');
      if (!response.ok) throw new Error('Failed to fetch companies');
      return response.json();
    }
  });

  // Обработчики
  const handleCategoryToggle = useCallback((categoryId: string, checked: boolean) => {
    const newCategories = checked
      ? [...filters.categories, categoryId]
      : filters.categories.filter(id => id !== categoryId);
    
    onFiltersChange({
      ...filters,
      categories: newCategories,
      clusters: [], // Сброс кластеров при изменении категорий
    });
  }, [filters, onFiltersChange]);

  const handleClusterToggle = useCallback((clusterId: number, checked: boolean) => {
    const newClusters = checked
      ? [...filters.clusters, clusterId]
      : filters.clusters.filter(id => id !== clusterId);
    
    onFiltersChange({
      ...filters,
      clusters: newClusters,
    });
  }, [filters, onFiltersChange]);

  const handleCompanyToggle = useCallback((companyName: string, checked: boolean) => {
    const newCompanies = checked
      ? [...filters.companies, companyName]
      : filters.companies.filter(name => name !== companyName);
    
    onFiltersChange({
      ...filters,
      companies: newCompanies,
    });
  }, [filters, onFiltersChange]);

  const handleReset = useCallback(() => {
    onFiltersChange({
      categories: [],
      clusters: [],
      companies: [],
      search: '',
    });
    setClusterSearch('');
    setCompanySearch('');
  }, [onFiltersChange]);

  const toggleSection = (section: keyof typeof expandedSections) => {
    setExpandedSections((prev) => ({
      ...prev,
      [section]: !prev[section],
    }));
  };

  const hasActiveFilters = () => {
    return !!(
      filters.categories.length ||
      filters.clusters.length ||
      filters.companies.length ||
      filters.search
    );
  };

  // Фильтрация кластеров и компаний для поиска
  const filteredClusters = clusters?.filter(cluster =>
    clusterSearch.length < 2 || 
    cluster.name.toLowerCase().includes(clusterSearch.toLowerCase())
  ) || [];

  const filteredCompanies = companies?.filter(company =>
    companySearch.length < 2 || 
    company.name.toLowerCase().includes(companySearch.toLowerCase())
  ) || [];

  return (
    <div className={`${styles.questionFilters} ${className || ''}`}>
      {hasActiveFilters() && (
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

      {/* Категории */}
      <div className={styles.filterSection}>
        <button
          className={styles.sectionHeader}
          onClick={() => toggleSection('categories')}
        >
          <span>📁 Категории</span>
          {expandedSections.categories ? (
            <ChevronUp size={16} />
          ) : (
            <ChevronDown size={16} />
          )}
        </button>

        {expandedSections.categories && (
          <div className={styles.sectionContent}>
            <div className={styles.checkboxGroup}>
              {categories?.map((category) => {
                const isChecked = filters.categories.includes(category.id);
                return (
                  <label key={category.id} className={styles.checkboxLabel}>
                    <input
                      type="checkbox"
                      checked={isChecked}
                      onChange={(e) => handleCategoryToggle(category.id, e.target.checked)}
                    />
                    <span>
                      {category.name} ({category.questions_count})
                    </span>
                  </label>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* Кластеры */}
      <div className={styles.filterSection}>
        <button
          className={styles.sectionHeader}
          onClick={() => toggleSection('clusters')}
        >
          <span>🏷️ Кластеры</span>
          {expandedSections.clusters ? (
            <ChevronUp size={16} />
          ) : (
            <ChevronDown size={16} />
          )}
        </button>

        {expandedSections.clusters && (
          <div className={styles.sectionContent}>
            <div className={styles.searchInputWrapper}>
              <Search size={16} className={styles.searchIcon} />
              <input
                type="text"
                placeholder="Поиск кластеров..."
                value={clusterSearch}
                onChange={(e) => setClusterSearch(e.target.value)}
                className={styles.searchInput}
              />
            </div>
            
            <div className={styles.checkboxGroup}>
              {filteredClusters.map((cluster) => {
                const isChecked = filters.clusters.includes(cluster.id);
                return (
                  <label key={cluster.id} className={styles.checkboxLabel}>
                    <input
                      type="checkbox"
                      checked={isChecked}
                      onChange={(e) => handleClusterToggle(cluster.id, e.target.checked)}
                    />
                    <span>
                      {cluster.name} ({cluster.questions_count})
                    </span>
                  </label>
                );
              })}
              {filteredClusters.length === 0 && clusterSearch.length >= 2 && (
                <div className={styles.noResults}>
                  Кластеры не найдены
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Компании */}
      <div className={styles.filterSection}>
        <button
          className={styles.sectionHeader}
          onClick={() => toggleSection('companies')}
        >
          <span>🏢 Компании</span>
          {expandedSections.companies ? (
            <ChevronUp size={16} />
          ) : (
            <ChevronDown size={16} />
          )}
        </button>

        {expandedSections.companies && (
          <div className={styles.sectionContent}>
            <div className={styles.searchInputWrapper}>
              <Search size={16} className={styles.searchIcon} />
              <input
                type="text"
                placeholder="Поиск компаний..."
                value={companySearch}
                onChange={(e) => setCompanySearch(e.target.value)}
                className={styles.searchInput}
              />
            </div>
            
            <div className={styles.checkboxGroup}>
              {filteredCompanies.map((company) => {
                const isChecked = filters.companies.includes(company.name);
                return (
                  <label key={company.name} className={styles.checkboxLabel}>
                    <input
                      type="checkbox"
                      checked={isChecked}
                      onChange={(e) => handleCompanyToggle(company.name, e.target.checked)}
                    />
                    <span>
                      {company.name} ({company.count})
                    </span>
                  </label>
                );
              })}
              {filteredCompanies.length === 0 && companySearch.length >= 2 && (
                <div className={styles.noResults}>
                  Компании не найдены
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};