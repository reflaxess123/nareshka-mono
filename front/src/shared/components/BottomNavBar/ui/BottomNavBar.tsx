import { AppRoutes } from '@/app/providers/router';
import { Link } from '@/shared/components/Link';
import { useAuth } from '@/shared/hooks';
import clsx from 'clsx';
import { Bird, Brain, Home, LogIn, User } from 'lucide-react';
import { useLocation } from 'react-router-dom';
import styles from './BottomNavBar.module.scss';

interface BottomNavBarProps {
  onOpenLogin?: () => void;
}

export const BottomNavBar = ({ onOpenLogin }: BottomNavBarProps) => {
  const { isAuthenticated } = useAuth();
  const { pathname } = useLocation();

  const links = [
    { href: AppRoutes.HOME, icon: <Home />, text: 'Главная' },
    { href: AppRoutes.THEORY, icon: <Brain />, text: 'Теория' },
    { href: AppRoutes.TASKS, icon: <Bird />, text: 'Нарешка' },
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
    </nav>
  );
};
