import type { RootState } from '@/app/providers/redux/model/store';
import { LoginForm } from '@/features/LoginForm';
import { useModal } from '@/shared/hooks';
import clsx from 'clsx';
import { useSelector } from 'react-redux';
import { BottomNavBar } from '../../BottomNavBar';
import styles from './PageWrapper.module.scss';

interface PageWrapperProps {
  children: React.ReactNode;
  hideBottomBar?: boolean;
}

export const PageWrapper = ({ children, hideBottomBar }: PageWrapperProps) => {
  const isOpen = useSelector((state: RootState) => state.sidebar.isOpen);
  const loginModal = useModal('login-modal');

  const onOpenLogin = () => {
    loginModal.open(<LoginForm />);
  };

  return (
    <>
      <div
        className={clsx(styles.sidebarOverlay, {
          [styles.visible]: isOpen,
        })}
      />
      <div className={styles.pageWrapper}>{children}</div>
      {!hideBottomBar && <BottomNavBar onOpenLogin={onOpenLogin} />}
    </>
  );
};
