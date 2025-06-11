import type { RootState } from '@/app/providers/redux/model/store';
import clsx from 'clsx';
import { useState } from 'react';
import { useSelector } from 'react-redux';
import BurgerButton from '../../BurgerButton';
import { MobileMenu } from '../../MobileMenu';
import styles from './PageWrapper.module.scss';

interface PageWrapperProps {
  children: React.ReactNode;
  onOpenLogin?: () => void;
}

export const PageWrapper = ({ children, onOpenLogin }: PageWrapperProps) => {
  const isOpen = useSelector((state: RootState) => state.sidebar.isOpen);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const handleBurgerClick = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  const handleMobileMenuClose = () => {
    setIsMobileMenuOpen(false);
  };

  return (
    <>
      <div
        className={clsx(styles.sidebarOverlay, {
          [styles.visible]: isOpen,
        })}
      />
      <div className={styles.pageWrapper}>
        <BurgerButton
          className={styles.burgerButton}
          onClick={handleBurgerClick}
          isActive={isMobileMenuOpen}
        />
        <MobileMenu
          isOpen={isMobileMenuOpen}
          onClose={handleMobileMenuClose}
          onOpenLogin={onOpenLogin}
        />
        {children}
      </div>
    </>
  );
};
