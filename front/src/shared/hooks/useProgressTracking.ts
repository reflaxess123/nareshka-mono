import { useMutation } from '@tanstack/react-query';
import { useCallback } from 'react';
import { toast } from 'react-toastify';

import progressApi from '@/shared/api/progress';
import { useAuth } from './useAuth';

interface UseProgressTrackingOptions {
  showToasts?: boolean;
  manualMode?: boolean;
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

interface ValidationRequest {
  blockId: string;
  sourceCode: string;
  language: string;
}

interface ValidationResult {
  blockId: string;
  allTestsPassed: boolean;
  testsResults?: Array<{
    testCaseId: string;
    testName: string;
    passed: boolean;
    input?: string;
    expectedOutput?: string;
    actualOutput?: string;
    error?: string;
    isPublic: boolean;
  }>;
  totalTests: number;
  passedTests: number;
  validatedAt: string;
  error?: string;
}

export const useProgressTracking = (
  options: UseProgressTrackingOptions = {}
) => {
  const { showToasts = true, manualMode = false } = options;
  const { user } = useAuth();

  const recordAttemptMutation = useMutation({
    mutationFn: async (attemptData: AttemptData) => {
      if (!user) {
        throw new Error('User not authenticated');
      }

      if (!manualMode) {
        console.warn(
          '⚠️ Manual progress recording is disabled. Progress is now recorded automatically on backend.'
        );
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
          toast.success('✅ Задача решена! 🎉');
        } else {
          toast.info('📝 Попытка записана');
        }
      }
    },
    onError: (error) => {
      if (showToasts) {
        toast.error('❌ Не удалось записать попытку');
      }
      console.error('Progress recording error:', error);
    },
  });

  const validateSolutionMutation = useMutation({
    mutationFn: async (validationData: ValidationRequest) => {
      if (!user) {
        throw new Error('User not authenticated');
      }

      return fetch(`/api/v2/code-editor/validate/${validationData.blockId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          sourceCode: validationData.sourceCode,
          language: validationData.language,
        }),
      }).then((res) => res.json());
    },
    // ❌ УБРАНО ДУБЛИРОВАНИЕ: уведомления теперь только в validateSolution функции
    onError: (error) => {
      console.error('Validation error:', error);
      // Уведомления об ошибках обрабатываются в validateSolution
    },
  });

  const validateSolution = useCallback(
    (
      validationData: ValidationRequest,
      callbacks?: {
        onSuccess?: (data: ValidationResult) => void;
        onError?: (error: Error) => void;
      }
    ) => {
      validateSolutionMutation.mutate(validationData, {
        onSuccess: (data) => {
          if (showToasts) {
            if (data.allTestsPassed) {
              toast.success(
                `✅ Все тесты пройдены! (${data.passedTests}/${data.totalTests})`
              );
            } else {
              toast.warning(
                `⚠️ Тесты не пройдены: ${data.passedTests}/${data.totalTests}`
              );
            }
          }
          callbacks?.onSuccess?.(data);
        },
        onError: (error) => {
          if (showToasts) {
            toast.error('❌ Ошибка валидации решения');
          }
          console.error('Validation error:', error);
          callbacks?.onError?.(error);
        },
      });
    },
    [validateSolutionMutation, showToasts]
  );

  const getTestCasesMutation = useMutation({
    mutationFn: async (blockId: string) => {
      if (!user) {
        throw new Error('User not authenticated');
      }

      return fetch(`/api/v2/code-editor/test_cases/${blockId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }).then((res) => res.json());
    },
    // ✅ УБРАНО: уведомления о генерации/загрузке тест-кейсов
    onError: (error) => {
      console.error('Test cases loading error:', error);
      // Тихо логируем ошибку без уведомлений пользователю
    },
  });

  // ✅ МЕМОИЗИРОВАННЫЕ ФУНКЦИИ для предотвращения бесконечных циклов
  const getTestCases = useCallback(
    (blockId: string) => {
      getTestCasesMutation.mutate(blockId);
    },
    [] // useMutation.mutate стабилен, зависимости не нужны
  );

  const showInfoMessage = useCallback(
    (message: string) => {
      if (showToasts) {
        toast.info(message);
      }
    },
    [showToasts]
  );

  return {
    recordAttempt: recordAttemptMutation.mutate,
    isRecording: recordAttemptMutation.isPending,
    validateSolution,
    isValidating: validateSolutionMutation.isPending,
    validationResult: validateSolutionMutation.data,
    getTestCases,
    isLoadingTests: getTestCasesMutation.isPending,
    testCases: getTestCasesMutation.data,
    showInfoMessage,
    isAutoRecordingEnabled: !manualMode,
  };
};

export default useProgressTracking;
