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
  fileId: string;
  pathTitles: string[]; // Иерархия заголовков ["Level 1", "Level 2", "Block Title"]
  blockTitle: string;
  blockLevel: number; // Уровень заголовка (1-4)
  orderInFile: number;
  textContent?: string;
  codeContent?: string;
  codeLanguage?: string;
  isCodeFoldable: boolean;
  codeFoldTitle?: string;
  extractedUrls: string[];
  rawBlockContentHash?: string;
  createdAt: string;
  updatedAt: string;
  currentUserSolvedCount: number; // Количество решений текущего пользователя
  file: ContentFile;
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
  mainCategory?: string;
  subCategory?: string;
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
