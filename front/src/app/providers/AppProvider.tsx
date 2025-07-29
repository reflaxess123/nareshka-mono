import { AuthProvider } from '@/app/providers/auth';
import { ModalProvider } from '@/shared/components/Modal/model/context';
import { ThemeProvider } from '@/shared/context';
import type { ReactNode } from 'react';
import { Provider } from 'react-redux';
import { ModalRenderer } from './modal/ui/ModalProvider';
import { NotificationProvider } from './notification';
import { QueryProvider } from './query';
import { store } from './redux';
import { AppRouter } from './router';

import 'react-toastify/dist/ReactToastify.css';

interface AppProviderProps {
  children?: ReactNode;
}

export const AppProvider = ({ children }: AppProviderProps) => {
  return (
    <ThemeProvider>
      <Provider store={store}>
        <QueryProvider>
          <ModalProvider>
            <AuthProvider>
              {children || <AppRouter />}
              <ModalRenderer />
              <NotificationProvider />
            </AuthProvider>
          </ModalProvider>
        </QueryProvider>
      </Provider>
    </ThemeProvider>
  );
};
