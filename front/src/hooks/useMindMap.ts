import { useCallback, useEffect, useState } from 'react';
import type {
  TopicMindMapData,
  TopicMindMapFilters,
  TopicMindMapResponse,
} from '../types/newMindmap';

interface UseMindMapResult {
  data: TopicMindMapData | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
  updateFilters: (filters: Partial<TopicMindMapFilters>) => void;
  filters: TopicMindMapFilters;
}

export const useMindMap = (
  initialFilters?: Partial<TopicMindMapFilters>
): UseMindMapResult => {
  const [data, setData] = useState<TopicMindMapData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<TopicMindMapFilters>({
    structure_type: 'topics',
    ...initialFilters,
  });

  const fetchMindMapData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      // Строим URL с параметрами
      const params = new URLSearchParams();

      if (filters.structure_type) {
        params.append('structure_type', filters.structure_type);
      }
      if (filters.difficulty_filter) {
        params.append('difficulty_filter', filters.difficulty_filter);
      }
      if (filters.topic_filter) {
        params.append('topic_filter', filters.topic_filter);
      }
      if (filters.concept_filter) {
        params.append('concept_filter', filters.concept_filter);
      }

      const url = `/api/mindmap/generate?${params.toString()}`;

      console.log('🚀 Загружаем MindMap:', { url, filters });

      const response = await fetch(url);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result: TopicMindMapResponse = await response.json();

      if (!result.success) {
        throw new Error(result.error || 'Неизвестная ошибка');
      }

      if (!result.data) {
        throw new Error('Данные не получены');
      }

      console.log('✅ MindMap загружена:', result.data);
      setData(result.data);
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : 'Неизвестная ошибка';
      console.error('❌ Ошибка загрузки MindMap:', errorMessage);
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  const updateFilters = useCallback(
    (newFilters: Partial<TopicMindMapFilters>) => {
      setFilters((prev) => ({ ...prev, ...newFilters }));
    },
    []
  );

  const refetch = useCallback(() => {
    fetchMindMapData();
  }, [fetchMindMapData]);

  useEffect(() => {
    fetchMindMapData();
  }, [fetchMindMapData]);

  return {
    data,
    loading,
    error,
    refetch,
    updateFilters,
    filters,
  };
};

// Дополнительный хук для работы с задачами
export const useTaskDetails = (taskId: string | null) => {
  const [task, setTask] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchTask = useCallback(async () => {
    if (!taskId) return;

    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`/api/mindmap/task/${taskId}`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();

      if (!result.success) {
        throw new Error(result.error || 'Задача не найдена');
      }

      setTask(result.task);
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : 'Ошибка загрузки задачи';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  }, [taskId]);

  useEffect(() => {
    if (taskId) {
      fetchTask();
    } else {
      setTask(null);
      setError(null);
    }
  }, [taskId, fetchTask]);

  return {
    task,
    loading,
    error,
    refetch: fetchTask,
  };
};
