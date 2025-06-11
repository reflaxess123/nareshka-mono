import { Modal } from '@/shared/components/Modal';
import { useModalContext } from '@/shared/components/Modal/model/hooks';

export const ModalRenderer = () => {
  const { modals, closeModal } = useModalContext();

  return (
    <>
      {modals.map((modalItem) => (
        <Modal
          key={modalItem.id}
          isOpen={modalItem.isOpen}
          onClose={() => closeModal(modalItem.id)}
        >
          {modalItem.component}
        </Modal>
      ))}
    </>
  );
};
