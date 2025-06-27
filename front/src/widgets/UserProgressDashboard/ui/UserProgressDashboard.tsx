import progressApi, { type UserDetailedProgress } from '@/shared/api/progress';
import axios from 'axios';
import { Activity, Clock } from 'lucide-react';
import React, { useEffect, useState } from 'react';
import styles from './UserProgressDashboard.module.scss';

interface UserProgressDashboardProps {
  userId?: number;
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
}) => {
  const [progressData, setProgressData] = useState<UserDetailedProgress | null>(
    null
  );
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const isFirstEffectCall = React.useRef(true);

  useEffect(() => {
    if (import.meta.env.DEV && isFirstEffectCall.current) {
      isFirstEffectCall.current = false;
      return;
    }

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

  if (loading) {
    return (
      <div className={styles.loading}>
        <Clock className={styles.spinner} />
        Загрузка активности...
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
        <p>Данные о активности не найдены</p>
      </div>
    );
  }

  return (
    <div className={styles.dashboard}>
      {/* Недавняя активность */}
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
    </div>
  );
};

export default UserProgressDashboard;
