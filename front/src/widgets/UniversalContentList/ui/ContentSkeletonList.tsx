import React from 'react';
import styles from './ContentSkeletonList.module.scss';

interface ContentSkeletonListProps {
  count?: number;
  viewMode?: 'cards' | 'list' | 'compact';
}

export const ContentSkeletonList: React.FC<ContentSkeletonListProps> = ({ 
  count = 6,
  viewMode = 'cards' 
}) => {
  const skeletons = Array.from({ length: count }, (_, i) => i);

  if (viewMode === 'compact') {
    return (
      <>
        {skeletons.map(index => (
          <div key={index} className={styles.skeletonCompact}>
            <div className={styles.compactLeft}>
              <div className={styles.icon} />
              <div className={styles.title} />
            </div>
            <div className={styles.compactRight}>
              <div className={styles.meta} />
              <div className={styles.action} />
            </div>
          </div>
        ))}
      </>
    );
  }

  if (viewMode === 'list') {
    return (
      <>
        {skeletons.map(index => (
          <div key={index} className={styles.skeletonList}>
            <div className={styles.listLeft}>
              <div className={styles.icon} />
              <div className={styles.content}>
                <div className={styles.title} />
                <div className={styles.description} />
                <div className={styles.meta} />
              </div>
            </div>
            <div className={styles.actions}>
              <div className={styles.action} />
              <div className={styles.action} />
            </div>
          </div>
        ))}
      </>
    );
  }

  // Карточки (по умолчанию)
  return (
    <>
      {skeletons.map(index => (
        <div key={index} className={styles.skeleton}>
          <div className={styles.header}>
            <div className={styles.typeLabel} />
            <div className={styles.badge} />
          </div>
          <div className={styles.body}>
            <div className={styles.title} />
            <div className={styles.description} />
            <div className={styles.meta}>
              <div className={styles.metaItem} />
              <div className={styles.metaItem} />
            </div>
          </div>
          <div className={styles.footer}>
            <div className={styles.primaryAction} />
            <div className={styles.secondaryAction} />
          </div>
        </div>
      ))}
    </>
  );
};