/**
 * Общие типы для унифицированной системы обучения
 */

import type { InterviewResponse, ContentBlockResponse, TheoryCardResponse, QuestionResponse } from './api-responses';

export type ContentType = 'interviews' | 'questions' | 'practice' | 'theory';

export interface UniversalContentItem {
  id: string;
  type: ContentType;
  title: string;
  description?: string;
  
  // Общие поля
  company?: string;           // для interviews и questions
  category?: string;          // для всех типов
  subCategory?: string;       // для practice/theory
  cluster?: string;           // для questions
  tags?: string[];
  difficulty?: 'easy' | 'medium' | 'hard';
  
  // Статусные поля
  hasAudio?: boolean;         // для interviews
  isCompleted?: boolean;      // для practice/theory
  studyCount?: number;        // для theory (количество изучений)
  solvedCount?: number;       // для practice (количество решений)
  codeLanguage?: string;      // для practice
  
  // Временные метки
  createdAt: string;
  updatedAt?: string;
  
  // Специфичные данные в metadata
  metadata: {
    interviewInfo?: {
      formattedName: string;
      id: string;
    };
    webdavPath?: string;
    technologies?: string[];
    duration?: string;
    cardType?: string;
    questionBlock?: string;
    answerBlock?: string;
    fullContent?: string;
    textContent?: string;
    interviewId?: string;
    originalData?: InterviewResponse | ContentBlockResponse | TheoryCardResponse | QuestionResponse;
  };
}

export interface LearningFilters {
  contentTypes?: ContentType[];
  search?: string;
  companies?: string[];
  categories?: string[];
  clusters?: number[];
  subCategories?: string[];
  difficulty?: ('easy' | 'medium' | 'hard')[];
  has_audio?: boolean;
  hasAudio?: boolean; // deprecated, use has_audio
  onlyCompleted?: boolean;
  onlyUnstudied?: boolean;
}

export interface LearningStats {
  totalItems: number;
  completedItems: number;
  itemsByType: Record<ContentType, number>;
  completionByType: Record<ContentType, number>;
}

export interface ContentTypeConfig {
  type: ContentType;
  label: string;
  icon: string;
  description: string;
  color: string;
  supportsAudio: boolean;
  supportsCompletion: boolean;
  supportsCompany: boolean;
  supportsCluster: boolean;
  defaultSort: string;
}

// Конфигурация типов контента
export const CONTENT_TYPE_CONFIG: Record<ContentType, ContentTypeConfig> = {
  interviews: {
    type: 'interviews',
    label: 'Интервью',
    icon: '🎤',
    description: 'Реальные интервью из IT компаний',
    color: '#3B82F6',
    supportsAudio: true,
    supportsCompletion: false,
    supportsCompany: true,
    supportsCluster: false,
    defaultSort: 'interview_date'
  },
  questions: {
    type: 'questions',
    label: 'Банк вопросов',
    icon: '❓',
    description: '8,560 вопросов из 380+ компаний',
    color: '#10B981',
    supportsAudio: false,
    supportsCompletion: false,
    supportsCompany: true,
    supportsCluster: true,
    defaultSort: 'created_at'
  },
  practice: {
    type: 'practice',
    label: 'Практика',
    icon: '💪',
    description: 'Задачи и упражнения для тренировки',
    color: '#F59E0B',
    supportsAudio: false,
    supportsCompletion: true,
    supportsCompany: false,
    supportsCluster: false,
    defaultSort: 'orderInFile'
  },
  theory: {
    type: 'theory',
    label: 'Теория',
    icon: '📚',
    description: 'Теоретические материалы и карточки',
    color: '#8B5CF6',
    supportsAudio: false,
    supportsCompletion: true,
    supportsCompany: false,
    supportsCluster: false,
    defaultSort: 'orderIndex'
  }
};

// Типы для API ответов
export interface LearningSearchResponse {
  items: UniversalContentItem[];
  total: number;
  hasNext: boolean;
  page: number;
  limit: number;
  stats?: LearningStats;
}

export interface LearningSearchRequest {
  contentTypes: ContentType[];
  search?: string;
  companies?: string[];
  categories?: string[];
  clusters?: number[];
  subCategories?: string[];
  difficulty?: ('easy' | 'medium' | 'hard')[];
  has_audio?: boolean;
  hasAudio?: boolean; // deprecated, use has_audio
  onlyCompleted?: boolean;
  onlyUnstudied?: boolean;
  page?: number;
  limit?: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
  userId?: string;
}