import { useCallback, useEffect, useRef, useState } from 'react';

interface UseInfiniteScrollOptions {
  hasNextPage: boolean;
  isLoading: boolean;
  onLoadMore: () => void;
  threshold?: number;
}

export const useInfiniteScroll = ({
  hasNextPage,
  isLoading,
  onLoadMore,
  threshold = 100
}: UseInfiniteScrollOptions) => {
  const [isFetching, setIsFetching] = useState(false);
  const sentinelRef = useRef<HTMLDivElement>(null);

  const handleObserver = useCallback(
    (entries: IntersectionObserverEntry[]) => {
      const [target] = entries;
      if (target.isIntersecting && hasNextPage && !isLoading && !isFetching) {
        setIsFetching(true);
        onLoadMore();
      }
    },
    [hasNextPage, isLoading, isFetching, onLoadMore]
  );

  useEffect(() => {
    const element = sentinelRef.current;
    const option = {
      root: null,
      rootMargin: `${threshold}px`,
      threshold: 0
    };

    const observer = new IntersectionObserver(handleObserver, option);
    
    if (element) observer.observe(element);

    return () => {
      if (element) observer.unobserve(element);
    };
  }, [handleObserver, threshold]);

  useEffect(() => {
    if (!isLoading) {
      setIsFetching(false);
    }
  }, [isLoading]);

  return { sentinelRef, isFetching };
};