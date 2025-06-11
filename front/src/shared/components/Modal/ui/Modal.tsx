import clsx from 'clsx';
import { AnimatePresence, motion } from 'framer-motion';
import styles from './Modal.module.scss';

enum ModalSize {
  SM = 'sm',
  MD = 'md',
  LG = 'lg',
}

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
  size?: ModalSize;
  closeOnOverlay?: boolean;
  closeOnEsc?: boolean;
}

export const Modal = ({
  children,
  isOpen,
  onClose,
  size = ModalSize.MD,
  closeOnOverlay = true,
  closeOnEsc = true,
}: ModalProps) => {
  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          className={clsx(styles.modal, styles[size.toLowerCase()])}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.3 }}
          onClick={closeOnOverlay ? onClose : undefined}
          onKeyDown={
            closeOnEsc ? (e) => e.key === 'Escape' && onClose() : undefined
          }
          role="dialog"
          aria-modal="true"
          tabIndex={-1}
        >
          <motion.div
            className={styles.modalContent}
            initial={{ opacity: 0, y: 0, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 0, scale: 0.95 }}
            transition={{ duration: 0.3, ease: 'easeOut' }}
            onClick={(e) => e.stopPropagation()}
          >
            {children}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};
