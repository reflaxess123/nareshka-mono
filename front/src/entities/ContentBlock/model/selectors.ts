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

export const selectContentBlockById = (blockId: string) => (state: RootState) =>
  state.contentBlock.blocks.find((block) => block.id === blockId);

export const selectFilteredBlocks = (state: RootState) => {
  const { blocks, filters } = state.contentBlock;

  let filteredBlocks = blocks;

  // Фильтр по основным категориям
  if (filters.mainCategories && filters.mainCategories.length > 0) {
    filteredBlocks = filteredBlocks.filter(
      (block) =>
        block.file && filters.mainCategories!.includes(block.file.mainCategory)
    );
  }

  // Фильтр по подкатегориям
  if (filters.subCategories && filters.subCategories.length > 0) {
    filteredBlocks = filteredBlocks.filter(
      (block) =>
        block.file && filters.subCategories!.includes(block.file.subCategory)
    );
  }

  return filteredBlocks;
};

export const selectContentBlocksByCategories =
  (mainCategories?: string[], subCategories?: string[]) =>
  (state: RootState) => {
    let filteredBlocks = state.contentBlock.blocks;

    if (mainCategories && mainCategories.length > 0) {
      filteredBlocks = filteredBlocks.filter(
        (block) =>
          block.file && mainCategories.includes(block.file.mainCategory)
      );
    }

    if (subCategories && subCategories.length > 0) {
      filteredBlocks = filteredBlocks.filter(
        (block) => block.file && subCategories.includes(block.file.subCategory)
      );
    }

    return filteredBlocks;
  };

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
    state.contentBlock.blocks
      .filter((block) => block.file)
      .map((block) => block.file!.mainCategory)
  );
  return Array.from(categories);
};

export const selectUniqueSubCategories = (mainCategory?: string) => {
  return (state: RootState) => {
    const blocks = mainCategory
      ? state.contentBlock.blocks.filter(
          (block) => block.file && block.file.mainCategory === mainCategory
        )
      : state.contentBlock.blocks.filter((block) => block.file);

    const subCategories = new Set(
      blocks.map((block) => block.file!.subCategory)
    );
    return Array.from(subCategories);
  };
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
