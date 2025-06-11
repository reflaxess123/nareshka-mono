import type { RootState } from '@/app/providers/redux/model/store';
import { AppRoutes } from '@/app/providers/router';
import { isAdmin } from '@/entities/User/model/types';
import { LoginForm } from '@/features/LoginForm';
import { Link } from '@/shared/components/Link';
import { useTheme } from '@/shared/context/ThemeContext';
import { useAppDispatch, useAuth, useModal } from '@/shared/hooks';
import { useLogout } from '@/shared/hooks/useAuth';
import {
  Bird,
  Brain,
  LogIn,
  LogOut,
  Moon,
  Shield,
  Sun,
  User,
} from 'lucide-react';
import { useEffect } from 'react';
import { useSelector } from 'react-redux';
import { toggleSidebar } from '../model/slice/sidebarSlice';
import styles from './Sidebar.module.scss';

export const Sidebar = ({ children }: { children: React.ReactNode }) => {
  const dispatch = useAppDispatch();
  const logoutMutation = useLogout();
  const isOpen = useSelector((state: RootState) => state.sidebar.isOpen);
  const { isAuthenticated, user } = useAuth();
  const { theme, setTheme } = useTheme();
  const loginModal = useModal('login-modal');

  const handleOpenLogin = () => {
    loginModal.open(<LoginForm />);
  };

  const handleLogout = () => {
    logoutMutation.mutate();
    dispatch(toggleSidebar());
  };

  const handleThemeToggle = () => {
    setTheme(theme === 'light' ? 'dark' : 'light');
  };

  const getThemeIcon = () => {
    return theme === 'light' ? <Sun size={24} /> : <Moon size={24} />;
  };

  const getThemeText = () => {
    return theme === 'light' ? 'Светлая' : 'Темная';
  };

  // Проверяем, является ли пользователь администратором
  const userIsAdmin = user?.role && isAdmin(user.role);

  useEffect(() => {
    if (isAuthenticated) {
      loginModal.close();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated]);

  return (
    <div className={styles.sidebarWrapper}>
      <div
        className={styles.sidebar}
        onMouseEnter={() => dispatch(toggleSidebar())}
        onMouseLeave={() => dispatch(toggleSidebar())}
      >
        <div className={styles.linksTop}>
          {/* Админка - только для администраторов */}
          {userIsAdmin && (
            <Link
              text="Админка"
              className={styles.link}
              icon={<Shield size={24} />}
              isParentHovered={isOpen}
              to={AppRoutes.ADMIN_PANEL}
              variant="sidebar"
            />
          )}

          {/* Теория - доступна всем */}
          <Link
            text="Теория"
            className={styles.link}
            icon={<Brain size={24} />}
            isParentHovered={isOpen}
            to={AppRoutes.THEORY}
            variant="sidebar"
          />

          {/* Нарешка - доступна всем */}
          <Link
            text="Нарешка"
            className={styles.link}
            icon={<Bird size={24} />}
            isParentHovered={isOpen}
            to={AppRoutes.TASKS}
            variant="sidebar"
          />

          {/* Чат - только для авторизованных пользователей */}
        </div>

        <div className={styles.linksBottom}>
          <Link
            text={getThemeText()}
            className={styles.link}
            icon={getThemeIcon()}
            isParentHovered={isOpen}
            onClick={handleThemeToggle}
            variant="sidebar"
          />

          {isAuthenticated ? (
            <Link
              text={user?.email || ''}
              className={styles.link}
              icon={<User size={24} />}
              isParentHovered={isOpen}
              to={AppRoutes.PROFILE}
              variant="sidebar"
            />
          ) : (
            <Link
              text="Войти"
              className={styles.link}
              icon={<LogIn size={24} />}
              isParentHovered={isOpen}
              onClick={handleOpenLogin}
              variant="sidebar"
            />
          )}
          {isAuthenticated && (
            <Link
              text="Выйти"
              className={styles.link}
              icon={<LogOut size={24} />}
              isParentHovered={isOpen}
              onClick={handleLogout}
              variant="sidebar"
            />
          )}
        </div>
      </div>
      <div className={styles.pageWrapper}>{children}</div>
    </div>
  );
};
