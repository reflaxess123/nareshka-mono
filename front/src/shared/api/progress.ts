import type { AxiosRequestConfig } from 'axios';
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
  completionRate: number;
  status: 'not_started' | 'in_progress' | 'completed';
}

export interface SubCategoryProgress {
  subCategory: string;
  totalTasks: number;
  completedTasks: number;
  completionRate: number;
  status: 'not_started' | 'in_progress' | 'completed';
}

export interface GroupedCategoryProgress {
  mainCategory: string;
  totalTasks: number;
  completedTasks: number;
  completionRate: number;
  status: 'not_started' | 'in_progress' | 'completed';
  subCategories: SubCategoryProgress[];
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

export interface SimplifiedOverallStats {
  totalTasksSolved: number;
  totalTasksAvailable: number;
  completionRate: number;
}

export interface RecentActivityItem {
  id: string;
  blockId: string;
  title: string;
  category: string;
  subCategory?: string;
  isSuccessful: boolean;
  activityType: 'attempt' | 'solution';
  timestamp: string;
}

export interface UserDetailedProgress {
  userId: number;
  lastActivityDate?: string;
  overallStats: SimplifiedOverallStats;
  categoryProgress: CategoryProgressSummary[];
  groupedCategoryProgress: GroupedCategoryProgress[];
  recentActivity: RecentActivityItem[];
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
  async getMyProgress(
    options?: AxiosRequestConfig
  ): Promise<UserDetailedProgress> {
    const response = await apiInstance.get(
      '/v2/progress/detailed',
      options
    );
    return response.data;
  },

  // Получить прогресс конкретного пользователя (для админов)
  async getUserProgress(
    userId: number,
    options?: AxiosRequestConfig
  ): Promise<UserDetailedProgress> {
    const response = await apiInstance.get(
      `/v2/progress/admin/users/${userId}/detailed`,
      options
    );
    return response.data;
  },

  // Записать попытку решения задачи
  async recordAttempt(attempt: TaskAttemptCreate): Promise<TaskAttempt> {
    const response = await apiInstance.post('/v2/progress/attempts', attempt);
    return response.data;
  },

  // Получить аналитику (для админов)
  async getAnalytics(): Promise<ProgressAnalytics> {
    const response = await apiInstance.get('/v2/progress/analytics');
    return response.data;
  },
};

export { progressAPI };
export default progressAPI;
