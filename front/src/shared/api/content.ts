import type {
  ContentBlock,
  ContentBlocksFilters,
  ContentBlocksResponse,
  ContentCategory,
  ContentProgressResponse,
  ContentProgressUpdate,
} from '@/entities/ContentBlock';
import { apiInstance } from './base';

// Тип для блока от сервера (с progressEntries)
interface ServerContentBlock {
  id: string;
  fileId: string;
  file: {
    id: string;
    webdavPath: string;
    mainCategory: string;
    subCategory: string;
    lastFileHash?: string;
    createdAt: string;
    updatedAt: string;
  };
  pathTitles: string[];
  blockTitle: string;
  blockLevel: number;
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
  progressEntries: Array<{
    solvedCount: number;
    // ... другие поля прогресса
  }>;
}

interface ServerContentBlocksResponse {
  blocks: ServerContentBlock[];
  pagination: {
    page: number;
    limit: number;
    totalItems: number;
    totalPages: number;
  };
}

class ContentAPI {
  // Получение списка блоков контента с фильтрацией и пагинацией
  async getBlocks(
    filters: ContentBlocksFilters = {}
  ): Promise<ContentBlocksResponse> {
    const params = new URLSearchParams();

    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        params.append(key, value.toString());
      }
    });

    const response = await apiInstance.get<ServerContentBlocksResponse>(
      `/api/content/blocks?${params.toString()}`
    );

    // Преобразуем данные сервера в нужный формат
    const transformedData: ContentBlocksResponse = {
      data: response.data.blocks.map((block) => ({
        ...block,
        // Извлекаем solvedCount из первого элемента progressEntries или ставим 0
        currentUserSolvedCount:
          block.progressEntries && block.progressEntries.length > 0
            ? block.progressEntries[0].solvedCount
            : 0,
      })),
      pagination: response.data.pagination,
    };

    return transformedData;
  }

  // Получение конкретного блока по ID
  async getBlock(blockId: string): Promise<ContentBlock> {
    const response = await apiInstance.get<ServerContentBlock>(
      `/api/content/blocks/${blockId}`
    );

    // Преобразуем данные блока
    const transformedBlock: ContentBlock = {
      ...response.data,
      currentUserSolvedCount:
        response.data.progressEntries &&
        response.data.progressEntries.length > 0
          ? response.data.progressEntries[0].solvedCount
          : 0,
    };

    return transformedBlock;
  }

  // Обновление прогресса пользователя для блока
  async updateProgress(
    blockId: string,
    data: ContentProgressUpdate
  ): Promise<ContentProgressResponse> {
    const response = await apiInstance.patch(
      `/api/content/blocks/${blockId}/progress`,
      data
    );
    return response.data;
  }

  // Получение иерархии категорий
  async getCategories(): Promise<ContentCategory[]> {
    const response = await apiInstance.get('/api/content/categories');
    return response.data;
  }

  // Поиск блоков по тексту
  async searchBlocks(
    query: string,
    filters: Omit<ContentBlocksFilters, 'q'> = {}
  ): Promise<ContentBlocksResponse> {
    return this.getBlocks({ ...filters, q: query });
  }

  // Получение блоков по категории
  async getBlocksByCategory(
    mainCategory: string,
    subCategory?: string,
    filters: Omit<ContentBlocksFilters, 'mainCategory' | 'subCategory'> = {}
  ): Promise<ContentBlocksResponse> {
    return this.getBlocks({
      ...filters,
      mainCategory,
      ...(subCategory && { subCategory }),
    });
  }

  // Получение блоков с пагинацией (для бесконечного скролла)
  async getMoreBlocks(
    currentPage: number,
    filters: ContentBlocksFilters = {}
  ): Promise<ContentBlocksResponse> {
    return this.getBlocks({ ...filters, page: currentPage + 1 });
  }
}

export const contentApi = new ContentAPI();
