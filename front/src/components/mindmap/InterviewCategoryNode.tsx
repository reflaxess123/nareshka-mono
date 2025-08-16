import React from 'react';
import { Handle, Position } from '@xyflow/react';
import type { NodeProps } from '@xyflow/react';
import styles from './InterviewNodes.module.scss';

interface InterviewCategoryNodeData {
  id: string;
  name: string;
  questionsCount: number;
  clustersCount: number;
  percentage: number;
}

const categoryColors: Record<string, string> = {
  'javascript_core': '#f7df1e',
  'react': '#61dafb',
  'typescript': '#3178c6',
  'soft_skills': '#ff6b6b',
  'алгоритмы': '#dc143c',
  'сеть': '#ff6b35',
  'верстка': '#e91e63',
  'браузеры': '#9c27b0',
  'архитектура': '#673ab7',
  'инструменты': '#3f51b5',
  'производительность': '#00bcd4',
  'тестирование': '#4caf50',
  'другое': '#9e9e9e'
};

const categoryIcons: Record<string, string> = {
  'javascript_core': '⚡',
  'react': '⚛️',
  'typescript': '🔷',
  'soft_skills': '👥',
  'алгоритмы': '🧮',
  'сеть': '🌐',
  'верстка': '🎨',
  'браузеры': '🌍',
  'архитектура': '🏗️',
  'инструменты': '🛠️',
  'производительность': '🚀',
  'тестирование': '🧪',
  'другое': '📝'
};

export const InterviewCategoryNode: React.FC<NodeProps<InterviewCategoryNodeData>> = ({ 
  data, 
  selected 
}) => {
  const categoryColor = categoryColors[data.id] || '#999';
  const categoryIcon = categoryIcons[data.id] || '📝';
  
  return (
    <div 
      className={`${styles.categoryNode} ${selected ? styles.selected : ''}`}
      style={{ backgroundColor: categoryColor }}
    >
      <Handle type="source" position={Position.Top} style={{ opacity: 0 }} />
      <Handle type="source" position={Position.Right} style={{ opacity: 0 }} />
      <Handle type="source" position={Position.Bottom} style={{ opacity: 0 }} />
      <Handle type="source" position={Position.Left} style={{ opacity: 0 }} />
      <Handle type="target" position={Position.Top} style={{ opacity: 0 }} />
      <Handle type="target" position={Position.Right} style={{ opacity: 0 }} />
      <Handle type="target" position={Position.Bottom} style={{ opacity: 0 }} />
      <Handle type="target" position={Position.Left} style={{ opacity: 0 }} />

      <div className={styles.categoryContent}>
        <div className={styles.categoryHeader}>
          <span className={styles.categoryIcon}>{categoryIcon}</span>
          <div className={styles.categoryName}>{data.name}</div>
        </div>
        
        <div className={styles.categoryStats}>
          <div className={styles.statItem}>
            <span className={styles.statNumber}>
              {data.questionsCount.toLocaleString('ru-RU')}
            </span>
            <span className={styles.statLabel}>вопросов</span>
          </div>
          <div className={styles.statItem}>
            <span className={styles.statNumber}>{data.clustersCount}</span>
            <span className={styles.statLabel}>кластеров</span>
          </div>
        </div>

        <div className={styles.categoryPercentage}>
          <span className={styles.percentageValue}>{data.percentage.toFixed(1)}%</span>
          <span className={styles.percentageLabel}>от всех вопросов</span>
        </div>
      </div>
    </div>
  );
};

export default InterviewCategoryNode;