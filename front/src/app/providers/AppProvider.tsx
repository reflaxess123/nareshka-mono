import { ModalProvider } from '@/shared/components/Modal/model/context';
import { ThemeProvider } from '@/shared/context';
import type { ReactNode } from 'react';
import { Provider } from 'react-redux';
import { AuthProvider } from './auth/ui/AuthProvider';
import { ModalRenderer } from './modal/ui/ModalProvider';
import { QueryProvider } from './query';
import { store } from './redux';
import { AppRouter } from './router';

interface AppProviderProps {
  children?: ReactNode;
}

export const AppProvider = ({ children }: AppProviderProps) => {
  return (
    <ThemeProvider>
      <Provider store={store}>
        <QueryProvider>
          <AuthProvider>
            <ModalProvider>
              {children || <AppRouter />}
              <ModalRenderer />
            </ModalProvider>
          </AuthProvider>
        </QueryProvider>
      </Provider>
    </ThemeProvider>
  );
};
