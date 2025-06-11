import { createSlice, type PayloadAction } from '@reduxjs/toolkit';
import type {
  ContentBlock,
  ContentBlockState,
  ContentBlocksFilters,
  ContentBlocksResponse,
  ContentCategory,
} from './types';

const initialState: ContentBlockState = {
  blocks: [],
  categories: [],
  currentBlock: null,
  filters: {
    page: 1,
    limit: 20,
    sortBy: 'orderInFile',
    sortOrder: 'asc',
  },
  pagination: {
    page: 1,
    limit: 20,
    totalItems: 0,
    totalPages: 0,
  },
  isLoading: false,
  error: null,
};

const contentBlockSlice = createSlice({
  name: 'contentBlock',
  initialState,
  reducers: {
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },

    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
      state.isLoading = false;
    },

    setBlocks: (state, action: PayloadAction<ContentBlocksResponse>) => {
      state.blocks = action.payload.data;
      state.pagination = action.payload.pagination;
      state.isLoading = false;
      state.error = null;
    },

    addBlocks: (state, action: PayloadAction<ContentBlocksResponse>) => {
      // Для пагинации - добавляем новые блоки к существующим
      state.blocks = [...state.blocks, ...action.payload.data];
      state.pagination = action.payload.pagination;
      state.isLoading = false;
      state.error = null;
    },

    setCurrentBlock: (state, action: PayloadAction<ContentBlock | null>) => {
      state.currentBlock = action.payload;
    },

    updateBlockProgress: (
      state,
      action: PayloadAction<{ blockId: string; solvedCount: number }>
    ) => {
      const { blockId, solvedCount } = action.payload;

      // Обновляем в списке блоков
      const blockIndex = state.blocks.findIndex(
        (block) => block && block.id === blockId
      );
      if (blockIndex !== -1) {
        state.blocks[blockIndex].currentUserSolvedCount = solvedCount;
      }

      // Обновляем текущий блок если это он
      if (state.currentBlock?.id === blockId) {
        state.currentBlock.currentUserSolvedCount = solvedCount;
      }
    },

    setCategories: (state, action: PayloadAction<ContentCategory[]>) => {
      state.categories = action.payload;
    },

    setFilters: (
      state,
      action: PayloadAction<Partial<ContentBlocksFilters>>
    ) => {
      state.filters = { ...state.filters, ...action.payload };
      // При изменении фильтров (кроме page) сбрасываем на первую страницу
      if (action.payload.page === undefined) {
        state.filters.page = 1;
      }
    },

    resetFilters: (state) => {
      state.filters = {
        page: 1,
        limit: 20,
        sortBy: 'orderInFile',
        sortOrder: 'asc',
      };
    },

    clearBlocks: (state) => {
      state.blocks = [];
      state.pagination = {
        page: 1,
        limit: 20,
        totalItems: 0,
        totalPages: 0,
      };
    },

    clearCurrentBlock: (state) => {
      state.currentBlock = null;
    },

    clearError: (state) => {
      state.error = null;
    },
  },
});

export const {
  setLoading,
  setError,
  setBlocks,
  addBlocks,
  setCurrentBlock,
  updateBlockProgress,
  setCategories,
  setFilters,
  resetFilters,
  clearBlocks,
  clearCurrentBlock,
  clearError,
} = contentBlockSlice.actions;

export default contentBlockSlice.reducer;
