import { Loading } from '@/shared/components/Loading';
import { useAuth } from '@/shared/hooks';

interface AuthProviderProps {
  children: React.ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const { isInitialized, isLoading } = useAuth();

  if (!isInitialized || isLoading) {
    return <Loading />;
  }

  return <>{children}</>;
};
