import React from 'react';
import { Handle, Position } from '@xyflow/react';
import type { NodeProps } from '@xyflow/react';
import styles from './CategoryNode.module.scss';

interface CategoryNodeData {
  id: string;
  name: string;
  questionsCount: number;
  clustersCount: number;
  avgPenetration: number;
  isExpanded: boolean;
  clusters: Array<{
    id: number;
    name: string;
    questions_count: number;
    interview_penetration: number;
  }>;
}

interface CategoryNodeProps extends NodeProps<CategoryNodeData> {
  isHovered?: boolean;
}

const categoryColors: Record<string, string> = {
  'javascript_core': '#f7df1e',
  'react': '#61dafb',
  'typescript': '#3178c6',
  'soft_skills': '#ff6b6b',
  'алгоритмы': '#dc143c',
  'сет': '#ff6b35',
  'верстка': '#e91e63',
  'браузеры': '#9c27b0',
  'архитектура': '#673ab7',
  'инструменты': '#3f51b5',
  'производителност': '#00bcd4',
  'тестирование': '#4caf50',
  'другое': '#9e9e9e'
};

const categoryIcons: Record<string, string> = {
  'javascript_core': '⚡',
  'react': '⚛️', 
  'typescript': '🔷',
  'soft_skills': '👥',
  'алгоритмы': '🧮',
  'сет': '🌐',
  'верстка': '🎨',
  'браузеры': '🌍',
  'архитектура': '🏗️',
  'инструменты': '🛠️',
  'производителност': '⚡',
  'тестирование': '🧪',
  'другое': '📝'
};

export const CategoryNode: React.FC<CategoryNodeProps> = ({ 
  data, 
  selected, 
  isHovered = false 
}) => {
  const categoryColor = categoryColors[data.id] || '#999';
  const categoryIcon = categoryIcons[data.id] || '📝';
  
  // Размер блока в зависимости от количества вопросов
  const maxQuestions = 2100; // JavaScript Core имеет больше всего
  const minWidth = 200;
  const maxWidth = 280;
  const width = Math.max(minWidth, Math.min(maxWidth, minWidth + (data.questionsCount / maxQuestions) * (maxWidth - minWidth)));
  
  // Убираем топ кластеры - они больше не нужны
  
  return (
    <div 
      className={`${styles.categoryNode} ${selected ? styles.selected : ''} ${isHovered ? styles.hovered : ''}`}
      style={{ width }}
    >
      {/* Handles для соединений */}
      <Handle type="source" position={Position.Top} style={{ background: categoryColor, opacity: 0 }} />
      <Handle type="source" position={Position.Right} style={{ background: categoryColor, opacity: 0 }} />
      <Handle type="source" position={Position.Bottom} style={{ background: categoryColor, opacity: 0 }} />
      <Handle type="source" position={Position.Left} style={{ background: categoryColor, opacity: 0 }} />
      <Handle type="target" position={Position.Top} style={{ background: categoryColor, opacity: 0 }} />
      <Handle type="target" position={Position.Right} style={{ background: categoryColor, opacity: 0 }} />
      <Handle type="target" position={Position.Bottom} style={{ background: categoryColor, opacity: 0 }} />
      <Handle type="target" position={Position.Left} style={{ background: categoryColor, opacity: 0 }} />

      {/* Блок категории */}
      <div 
        className={styles.block}
        style={{ backgroundColor: categoryColor }}
      >
        {/* Заголовок */}
        <div className={styles.header}>
          <div className={styles.icon}>{categoryIcon}</div>
          <div className={styles.categoryName}>{data.name}</div>
        </div>
        
        {/* Статистика */}
        <div className={styles.stats}>
          <div className={styles.statItem}>
            <span className={styles.statNumber}>{data.questionsCount.toLocaleString('ru-RU')}</span>
            <span className={styles.statLabel}>вопросов</span>
          </div>
          <div className={styles.statItem}>
            <span className={styles.statNumber}>{data.clustersCount}</span>
            <span className={styles.statLabel}>кластеров</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CategoryNode;