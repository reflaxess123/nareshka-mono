import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useGetInterviewDetailApiV2InterviewsInterviewIdGet } from '../../../shared/api/generated/api';
import styles from './InterviewDetailPage.module.scss';

const DIFFICULTY_LABELS = {
  1: 'Легко',
  2: 'Средне-',
  3: 'Средне',
  4: 'Средне+',
  5: 'Сложно'
};

const STAGE_LABELS = {
  1: 'Скрининг',
  2: 'Техническое',
  3: 'Системное',
  4: 'Финальное'
};

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

  const getDifficultyStars = (level?: number) => {
    if (!level) return null;
    return '★'.repeat(level) + '☆'.repeat(5 - level);
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

          {interview.stage_number && (
            <div className={styles.metaItem}>
              <span>🏃</span>
              <span className={styles.metaValue}>
                {STAGE_LABELS[interview.stage_number as keyof typeof STAGE_LABELS] || `Этап ${interview.stage_number}`}
              </span>
            </div>
          )}

          {interview.difficulty_level && (
            <div className={styles.metaItem}>
              <span>⭐</span>
              <span className={`${styles.metaValue} ${styles.difficulty}`}>
                {getDifficultyStars(interview.difficulty_level)} {DIFFICULTY_LABELS[interview.difficulty_level as keyof typeof DIFFICULTY_LABELS]}
              </span>
            </div>
          )}

          {interview.duration_minutes && (
            <div className={styles.metaItem}>
              <span>⏱️</span>
              <span className={styles.metaValue}>
                {interview.duration_minutes} минут
              </span>
            </div>
          )}

          {interview.questions_count && (
            <div className={styles.metaItem}>
              <span>❓</span>
              <span className={styles.metaValue}>
                {interview.questions_count} вопросов
              </span>
            </div>
          )}

          {interview.telegram_author && (
            <div className={styles.metaItem}>
              <span>👤</span>
              <span className={styles.metaValue}>
                {interview.telegram_author}
              </span>
            </div>
          )}
        </div>

        {interview.technologies.length > 0 && (
          <div className={styles.technologies}>
            {interview.technologies.map(tech => (
              <span key={tech} className={styles.tech}>
                {tech}
              </span>
            ))}
          </div>
        )}
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
          <div className={styles.infoCard}>
            <h3 className={styles.infoTitle}>Информация</h3>
            <ul className={styles.infoList}>
              <li className={styles.infoItem}>
                <span className={styles.infoLabel}>Компания</span>
                <span className={styles.infoValue}>{interview.company_name}</span>
              </li>
              
              {interview.position && (
                <li className={styles.infoItem}>
                  <span className={styles.infoLabel}>Позиция</span>
                  <span className={styles.infoValue}>{interview.position}</span>
                </li>
              )}

              <li className={styles.infoItem}>
                <span className={styles.infoLabel}>Дата</span>
                <span className={styles.infoValue}>
                  {new Date(interview.interview_date).toLocaleDateString('ru-RU')}
                </span>
              </li>

              {interview.stage_number && (
                <li className={styles.infoItem}>
                  <span className={styles.infoLabel}>Этап</span>
                  <span className={styles.infoValue}>
                    {STAGE_LABELS[interview.stage_number as keyof typeof STAGE_LABELS] || interview.stage_number}
                  </span>
                </li>
              )}

              {interview.difficulty_level && (
                <li className={styles.infoItem}>
                  <span className={styles.infoLabel}>Сложность</span>
                  <span className={`${styles.infoValue} ${styles.difficulty}`}>
                    {getDifficultyStars(interview.difficulty_level)}
                  </span>
                </li>
              )}

              {interview.duration_minutes && (
                <li className={styles.infoItem}>
                  <span className={styles.infoLabel}>Длительность</span>
                  <span className={styles.infoValue}>{interview.duration_minutes} мин</span>
                </li>
              )}

              {interview.questions_count && (
                <li className={styles.infoItem}>
                  <span className={styles.infoLabel}>Вопросов</span>
                  <span className={styles.infoValue}>{interview.questions_count}</span>
                </li>
              )}
            </ul>
          </div>

          {interview.extracted_urls.length > 0 && (
            <div className={styles.infoCard}>
              <h3 className={styles.infoTitle}>Ссылки</h3>
              <div className={styles.urls}>
                {interview.extracted_urls.map((url, index) => (
                  <a
                    key={index}
                    href={url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className={styles.url}
                  >
                    {url}
                  </a>
                ))}
              </div>
            </div>
          )}

          {interview.tags.length > 0 && (
            <div className={styles.infoCard}>
              <h3 className={styles.infoTitle}>Теги</h3>
              <div className={styles.technologies}>
                {interview.tags.map(tag => (
                  <span key={tag} className={styles.tech}>
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};