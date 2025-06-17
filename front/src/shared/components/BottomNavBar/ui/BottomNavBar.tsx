import { AppRoutes } from '@/app/providers/router';
import { Link } from '@/shared/components/Link';
import clsx from 'clsx';
import {
  Bird,
  Brain,
  Code,
  Home,
  Map,
} from 'lucide-react';
import { useLocation } from 'react-router-dom';
import styles from './BottomNavBar.module.scss';

export const BottomNavBar = () => {
  const { pathname } = useLocation();
  const links = [
    { href: AppRoutes.HOME, icon: <Home />, text: 'Админка' },
    { href: AppRoutes.THEORY, icon: <Brain />, text: 'Теория' },
    { href: AppRoutes.TASKS, icon: <Bird />, text: 'Нарешка' },
    { href: AppRoutes.CODE_EDITOR, icon: <Code />, text: 'Кодер' },
    { href: AppRoutes.MINDMAP, icon: <Map />, text: 'Карта' },
  ];

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
    </nav>
  );
};
