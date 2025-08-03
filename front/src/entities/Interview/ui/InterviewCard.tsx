import React from 'react';
import { Link } from 'react-router-dom';
import type { InterviewRecordResponseType } from '../../../shared/api/generated/api';
import styles from './InterviewCard.module.scss';

interface InterviewCardProps {
  interview: InterviewRecordResponseType;
}


export const InterviewCard: React.FC<InterviewCardProps> = ({ interview }) => {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };

  const formatTime = (dateString: string) => {
    return new Date(dateString).toLocaleTimeString('ru-RU', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className={styles.listItem}>
      <div className={styles.mainContent}>
        <div className={styles.header}>
          <h3 className={styles.company}>{interview.company_name}</h3>
          <div className={styles.dateTime}>
            <span className={styles.date}>{formatDate(interview.interview_date)}</span>
            <span className={styles.time}>{formatTime(interview.interview_date)}</span>
          </div>
        </div>

        {/* Position display disabled */}

        <div className={styles.preview}>
          {interview.full_content.substring(0, 150)}...
        </div>

        <div className={styles.metadata}>
          {/* Tags display disabled */}
        </div>
      </div>

      <div className={styles.actions}>
        <Link to={`/interviews/${interview.id}`} className={styles.readMoreBtn}>
          Открыть
        </Link>
      </div>
    </div>
  );
};