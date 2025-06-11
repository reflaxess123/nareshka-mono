import { AppRoutes } from '@/app/providers/router';
import { isAdmin } from '@/entities/User/model/types';
import { Link } from '@/shared/components/Link';
import { useTheme } from '@/shared/context/ThemeContext';
import { useAuth } from '@/shared/hooks';
import { useLogout } from '@/shared/hooks/useAuth';
import { AnimatePresence, motion } from 'framer-motion';
import {
  Bird,
  Brain,
  Home,
  LogIn,
  LogOut,
  Moon,
  Shield,
  Sun,
  User,
} from 'lucide-react';
import styles from './MobileMenu.module.scss';

interface MobileMenuProps {
  isOpen: boolean;
  onClose: () => void;
  onOpenLogin?: () => void;
}

export const MobileMenu = ({
  isOpen,
  onClose,
  onOpenLogin,
}: MobileMenuProps) => {
  const logoutMutation = useLogout();
  const { isAuthenticated, user } = useAuth();
  const { theme, setTheme } = useTheme();

  const handleOpenLogin = () => {
    if (onOpenLogin) {
      onOpenLogin();
    }
    onClose();
  };

  const handleLogout = () => {
    logoutMutation.mutate();
    onClose();
  };

  const handleLinkClick = () => {
    onClose();
  };

  const handleThemeToggle = () => {
    setTheme(theme === 'light' ? 'dark' : 'light');
  };

  const getThemeIcon = () => {
    return theme === 'light' ? <Sun size={64} /> : <Moon size={64} />;
  };

  const getThemeText = () => {
    return theme === 'light' ? 'Светлая' : 'Темная';
  };

  // Проверяем, является ли пользователь администратором
  const userIsAdmin = user?.role && isAdmin(user.role);

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Overlay для закрытия меню */}
          <motion.div
            className={styles.overlay}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />

          {/* Само меню */}
          <motion.div
            className={styles.mobileMenu}
            initial={{ x: '-100%' }}
            animate={{ x: 0 }}
            exit={{ x: '-100%' }}
            transition={{ type: 'tween', duration: 0.3 }}
          >
            <div className={styles.menuContent}>
              <div className={styles.linksTop}>
                <Link
                  text="Главная"
                  className={styles.link}
                  icon={<Home size={64} />}
                  to="/"
                  onClick={handleLinkClick}
                  isParentHovered={true}
                  size="large"
                  variant="sidebar"
                />

                {/* Админка - только для администраторов */}
                {userIsAdmin && (
                  <Link
                    text="Админка"
                    className={styles.link}
                    icon={<Shield size={64} />}
                    to={AppRoutes.ADMIN_PANEL}
                    onClick={handleLinkClick}
                    isParentHovered={true}
                    size="large"
                    variant="sidebar"
                  />
                )}

                {/* Теория - доступна всем */}
                <Link
                  text="Теория"
                  className={styles.link}
                  icon={<Brain size={64} />}
                  to={AppRoutes.THEORY}
                  onClick={handleLinkClick}
                  isParentHovered={true}
                  size="large"
                  variant="sidebar"
                />

                {/* Нарешка - доступна всем */}
                <Link
                  text="Нарешка"
                  className={styles.link}
                  icon={<Bird size={64} />}
                  to={AppRoutes.TASKS}
                  onClick={handleLinkClick}
                  isParentHovered={true}
                  size="large"
                  variant="sidebar"
                />

                {/* Чат - только для авторизованных пользователей */}
              </div>

              <div className={styles.linksBottom}>
                <Link
                  text={getThemeText()}
                  className={styles.link}
                  icon={getThemeIcon()}
                  onClick={() => {
                    handleThemeToggle();
                    handleLinkClick();
                  }}
                  isParentHovered={true}
                  size="large"
                  variant="sidebar"
                />
                {isAuthenticated ? (
                  <Link
                    text={user?.email || ''}
                    className={styles.link}
                    icon={<User size={64} />}
                    to={AppRoutes.PROFILE}
                    onClick={handleLinkClick}
                    isParentHovered={true}
                    size="large"
                    variant="sidebar"
                  />
                ) : (
                  <Link
                    text="Войти"
                    className={styles.link}
                    icon={<LogIn size={64} />}
                    onClick={handleOpenLogin}
                    isParentHovered={true}
                    size="large"
                    variant="sidebar"
                  />
                )}
                {isAuthenticated && (
                  <Link
                    text="Выйти"
                    className={styles.link}
                    icon={<LogOut size={64} />}
                    onClick={handleLogout}
                    isParentHovered={true}
                    size="large"
                    variant="sidebar"
                  />
                )}
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};
