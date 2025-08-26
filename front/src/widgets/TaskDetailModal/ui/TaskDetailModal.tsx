import React from 'react';
import { MarkdownContent } from '@/shared/components/MarkdownContent';
import type { TaskDetail } from '@/types/mindmap';
import styles from '@/widgets/ContentBlockCard/ui/ContentBlockCard.module.scss';

interface TaskDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  task: TaskDetail | null;
}

export const TaskDetailModal: React.FC<TaskDetailModalProps> = ({
  isOpen,
  onClose,
  task,
}) => {
  if (!isOpen || !task) return null;

  return (
    <div style={{ position: 'fixed', inset: 0, zIndex: 9999 }}>
      <div
        style={{
          position: 'fixed',
          inset: 0,
          background: 'rgba(30,32,38,0.65)',
          zIndex: 1,
        }}
        onClick={onClose}
      />
      <div
        style={{
          position: 'fixed',
          inset: 0,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 2,
        }}
      >
        <article
          className={`${styles.contentBlockCard} ${styles.default}`}
          style={{
            minWidth: 0,
            maxWidth: 700,
            width: '95vw',
            maxHeight: '90vh',
            overflowY: 'auto',
            position: 'relative',
          }}
        >
          <button
            onClick={onClose}
            aria-label="Закрыть"
            style={{
              position: 'absolute',
              top: 18,
              right: 18,
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              zIndex: 10,
            }}
          >
            <svg
              width={28}
              height={28}
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
          <header className={styles.header}>
            <div className={styles.titleRow}>
              <h2 className={styles.title}>{task.title}</h2>
            </div>
            <div className={styles.meta}>
              <span className={styles.category}>
                {task.category}
                {task.subcategory ? ` / ${task.subcategory}` : ''}
              </span>
            </div>
          </header>
          <div className={styles.content}>
            {task.text_content && (
              <div className={styles.textContent}>
                <MarkdownContent content={task.text_content} />
              </div>
            )}
            {task.code_content && (
              <div className={styles.codeBox}>
                <pre>
                  <code>{task.code_content}</code>
                </pre>
              </div>
            )}
          </div>
        </article>
      </div>
    </div>
  );
};
