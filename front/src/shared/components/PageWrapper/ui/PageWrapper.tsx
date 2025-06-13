import type { RootState } from '@/app/providers/redux/model/store';
import clsx from 'clsx';
import { useSelector } from 'react-redux';
import { BottomNavBar } from '../../BottomNavBar';
import styles from './PageWrapper.module.scss';

interface PageWrapperProps {
  children: React.ReactNode;
  onOpenLogin?: () => void;
  hideBottomBar?: boolean;
}

export const PageWrapper = ({
  children,
  onOpenLogin,
  hideBottomBar,
}: PageWrapperProps) => {
  const isOpen = useSelector((state: RootState) => state.sidebar.isOpen);

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
