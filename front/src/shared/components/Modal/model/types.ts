export interface ModalItem {
  id: string;
  component: React.ReactNode;
  isOpen: boolean;
}

export interface ModalContextType {
  modals: ModalItem[];
  openModal: (id: string, component: React.ReactNode) => void;
  closeModal: (id: string) => void;
  removeModal: (id: string) => void;
}
