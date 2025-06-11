import { Loading } from '@/shared/components/Loading';
import { usePageTransition } from '@/shared/hooks/usePageTransition';

interface PageTransitionProps {
  children: React.ReactNode;
}

export const PageTransition = ({ children }: PageTransitionProps) => {
  const isLoading = usePageTransition();

  if (isLoading) {
    return <Loading />;
  }

  return <>{children}</>;
};
