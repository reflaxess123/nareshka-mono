import { createSlice, type PayloadAction } from '@reduxjs/toolkit';
import type { TheoryFilters } from './types';

interface TheoryState {
  filters: TheoryFilters;
}

const initialState: TheoryState = {
  filters: {
    sortBy: 'orderIndex',
    sortOrder: 'asc',
  },
};

const theorySlice = createSlice({
  name: 'theory',
  initialState,
  reducers: {
    setFilters: (state, action: PayloadAction<TheoryFilters>) => {
      state.filters = action.payload;
    },
    resetFilters: (state) => {
      state.filters = initialState.filters;
    },
  },
});

export const { setFilters, resetFilters } = theorySlice.actions;
export default theorySlice.reducer;

// Селекторы
export const selectTheoryFilters = (state: { theory: TheoryState }) =>
  state.theory.filters;
