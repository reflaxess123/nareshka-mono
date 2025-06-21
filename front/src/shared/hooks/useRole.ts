import {
  canUseAdvancedFilters,
  isAdmin as checkIsAdmin,
  isGuest as checkIsGuest,
  isUser as checkIsUser,
  hasNareshkaPlusSubscription,
  hasRole,
  type UserRole,
} from '@/entities/User';
import { useAuth } from './useAuth';

export const useRole = () => {
  const { user } = useAuth();
  const userRole: UserRole = user?.role || 'GUEST';

  const isAdmin = checkIsAdmin(userRole);
  const isUser = checkIsUser(userRole);
  const isGuest = checkIsGuest(userRole);

  const checkRole = (requiredRole: UserRole): boolean => {
    return hasRole(userRole, requiredRole);
  };

  const hasNareshkaPlus = hasNareshkaPlusSubscription(user);
  const canUseFilters = canUseAdvancedFilters(user);

  return {
    userRole,
    isAdmin,
    isUser,
    isGuest,
    checkRole,
    hasNareshkaPlus,
    canUseFilters,
  };
};
