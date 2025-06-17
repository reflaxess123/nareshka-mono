import { AppRoutes } from '@/app/providers/router';
import { LoginForm } from '@/features/LoginForm';
import { Link } from '@/shared/components/Link';
import { useTheme } from '@/shared/context/ThemeContext';
import { useAuth, useModal } from '@/shared/hooks';
import { useLogout } from '@/shared/hooks/useAuth';
import clsx from 'clsx';
import {
  Brain,
  ChevronDown,
  LogIn,
  LogOut,
  Moon,
  Settings,
  Sun,
  User,
} from 'lucide-react';
import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './Navbar.module.scss';

export const Navbar = () => {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const { isAuthenticated, user } = useAuth();
  const { theme, setTheme } = useTheme();
  const loginModal = useModal('login-modal');
  const logoutMutation = useLogout();
  const navigate = useNavigate();

  const handleOpenLogin = () => {
    loginModal.open(<LoginForm />);
  };

  const handleLogout = () => {
    logoutMutation.mutate();
    setIsDropdownOpen(false);
  };

  const handleThemeToggle = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setTheme(theme === 'light' ? 'dark' : 'light');
  };

  const handleNavigateToProfile = () => {
    navigate(AppRoutes.PROFILE);
    setIsDropdownOpen(false);
  };

  const handleNavigateToSettings = () => {
    navigate(AppRoutes.SETTINGS);
    setIsDropdownOpen(false);
  };

  const getThemeIcon = () => {
    return theme === 'light' ? <Sun size={18} /> : <Moon size={18} />;
  };

  const getThemeText = () => {
    return theme === 'light' ? 'Светлая тема' : 'Темная тема';
  };

  const getUserInitials = () => {
    if (!user?.email) return 'U';
    return user.email.charAt(0).toUpperCase();
  };

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setIsDropdownOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  useEffect(() => {
    if (isAuthenticated) {
      loginModal.close();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated]);

  return (
    <nav className={styles.navbar}>
      <Link
        to={AppRoutes.THEORY}
        className={styles.logo}
        text="Nareshka"
        icon={<Brain size={28} />}
        variant="default"
      />

      {isAuthenticated ? (
        <div className={styles.userMenu} ref={dropdownRef}>
          <button
            className={styles.userButton}
            onClick={() => setIsDropdownOpen(!isDropdownOpen)}
          >
            <div className={styles.avatar}>{getUserInitials()}</div>
            <div className={styles.userInfo}>
              <div className={styles.userName}>Пользователь</div>
              <div className={styles.userEmail}>{user?.email}</div>
            </div>
            <ChevronDown size={16} color="var(--text-primary)" />
          </button>

          <div
            className={clsx(styles.dropdown, {
              [styles.open]: isDropdownOpen,
            })}
          >
            <button
              className={styles.dropdownItem}
              onClick={handleNavigateToProfile}
            >
              <User size={18} />
              Профиль
            </button>

            <button className={styles.dropdownItem} onClick={handleThemeToggle}>
              {getThemeIcon()}
              {getThemeText()}
            </button>

            <button
              className={styles.dropdownItem}
              onClick={handleNavigateToSettings}
            >
              <Settings size={18} />
              Настройки
            </button>

            <button className={styles.dropdownItem} onClick={handleLogout}>
              <LogOut size={18} />
              Выйти
            </button>
          </div>
        </div>
      ) : (
        <button className={styles.loginButton} onClick={handleOpenLogin}>
          <LogIn size={18} />
          Войти
        </button>
      )}
    </nav>
  );
};
