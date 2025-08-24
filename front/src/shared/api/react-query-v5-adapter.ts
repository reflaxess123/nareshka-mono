// Адаптер для React Query v5
// Этот файл временно исправляет проблемы совместимости между Orval и React Query v5

import { useQuery as useQueryV5, useMutation as useMutationV5 } from '@tanstack/react-query';

// Переопределяем useQuery чтобы игнорировать queryClient параметр
export function useQuery(options: any, queryClient?: any) {
  // В v5 queryClient больше не передается как параметр
  return useQueryV5(options);
}

// Переопределяем useMutation чтобы игнорировать queryClient параметр  
export function useMutation(options: any, queryClient?: any) {
  // В v5 queryClient больше не передается как параметр
  return useMutationV5(options);
}