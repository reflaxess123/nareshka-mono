import React from 'react';
import { PageWrapper } from '@/shared/components/PageWrapper/ui/PageWrapper';
import { Text, TextAlign, TextSize, TextWeight } from '@/shared/components/Text';
import { InterviewCategories } from '@/features/InterviewCategories';
import { Database } from 'lucide-react';
import styles from './QuestionsDatabasePage.module.scss';

export const QuestionsDatabasePage: React.FC = () => {
  return (
    <PageWrapper>
      <div className={styles.page}>
        <header className={styles.header}>
          <div className={styles.headerContent}>
            <div className={styles.iconWrapper}>
              <Database size={40} className={styles.pageIcon} />
            </div>
            <div className={styles.headerText}>
              <Text
                text="База вопросов"
                size={TextSize.XXL}
                weight={TextWeight.BOLD}
                align={TextAlign.LEFT}
                className={styles.title}
              />
              <Text
                text="Категоризированная база из 8,560 вопросов для подготовки к собеседованиям"
                size={TextSize.MD}
                align={TextAlign.LEFT}
                className={styles.description}
              />
            </div>
          </div>
        </header>

        <div className={styles.content}>
          <InterviewCategories />
        </div>
      </div>
    </PageWrapper>
  );
};