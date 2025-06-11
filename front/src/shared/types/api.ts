// Базовые типы API
export interface ApiError {
  message: string;
  code?: string;
  details?: Record<string, unknown>;
}

export interface ApiResponse<TData = unknown> {
  data: TData;
  message?: string;
  timestamp: string;
}

export interface PaginatedResponse<TData = unknown> {
  data: TData[];
  pagination: {
    page: number;
    limit: number;
    totalItems: number;
    totalPages: number;
    hasNext: boolean;
    hasPrev: boolean;
  };
}

export interface ApiListParams {
  page?: number;
  limit?: number;
  search?: string;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

// Типы для HTTP методов
export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

export interface RequestConfig {
  method: HttpMethod;
  url: string;
  data?: unknown;
  params?: Record<string, unknown>;
  headers?: Record<string, string>;
}

// Статусы запросов
export type RequestStatus = 'idle' | 'pending' | 'fulfilled' | 'rejected';

export interface RequestState<TData = unknown> {
  data: TData | null;
  status: RequestStatus;
  error: string | null;
}
