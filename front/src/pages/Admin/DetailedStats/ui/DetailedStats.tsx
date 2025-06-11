import { ButtonVariant } from '@/shared/components/Button/model/types';
import { Button } from '@/shared/components/Button/ui/Button';
import { PageWrapper } from '@/shared/components/PageWrapper/ui/PageWrapper';
import { Text, TextSize } from '@/shared/components/Text';
import { useDetailedStats } from '@/shared/hooks/useAdminAPI';
import { BarChart3, FileText, Target, TrendingUp, Users } from 'lucide-react';
import styles from './DetailedStats.module.scss';

export const DetailedStats = () => {
  const {
    data: stats,
    isLoading: loading,
    error,
    refetch,
  } = useDetailedStats();

  const formatTime = (minutes: number) => {
    if (minutes < 60) return `${Math.round(minutes)} мин`;
    const hours = Math.floor(minutes / 60);
    const mins = Math.round(minutes % 60);
    return `${hours}ч ${mins}м`;
  };

  const formatUptime = (hours: number) => {
    if (hours < 24) return `${Math.round(hours)} ч`;
    const days = Math.floor(hours / 24);
    const remainingHours = Math.round(hours % 24);
    return `${days}д ${remainingHours}ч`;
  };

  const formatPercentage = (value: number) => {
    return `${(value * 100).toFixed(1)}%`;
  };

  if (loading) {
    return (
      <PageWrapper>
        <div className={styles.detailedStats}>
          <div className={styles.loading}>
            <BarChart3 size={48} className={styles.loadingIcon} />
            <Text
              text="📊 Загрузка детальной статистики..."
              size={TextSize.LG}
            />
          </div>
        </div>
      </PageWrapper>
    );
  }

  if (error || !stats) {
    return (
      <PageWrapper>
        <div className={styles.detailedStats}>
          <div className={styles.error}>
            <Text text="❌ Ошибка загрузки" size={TextSize.LG} />
            <Text
              text={error instanceof Error ? error.message : 'Нет данных'}
              size={TextSize.MD}
            />
            <Button onClick={() => refetch()} variant={ButtonVariant.PRIMARY}>
              Попробовать снова
            </Button>
          </div>
        </div>
      </PageWrapper>
    );
  }

  return (
    <PageWrapper>
      <div className={styles.detailedStats}>
        <div className={styles.header}>
          <div className={styles.titleSection}>
            <BarChart3 size={32} className={styles.titleIcon} />
            <div>
              <Text text="📊 Детальная статистика" size={TextSize.LG} />
              <Text
                text="Расширенные метрики и аналитика системы"
                size={TextSize.MD}
                className={styles.subtitle}
              />
            </div>
          </div>

          <div className={styles.actions}>
            <Button
              onClick={() => refetch()}
              variant={ButtonVariant.SECONDARY}
              disabled={loading}
            >
              🔄 Обновить
            </Button>
            <button className={styles.actionButton}>
              📊 Подробная статистика
            </button>
            <button className={styles.actionButton}>
              👥 Управление пользователями
            </button>
          </div>
        </div>

        <div className={styles.statsGrid}>
          {/* Пользователи */}
          <div className={styles.statsSection}>
            <div className={styles.sectionHeader}>
              <Users size={24} />
              <Text text="👥 Пользователи" size={TextSize.LG} />
            </div>

            <div className={styles.metricsGrid}>
              <div className={styles.metricCard}>
                <div className={styles.metricValue}>{stats.users.total}</div>
                <div className={styles.metricLabel}>Всего пользователей</div>
              </div>

              <div className={styles.metricCard}>
                <div className={styles.metricValue}>
                  {stats.users.activeThisMonth}
                </div>
                <div className={styles.metricLabel}>Активных в месяце</div>
              </div>

              <div className={styles.metricCard}>
                <div className={styles.metricValue}>
                  {stats.users.newThisWeek}
                </div>
                <div className={styles.metricLabel}>Новых за неделю</div>
              </div>

              <div className={styles.metricCard}>
                <div className={styles.metricValue}>
                  {formatTime(stats.users.avgSessionTime)}
                </div>
                <div className={styles.metricLabel}>Среднее время сессии</div>
              </div>
            </div>
          </div>

          {/* Контент */}
          <div className={styles.statsSection}>
            <div className={styles.sectionHeader}>
              <FileText size={24} />
              <Text text="📚 Контент" size={TextSize.LG} />
            </div>

            <div className={styles.metricsGrid}>
              <div className={styles.metricCard}>
                <div className={styles.metricValue}>
                  {stats.content.totalBlocks}
                </div>
                <div className={styles.metricLabel}>Всего блоков</div>
              </div>

              <div className={styles.metricCard}>
                <div className={styles.metricValue}>
                  {stats.content.totalTheoryCards}
                </div>
                <div className={styles.metricLabel}>Карточек теории</div>
              </div>

              <div className={styles.metricCard}>
                <div className={styles.metricValue}>
                  {stats.content.categoriesCount}
                </div>
                <div className={styles.metricLabel}>Категорий</div>
              </div>

              <div className={styles.metricCard}>
                <div className={styles.metricValue}>
                  {stats.content.avgBlocksPerFile.toFixed(1)}
                </div>
                <div className={styles.metricLabel}>Блоков на файл</div>
              </div>
            </div>
          </div>

          {/* Прогресс */}
          <div className={styles.statsSection}>
            <div className={styles.sectionHeader}>
              <Target size={24} />
              <Text text="📈 Прогресс" size={TextSize.LG} />
            </div>

            <div className={styles.metricsGrid}>
              <div className={styles.metricCard}>
                <div className={styles.metricValue}>
                  {stats.progress.totalContentProgress}
                </div>
                <div className={styles.metricLabel}>Прогресс контента</div>
              </div>

              <div className={styles.metricCard}>
                <div className={styles.metricValue}>
                  {stats.progress.totalTheoryProgress}
                </div>
                <div className={styles.metricLabel}>Прогресс теории</div>
              </div>

              <div className={styles.metricCard}>
                <div className={styles.metricValue}>
                  {stats.progress.avgProgressPerUser.toFixed(1)}
                </div>
                <div className={styles.metricLabel}>
                  Среднее на пользователя
                </div>
              </div>
            </div>

            {/* Топ активных пользователей */}
            {stats.progress.mostActiveUsers.length > 0 && (
              <div className={styles.topList}>
                <Text
                  text="🏆 Самые активные пользователи"
                  size={TextSize.MD}
                />
                <div className={styles.topItems}>
                  {stats.progress.mostActiveUsers
                    .slice(0, 5)
                    .map((user, index) => (
                      <div key={user.email} className={styles.topItem}>
                        <span className={styles.topRank}>#{index + 1}</span>
                        <span className={styles.topName}>{user.email}</span>
                        <span className={styles.topValue}>
                          {user.progressCount}
                        </span>
                      </div>
                    ))}
                </div>
              </div>
            )}
          </div>

          {/* Система */}
          <div className={styles.statsSection}>
            <div className={styles.sectionHeader}>
              <TrendingUp size={24} />
              <Text text="⚙️ Система" size={TextSize.LG} />
            </div>

            <div className={styles.metricsGrid}>
              <div className={styles.metricCard}>
                <div className={styles.metricValue}>
                  {formatUptime(stats.system.uptime)}
                </div>
                <div className={styles.metricLabel}>Время работы</div>
              </div>

              <div className={styles.metricCard}>
                <div className={styles.metricValue}>
                  {stats.system.responseTime}мс
                </div>
                <div className={styles.metricLabel}>Время ответа</div>
              </div>

              <div className={styles.metricCard}>
                <div className={styles.metricValue}>
                  {formatPercentage(stats.system.errorRate)}
                </div>
                <div className={styles.metricLabel}>Уровень ошибок</div>
              </div>

              <div className={styles.metricCard}>
                <div className={styles.metricValue}>
                  {stats.system.apiCalls24h}
                </div>
                <div className={styles.metricLabel}>API-вызовов за 24ч</div>
              </div>
            </div>
          </div>

          {/* Топ категории */}
          {stats.progress.topCategories.length > 0 && (
            <div className={styles.statsSection}>
              <div className={styles.sectionHeader}>
                <Target size={24} />
                <Text text="📂 Популярные категории" size={TextSize.LG} />
              </div>

              <div className={styles.topList}>
                <div className={styles.topItems}>
                  {stats.progress.topCategories
                    .slice(0, 10)
                    .map((category, index) => (
                      <div key={category.category} className={styles.topItem}>
                        <span className={styles.topRank}>#{index + 1}</span>
                        <span className={styles.topName}>
                          {category.category}
                        </span>
                        <span className={styles.topValue}>
                          {category.progressCount}
                        </span>
                      </div>
                    ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </PageWrapper>
  );
};
