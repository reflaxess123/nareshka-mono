export type UserRole = 'GUEST' | 'USER' | 'ADMIN';

export const ROLE_HIERARCHY: Record<UserRole, number> = {
  GUEST: 0,
  USER: 1,
  ADMIN: 2,
} as const;

export interface User {
  id: number;
  email: string;
  role: UserRole;
  createdAt: string;
  subscription?: {
    type: 'BASIC' | 'NARESHKA_PLUS';
    expiresAt?: string;
    isActive: boolean;
  };
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
}

export interface AdminStats {
  users: {
    total: number;
    admins: number;
    regularUsers: number;
    guests: number;
  };
  content: {
    totalFiles: number;
    totalBlocks: number;
    totalTheoryCards: number;
  };
  progress: {
    totalContentProgress: number;
    totalTheoryProgress: number;
  };
}

export interface AdminUser {
  id: number;
  email: string;
  role: UserRole;
  createdAt: string;
  updatedAt: string;
  lastActiveAt?: string;
}

export interface CreateUserRequest {
  email: string;
  password: string;
  role: UserRole;
}

export interface UpdateUserRequest {
  email?: string;
  password?: string;
  role?: UserRole;
}

export const hasRole = (
  userRole: UserRole,
  requiredRole: UserRole
): boolean => {
  return ROLE_HIERARCHY[userRole] >= ROLE_HIERARCHY[requiredRole];
};

export const isAdmin = (userRole: UserRole): boolean => userRole === 'ADMIN';
export const isUser = (userRole: UserRole): boolean => userRole === 'USER';
export const isGuest = (userRole: UserRole): boolean => userRole === 'GUEST';

export const hasNareshkaPlusSubscription = (
  user: User | null | undefined
): boolean => {
  if (!user) return false;
  return (
    user.subscription?.type === 'NARESHKA_PLUS' && user.subscription?.isActive
  );
};

export const canUseAdvancedFilters = (
  user: User | null | undefined
): boolean => {
  if (!user) return false;
  return isAdmin(user.role) || hasNareshkaPlusSubscription(user);
};
