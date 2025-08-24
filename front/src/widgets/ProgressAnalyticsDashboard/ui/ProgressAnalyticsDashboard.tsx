import progressApi, { type ProgressAnalytics } from '@/shared/api/progress';
import {
  AlertCircle,
  AlertTriangle,
  BarChart3,
  Clock,
  RefreshCw,
  Target,
  TrendingUp,
  Users,
  Zap,
} from 'lucide-react';
import React, { useEffect, useState } from 'react';
import styles from './ProgressAnalyticsDashboard.module.scss';

interface ProgressAnalyticsDashboardProps {
  autoRefresh?: boolean; 
}

const ProgressAnalyticsDashboard: React.FC<ProgressAnalyticsDashboardProps> = ({
  autoRefresh = false,
}) => {
  const [analytics, setAnalytics] = useState<ProgressAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchAnalytics = async (isRefresh = false) => {
    try {
      if (isRefresh) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }
      setError(null);

      const data = await progressApi.getAnalytics();
      setAnalytics(data);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Ошибка загрузки аналитики'
      );
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, []);

  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(() => {
        fetchAnalytics(true);
      }, 30000); 

      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const handleRefresh = () => {
    fetchAnalytics(true);
  };

  if (loading) {
    return (
      <div className={styles.loading}>
        <Clock className={styles.spinner} />
        Загрузка аналитики...
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.error}>
        <AlertCircle className={styles.errorIcon} />
        <div className={styles.errorTitle}>Ошибка загрузки</div>
        <div className={styles.errorMessage}>{error}</div>
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className={styles.error}>
        <div className={styles.errorTitle}>Данные не найдены</div>
      </div>
    );
  }

  return (
    <div className={styles.analytics}>
      {/* Заголовок */}
      <div className={styles.header}>
        <div className={styles.title}>
          <BarChart3 className={styles.icon} />
          Аналитика прогресса
        </div>
        <button
          className={styles.refreshButton}
          onClick={handleRefresh}
          disabled={refreshing}
        >
          <RefreshCw className={refreshing ? styles.spinner : ''} />
          {refreshing ? 'Обновление...' : 'Обновить'}
        </button>
      </div>

      {/* Общая статистика */}
      <div className={styles.overviewCards}>
        <div className={styles.card}>
          <div className={styles.cardIcon}>
            <Users />
          </div>
          <div className={styles.cardValue}>{analytics.totalUsers}</div>
          <div className={styles.cardLabel}>Всего пользователей</div>
          <div className={styles.cardDescription}>
            Активных: {analytics.activeUsers}
          </div>
        </div>

        <div className={styles.card}>
          <div className={styles.cardIcon}>
            <Target />
          </div>
          <div className={styles.cardValue}>{analytics.totalTasksSolved}</div>
          <div className={styles.cardLabel}>Решено задач</div>
          <div className={styles.cardDescription}>Всего выполнено</div>
        </div>

        <div className={styles.card}>
          <div className={styles.cardIcon}>
            <TrendingUp />
          </div>
          <div className={styles.cardValue}>
            {Math.round(analytics.averageTasksPerUser)}
          </div>
          <div className={styles.cardLabel}>Среднее на пользователя</div>
          <div className={styles.cardDescription}>Задач на пользователя</div>
        </div>

        <div className={styles.card}>
          <div className={styles.cardIcon}>
            <Zap />
          </div>
          <div className={styles.cardValue}>
            {Math.round((analytics.activeUsers / analytics.totalUsers) * 100)}%
          </div>
          <div className={styles.cardLabel}>Активность</div>
          <div className={styles.cardDescription}>
            Доля активных пользователей
          </div>
        </div>
      </div>

      {/* Диаграммы и списки */}
      <div className={styles.chartsSection}>
        {/* Популярные категории */}
        <div className={styles.chartCard}>
          <div className={styles.chartHeader}>
            <div className={styles.chartTitle}>Популярные категории</div>
            <TrendingUp className={styles.chartIcon} />
          </div>
          <div className={styles.chartContent}>
            {analytics.mostPopularCategories?.length > 0 ? (
              <div className={styles.categoryList}>
                {analytics.mostPopularCategories
                  .slice(0, 10)
                  .map((category, index) => (
                    <div key={index} className={styles.categoryItem}>
                      <div className={styles.categoryInfo}>
                        <div className={styles.categoryName}>
                          {category.mainCategory}
                        </div>
                        <div className={styles.categoryDetails}>
                          {category.subCategory && `${category.subCategory} • `}
                          #{index + 1} по популярности
                        </div>
                      </div>
                      <div className={styles.categoryValue}>
                        <div className={styles.value}>{category.completed}</div>
                        <div className={styles.metric}>решений</div>
                      </div>
                    </div>
                  ))}
              </div>
            ) : (
              <div className={styles.emptyState}>
                Нет данных о популярных категориях
              </div>
            )}
          </div>
        </div>

        {/* Проблемные области */}
        <div className={styles.chartCard}>
          <div className={styles.chartHeader}>
            <div className={styles.chartTitle}>Проблемные области</div>
            <AlertTriangle className={styles.chartIcon} />
          </div>
          <div className={styles.chartContent}>
            {analytics.strugglingAreas?.length > 0 ? (
              <div className={styles.categoryList}>
                {analytics.strugglingAreas.slice(0, 10).map((area, index) => (
                  <div key={index} className={styles.categoryItem}>
                    <div className={styles.categoryInfo}>
                      <div className={styles.categoryName}>
                        {area.mainCategory}
                      </div>
                      <div className={styles.categoryDetails}>
                        {area.subCategory && `${area.subCategory} • `}
                        Требует внимания
                      </div>
                    </div>
                    <div className={styles.categoryValue}>
                      <div className={styles.value}>
                        {Math.round(area.averageAttempts)}
                      </div>
                      <div className={styles.metric}>попыток</div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className={styles.emptyState}>Нет проблемных областей</div>
            )}
          </div>
        </div>
      </div>

      {/* Дополнительная информация */}
      <div className={styles.usersSection}>
        <div className={styles.sectionHeader}>
          <div className={styles.sectionTitle}>
            <Users className={styles.icon} />
            Активность пользователей
          </div>
          <div className={styles.userCount}>
            {analytics.activeUsers} из {analytics.totalUsers} активны
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProgressAnalyticsDashboard;
