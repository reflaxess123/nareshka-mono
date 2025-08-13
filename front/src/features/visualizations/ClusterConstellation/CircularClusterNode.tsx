import React from 'react';
import { Handle, Position } from '@xyflow/react';
import type { NodeProps } from '@xyflow/react';
import styles from './CircularClusterNode.module.scss';

interface CircularClusterNodeData {
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

interface CircularClusterNodeProps extends NodeProps<CircularClusterNodeData> {
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

export const CircularClusterNode: React.FC<CircularClusterNodeProps> = ({ 
  data, 
  selected, 
  isHovered = false,
  isFocused = false 
}) => {
  const categoryColor = categoryColors[data.category_id] || '#999';
  const categoryIcon = categoryIcons[data.category_id] || '📝';
  
  // Размер круга в зависимости от важности
  const circleSize = data.isTopCluster ? 120 : 100;
  const fontSize = data.isTopCluster ? '14px' : '12px';
  
  return (
    <div 
      className={`${styles.circularNode} ${selected ? styles.selected : ''} ${isHovered ? styles.hovered : ''} ${isFocused ? styles.focused : ''} ${data.isTopCluster ? styles.topCluster : ''}`}
      style={{ width: circleSize, height: circleSize }}
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

      {/* Круглый узел */}
      <div 
        className={styles.circle}
        style={{ 
          backgroundColor: categoryColor,
          width: circleSize,
          height: circleSize,
          fontSize
        }}
      >
        {/* Иконка категории */}
        <div className={styles.icon}>
          {categoryIcon}
        </div>
        
        {/* Основная информация */}
        <div className={styles.mainInfo}>
          <div className={styles.rank}>
            #{data.rank}
          </div>
          <div className={styles.penetration}>
            {data.interview_penetration.toFixed(0)}%
          </div>
          <div className={styles.questionsCount}>
            {data.questions_count}
          </div>
        </div>

        {/* Название кластера (показывается при hover) */}
        {(isHovered || isFocused) && (
          <div className={styles.tooltip}>
            <div className={styles.clusterName}>
              {data.name.length > 30 ? `${data.name.substring(0, 27)}...` : data.name}
            </div>
            <div className={styles.categoryName}>
              {data.category_name}
            </div>
            <div className={styles.demandStatus}>
              {data.demandStatus}
            </div>
            <div className={styles.companies}>
              {data.top_companies.slice(0, 3).join(', ')}
            </div>
          </div>
        )}
        
        {/* Индикатор важности для топ кластеров */}
        {data.isTopCluster && (
          <div className={styles.topBadge}>
            ⭐
          </div>
        )}
      </div>
    </div>
  );
};

export default CircularClusterNode;