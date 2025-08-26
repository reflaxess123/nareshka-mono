import type {
  ContentBlock,
  ContentBlocksFilters,
  ContentBlocksResponse,
  ContentProgressResponse,
  ContentProgressUpdate,
} from '@/entities/ContentBlock';
import { apiInstance } from './base';

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
      `/v2/content/blocks?${params.toString()}`
    );

    // Преобразуем данные сервера в нужный формат
    return {
      data: response.data.blocks.map((block) => ({
        ...block,
        title: block.blockTitle,
        // Извлекаем solvedCount из первого элемента progressEntries или ставим 0
        currentUserSolvedCount:
          block.progressEntries && block.progressEntries.length > 0
            ? block.progressEntries[0].solvedCount
            : 0,
      })),
      pagination: response.data.pagination,
    };
  }

  // Получение конкретного блока по ID
  async getBlock(blockId: string): Promise<ContentBlock> {
    const response = await apiInstance.get<ServerContentBlock>(
      `/v2/content/blocks/${blockId}`
    );

    // Преобразуем данные блока
    const transformedBlock: ContentBlock = {
      ...response.data,
      title: response.data.blockTitle,
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
      `/v2/content/blocks/${blockId}/progress`,
      data
    );
    return response.data;
  }

  // Поиск блоков по тексту
  async searchBlocks(
    query: string,
    filters: Omit<ContentBlocksFilters, 'q'> = {}
  ): Promise<ContentBlocksResponse> {
    return this.getBlocks({ ...filters, q: query });
  }

  // Получение блоков по категориям
  async getBlocksByCategories(
    mainCategories?: string[],
    subCategories?: string[],
    filters: ContentBlocksFilters = {}
  ): Promise<ContentBlocksResponse> {
    return this.getBlocks({
      ...filters,
      ...(mainCategories && mainCategories.length > 0 && { mainCategories }),
      ...(subCategories && subCategories.length > 0 && { subCategories }),
    });
  }

}

export const contentApi = new ContentAPI();
