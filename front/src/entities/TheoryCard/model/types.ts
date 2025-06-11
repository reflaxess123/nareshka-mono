// Интерфейс для прогресса изучения карточки
export interface CardProgress {
  solvedCount: number;
  easeFactor: number;
  interval: number;
  dueDate: string | null;
  reviewCount: number;
  lapseCount: number;
  cardState: string;
  learningStep: number;
  lastReviewDate: string | null;
}

// Основная сущность карточки
export interface TheoryCard {
  id: string;
  ankiGuid: string;
  cardType: string;
  deck: string;
  category: string;
  subCategory: string | null;
  questionBlock: string;
  answerBlock: string;
  tags: string[];
  orderIndex: number;
  createdAt: string;
  updatedAt: string;
  progress: CardProgress;
}

// Информация о пагинации
export interface Pagination {
  page: number;
  limit: number;
  totalItems: number;
  totalPages: number;
}

// Ответ API для получения карточек
export interface TheoryCardsResponse {
  cards: TheoryCard[];
  pagination: Pagination;
}

// Параметры запроса для фильтрации и поиска
export interface TheoryCardsQueryParams {
  page?: number;
  limit?: number;
  category?: string;
  subCategory?: string;
  deck?: string;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
  q?: string; // полнотекстовый поиск
  onlyUnstudied?: boolean;
}

// Тип для сортировки (можете расширить по необходимости)
export type SortField = 'orderIndex' | 'createdAt' | 'updatedAt';
export type SortOrder = 'asc' | 'desc';

// Новые типы для категорий
export interface SubCategory {
  name: string;
  cardCount: number;
}

export interface Category {
  name: string;
  subCategories: SubCategory[];
  totalCards: number;
}

// Тип для фильтров
export interface TheoryFilters {
  category?: string;
  subCategory?: string;
  onlyUnstudied?: boolean;
  sortBy?: SortField;
  sortOrder?: SortOrder;
  searchQuery?: string;
}

// Тип для обновления прогресса
export interface UpdateProgressRequest {
  action: 'increment' | 'decrement';
}

export interface UpdateProgressResponse {
  userId: number;
  cardId: string;
  solvedCount: number;
}

// Тип для иконок категорий
export interface CategoryIcon {
  category: string;
  icon: string;
  color: string;
}

// Константы цветов прогресса
export const PROGRESS_COLORS = {
  NOT_STUDIED: 'var(--color-error)',
  BEGINNER: 'var(--color-warning)',
  INTERMEDIATE: 'var(--color-info)',
  STUDIED: 'var(--color-success)',
} as const;

// Предустановленные иконки для категорий
export const CATEGORY_ICONS: Record<string, CategoryIcon> = {
  'JS ТЕОРИЯ': {
    category: 'JS ТЕОРИЯ',
    icon: '⚡',
    color: '#f7df1e',
  },
  REACT: {
    category: 'REACT',
    icon: '⚛️',
    color: '#61dafb',
  },
  'NODE.JS': {
    category: 'NODE.JS',
    icon: '🟢',
    color: '#339933',
  },
  CSS: {
    category: 'CSS',
    icon: '🎨',
    color: '#1572b6',
  },
  HTML: {
    category: 'HTML',
    icon: '📄',
    color: '#e34f26',
  },
  TYPESCRIPT: {
    category: 'TYPESCRIPT',
    icon: '🔷',
    color: '#3178c6',
  },
  DEFAULT: {
    category: 'DEFAULT',
    icon: '📚',
    color: 'var(--text-muted)',
  },
};
