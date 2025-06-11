import { AppRoutes } from '@/app/providers/router';
import {
  Text,
  TextAlign,
  TextSize,
  TextWeight,
} from '@/shared/components/Text';
import { useAdminStats } from '@/shared/hooks/useAdminAPI';
import { useNavigate } from 'react-router-dom';
import styles from './AdminDashboard.module.scss';

export const AdminDashboard = () => {
  const { data: stats, isLoading: loading, error, refetch } = useAdminStats();
  const navigate = useNavigate();

  const handleDetailedStats = () => {
    void navigate(AppRoutes.ADMIN_STATS);
  };

  const handleUserManagement = () => {
    void navigate(AppRoutes.ADMIN_USERS);
  };

  const handleRetry = () => {
    void refetch();
  };

  if (loading) {
    return (
      <div className={styles.dashboard}>
        <div className={styles.loading}>
          <Text
            text="⏳ Загрузка статистики..."
            size={TextSize.MD}
            align={TextAlign.CENTER}
          />
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.dashboard}>
        <div className={styles.error}>
          <Text
            text="❌ Ошибка"
            size={TextSize.LG}
            weight={TextWeight.MEDIUM}
            align={TextAlign.CENTER}
          />
          <Text
            text={error instanceof Error ? error.message : 'Неизвестная ошибка'}
            size={TextSize.MD}
            align={TextAlign.CENTER}
          />
          <button className={styles.retryButton} onClick={handleRetry}>
            Попробовать снова
          </button>
        </div>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className={styles.dashboard}>
        <div className={styles.error}>
          <Text
            text="📊 Нет данных"
            size={TextSize.LG}
            align={TextAlign.CENTER}
          />
        </div>
      </div>
    );
  }

  return (
    <div className={styles.dashboard}>
      <div className={styles.statsGrid}>
        {/* Статистика пользователей */}
        <div className={styles.statsCard}>
          <Text
            text="👥 Пользователи"
            size={TextSize.LG}
            weight={TextWeight.MEDIUM}
            align={TextAlign.CENTER}
          />
          <div className={styles.statsContent}>
            <div className={styles.statItem}>
              <span className={styles.statLabel}>Всего:</span>
              <span className={styles.statValue}>{stats.users.total}</span>
            </div>
            <div className={styles.statItem}>
              <span className={styles.statLabel}>Администраторы:</span>
              <span className={styles.statValue}>{stats.users.admins}</span>
            </div>
            <div className={styles.statItem}>
              <span className={styles.statLabel}>Пользователи:</span>
              <span className={styles.statValue}>
                {stats.users.regularUsers}
              </span>
            </div>
            <div className={styles.statItem}>
              <span className={styles.statLabel}>Гости:</span>
              <span className={styles.statValue}>{stats.users.guests}</span>
            </div>
          </div>
        </div>

        {/* Статистика контента */}
        <div className={styles.statsCard}>
          <Text
            text="📚 Контент"
            size={TextSize.LG}
            weight={TextWeight.MEDIUM}
            align={TextAlign.CENTER}
          />
          <div className={styles.statsContent}>
            <div className={styles.statItem}>
              <span className={styles.statLabel}>Файлы:</span>
              <span className={styles.statValue}>
                {stats.content.totalFiles}
              </span>
            </div>
            <div className={styles.statItem}>
              <span className={styles.statLabel}>Блоки:</span>
              <span className={styles.statValue}>
                {stats.content.totalBlocks}
              </span>
            </div>
            <div className={styles.statItem}>
              <span className={styles.statLabel}>Теория:</span>
              <span className={styles.statValue}>
                {stats.content.totalTheoryCards}
              </span>
            </div>
          </div>
        </div>

        {/* Статистика прогресса */}
        <div className={styles.statsCard}>
          <Text
            text="📊 Прогресс"
            size={TextSize.LG}
            weight={TextWeight.MEDIUM}
            align={TextAlign.CENTER}
          />
          <div className={styles.statsContent}>
            <div className={styles.statItem}>
              <span className={styles.statLabel}>Контент:</span>
              <span className={styles.statValue}>
                {stats.progress.totalContentProgress}
              </span>
            </div>
            <div className={styles.statItem}>
              <span className={styles.statLabel}>Теория:</span>
              <span className={styles.statValue}>
                {stats.progress.totalTheoryProgress}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Кнопки управления */}
      <div className={styles.actions}>
        <button className={styles.actionButton} onClick={() => void refetch()}>
          🔄 Обновить данные
        </button>
        <button className={styles.actionButton} onClick={handleDetailedStats}>
          📊 Подробная статистика
        </button>
        <button className={styles.actionButton} onClick={handleUserManagement}>
          👥 Управление пользователями
        </button>
      </div>
    </div>
  );
};
