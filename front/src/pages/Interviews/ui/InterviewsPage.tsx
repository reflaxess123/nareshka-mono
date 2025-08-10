import React, { useState } from 'react';
import { PageWrapper } from '@/shared/components/PageWrapper/ui/PageWrapper';
import { Text, TextAlign, TextSize, TextWeight } from '@/shared/components/Text';
import { InterviewsList } from '../../../widgets/InterviewsList';
import { InterviewCategories } from '@/features/InterviewCategories';
import { List, Database } from 'lucide-react';
import styles from './InterviewsPage.module.scss';

type ActiveTab = 'interviews' | 'questions';

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
            text={
              activeTab === 'interviews' ? 'Интервью' : 'База вопросов'
            }
            size={TextSize.XXL}
            weight={TextWeight.MEDIUM}
            align={TextAlign.CENTER}
          />
          <Text
            text={
              activeTab === 'interviews'
                ? 'База интервью для изучения реального опыта собеседований'
                : 'Категоризированная база вопросов для подготовки к собеседованиям'
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
            className={`${styles.tabButton} ${activeTab === 'questions' ? styles.active : ''}`}
            onClick={() => handleTabChange('questions')}
          >
            <Database size={16} />
            База вопросов
          </button>
        </div>

        <div className={styles.content}>
          {activeTab === 'interviews' && <InterviewsList />}
          {activeTab === 'questions' && <InterviewCategories />}
        </div>
      </div>
    </PageWrapper>
  );
};