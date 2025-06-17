import type { RootState } from '@/app/providers/redux';
import { Link } from '@/shared/components/Link';
import { PageWrapper } from '@/shared/components/PageWrapper/ui/PageWrapper';
import {
  Text,
  TextAlign,
  TextSize,
  TextWeight,
} from '@/shared/components/Text';
import { useAppDispatch, useAuth, useLogout } from '@/shared/hooks';
import { toggleSidebar } from '@/widgets/Sidebar/model/slice/sidebarSlice';
import { LogOut } from 'lucide-react';
import { useEffect, useRef } from 'react';
import { useSelector } from 'react-redux';
import { toast } from 'react-toastify';
import styles from './Profile.module.scss';

const Profile = () => {
  const dispatch = useAppDispatch();
  const isOpen = useSelector((state: RootState) => state.sidebar.isOpen);
  const logoutMutation = useLogout();
  const handleLogout = () => {
    logoutMutation.mutate();
    dispatch(toggleSidebar());
  };

  const { user } = useAuth();
  const toastShownRef = useRef(false);

  useEffect(() => {
    if (user?.email && !toastShownRef.current) {
      toast.success(`ПРИВЕТ ${user.email.split('@')[0]}!`);
      toastShownRef.current = true;
    }
  }, [user]);

  return (
    <PageWrapper>
      <div className={styles.profile}>
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
    </PageWrapper>
  );
};

export default Profile;
