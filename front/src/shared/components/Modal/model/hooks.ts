import { useContext } from 'react';
import { ModalContext } from './context';

export const useModalContext = () => {
  const context = useContext(ModalContext);
  if (!context) {
    throw new Error('useModalContext must be used within ModalProvider');
  }
  return context;
};

export const useModal = (modalId: string) => {
  const { modals, openModal, closeModal, removeModal } = useModalContext();

  const modal = modals.find((m) => m.id === modalId);
  const isOpen = modal?.isOpen ?? false;

  const open = (component: React.ReactNode) => {
    openModal(modalId, component);
  };

  const close = () => {
    closeModal(modalId);
  };

  const remove = () => {
    removeModal(modalId);
  };

  return { isOpen, open, close, remove };
};
