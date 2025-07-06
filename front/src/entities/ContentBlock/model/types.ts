export interface ContentFile {
  id: string;
  webdavPath: string;
  mainCategory: string;
  subCategory: string;
  lastFileHash?: string;
  createdAt: string;
  updatedAt: string;
}

export interface ContentBlock {
  id: string;
  fileId?: string | null;
  pathTitles?: string[] | null; // Иерархия заголовков ["Level 1", "Level 2", "Block Title"]
  title: string;
  blockLevel?: number | null; // Уровень заголовка (1-4)
  orderInFile?: number | null;
  textContent?: string | null;
  codeContent?: string | null;
  codeLanguage?: string | null;
  isCodeFoldable?: boolean | null;
  codeFoldTitle?: string | null;
  extractedUrls?: string[] | null;
  companies?: string[] | null; // Список компаний где встречалась задача
  rawBlockContentHash?: string | null;
  createdAt: string;
  updatedAt: string;
  currentUserSolvedCount: number; // Количество решений текущего пользователя
  file?: ContentFile | null;
  // Дополнительные поля для теоретических квизов
  type?: 'content_block' | 'theory_quiz';
  category?: string;
  subCategory?: string;
  questionBlock?: string;
  answerBlock?: string;
}

export interface ContentBlocksResponse {
  data: ContentBlock[];
  pagination: {
    page: number;
    limit: number;
    totalItems: number;
    totalPages: number;
  };
}

export interface ContentCategory {
  name: string; // Основная категория
  subCategories: string[]; // Список подкатегорий
}

export interface ContentProgressUpdate {
  action: 'increment' | 'decrement';
}

export interface ContentProgressResponse {
  userId: number;
  blockId: string;
  solvedCount: number;
}

export interface ContentBlocksFilters {
  page?: number;
  limit?: number;
  webdavPath?: string;
  mainCategories?: string[]; // Множественный выбор основных категорий
  subCategories?: string[]; // Множественный выбор подкатегорий
  filePathId?: string;
  q?: string;
  sortBy?:
    | 'orderInFile'
    | 'blockLevel'
    | 'createdAt'
    | 'updatedAt'
    | 'file.webdavPath';
  sortOrder?: 'asc' | 'desc';
  onlyUnsolved?: boolean; // Показывать только нерешенные блоки
  companies?: string[]; // Массив выбранных компаний
  difficulties?: ('easy' | 'medium' | 'hard')[]; // Фильтр по сложности
  importance?: ('low' | 'medium' | 'high')[]; // Фильтр по важности
  progress?: ('completed' | 'not_completed')[]; // Фильтр по прогрессу
}

export interface ContentBlockState {
  blocks: ContentBlock[];
  categories: ContentCategory[];
  currentBlock: ContentBlock | null;
  filters: ContentBlocksFilters;
  pagination: {
    page: number;
    limit: number;
    totalItems: number;
    totalPages: number;
  };
  isLoading: boolean;
  error: string | null;
}
