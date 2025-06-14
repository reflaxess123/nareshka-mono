import { apiInstance } from './base';

// Types
export interface SupportedLanguage {
  id: string;
  name: string;
  language: string;
  version: string;
  fileExtension: string;
  timeoutSeconds: number;
  memoryLimitMB: number;
  isEnabled: boolean;
}

export interface CodeExecutionRequest {
  sourceCode: string;
  language: string;
  stdin?: string;
  blockId?: string;
}

export interface CodeExecutionResponse {
  id: string;
  status:
    | 'PENDING'
    | 'RUNNING'
    | 'SUCCESS'
    | 'ERROR'
    | 'TIMEOUT'
    | 'MEMORY_LIMIT';
  stdout?: string;
  stderr?: string;
  exitCode?: number;
  executionTimeMs?: number;
  memoryUsedMB?: number;
  errorMessage?: string;
  createdAt: string;
  completedAt?: string;
}

export interface UserCodeSolution {
  id: string;
  userId: number;
  blockId: string;
  languageId: string;
  sourceCode: string;
  isCompleted: boolean;
  executionCount: number;
  successfulExecutions: number;
  createdAt: string;
  updatedAt: string;
  supportedLanguage: SupportedLanguage;
  lastExecution?: CodeExecutionResponse;
}

export interface CodeSolutionCreate {
  blockId: string;
  language: string;
  sourceCode: string;
  isCompleted?: boolean;
}

export interface CodeSolutionUpdate {
  sourceCode?: string;
  isCompleted?: boolean;
}

export interface ExecutionStats {
  totalExecutions: number;
  successfulExecutions: number;
  averageExecutionTime: number;
  languageStats: Array<{
    language: string;
    name: string;
    executions: number;
  }>;
}

// API Functions
export const codeEditorApi = {
  // Получение поддерживаемых языков
  async getSupportedLanguages(): Promise<SupportedLanguage[]> {
    const response = await apiInstance.get('/code-editor/languages');
    return response.data;
  },

  // Выполнение кода
  async executeCode(
    request: CodeExecutionRequest
  ): Promise<CodeExecutionResponse> {
    const response = await apiInstance.post('/code-editor/execute', request);
    return response.data;
  },

  // Получение результата выполнения
  async getExecutionResult(
    executionId: string
  ): Promise<CodeExecutionResponse> {
    const response = await apiInstance.get(
      `/code-editor/executions/${executionId}`
    );
    return response.data;
  },

  // Получение истории выполнений
  async getUserExecutions(params?: {
    blockId?: string;
    limit?: number;
    offset?: number;
  }): Promise<CodeExecutionResponse[]> {
    const response = await apiInstance.get('/code-editor/executions', {
      params,
    });
    return response.data;
  },

  // Сохранение решения
  async saveSolution(solution: CodeSolutionCreate): Promise<UserCodeSolution> {
    const response = await apiInstance.post('/code-editor/solutions', solution);
    return response.data;
  },

  // Получение решений для блока
  async getBlockSolutions(blockId: string): Promise<UserCodeSolution[]> {
    const response = await apiInstance.get(`/code-editor/solutions/${blockId}`);
    return response.data;
  },

  // Обновление решения
  async updateSolution(
    solutionId: string,
    update: CodeSolutionUpdate
  ): Promise<UserCodeSolution> {
    const response = await apiInstance.put(
      `/code-editor/solutions/${solutionId}`,
      update
    );
    return response.data;
  },

  // Получение статистики
  async getExecutionStats(): Promise<ExecutionStats> {
    const response = await apiInstance.get('/code-editor/stats');
    return response.data;
  },

  // Polling для получения результата выполнения
  async pollExecutionResult(
    executionId: string,
    onUpdate?: (result: CodeExecutionResponse) => void,
    maxAttempts: number = 30,
    intervalMs: number = 1000
  ): Promise<CodeExecutionResponse> {
    let attempts = 0;

    const poll = async (): Promise<CodeExecutionResponse> => {
      const result = await this.getExecutionResult(executionId);

      if (onUpdate) {
        onUpdate(result);
      }

      // Если выполнение завершено, возвращаем результат
      if (
        result.status === 'SUCCESS' ||
        result.status === 'ERROR' ||
        result.status === 'TIMEOUT' ||
        result.status === 'MEMORY_LIMIT'
      ) {
        return result;
      }

      attempts++;
      if (attempts >= maxAttempts) {
        throw new Error('Polling timeout: execution taking too long');
      }

      // Ждем перед следующей попыткой
      await new Promise((resolve) => setTimeout(resolve, intervalMs));
      return poll();
    };

    return poll();
  },
};

// React Query hooks keys
export const codeEditorKeys = {
  all: ['codeEditor'] as const,
  languages: () => [...codeEditorKeys.all, 'languages'] as const,
  executions: () => [...codeEditorKeys.all, 'executions'] as const,
  execution: (id: string) => [...codeEditorKeys.executions(), id] as const,
  solutions: () => [...codeEditorKeys.all, 'solutions'] as const,
  blockSolutions: (blockId: string) =>
    [...codeEditorKeys.solutions(), blockId] as const,
  stats: () => [...codeEditorKeys.all, 'stats'] as const,
};

export default codeEditorApi;
