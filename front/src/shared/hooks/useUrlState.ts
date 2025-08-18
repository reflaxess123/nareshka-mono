import { useCallback, useMemo } from 'react';
import { useSearchParams } from 'react-router-dom';

export interface FilterState {
  categories: string[];
  clusters: number[];
  companies: string[];
  search: string;
}

interface UseUrlStateReturn {
  filters: FilterState;
  currentPage: number;
  updateFilters: (filters: FilterState) => void;
  updatePage: (page: number) => void;
  resetFilters: () => void;
}

const DEFAULT_FILTERS: FilterState = {
  categories: [],
  clusters: [],
  companies: [],
  search: '',
};

// Парсинг URL параметров в FilterState
const parseFiltersFromUrl = (params: URLSearchParams): FilterState => {
  return {
    search: params.get('q') || '',
    categories: params.get('cat')?.split(',').filter(Boolean) || [],
    clusters: params.get('cluster')?.split(',').map(Number).filter(num => !isNaN(num)) || [],
    companies: params.get('comp')?.split(',').filter(Boolean) || [],
  };
};

// Сериализация FilterState в URL параметры
const serializeFiltersToUrl = (filters: FilterState, page: number): URLSearchParams => {
  const params = new URLSearchParams();
  
  // Поисковый запрос
  if (filters.search.trim()) {
    params.set('q', filters.search.trim());
  }
  
  // Категории
  if (filters.categories.length > 0) {
    params.set('cat', filters.categories.join(','));
  }
  
  // Кластеры
  if (filters.clusters.length > 0) {
    params.set('cluster', filters.clusters.join(','));
  }
  
  // Компании
  if (filters.companies.length > 0) {
    params.set('comp', filters.companies.join(','));
  }
  
  // Страница (только если не первая)
  if (page > 1) {
    params.set('page', page.toString());
  }
  
  return params;
};


export const useUrlState = (): UseUrlStateReturn => {
  const [searchParams, setSearchParams] = useSearchParams();

  // Парсинг текущих фильтров из URL
  const filters = useMemo(() => parseFiltersFromUrl(searchParams), [searchParams]);

  // Парсинг текущей страницы из URL
  const currentPage = useMemo(() => {
    const page = parseInt(searchParams.get('page') || '1');
    return isNaN(page) || page < 1 ? 1 : page;
  }, [searchParams]);

  // Обновление фильтров (автоматически сбрасывает страницу на 1)
  const updateFilters = useCallback((newFilters: FilterState) => {
    const params = serializeFiltersToUrl(newFilters, 1);
    setSearchParams(params);
  }, [setSearchParams]);

  // Обновление страницы (сохраняет текущие фильтры)
  const updatePage = useCallback((page: number) => {
    const params = serializeFiltersToUrl(filters, page);
    setSearchParams(params);
  }, [filters, setSearchParams]);

  // Сброс всех фильтров и возврат на первую страницу
  const resetFilters = useCallback(() => {
    const params = serializeFiltersToUrl(DEFAULT_FILTERS, 1);
    setSearchParams(params);
  }, [setSearchParams]);

  return {
    filters,
    currentPage,
    updateFilters,
    updatePage,
    resetFilters,
  };
};