import progressApi, { type UserDetailedProgress } from '@/shared/api/progress';
import { ProgressBar } from '@/shared/components/ProgressBar';
import {
  Activity,
  BookOpen,
  Clock,
  Target,
  TrendingUp,
  Zap,
} from 'lucide-react';
import React, { useEffect, useState } from 'react';
import styles from './UserProgressDashboard.module.scss';

interface UserProgressDashboardProps {
  userId?: number;
  compact?: boolean;
}

const UserProgressDashboard: React.FC<UserProgressDashboardProps> = ({
  userId,
  compact = false,
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
        setError(err instanceof Error ? err.message : 'Ошибка загрузки данных');
      } finally {
        setLoading(false);
      }
    };

    fetchProgress();
  }, [userId]);

  const formatTime = (minutes: number) => {
    if (minutes < 60) return `${minutes}м`;
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    return `${hours}ч ${remainingMinutes}м`;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ru-RU', {
      day: 'numeric',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed':
        return 'Завершено';
      case 'in_progress':
        return 'В процессе';
      case 'struggling':
        return 'Сложности';
      case 'not_started':
        return 'Не начато';
      default:
        return status;
    }
  };

  const getStatusClass = (status: string) => {
    switch (status) {
      case 'completed':
        return 'completed';
      case 'in_progress':
        return 'inProgress';
      case 'struggling':
        return 'struggling';
      case 'not_started':
        return 'notStarted';
      default:
        return 'notStarted';
    }
  };

  if (loading) {
    return (
      <div className={styles.loading}>
        <Clock className={styles.spinner} />
        Загрузка прогресса...
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.error}>
        <p>Ошибка: {error}</p>
      </div>
    );
  }

  if (!progressData) {
    return (
      <div className={styles.error}>
        <p>Данные о прогрессе не найдены</p>
      </div>
    );
  }

  return (
    <div className={styles.dashboard}>
      {/* Заголовок */}
      <div className={styles.header}>
        <div className={styles.title}>
          <TrendingUp className={styles.icon} />
          Прогресс обучения
        </div>
        {progressData.lastActivityDate && (
          <div className={styles.lastActivity}>
            Последняя активность: {formatDate(progressData.lastActivityDate)}
          </div>
        )}
      </div>

      {/* Общая статистика */}
      <div className={styles.overallStats}>
        <div className={styles.statCard}>
          <div className={styles.statValue}>
            {progressData.totalTasksSolved}
          </div>
          <div className={styles.statLabel}>Решено задач</div>
          <div className={styles.statDescription}>Всего выполнено</div>
        </div>

        <div className={styles.statCard}>
          <div className={styles.statValue}>
            {Math.round(progressData.overallStats.successRate)}%
          </div>
          <div className={styles.statLabel}>Успешность</div>
          <div className={styles.statDescription}>
            {progressData.overallStats.successfulAttempts} из{' '}
            {progressData.overallStats.totalAttempts}
          </div>
        </div>

        <div className={styles.statCard}>
          <div className={styles.statValue}>
            {Math.round(
              progressData.overallStats.totalAttempts /
                Math.max(progressData.totalTasksSolved, 1)
            )}
          </div>
          <div className={styles.statLabel}>Среднее попыток</div>
          <div className={styles.statDescription}>На задачу</div>
        </div>

        <div className={styles.statCard}>
          <div className={styles.statValue}>
            {formatTime(progressData.overallStats.totalTimeSpent)}
          </div>
          <div className={styles.statLabel}>Время</div>
          <div className={styles.statDescription}>Общее время изучения</div>
        </div>
      </div>

      {/* Прогресс по категориям */}
      {progressData.categoryProgress.length > 0 && (
        <div className={styles.categoriesSection}>
          <div className={styles.sectionTitle}>
            <BookOpen className={styles.icon} />
            Прогресс по категориям
          </div>

          <div className={styles.categoriesGrid}>
            {progressData.categoryProgress.map((category, index) => (
              <div key={index} className={styles.categoryCard}>
                <div className={styles.categoryHeader}>
                  <div className={styles.categoryName}>
                    {category.mainCategory}
                    {category.subCategory && ` • ${category.subCategory}`}
                  </div>
                  <div
                    className={`${styles.statusBadge} ${styles[getStatusClass(category.status)]}`}
                  >
                    {getStatusText(category.status)}
                  </div>
                </div>

                <ProgressBar
                  percentage={category.completionRate}
                  status={
                    category.status as
                      | 'not_started'
                      | 'in_progress'
                      | 'completed'
                      | 'struggling'
                  }
                  title=""
                  current={category.completedTasks}
                  total={category.totalTasks}
                  showStats
                  attempts={Math.round(category.averageAttempts)}
                  timeSpent={Math.round(category.totalTimeSpent)}
                />

                <div className={styles.categoryStats}>
                  <div className={styles.stat}>
                    <Target className={styles.icon} />
                    {category.completedTasks}/{category.totalTasks}
                  </div>
                  <div className={styles.stat}>
                    <Zap className={styles.icon} />
                    {Math.round(category.averageAttempts)} попыток
                  </div>
                  <div className={styles.stat}>
                    <Clock className={styles.icon} />
                    {formatTime(category.totalTimeSpent)}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Недавняя активность */}
      {!compact && (
        <div className={styles.recentActivity}>
          <div className={styles.sectionTitle}>
            <Activity className={styles.icon} />
            Недавняя активность
          </div>

          {progressData.recentAttempts.length > 0 ? (
            <div className={styles.activityList}>
              {progressData.recentAttempts.slice(0, 5).map((attempt) => (
                <div
                  key={attempt.id}
                  className={`${styles.activityItem} ${attempt.isSuccessful ? styles.success : styles.error}`}
                >
                  <div className={styles.activityHeader}>
                    <div className={styles.activityTitle}>
                      {attempt.isSuccessful ? '✅' : '❌'} Задача{' '}
                      {attempt.blockId}
                    </div>
                    <div className={styles.activityTime}>
                      {formatDate(attempt.createdAt)}
                    </div>
                  </div>
                  <div className={styles.activityDescription}>
                    Попытка #{attempt.attemptNumber} • {attempt.language}
                    {attempt.durationMinutes &&
                      ` • ${attempt.durationMinutes}м`}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className={styles.emptyState}>
              Пока нет активности. Начните решать задачи!
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default UserProgressDashboard;
