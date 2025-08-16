import React from 'react';
import { Handle, Position } from '@xyflow/react';
import type { NodeProps } from '@xyflow/react';
import styles from './ClusterNode.module.scss';

interface ClusterNodeData {
  id: number;
  name: string;
  category_id: string;
  category_name: string;
  questions_count: number;
  interview_penetration: number;
  keywords: string[];
  example_question: string;
  top_companies: string[];
  difficulty_distribution: { 
    junior: number; 
    middle: number; 
    senior: number; 
  };
  size: number;
  // Новые полезные поля
  rank: number;
  isTopCluster: boolean;
  difficultyLevel: 'high' | 'medium' | 'low';
  demandStatus: string;
}

interface ClusterNodeProps extends NodeProps<ClusterNodeData> {
  isHovered?: boolean;
  isFocused?: boolean;
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

export const ClusterNode: React.FC<ClusterNodeProps> = ({ 
  data, 
  selected, 
  isHovered = false,
  isFocused = false 
}) => {
  const categoryColor = categoryColors[data.category_id] || '#999';
  const categoryIcon = categoryIcons[data.category_id] || '📝';
  
  // Размер блока в зависимости от важности  
  const width = data.isTopCluster ? 180 : 160;
  const minHeight = data.isTopCluster ? 120 : 100;
  
  return (
    <div 
      className={`${styles.clusterNode} ${selected ? styles.selected : ''} ${isHovered ? styles.hovered : ''} ${isFocused ? styles.focused : ''} ${data.isTopCluster ? styles.topCluster : ''}`}
      style={{ width, minHeight }}
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

      {/* Блок кластера */}
      <div 
        className={styles.block}
        style={{ backgroundColor: categoryColor }}
      >
        {/* Заголовок */}
        <div className={styles.header}>
          <div className={styles.icon}>{categoryIcon}</div>
          <div className={styles.rank}>#{data.rank}</div>
          {data.isTopCluster && (
            <div className={styles.topBadge}>⭐</div>
          )}
        </div>
        
        {/* Название кластера */}
        <div className={styles.clusterName}>
          {data.name.length > 35 ? `${data.name.substring(0, 32)}...` : data.name}
        </div>
        
        {/* Статистика */}
        <div className={styles.stats}>
          <div className={styles.statItem}>
            <span className={styles.statNumber}>{data.questions_count}</span>
            <span className={styles.statLabel}>вопросов</span>
          </div>
          <div className={styles.statItem}>
            <span className={styles.statNumber}>{data.interview_penetration.toFixed(0)}%</span>
            <span className={styles.statLabel}>популярность</span>
          </div>
        </div>
        
        {/* Топ компании */}
        {data.top_companies && data.top_companies.length > 0 && (
          <div className={styles.companies}>
            <div className={styles.companiesTitle}>Топ компании:</div>
            <div className={styles.companiesList}>
              {data.top_companies.slice(0, 3).map((company, index) => (
                <span key={company} className={styles.company}>
                  {company}{index < Math.min(2, data.top_companies.length - 1) ? ', ' : ''}
                </span>
              ))}
              {data.top_companies.length > 3 && (
                <span className={styles.moreCompanies}>+{data.top_companies.length - 3}</span>
              )}
            </div>
          </div>
        )}
        
        {/* Статус востребованности */}
        <div className={styles.demandStatus}>
          {data.demandStatus}
        </div>
      </div>
    </div>
  );
};

export default ClusterNode;