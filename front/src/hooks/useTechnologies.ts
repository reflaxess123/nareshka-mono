import { useGetAvailableTechnologiesApiV2MindmapTechnologiesGet } from '@/shared/api/generated/api';
import type { TechnologiesResponse } from '../types/mindmap';

export const useTechnologies = () => {
  const result = useGetAvailableTechnologiesApiV2MindmapTechnologiesGet({
    query: {
      staleTime: 10 * 60 * 1000, // Кешируем на 10 минут
      gcTime: 30 * 60 * 1000, // Держим в памяти 30 минут
    },
  });

  return {
    ...result,
    data: result.data as TechnologiesResponse | undefined,
  };
};
