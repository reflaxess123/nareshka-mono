import React from 'react';
import { Link } from 'react-router-dom';
import type { InterviewRecordResponseType } from '../../../shared/api/generated/api';
import styles from './InterviewCard.module.scss';

interface InterviewCardProps {
  interview: InterviewRecordResponseType;
}

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

export const InterviewCard: React.FC<InterviewCardProps> = ({ interview }) => {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };

  const renderDifficulty = (level: number | null) => {
    if (!level) return null;
    return (
      <span className={`${styles.difficulty} ${styles[`difficulty-${level}`]}`}>
        {'★'.repeat(level)}{'☆'.repeat(5 - level)} {DIFFICULTY_LABELS[level as keyof typeof DIFFICULTY_LABELS]}
      </span>
    );
  };

  const renderTechnologies = (technologies: string[]) => {
    if (!technologies || technologies.length === 0) return null;
    
    return (
      <div className={styles.technologies}>
        {technologies.slice(0, 3).map((tech, index) => (
          <span key={index} className={styles.tech}>
            {tech}
          </span>
        ))}
        {technologies.length > 3 && (
          <span className={styles.techMore}>+{technologies.length - 3}</span>
        )}
      </div>
    );
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
        {interview.stage_number && (
          <span className={styles.stage}>
            Этап: {STAGE_LABELS[interview.stage_number as keyof typeof STAGE_LABELS] || interview.stage_number}
          </span>
        )}
        
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

      {renderDifficulty(interview.difficulty_level)}
      {renderTechnologies(interview.technologies)}

      <div className={styles.content}>
        <p>{interview.content.substring(0, 200)}...</p>
      </div>

      <div className={styles.footer}>
        <Link to={`/interviews/${interview.id}`} className={styles.readMore}>
          Читать полностью →
        </Link>
        
        {interview.telegram_author && (
          <span className={styles.author}>@{interview.telegram_author}</span>
        )}
      </div>
    </div>
  );
};