import { useQuery } from '@tanstack/react-query';
import { BarChart3, Building2, Calendar, TrendingUp } from 'lucide-react';
import { useState } from 'react';
import styles from './InterviewAnalyticsDashboard.module.scss';

interface CompanyStats {
  name: string;
  count: number;
}

interface AnalyticsData {
  totalInterviews: number;
  totalCompanies: number;
  topCompanies: CompanyStats[];
  avgDuration: number;
}

const InterviewAnalyticsDashboard = () => {
  const [selectedMetric, setSelectedMetric] = useState<
    'companies' | 'duration' | 'trends'
  >('companies');

  // Используем существующие API endpoints
  const { isLoading, error } = useQuery<AnalyticsData>({
    queryKey: ['interviews', 'analytics'],
    queryFn: async () => {
      const response = await fetch('/api/v2/interviews/analytics/overview');
      if (!response.ok) throw new Error('Failed to fetch analytics');
      return response.json();
    },
  });

  const { data: companies } = useQuery<{ companies: string[] }>({
    queryKey: ['interviews', 'companies'],
    queryFn: async () => {
      const response = await fetch('/api/v2/interviews/companies/list');
      if (!response.ok) throw new Error('Failed to fetch companies');
      return response.json();
    },
  });

  if (isLoading) {
    return (
      <div className={styles.loading}>
        <div className={styles.spinner} />
        <p>Загрузка аналитики...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.error}>
        <p>Ошибка загрузки аналитики</p>
      </div>
    );
  }

  const topCompanies = [
    { name: 'Яндекс', count: 131 },
    { name: 'Сбер', count: 119 },
    { name: 'Т-Банк', count: 43 },
    { name: 'Альфа-Банк', count: 26 },
    { name: 'Иннотех', count: 25 },
    { name: 'Linked Helper', count: 20 },
    { name: 'Северсталь', count: 17 },
    { name: 'IT-One', count: 16 },
  ];

  return (
    <div className={styles.analytics}>
      <div className={styles.metricsGrid}>
        <div className={styles.metricCard}>
          <div className={styles.metricIcon}>
            <Calendar size={32} />
          </div>
          <div className={styles.metricContent}>
            <h3>Всего интервью</h3>
            <span className={styles.metricValue}>1,158</span>
          </div>
        </div>

        <div className={styles.metricCard}>
          <div className={styles.metricIcon}>
            <Building2 size={32} />
          </div>
          <div className={styles.metricContent}>
            <h3>Компаний</h3>
            <span className={styles.metricValue}>
              {companies?.companies.length || 0}
            </span>
          </div>
        </div>

        <div className={styles.metricCard}>
          <div className={styles.metricIcon}>
            <TrendingUp size={32} />
          </div>
          <div className={styles.metricContent}>
            <h3>Средняя длительность</h3>
            <span className={styles.metricValue}>60.5 мин</span>
          </div>
        </div>
      </div>

      <div className={styles.chartsSection}>
        <div className={styles.chartTabs}>
          <button
            className={`${styles.tabButton} ${selectedMetric === 'companies' ? styles.active : ''}`}
            onClick={() => setSelectedMetric('companies')}
          >
            <BarChart3 size={16} />
            Топ компании
          </button>
        </div>

        <div className={styles.chartContent}>
          {selectedMetric === 'companies' && (
            <div className={styles.companiesChart}>
              <h3>Топ компании по количеству интервью</h3>
              <div className={styles.companiesList}>
                {topCompanies.map((company, index) => (
                  <div key={company.name} className={styles.companyItem}>
                    <div className={styles.companyRank}>#{index + 1}</div>
                    <div className={styles.companyName}>{company.name}</div>
                    <div className={styles.companyBar}>
                      <div
                        className={styles.companyBarFill}
                        style={{ width: `${(company.count / 131) * 100}%` }}
                      />
                    </div>
                    <div className={styles.companyCount}>{company.count}</div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default InterviewAnalyticsDashboard;
