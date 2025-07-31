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


  return (
    <div className={styles.card}>
      <div className={styles.header}>
        <h3 className={styles.company}>{interview.company_name}</h3>
        <span className={styles.date}>{formatDate(interview.interview_date)}</span>
      </div>

      {interview.position && (
        <div className={styles.position}>{interview.position}</div>
      )}

      <div className={styles.metadata}>
        {interview.duration_minutes && (
          <span className={styles.duration}>
            {interview.duration_minutes} мин
          </span>
        )}

        {interview.questions_count && (
          <span className={styles.questions}>
            {interview.questions_count} вопросов
          </span>
        )}
      </div>

      <div className={styles.content}>
        <p>{interview.content.substring(0, 200)}...</p>
      </div>

      <div className={styles.footer}>
        <Link to={`/interviews/${interview.id}`} className={styles.readMore}>
          Читать полностью →
        </Link>
        
      </div>
    </div>
  );
};