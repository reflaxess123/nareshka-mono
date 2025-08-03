import React from 'react';
import styles from './InterviewSkeleton.module.scss';

export const InterviewSkeleton: React.FC = () => {
  return (
    <div className={styles.skeletonItem}>
      <div className={styles.mainContent}>
        <div className={styles.header}>
          <div className={styles.skeletonCompany}></div>
          <div className={styles.skeletonDateTime}>
            <div className={styles.skeletonDate}></div>
            <div className={styles.skeletonTime}></div>
          </div>
        </div>

        <div className={styles.skeletonPosition}></div>
        
        <div className={styles.skeletonPreview}>
          <div className={styles.skeletonLine}></div>
          <div className={styles.skeletonLine} style={{ width: '80%' }}></div>
          <div className={styles.skeletonLine} style={{ width: '60%' }}></div>
        </div>

        <div className={styles.skeletonMetadata}>
          <div className={styles.skeletonTag}></div>
          <div className={styles.skeletonTag}></div>
        </div>
      </div>

      <div className={styles.skeletonActions}>
        <div className={styles.skeletonButton}></div>
      </div>
    </div>
  );
};

interface InterviewSkeletonListProps {
  count?: number;
}

export const InterviewSkeletonList: React.FC<InterviewSkeletonListProps> = ({ 
  count = 5 
}) => {
  return (
    <>
      {Array.from({ length: count }, (_, index) => (
        <InterviewSkeleton key={index} />
      ))}
    </>
  );
};