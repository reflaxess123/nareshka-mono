import type {
  AdminStats,
  AdminUser,
  LoginRequest,
  RegisterRequest,
  UpdateUserRequest,
  User,
} from '@/entities/User/model/types';
import { apiInstance } from './base';

export const authApi = {
  async login(credentials: LoginRequest) {
    const response = await apiInstance.post<User>(
      '/v2/auth/login',
      credentials
    );
    return response.data;
  },

  async register(credentials: RegisterRequest) {
    const response = await apiInstance.post<User>(
      '/v2/auth/register',
      credentials
    );
    return response.data;
  },

  async logout() {
    await apiInstance.post('/v2/auth/logout');
  },

  async getProfile() {
    const response = await apiInstance.get<User>('/v2/auth/me');
    return response.data;
  },

  admin: {
    async getStats(): Promise<AdminStats> {
      const response = await apiInstance.get<AdminStats>('/v2/admin/stats');
      return response.data;
    },

    async getUsers(params?: {
      page?: number;
      limit?: number;
      role?: string;
      search?: string;
    }): Promise<{
      items: AdminUser[];
      pagination: {
        page: number;
        limit: number;
        total: number;
        totalPages: number;
      };
    }> {
      const response = await apiInstance.get<{
        items: AdminUser[];
        pagination: {
          page: number;
          limit: number;
          total: number;
          totalPages: number;
        };
      }>('/v2/admin/users', { params });
      return response.data;
    },

    async updateUser(
      userId: number,
      data: UpdateUserRequest
    ): Promise<AdminUser> {
      const response = await apiInstance.put<AdminUser>(
        `/v2/admin/users/${userId}`,
        data
      );
      return response.data;
    },

    async deleteUser(userId: number): Promise<void> {
      const response = await apiInstance.delete<void>(
        `/v2/admin/users/${userId}`
      );
      return response.data;
    },
  },
};
