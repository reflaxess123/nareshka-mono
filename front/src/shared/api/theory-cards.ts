import type {
  CategoriesResponse,
  TheoryCardsQueryParams,
  TheoryCardsResponse,
  UpdateProgressRequest,
  UpdateProgressResponse,
} from '@/entities/TheoryCard/model/types';
import { apiInstance } from './base';

interface ServerTheoryCard {
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
  progress: {
    solvedCount: number;
    easeFactor: number;
    interval: number;
    dueDate: string | null;
    reviewCount: number;
    lapseCount: number;
    cardState: string;
    learningStep: number;
    lastReviewDate: string | null;
  };
}

interface ServerTheoryCardsResponse {
  cards: ServerTheoryCard[];
  pagination: {
    page: number;
    limit: number;
    totalItems: number;
    totalPages: number;
  };
}

export const theoryCardsApi = {
  async getTheoryCards(
    params: TheoryCardsQueryParams
  ): Promise<TheoryCardsResponse> {
    const response = await apiInstance.get<ServerTheoryCardsResponse>(
      '/v2/theory/cards',
      {
        params,
      }
    );

    return {
      cards: response.data.cards.map((card) => ({
        id: card.id,
        ankiGuid: card.ankiGuid,
        cardType: card.cardType,
        deck: card.deck,
        category: card.category,
        subCategory: card.subCategory,
        questionBlock: card.questionBlock,
        answerBlock: card.answerBlock,
        tags: card.tags,
        orderIndex: card.orderIndex,
        createdAt: card.createdAt,
        updatedAt: card.updatedAt,
        progress: card.progress,
      })),
      pagination: response.data.pagination,
    };
  },

  async getCategories(): Promise<CategoriesResponse> {
    const response = await apiInstance.get<CategoriesResponse>(
      '/v2/theory/categories'
    );
    return response.data;
  },

  async updateProgress(cardId: string, data: UpdateProgressRequest) {
    const response = await apiInstance.patch<UpdateProgressResponse>(
      `/v2/theory/cards/${cardId}/progress`,
      data
    );
    return response.data;
  },
};
