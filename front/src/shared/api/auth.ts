import type {
  AdminStats,
  AdminUser,
  CreateUserRequest,
  LoginRequest,
  RegisterRequest,
  UpdateUserRequest,
  User,
} from '@/entities/User/model/types';
import { apiInstance } from './base';

export const authApi = {
  async login(credentials: LoginRequest) {
    const response = await apiInstance.post<User>('/auth/login', credentials);
    return response.data;
  },

  async register(credentials: RegisterRequest) {
    const response = await apiInstance.post<User>(
      '/auth/register',
      credentials
    );
    return response.data;
  },

  async logout() {
    await apiInstance.post('/auth/logout');
  },

  async getProfile() {
    const response = await apiInstance.get<User>('/api/profile');
    return response.data;
  },

  admin: {
    async getStats(): Promise<AdminStats> {
      const response = await apiInstance.get<AdminStats>('/api/admin/stats');
      return response.data;
    },

    async getUsers(params?: {
      page?: number;
      limit?: number;
      role?: string;
      search?: string;
    }): Promise<{ users: AdminUser[]; total: number; pages: number }> {
      const response = await apiInstance.get<{
        users: AdminUser[];
        total: number;
        pages: number;
      }>('/api/admin/users', { params });
      return response.data;
    },

    async createUser(data: CreateUserRequest): Promise<AdminUser> {
      const response = await apiInstance.post<AdminUser>(
        '/api/admin/users',
        data
      );
      return response.data;
    },

    async updateUser(
      userId: number,
      data: UpdateUserRequest
    ): Promise<AdminUser> {
      const response = await apiInstance.put<AdminUser>(
        `/api/admin/users/${userId}`,
        data
      );
      return response.data;
    },

    async deleteUser(userId: number): Promise<void> {
      const response = await apiInstance.delete<void>(
        `/api/admin/users/${userId}`
      );
      return response.data;
    },

    async getContentStats(): Promise<Record<string, unknown>> {
      const response = await apiInstance.get<Record<string, unknown>>(
        '/api/admin/content/stats'
      );
      return response.data;
    },

    async deleteContentFile(fileId: string): Promise<void> {
      const response = await apiInstance.delete<void>(
        `/api/admin/content/files/${fileId}`
      );
      return response.data;
    },
  },
};
