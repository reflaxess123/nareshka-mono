import { useMutation } from '@tanstack/react-query';
import { toast } from 'react-toastify';

import progressApi from '@/shared/api/progress';
import { useAuth } from './useAuth';

interface UseProgressTrackingOptions {
  showToasts?: boolean;
  autoRecord?: boolean;
}

interface AttemptData {
  blockId: string;
  sourceCode: string;
  language: string;
  isSuccessful: boolean;
  executionTimeMs?: number;
  memoryUsedMB?: number;
  errorMessage?: string;
  stderr?: string;
  durationMinutes?: number;
}

export const useProgressTracking = (
  options: UseProgressTrackingOptions = {}
) => {
  const { showToasts = true, autoRecord = true } = options;
  const { user } = useAuth();

  const recordAttemptMutation = useMutation({
    mutationFn: async (attemptData: AttemptData) => {
      if (!user) {
        return null;
      }

      if (!autoRecord) {
        return null;
      }

      const payload = {
        ...attemptData,
        userId: user.id,
      };

      return progressApi.recordAttempt(payload);
    },
    onSuccess: (data, variables) => {
      if (data && showToasts) {
        if (variables.isSuccessful) {
          toast.success('Задача решена! 🎉');
        } else {
          toast.info('Попытка записана');
        }
      }
    },
    onError: () => {
      if (showToasts) {
        toast.error('Не удалось записать попытку');
      }
    },
  });

  return {
    recordAttempt: recordAttemptMutation.mutate,
    isRecording: recordAttemptMutation.isPending,
  };
};

export default useProgressTracking;
