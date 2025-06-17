import type { RootState } from '@/app/providers/redux/model/store';
import { AppRoutes } from '@/app/providers/router';
import { isAdmin } from '@/entities/User/model/types';
import { Link } from '@/shared/components/Link';
import { useAppDispatch, useAuth } from '@/shared/hooks';
import { Bird, Brain, Code, Map, Shield } from 'lucide-react';
import { useSelector } from 'react-redux';
import { toggleSidebar } from '../model/slice/sidebarSlice';
import styles from './Sidebar.module.scss';

export const Sidebar = ({ children }: { children: React.ReactNode }) => {
  const dispatch = useAppDispatch();
  const isOpen = useSelector((state: RootState) => state.sidebar.isOpen);
  const { user } = useAuth();

  const userIsAdmin = user?.role && isAdmin(user.role);

  return (
    <div className={styles.sidebarWrapper}>
      <div
        className={styles.sidebar}
        onMouseEnter={() => dispatch(toggleSidebar())}
        onMouseLeave={() => dispatch(toggleSidebar())}
      >
        <div className={styles.linksTop}>
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

          <Link
            text="Теория"
            className={styles.link}
            icon={<Brain size={24} />}
            isParentHovered={isOpen}
            to={AppRoutes.THEORY}
            variant="sidebar"
          />

          <Link
            text="Карта"
            className={styles.link}
            icon={<Map size={24} />}
            isParentHovered={isOpen}
            to={AppRoutes.MINDMAP}
            variant="sidebar"
          />

          <Link
            text="Редактор кода"
            className={styles.link}
            icon={<Code size={24} />}
            isParentHovered={isOpen}
            to={AppRoutes.CODE_EDITOR}
            variant="sidebar"
          />

          <Link
            text="Нарешка"
            className={styles.link}
            icon={<Bird size={24} />}
            isParentHovered={isOpen}
            to={AppRoutes.TASKS}
            variant="sidebar"
          />
        </div>

        <div className={styles.linksBottom}></div>
      </div>
      <div className={styles.pageWrapper}>{children}</div>
    </div>
  );
};
