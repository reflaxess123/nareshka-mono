import type { RootState } from '@/app/providers/redux';
import { Link } from '@/shared/components/Link';
import { PageWrapper } from '@/shared/components/PageWrapper/ui/PageWrapper';
import {
  Text,
  TextAlign,
  TextSize,
  TextWeight,
} from '@/shared/components/Text';
import { useAppDispatch, useLogout } from '@/shared/hooks';
import { toggleSidebar } from '@/widgets/Sidebar/model/slice/sidebarSlice';
import { UserProgressDashboard } from '@/widgets/UserProgressDashboard';
import { LogOut } from 'lucide-react';
import { useSelector } from 'react-redux';
import styles from './Profile.module.scss';

const Profile = () => {
  const dispatch = useAppDispatch();
  const isOpen = useSelector((state: RootState) => state.sidebar.isOpen);
  const logoutMutation = useLogout();
  const handleLogout = () => {
    logoutMutation.mutate();
    dispatch(toggleSidebar());
  };

  return (
    <PageWrapper>
      <div className={styles.profile}>
        <div className={styles.header}>
          <Text
            text="Профиль"
            size={TextSize.XXL}
            weight={TextWeight.MEDIUM}
            align={TextAlign.CENTER}
          />
          <Link
            text="Выйти"
            className={styles.link}
            icon={<LogOut size={24} />}
            isParentHovered={isOpen}
            onClick={handleLogout}
            variant="sidebar"
          />
        </div>

        <div className={styles.progressSection}>
          <UserProgressDashboard />
        </div>
      </div>
    </PageWrapper>
  );
};

export default Profile;
