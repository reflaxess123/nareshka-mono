import { hasRole, type UserRole } from '@/entities/User/model/types';
import { useAuth } from '@/shared/hooks';
import type { ReactNode } from 'react';

interface RoleGuardProps {
  children: ReactNode;
  requiredRole: UserRole;
  fallback?: ReactNode;
}

export const RoleGuard = ({
  children,
  requiredRole,
  fallback = <div>У вас нет доступа к этой функции</div>,
}: RoleGuardProps) => {
  const { user } = useAuth();

  // Если пользователь не авторизован, считаем его гостем
  const userRole: UserRole = user?.role || 'GUEST';

  // Проверяем права доступа
  const hasAccess = hasRole(userRole, requiredRole);

  return hasAccess ? <>{children}</> : <>{fallback}</>;
};
