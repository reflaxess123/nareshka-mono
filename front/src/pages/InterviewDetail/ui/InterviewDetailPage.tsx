import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useGetInterviewDetailApiV2InterviewsInterviewIdGet } from '../../../shared/api/generated/api';
import styles from './InterviewDetailPage.module.scss';


export const InterviewDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  
  const { data: interview, isLoading, error } = useGetInterviewDetailApiV2InterviewsInterviewIdGet(
    id!,
    {
      query: {
        enabled: !!id
      }
    }
  );

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ru-RU', {
      day: '2-digit',
      month: 'long',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };



  if (isLoading) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>
          Загрузка интервью...
        </div>
      </div>
    );
  }

  if (error || !interview) {
    return (
      <div className={styles.container}>
        <Link to="/interviews" className={styles.backButton}>
          ← Назад к списку
        </Link>
        <div className={styles.error}>
          Интервью не найдено или произошла ошибка при загрузке
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <Link to="/interviews" className={styles.backButton}>
        ← Назад к списку
      </Link>

      <div className={styles.header}>
        <h1 className={styles.company}>{interview.company_name}</h1>
        
        {interview.position && (
          <p className={styles.position}>{interview.position}</p>
        )}

        <div className={styles.metadata}>
          <div className={styles.metaItem}>
            <span>📅</span>
            <span className={styles.metaValue}>
              {formatDate(interview.interview_date)}
            </span>
          </div>

        </div>

      </div>

      <div className={styles.sidebar}>
        <div className={styles.mainContent}>
          <div className={styles.content}>
            <h2 className={styles.contentTitle}>Содержание интервью</h2>
            <div className={styles.contentText}>
              {interview.full_content}
            </div>
          </div>
        </div>

        <div className={styles.sidebarContent}>
          {/* Sidebar content removed */}
        </div>
      </div>
    </div>
  );
};