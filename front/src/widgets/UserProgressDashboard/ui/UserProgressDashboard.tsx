import progressApi, { type UserDetailedProgress } from '@/shared/api/progress';
import { ProgressBar } from '@/shared/components/ProgressBar';
import axios from 'axios';
import {
  Activity,
  BookOpen,
  CheckCircle,
  Clock,
  Target,
  TrendingUp,
} from 'lucide-react';
import React, { useEffect, useState } from 'react';
import styles from './UserProgressDashboard.module.scss';

interface UserProgressDashboardProps {
  userId?: number;
  compact?: boolean;
}

function toMoscowTime(dateString: string) {
  const date = new Date(dateString);
  // Получаем UTC-время и прибавляем 3 часа
  const msk = new Date(date.getTime() + 3 * 60 * 60 * 1000);
  return (
    msk.toLocaleString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    }) + ' МСК'
  );
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
    const source = axios.CancelToken.source();
    const fetchProgress = async () => {
      try {
        setLoading(true);
        setError(null);

        const data = userId
          ? await progressApi.getUserProgress(userId, {
              cancelToken: source.token,
            })
          : await progressApi.getMyProgress({ cancelToken: source.token });

        setProgressData(data);
      } catch (err) {
        if (axios.isCancel(err)) {
          // Не показываем ошибку отмены
          return;
        }
        setError(err instanceof Error ? err.message : 'Ошибка загрузки данных');
      } finally {
        setLoading(false);
      }
    };

    fetchProgress();
    return () => {
      source.cancel('Component unmounted or effect cleaned up');
    };
  }, [userId]);

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
      case 'not_started':
        return 'notStarted';
      default:
        return 'notStarted';
    }
  };

  // Фиктивные названия задач не нужны - будем использовать реальные данные из API

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

      {/* Упрощенная общая статистика */}
      <div className={styles.overallStats}>
        <div className={styles.statCard}>
          <div className={styles.statValue}>
            {progressData.overallStats?.totalTasksSolved || 0}
          </div>
          <div className={styles.statLabel}>Решено задач</div>
          <div className={styles.statDescription}>
            из {progressData.overallStats?.totalTasksAvailable || 0} доступных
          </div>
        </div>

        <div className={styles.statCard}>
          <div className={styles.statValue}>
            {Math.round(progressData.overallStats?.completionRate || 0)}%
          </div>
          <div className={styles.statLabel}>Прогресс</div>
          <div className={styles.statDescription}>Общий процент завершения</div>
        </div>
      </div>

      {/* Прогресс по категориям */}
      {progressData.groupedCategoryProgress &&
        progressData.groupedCategoryProgress.length > 0 && (
          <div className={styles.categoriesSection}>
            <div className={styles.sectionTitle}>
              <BookOpen className={styles.icon} />
              Прогресс по категориям
            </div>

            <div className={styles.categoriesGrid}>
              {(progressData.groupedCategoryProgress || []).map(
                (category, index) => (
                  <div key={index} className={styles.categoryCard}>
                    <div className={styles.categoryHeader}>
                      <div className={styles.categoryName}>
                        {category.mainCategory}
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
                      }
                      title=""
                      current={category.completedTasks}
                      total={category.totalTasks}
                      showStats={false}
                    />

                    {/* Общий прогресс категории */}
                    <div className={styles.tasksIndicator}>
                      <div className={styles.indicatorLabel}>
                        Общий прогресс:
                      </div>
                      <div className={styles.progressSummary}>
                        <span className={styles.progressText}>
                          {category.completedTasks > 0
                            ? `Решено ${category.completedTasks} из ${category.totalTasks} задач`
                            : `Доступно ${category.totalTasks} задач`}
                        </span>
                      </div>
                    </div>

                    {/* Подкатегории */}
                    <div className={styles.subCategoriesContainer}>
                      <div className={styles.subCategoriesLabel}>
                        Подкатегории:
                      </div>
                      <div className={styles.subCategoriesList}>
                        {category.subCategories.map((subCategory, subIndex) => (
                          <div
                            key={subIndex}
                            className={styles.subCategoryItem}
                          >
                            <div className={styles.subCategoryHeader}>
                              <span className={styles.subCategoryName}>
                                {subCategory.subCategory}
                              </span>
                              <span className={styles.subCategoryProgress}>
                                {subCategory.completedTasks}/
                                {subCategory.totalTasks}
                              </span>
                            </div>
                            <div className={styles.subCategoryBar}>
                              <div
                                className={styles.subCategoryFill}
                                style={{
                                  width: `${subCategory.completionRate}%`,
                                }}
                              />
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className={styles.categoryStats}>
                      <div className={styles.stat}>
                        <CheckCircle className={styles.icon} />
                        <span className={styles.solvedCount}>
                          {category.completedTasks}
                        </span>
                        <span className={styles.statSeparator}>/</span>
                        <span className={styles.totalCount}>
                          {category.totalTasks}
                        </span>
                        <span className={styles.statLabel}>задач</span>
                      </div>
                      <div className={styles.stat}>
                        <Target className={styles.icon} />
                        <span className={styles.progressPercent}>
                          {Math.round(category.completionRate)}%
                        </span>
                      </div>
                    </div>
                  </div>
                )
              )}
            </div>
          </div>
        )}

      {/* Недавняя активность с нормальными названиями */}
      {!compact && (
        <div className={styles.recentActivity}>
          <div className={styles.sectionTitle}>
            <Activity className={styles.icon} />
            Недавняя активность
          </div>

          {progressData.recentActivity &&
          progressData.recentActivity.length > 0 ? (
            <div className={styles.activityList}>
              {(progressData.recentActivity || []).map((activity) => (
                <div key={activity.id} className={styles.activityItem}>
                  <span>Совершена попытка</span>
                  <span>{activity.blockTitle}</span>
                  <span
                    style={{
                      marginLeft: 'auto',
                      color: '#aaa',
                      fontSize: 12,
                    }}
                  >
                    {toMoscowTime(activity.timestamp)}
                  </span>
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
