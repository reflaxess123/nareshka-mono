import React from 'react';
import { InterviewsList } from '../../../widgets/InterviewsList';
import styles from './InterviewsPage.module.scss';

export const InterviewsPage: React.FC = () => {
  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <h1 className={styles.title}>Интервью по разработке</h1>
        <p className={styles.description}>
          Коллекция реальных интервью с разработчиками из различных компаний. 
          Изучайте вопросы, технологии и подходы к собеседованиям.
        </p>
      </div>
      
      <InterviewsList />
    </div>
  );
};