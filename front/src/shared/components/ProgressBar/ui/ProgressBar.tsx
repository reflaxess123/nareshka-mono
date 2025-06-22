import { AlertTriangle, CheckCircle2, Clock } from 'lucide-react';
import React from 'react';
import styles from './ProgressBar.module.scss';

type ProgressStatus =
  | 'not_started'
  | 'in_progress'
  | 'completed'
  | 'struggling';
type ProgressSize = 'small' | 'medium' | 'large';

interface ProgressBarProps {
  /** Процент завершения (0-100) */
  percentage: number;
  /** Статус прогресса */
  status?: ProgressStatus;
  /** Размер прогресс-бара */
  size?: ProgressSize;
  /** Показывать ли лейбл с процентами */
  showLabel?: boolean;
  /** Заголовок */
  title?: string;
  /** Текущее значение */
  current?: number;
  /** Максимальное значение */
  total?: number;
  /** Показывать ли дополнительную статистику */
  showStats?: boolean;
  /** Количество попыток */
  attempts?: number;
  /** Время, потраченное в минутах */
  timeSpent?: number;
  /** CSS класс */
  className?: string;
}

const ProgressBar: React.FC<ProgressBarProps> = ({
  percentage,
  status = 'in_progress',
  size = 'medium',
  showLabel = false,
  title,
  current,
  total,
  showStats = false,
  attempts,
  timeSpent,
  className,
}) => {
  const clampedPercentage = Math.max(0, Math.min(100, percentage));

  const getStatusIcon = () => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className={styles.icon} />;
      case 'struggling':
        return <AlertTriangle className={styles.icon} />;
      case 'in_progress':
        return <Clock className={styles.icon} />;
      default:
        return null;
    }
  };

  const formatTime = (minutes: number) => {
    if (minutes < 60) return `${minutes}м`;
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    return `${hours}ч ${remainingMinutes}м`;
  };

  if (title || showStats) {
    return (
      <div className={`${styles.progressContainer} ${className || ''}`}>
        {title && (
          <div className={styles.progressHeader}>
            <span>{title}</span>
            <span className={styles.percentage}>
              {Math.round(clampedPercentage)}%
            </span>
          </div>
        )}

        <div className={`${styles.progressBar} ${styles[size]}`}>
          <div
            className={`${styles.fill} ${styles[status]}`}
            style={{ width: `${clampedPercentage}%` }}
          >
            {showLabel && (
              <span className={styles.label}>
                {Math.round(clampedPercentage)}%
              </span>
            )}
          </div>
        </div>

        {(showStats || current !== undefined || total !== undefined) && (
          <div className={styles.progressFooter}>
            <div className={styles.stats}>
              {current !== undefined && total !== undefined && (
                <span className={styles.stat}>
                  {current} из {total}
                </span>
              )}
              {attempts !== undefined && (
                <span className={styles.stat}>
                  {getStatusIcon()}
                  {attempts} попыток
                </span>
              )}
              {timeSpent !== undefined && timeSpent > 0 && (
                <span className={styles.stat}>
                  <Clock className={styles.icon} />
                  {formatTime(timeSpent)}
                </span>
              )}
            </div>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className={`${styles.progressBar} ${styles[size]} ${className || ''}`}>
      <div
        className={`${styles.fill} ${styles[status]}`}
        style={{ width: `${clampedPercentage}%` }}
      >
        {showLabel && (
          <span className={styles.label}>{Math.round(clampedPercentage)}%</span>
        )}
      </div>
    </div>
  );
};

export default ProgressBar;
