import { configureStore } from '@reduxjs/toolkit';
import { rootReducer } from './rootReducer';

type RootState = ReturnType<typeof store.getState>;
type AppDispatch = typeof store.dispatch;

export const store = configureStore({
  reducer: rootReducer,
});

export type { AppDispatch, RootState };
