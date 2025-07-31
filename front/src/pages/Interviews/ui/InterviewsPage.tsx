import React from 'react';
import { InterviewsList } from '../../../widgets/InterviewsList';
import styles from './InterviewsPage.module.scss';

export const InterviewsPage: React.FC = () => {
  return (
    <div className={styles.page}>
      <InterviewsList />
    </div>
  );
};