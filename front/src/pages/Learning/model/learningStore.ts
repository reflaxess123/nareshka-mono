/**
 * Zustand store для управления состоянием страницы Learning
 */

import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';
import type { ContentType, LearningFilters, UniversalContentItem } from '@/shared/types/learning';

interface LearningState {
  // Основное состояние
  activeTab: ContentType;
  filters: LearningFilters;
  searchHistory: string[];
  
  // Данные
  items: UniversalContentItem[];
  isLoading: boolean;
  error: string | null;
  
  // Пагинация
  page: number;
  limit: number;
  total: number;
  hasNextPage: boolean;
  
  // Настройки отображения
  viewMode: 'cards' | 'list' | 'compact';
  sortBy: string;
  sortOrder: 'asc' | 'desc';
  
  // Actions
  setActiveTab: (tab: ContentType) => void;
  updateFilters: (filters: Partial<LearningFilters>) => void;
  resetFilters: () => void;
  addToSearchHistory: (query: string) => void;
  clearSearchHistory: () => void;
  
  // Data actions
  setItems: (items: UniversalContentItem[]) => void;
  appendItems: (items: UniversalContentItem[]) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  
  // Pagination actions
  setPage: (page: number) => void;
  nextPage: () => void;
  setPaginationData: (data: { total: number; hasNextPage: boolean }) => void;
  
  // View actions
  setViewMode: (mode: 'cards' | 'list' | 'compact') => void;
  setSorting: (sortBy: string, sortOrder?: 'asc' | 'desc') => void;
  
  // Utility
  reset: () => void;
}

const initialFilters: LearningFilters = {
  contentTypes: ['interviews'],
  search: undefined,
  companies: undefined,
  categories: undefined,
  clusters: undefined,
  subCategories: undefined,
  difficulty: undefined,
  hasAudio: undefined,
  onlyCompleted: undefined,
  onlyUnstudied: undefined,
};

export const useLearningStore = create<LearningState>()(
  devtools(
    persist(
      (set, get) => ({
        // Initial state
        activeTab: 'interviews',
        filters: initialFilters,
        searchHistory: [],
        items: [],
        isLoading: false,
        error: null,
        page: 1,
        limit: 20,
        total: 0,
        hasNextPage: false,
        viewMode: 'list',
        sortBy: 'created_at',
        sortOrder: 'desc',

        // Tab actions
        setActiveTab: (tab) => {
          set((state) => ({
            activeTab: tab,
            filters: {
              ...initialFilters,
              contentTypes: [tab],
              // Сохраняем поиск при переключении табов
              search: state.filters.search,
            },
            items: [], // Очищаем items при смене таба
            page: 1,
            total: 0,
            hasNextPage: false,
            error: null,
          }));
        },

        // Filter actions
        updateFilters: (newFilters) => {
          const currentFilters = get().filters;
          set({
            filters: { ...currentFilters, ...newFilters },
            page: 1, // Сбрасываем на первую страницу при изменении фильтров
            items: [], // Очищаем items при изменении фильтров
          });
        },

        resetFilters: () => {
          const activeTab = get().activeTab;
          set({
            filters: {
              ...initialFilters,
              contentTypes: [activeTab],
            },
            page: 1,
            items: [],
            total: 0,
            hasNextPage: false,
          });
        },

        // Search history
        addToSearchHistory: (query) => {
          if (!query.trim()) return;
          
          set((state) => {
            const history = state.searchHistory.filter(q => q !== query);
            return {
              searchHistory: [query, ...history].slice(0, 10), // Храним максимум 10 запросов
            };
          });
        },

        clearSearchHistory: () => {
          set({ searchHistory: [] });
        },

        // Data actions
        setItems: (items) => {
          set({ items });
        },

        appendItems: (newItems) => {
          set((state) => ({
            items: [...state.items, ...newItems],
          }));
        },

        setLoading: (loading) => {
          set({ isLoading: loading });
        },

        setError: (error) => {
          set({ error });
        },

        // Pagination
        setPage: (page) => {
          set({ page });
        },

        nextPage: () => {
          set((state) => ({
            page: state.page + 1,
          }));
        },

        setPaginationData: ({ total, hasNextPage }) => {
          set({ total, hasNextPage });
        },

        // View settings
        setViewMode: (viewMode) => {
          set({ viewMode });
        },

        setSorting: (sortBy, sortOrder) => {
          set((state) => ({
            sortBy,
            sortOrder: sortOrder || state.sortOrder,
            page: 1, // Сбрасываем на первую страницу при изменении сортировки
            items: [],
          }));
        },

        // Reset entire store
        reset: () => {
          set({
            activeTab: 'interviews',
            filters: initialFilters,
            searchHistory: [],
            items: [],
            isLoading: false,
            error: null,
            page: 1,
            limit: 20,
            total: 0,
            hasNextPage: false,
            viewMode: 'list',
            sortBy: 'created_at',
            sortOrder: 'desc',
          });
        },
      }),
      {
        name: 'learning-store',
        partialize: (state) => ({
          // Сохраняем только пользовательские настройки
          viewMode: state.viewMode,
          searchHistory: state.searchHistory,
          sortBy: state.sortBy,
          sortOrder: state.sortOrder,
          limit: state.limit,
        }),
      }
    ),
    {
      name: 'LearningStore',
    }
  )
);

// Селекторы для оптимизации ререндеров
export const useLearningFilters = () => useLearningStore((state) => state.filters);
export const useLearningItems = () => useLearningStore((state) => state.items);
export const useLearningLoading = () => useLearningStore((state) => state.isLoading);
export const useLearningPagination = () => 
  useLearningStore((state) => ({
    page: state.page,
    limit: state.limit,
    total: state.total,
    hasNextPage: state.hasNextPage,
  }));

export default useLearningStore;