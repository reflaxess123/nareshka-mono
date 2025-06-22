import { apiInstance } from './base';

export interface LearningPath {
  id: string;
  name: string;
  description?: string;
  isCompleted: boolean;
  currentBlockIndex: number;
  completedBlockIds: string[];
}

export interface CategoryProgressSummary {
  mainCategory: string;
  subCategory?: string;
  totalTasks: number;
  completedTasks: number;
  attemptedTasks: number;
  completionRate: number;
  averageAttempts: number;
  totalTimeSpent: number;
  lastActivity?: string;
  status: 'not_started' | 'in_progress' | 'completed' | 'struggling';
}

export interface TaskAttempt {
  id: string;
  userId: number;
  blockId: string;
  sourceCode: string;
  language: string;
  isSuccessful: boolean;
  attemptNumber: number;
  executionTimeMs?: number;
  memoryUsedMB?: number;
  errorMessage?: string;
  stderr?: string;
  durationMinutes?: number;
  createdAt: string;
}

export interface TaskSolution {
  id: string;
  userId: number;
  blockId: string;
  finalCode: string;
  language: string;
  totalAttempts: number;
  timeToSolveMinutes: number;
  firstAttempt: string;
  solvedAt: string;
  createdAt: string;
  updatedAt: string;
}

export interface UserDetailedProgress {
  userId: number;
  totalTasksSolved: number;
  lastActivityDate?: string;
  overallStats: {
    totalAttempts: number;
    successfulAttempts: number;
    successRate: number;
    totalTimeSpent: number;
  };
  categoryProgress: CategoryProgressSummary[];
  recentAttempts: TaskAttempt[];
  recentSolutions: TaskSolution[];
  learningPaths: LearningPath[];
}

export interface ProgressAnalytics {
  totalUsers: number;
  activeUsers: number;
  totalTasksSolved: number;
  averageTasksPerUser: number;
  mostPopularCategories: Array<{
    mainCategory: string;
    subCategory: string;
    completed: number;
  }>;
  strugglingAreas: Array<{
    mainCategory: string;
    subCategory: string;
    averageAttempts: number;
  }>;
}

export interface TaskAttemptCreate {
  userId: number;
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

// API функции
const progressAPI = {
  // Получить детальный прогресс текущего пользователя
  async getMyProgress(): Promise<UserDetailedProgress> {
    const response = await apiInstance.get('/progress/user/my/detailed');
    return response.data;
  },

  // Получить прогресс конкретного пользователя (для админов)
  async getUserProgress(userId: number): Promise<UserDetailedProgress> {
    const response = await apiInstance.get(`/progress/user/${userId}/detailed`);
    return response.data;
  },

  // Записать попытку решения задачи
  async recordAttempt(attempt: TaskAttemptCreate): Promise<TaskAttempt> {
    const response = await apiInstance.post('/progress/attempts', attempt);
    return response.data;
  },

  // Получить аналитику (для админов)
  async getAnalytics(): Promise<ProgressAnalytics> {
    const response = await apiInstance.get('/progress/analytics');
    return response.data;
  },

  // Проверка работоспособности
  async healthCheck(): Promise<{ status: string }> {
    const response = await apiInstance.get('/progress/health');
    return response.data;
  },
};

export { progressAPI };
export default progressAPI;
