import { AppRoutes } from '@/app/providers/router';
import { Link } from '@/shared/components/Link';
import { useTheme } from '@/shared/context/ThemeContext';
import { useAuth } from '@/shared/hooks';
import clsx from 'clsx';
import { Bird, Brain, Code, Home, LogIn, Moon, Sun, User } from 'lucide-react';
import { useLocation } from 'react-router-dom';
import styles from './BottomNavBar.module.scss';

interface BottomNavBarProps {
  onOpenLogin?: () => void;
}

export const BottomNavBar = ({ onOpenLogin }: BottomNavBarProps) => {
  const { isAuthenticated } = useAuth();
  const { pathname } = useLocation();
  const { theme, setTheme } = useTheme();
  const handleThemeToggle = () => {
    setTheme(theme === 'light' ? 'dark' : 'light');
  };

  const getThemeIcon = () => {
    return theme === 'light' ? <Sun size={24} /> : <Moon size={24} />;
  };

  const getThemeText = () => {
    return theme === 'light' ? 'Светлая' : 'Темная';
  };

  const links = [
    { href: AppRoutes.HOME, icon: <Home />, text: 'Админка' },
    { href: AppRoutes.THEORY, icon: <Brain />, text: 'Теория' },
    { href: AppRoutes.TASKS, icon: <Bird />, text: 'Нарешка' },
    { href: AppRoutes.CODE_EDITOR, icon: <Code />, text: 'Кодер' },
  ];

  const handleOpenLogin = () => {
    onOpenLogin?.();
  };

  return (
    <nav className={styles.bottomNav}>
      {links.map((link) => (
        <Link
          key={link.href}
          to={link.href}
          icon={link.icon}
          text={link.text}
          variant="bottomBar"
          isActive={pathname === link.href}
          className={styles.link}
          iconClassName={clsx({ [styles.isSelected]: pathname === link.href })}
          size="small"
        />
      ))}
      {isAuthenticated ? (
        <Link
          to={AppRoutes.PROFILE}
          icon={<User />}
          text="Профиль"
          variant="bottomBar"
          isActive={pathname === AppRoutes.PROFILE}
          className={styles.link}
          iconClassName={clsx({
            [styles.isSelected]: pathname === AppRoutes.PROFILE,
          })}
          size="small"
        />
      ) : (
        <Link
          onClick={handleOpenLogin}
          icon={<LogIn />}
          text="Войти"
          variant="bottomBar"
          className={styles.link}
          size="small"
        />
      )}
      <Link
        text={getThemeText()}
        className={styles.link}
        icon={getThemeIcon()}
        onClick={handleThemeToggle}
        variant="bottomBar"
        size="small"
      />
    </nav>
  );
};
