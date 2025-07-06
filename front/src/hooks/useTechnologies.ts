import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import type { TechnologiesResponse } from '../types/mindmap';

export const useTechnologies = () => {
  return useQuery<TechnologiesResponse>({
    queryKey: ['mindmap-technologies'],
    queryFn: async () => {
      const response = await axios.get('/api/v2/mindmap/technologies');
      return response.data;
    },
    staleTime: 10 * 60 * 1000, // Кешируем на 10 минут
    gcTime: 30 * 60 * 1000, // Держим в памяти 30 минут
  });
};
