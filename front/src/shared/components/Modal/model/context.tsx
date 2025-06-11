import { createContext, type ReactNode, useState } from 'react';
import type { ModalContextType, ModalItem } from './types';

const ModalContext = createContext<ModalContextType | undefined>(undefined);

export const ModalProvider = ({ children }: { children: ReactNode }) => {
  const [modals, setModals] = useState<ModalItem[]>([]);

  const openModal = (id: string, component: ReactNode) => {
    setModals((prev) => {
      const existing = prev.find((modal) => modal.id === id);
      if (existing) {
        return prev.map((modal) =>
          modal.id === id ? { ...modal, isOpen: true } : modal
        );
      }
      return [...prev, { id, component, isOpen: true }];
    });
  };

  const closeModal = (id: string) => {
    setModals((prev) =>
      prev.map((modal) =>
        modal.id === id ? { ...modal, isOpen: false } : modal
      )
    );

    setTimeout(() => {
      setModals((prev) => prev.filter((modal) => modal.id !== id));
    }, 300);
  };

  const removeModal = (id: string) => {
    setModals((prev) => prev.filter((modal) => modal.id !== id));
  };

  return (
    <ModalContext.Provider
      value={{ modals, openModal, closeModal, removeModal }}
    >
      {children}
    </ModalContext.Provider>
  );
};

export { ModalContext };
