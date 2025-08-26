/**
 * Типы для API ответов - правильная типизация без any/unknown
 */

// Интерфейс для интервью  
export interface InterviewResponse {
  id: string;
  company_name?: string;
  company?: string;
  full_content?: string;
  content?: string;
  excerpt?: string;
  interview_date?: string;
  has_audio?: boolean;
  position_type?: string;
  audio_url?: string;
  video_url?: string;
  has_audio_recording?: boolean;
  created_at?: string;
  updated_at?: string;
  technologies?: string[];
  difficulty?: string;
  duration?: string;
  metadata?: {
    interviewInfo?: {
      formattedName: string;
      id: string;
    };
  };
}

// Интерфейс для блока контента
export interface ContentBlockResponse {
  id: string;
  title: string;
  content: string;
  textContent?: string;
  mainCategory?: string;
  subCategory?: string;
  category?: string;
  file?: string;
  blockLevel?: string | number;
  orderInFile?: number;
  codeLanguage?: string;
  createdAt?: string;
  updatedAt?: string;
  codeContent?: string;
  pathTitles?: string[];
  companies?: string[];
  metadata?: {
    webdavPath?: string;
    technologies?: string[];
  };
}

// Интерфейс для теоретической карточки
export interface TheoryCardResponse {
  id: string;
  title: string;
  content: string;
  category?: string;
  tags?: string[];
  studyCount?: number;
  orderIndex?: number;
  questionBlock?: string;
  answerBlock?: string;
  metadata?: Record<string, string | number | boolean>;
}

// Интерфейс для вопроса
export interface QuestionResponse {
  id: string;
  question_text: string;
  company?: string;
  topic_name?: string;
  cluster_id?: number;
  category_id?: string;
  interview_id?: string;
}

// API ответы
export interface InterviewsApiResponse {
  interviews: InterviewResponse[];
  total: number;
  has_next: boolean;
  page: number;
}

export interface QuestionsApiResponse {
  questions: QuestionResponse[];
  total: number;
  has_next: boolean;
  page: number;
}

export interface ContentBlocksApiResponse {
  content_blocks: ContentBlockResponse[];
  total: number;
  has_next: boolean;
  page: number;
}

export interface TheoryCardsApiResponse {
  theory_cards: TheoryCardResponse[];
  total: number;
  has_next: boolean;
  page: number;
}