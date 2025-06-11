import { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';

export const usePageTransition = () => {
  const [isLoading, setIsLoading] = useState(false);
  const location = useLocation();

  useEffect(() => {
    setIsLoading(true);
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 0); // Время показа loading для демонстрации

    return () => clearTimeout(timer);
  }, [location.pathname]);

  return isLoading;
};
