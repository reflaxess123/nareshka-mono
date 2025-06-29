import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import { useCallback, useEffect, useState } from 'react';
import type {
  TopicMindMapData,
  TopicMindMapFilters,
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
  const [filters, setFilters] = useState<TopicMindMapFilters>({
    structure_type: 'topics',
    technology: 'javascript',
    ...initialFilters,
  });

  const query = useQuery<TopicMindMapData>({
    queryKey: ['mindmap', filters],
    queryFn: async () => {
      try {
        const searchParams = new URLSearchParams();

        if (filters.structure_type) {
          searchParams.append('structure_type', filters.structure_type);
        }
        if (filters.technology) {
          searchParams.append('technology', filters.technology);
        }
        if (filters.difficulty_filter) {
          searchParams.append('difficulty_filter', filters.difficulty_filter);
        }
        if (filters.topic_filter) {
          searchParams.append('topic_filter', filters.topic_filter);
        }

        const url = `/api/mindmap/generate?${searchParams.toString()}`;

        const response = await axios.get(url);

        if (response.data?.error) {
          throw new Error(response.data.error);
        }

        return response.data;
      } catch (error) {
        if (axios.isAxiosError(error)) {
          const errorMessage = error.response?.data?.detail || error.message;
          throw new Error(errorMessage);
        }
        throw error;
      }
    },
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
    retry: 2,
    retryDelay: 1000,
  });

  const updateFilters = useCallback(
    (newFilters: Partial<TopicMindMapFilters>) => {
      setFilters((prev) => ({ ...prev, ...newFilters }));
    },
    []
  );

  const refetch = useCallback(() => {
    query.refetch();
  }, [query.refetch]);

  useEffect(() => {
    query.refetch();
  }, [query.refetch]);

  return {
    data: query.data || null,
    loading: query.isLoading,
    error: query.error?.message || null,
    refetch,
    updateFilters,
    filters,
  };
};

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

      // Нормализация task для TaskDetailModal
      const rawTask = result.task;
      const normalizedTask = {
        ...rawTask,
        text_content: rawTask.text_content || rawTask.description || '',
        programming_concepts: rawTask.programming_concepts || [],
        js_features_used: rawTask.js_features_used || [],
        complexity_score: rawTask.complexity_score || '',
        estimated_time_minutes: rawTask.estimated_time_minutes || '',
        code_lines: rawTask.code_lines || 0,
        code_content: rawTask.code_content || rawTask.codeContent || '',
        path_titles: rawTask.path_titles || [],
        target_skill_level: rawTask.target_skill_level || '',
        pedagogical_type: rawTask.pedagogical_type || '',
        category: rawTask.category || '',
        subcategory: rawTask.subcategory || '',
      };

      setTask(normalizedTask);
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

export const useTopicTasks = (
  topicKey: string,
  technology: string = 'javascript',
  difficultyFilter?: string
) => {
  return useQuery({
    queryKey: ['topic-tasks', topicKey, technology, difficultyFilter],
    queryFn: async () => {
      const searchParams = new URLSearchParams();
      searchParams.append('technology', technology);
      if (difficultyFilter) {
        searchParams.append('difficulty_filter', difficultyFilter);
      }

      const url = `/api/mindmap/topic/${topicKey}/tasks?${searchParams.toString()}`;
      const response = await axios.get(url);
      return response.data;
    },
    enabled: !!topicKey,
    staleTime: 5 * 60 * 1000,
  });
};
