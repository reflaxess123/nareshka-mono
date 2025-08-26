import React from 'react';
import { Handle, Position } from '@xyflow/react';
import styles from '../InterviewNodes.module.scss';

interface InterviewRootNodeData {
  totalQuestions: number;
  totalClusters: number;
  totalCategories: number;
}

interface InterviewRootNodeProps {
  data: InterviewRootNodeData;
  selected: boolean;
}

export const InterviewRootNode: React.FC<InterviewRootNodeProps> = ({ 
  data, 
  selected 
}) => {
  const color = '#667eea';
  
  return (
    <div className={`${styles.rootNode} ${selected ? styles.selected : ''}`}>
      <Handle 
        type="source" 
        position={Position.Top} 
        style={{ 
          background: color, 
          width: '12px', 
          height: '12px', 
          top: '-6px' 
        }} 
      />
      <Handle 
        type="source" 
        position={Position.Right} 
        style={{ 
          background: color, 
          width: '12px', 
          height: '12px', 
          right: '-6px' 
        }} 
      />
      <Handle 
        type="source" 
        position={Position.Bottom} 
        style={{ 
          background: color, 
          width: '12px', 
          height: '12px', 
          bottom: '-6px' 
        }} 
      />
      <Handle 
        type="source" 
        position={Position.Left} 
        style={{ 
          background: color, 
          width: '12px', 
          height: '12px', 
          left: '-6px' 
        }} 
      />

      <div className={styles.centerContent}>
        <div className={styles.centerHeader}>
          <div className={styles.centerIcon}>
            <span role="img" aria-label="interviews">💎</span>
          </div>
          <h2 className={styles.centerTitle}>База вопросов</h2>
        </div>
        <p className={styles.centerDescription}>Вопросы для интервью по IT специальностям</p>
        
        <div className={styles.centerProgress}>
          <div className={styles.progressText}>
            {data.totalQuestions.toLocaleString('ru-RU')} вопросов
          </div>
          <div className={styles.progressText}>
            {data.totalClusters} кластеров • {data.totalCategories} категорий
          </div>
        </div>
        
        <div className={styles.centerBadge}>
          <span>Карта вопросов для собеседований</span>
        </div>
      </div>
    </div>
  );
};

export default InterviewRootNode;