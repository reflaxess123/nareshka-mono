import { useCallback, useEffect, useState } from 'react';
import type { MindMapResponse } from '../types/mindmap';

interface UseMindMapDataReturn {
  data: MindMapResponse | null;
  isLoading: boolean;
  error: Error | null;
  refetch: () => void;
}

export const useMindMapData = (
  difficultyFilter?: string,
  conceptFilter?: string
): UseMindMapDataReturn => {
  const [data, setData] = useState<MindMapResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      // Построение URL с параметрами
      const params = new URLSearchParams();
      if (difficultyFilter) {
        params.append('difficulty_filter', difficultyFilter);
      }
      if (conceptFilter) {
        params.append('concept_filter', conceptFilter);
      }

      const url = `/api/v2/mindmap/generate${params.toString() ? `?${params.toString()}` : ''}`;

      const response = await fetch(url);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();

      if (!result.success) {
        throw new Error(result.message || 'Ошибка загрузки данных');
      }

      setData(result);
    } catch (err) {
      console.error('Ошибка загрузки MindMap:', err);
      setError(err instanceof Error ? err : new Error('Неизвестная ошибка'));
    } finally {
      setIsLoading(false);
    }
  }, [difficultyFilter, conceptFilter]);

  // Загружаем данные при изменении фильтров
  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const refetch = useCallback(() => {
    fetchData();
  }, [fetchData]);

  return {
    data,
    isLoading,
    error,
    refetch,
  };
};
