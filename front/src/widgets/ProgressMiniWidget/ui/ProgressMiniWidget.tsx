import progressApi, { type UserDetailedProgress } from '@/shared/api/progress';
import { ProgressBar } from '@/shared/components/ProgressBar';
import { Clock, TrendingUp } from 'lucide-react';
import React, { useEffect, useState } from 'react';
import styles from './ProgressMiniWidget.module.scss';

interface ProgressMiniWidgetProps {
  userId?: number;
  size?: 'compact' | 'normal' | 'expanded';
  showCategories?: boolean;
  clickable?: boolean;
  onClick?: () => void;
  className?: string;
}

const ProgressMiniWidget: React.FC<ProgressMiniWidgetProps> = ({
  userId,
  size = 'normal',
  showCategories = false,
  clickable = false,
  onClick,
  className,
}) => {
  const [progressData, setProgressData] = useState<UserDetailedProgress | null>(
    null
  );
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProgress = async () => {
      try {
        setLoading(true);
        setError(null);

        const data = userId
          ? await progressApi.getUserProgress(userId)
          : await progressApi.getMyProgress();

        setProgressData(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Ошибка загрузки');
      } finally {
        setLoading(false);
      }
    };

    fetchProgress();
  }, [userId]);

  const isActive = progressData?.lastActivityDate
    ? Date.now() - new Date(progressData.lastActivityDate).getTime() <
      7 * 24 * 60 * 60 * 1000 // 7 дней
    : false;

  const overallProgress =
    progressData?.categoryProgress && progressData.categoryProgress.length > 0
      ? progressData.categoryProgress.reduce(
          (sum, cat) => sum + cat.completionRate,
          0
        ) / progressData.categoryProgress.length
      : 0;

  if (loading) {
    return (
      <div
        className={`${styles.miniWidget} ${styles[size]} ${className || ''}`}
      >
        <div className={styles.loading}>
          <Clock className={styles.spinner} />
          Загрузка...
        </div>
      </div>
    );
  }

  if (error || !progressData) {
    return (
      <div
        className={`${styles.miniWidget} ${styles[size]} ${className || ''}`}
      >
        <div className={styles.error}>{error || 'Нет данных'}</div>
      </div>
    );
  }

  return (
    <div
      className={`
        ${styles.miniWidget} 
        ${styles[size]} 
        ${clickable ? styles.clickable : ''} 
        ${className || ''}
      `}
      onClick={clickable ? onClick : undefined}
    >
      {/* Заголовок */}
      <div className={styles.header}>
        <div className={styles.title}>
          <TrendingUp className={styles.icon} />
          Прогресс
        </div>
        <div
          className={`${styles.badge} ${isActive ? styles.active : styles.inactive}`}
        >
          {isActive ? 'Активен' : 'Неактивен'}
        </div>
      </div>

      {/* Основная статистика */}
      <div className={styles.stats}>
        <div className={styles.stat}>
          <div className={styles.value}>{progressData.totalTasksSolved}</div>
          <div className={styles.label}>Решено</div>
        </div>

        <div className={styles.divider}></div>

        <div className={styles.stat}>
          <div className={styles.value}>
            {Math.round(progressData.overallStats.successRate)}%
          </div>
          <div className={styles.label}>Успех</div>
        </div>

        <div className={styles.divider}></div>

        <div className={styles.stat}>
          <div className={styles.value}>
            {Math.round(
              progressData.overallStats.totalAttempts /
                Math.max(progressData.totalTasksSolved, 1)
            )}
          </div>
          <div className={styles.label}>Попыток</div>
        </div>
      </div>

      {/* Общий прогресс */}
      <div className={styles.progressSection}>
        <div className={styles.progressLabel}>
          <span>Общий прогресс</span>
          <span className={styles.percentage}>
            {Math.round(overallProgress)}%
          </span>
        </div>
        <ProgressBar
          percentage={overallProgress}
          status={
            overallProgress === 100
              ? 'completed'
              : overallProgress > 60
                ? 'in_progress'
                : overallProgress > 20
                  ? 'struggling'
                  : 'not_started'
          }
          size="small"
          showLabel={false}
        />
      </div>

      {/* Категории (опционально) */}
      {showCategories && progressData.categoryProgress.length > 0 && (
        <div className={styles.categories}>
          {progressData.categoryProgress
            .slice(0, 3)
            .sort((a, b) => b.completionRate - a.completionRate)
            .map((category, index) => (
              <div key={index} className={styles.category}>
                <div className={styles.categoryName}>
                  {category.mainCategory}
                  {category.subCategory && ` • ${category.subCategory}`}
                </div>
                <div className={styles.categoryProgress}>
                  {Math.round(category.completionRate)}%
                </div>
              </div>
            ))}
        </div>
      )}
    </div>
  );
};

export default ProgressMiniWidget;
