import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { AppProvider } from './providers';
import './styles/globals.scss';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <AppProvider />
  </StrictMode>
);
