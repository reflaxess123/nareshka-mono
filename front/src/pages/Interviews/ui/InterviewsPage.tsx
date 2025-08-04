import React, { useState } from 'react';
import { PageWrapper } from '@/shared/components/PageWrapper/ui/PageWrapper';
import { Text, TextAlign, TextSize, TextWeight } from '@/shared/components/Text';
import { InterviewsList } from '../../../widgets/InterviewsList';
import InterviewAnalytics from '../../../components/InterviewAnalytics/InterviewAnalytics';
import { BarChart3, List } from 'lucide-react';
import styles from './InterviewsPage.module.scss';

type ActiveTab = 'interviews' | 'analytics';

export const InterviewsPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<ActiveTab>('interviews');

  const handleTabChange = (tab: ActiveTab) => {
    setActiveTab(tab);
  };

  return (
    <PageWrapper>
      <div className={styles.page}>
        <header className={styles.header}>
          <Text
            text={activeTab === 'interviews' ? 'Интервью' : 'Аналитика интервью'}
            size={TextSize.XXL}
            weight={TextWeight.MEDIUM}
            align={TextAlign.CENTER}
          />
          <Text
            text={
              activeTab === 'interviews'
                ? 'База интервью для изучения реального опыта собеседований'
                : 'Статистика и аналитика по интервью в базе данных'
            }
            size={TextSize.MD}
            align={TextAlign.CENTER}
            className={styles.description}
          />
        </header>

        <div className={styles.tabsContainer}>
          <button
            className={`${styles.tabButton} ${activeTab === 'interviews' ? styles.active : ''}`}
            onClick={() => handleTabChange('interviews')}
          >
            <List size={16} />
            Список интервью
          </button>
          <button
            className={`${styles.tabButton} ${activeTab === 'analytics' ? styles.active : ''}`}
            onClick={() => handleTabChange('analytics')}
          >
            <BarChart3 size={16} />
            Аналитика
          </button>
        </div>

        <div className={styles.content}>
          {activeTab === 'interviews' ? (
            <InterviewsList />
          ) : (
            <InterviewAnalytics />
          )}
        </div>
      </div>
    </PageWrapper>
  );
};