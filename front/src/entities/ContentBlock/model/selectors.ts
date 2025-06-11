import type { RootState } from '@/app/providers/redux/model/store';

export const selectContentBlockState = (state: RootState) => state.contentBlock;

export const selectContentBlocks = (state: RootState) =>
  state.contentBlock.blocks;

export const selectCurrentContentBlock = (state: RootState) =>
  state.contentBlock.currentBlock;

export const selectContentCategories = (state: RootState) =>
  state.contentBlock.categories;

export const selectContentBlocksFilters = (state: RootState) =>
  state.contentBlock.filters;

export const selectContentBlocksPagination = (state: RootState) =>
  state.contentBlock.pagination;

export const selectContentBlocksLoading = (state: RootState) =>
  state.contentBlock.isLoading;

export const selectContentBlocksError = (state: RootState) =>
  state.contentBlock.error;

// Производные селекторы
export const selectContentBlockById = (blockId: string) => (state: RootState) =>
  state.contentBlock.blocks.find((block) => block.id === blockId);

export const selectContentBlocksByCategory =
  (mainCategory: string) => (state: RootState) =>
    state.contentBlock.blocks.filter(
      (block) => block.file.mainCategory === mainCategory
    );

export const selectContentBlocksBySubCategory =
  (subCategory: string) => (state: RootState) =>
    state.contentBlock.blocks.filter(
      (block) => block.file.subCategory === subCategory
    );

export const selectSolvedContentBlocks = (state: RootState) =>
  state.contentBlock.blocks.filter((block) => block.currentUserSolvedCount > 0);

export const selectUnsolvedContentBlocks = (state: RootState) =>
  state.contentBlock.blocks.filter(
    (block) => block.currentUserSolvedCount === 0
  );

export const selectTotalSolvedCount = (state: RootState) =>
  state.contentBlock.blocks.reduce(
    (total, block) => total + block.currentUserSolvedCount,
    0
  );

export const selectUniqueMainCategories = (state: RootState) => {
  const categories = new Set(
    state.contentBlock.blocks.map((block) => block.file.mainCategory)
  );
  return Array.from(categories);
};

export const selectUniqueSubCategories =
  (mainCategory?: string) => (state: RootState) => {
    const blocks = mainCategory
      ? state.contentBlock.blocks.filter(
          (block) => block.file.mainCategory === mainCategory
        )
      : state.contentBlock.blocks;

    const subCategories = new Set(
      blocks.map((block) => block.file.subCategory)
    );
    return Array.from(subCategories);
  };

export const selectHasMorePages = (state: RootState) => {
  const { page, totalPages } = state.contentBlock.pagination;
  return page < totalPages;
};

export const selectIsFirstPage = (state: RootState) => {
  return state.contentBlock.pagination.page === 1;
};

export const selectIsLastPage = (state: RootState) => {
  const { page, totalPages } = state.contentBlock.pagination;
  return page >= totalPages;
};
