import { apiInstance } from './base';

export interface TaskItem {
  id: string;
  type: 'content_block' | 'theory_quiz';
  title: string;
  description?: string;
  category: string;
  subCategory?: string;

  fileId?: string;
  pathTitles?: string[];
  blockLevel?: number;
  orderInFile?: number;
  textContent?: string;
  codeContent?: string;
  codeLanguage?: string;
  isCodeFoldable?: boolean;
  codeFoldTitle?: string;
  extractedUrls?: string[];

  questionBlock?: string;
  answerBlock?: string;
  tags?: string[];
  orderIndex?: number;

  currentUserSolvedCount: number;

  createdAt: string;
  updatedAt: string;
}

export interface TaskCategory {
  name: string;
  subCategories: Array<{
    name: string;
    itemCount: number;
    type: 'content_block' | 'theory_quiz';
  }>;
  totalItems: number;
}

export interface TaskItemsFilters {
  page?: number;
  limit?: number;
  category?: string;
  subCategory?: string;
  q?: string;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
  itemType?: 'content_block' | 'theory_quiz' | 'all';
}

export interface TaskItemsResponse {
  items: TaskItem[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
    hasNext: boolean;
    hasPrev: boolean;
  };
}

class TasksAPI {
  async getTaskItems(
    filters: TaskItemsFilters = {}
  ): Promise<TaskItemsResponse> {
    const params = new URLSearchParams();

    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString());
      }
    });

    const response = await apiInstance.get<TaskItemsResponse>(
      `/tasks/items?${params.toString()}`
    );

    return response.data;
  }

  async getTaskCategories(): Promise<TaskCategory[]> {
    const response = await apiInstance.get<TaskCategory[]>('/tasks/categories');
    return response.data;
  }

  async searchTasks(
    query: string,
    filters: Omit<TaskItemsFilters, 'q'> = {}
  ): Promise<TaskItemsResponse> {
    return this.getTaskItems({ ...filters, q: query });
  }

  async getTasksByCategory(
    category: string,
    subCategory?: string,
    filters: Omit<TaskItemsFilters, 'category' | 'subCategory'> = {}
  ): Promise<TaskItemsResponse> {
    return this.getTaskItems({
      ...filters,
      category,
      ...(subCategory && { subCategory }),
    });
  }

  async getContentBlocks(
    filters: Omit<TaskItemsFilters, 'itemType'> = {}
  ): Promise<TaskItemsResponse> {
    return this.getTaskItems({ ...filters, itemType: 'content_block' });
  }

  async getQuizCards(
    filters: Omit<TaskItemsFilters, 'itemType'> = {}
  ): Promise<TaskItemsResponse> {
    return this.getTaskItems({ ...filters, itemType: 'theory_quiz' });
  }

  async getMoreTasks(
    currentPage: number,
    filters: TaskItemsFilters = {}
  ): Promise<TaskItemsResponse> {
    return this.getTaskItems({ ...filters, page: currentPage + 1 });
  }
}

export const tasksApi = new TasksAPI();
