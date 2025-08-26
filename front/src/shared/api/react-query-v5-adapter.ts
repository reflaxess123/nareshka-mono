// Адаптер для React Query v5

import { 
  useQuery as useQueryV5, 
  useMutation as useMutationV5,
  type UseQueryOptions,
  type UseMutationOptions 
} from '@tanstack/react-query';

export function useQuery<TQueryFnData = unknown, TError = unknown, TData = TQueryFnData, TQueryKey extends readonly unknown[] = readonly unknown[]>(
  options: UseQueryOptions<TQueryFnData, TError, TData, TQueryKey>
) {
  return useQueryV5(options);
}

export function useMutation<TData = unknown, TError = unknown, TVariables = void, TContext = unknown>(
  options: UseMutationOptions<TData, TError, TVariables, TContext>
) {
  return useMutationV5(options);
}
