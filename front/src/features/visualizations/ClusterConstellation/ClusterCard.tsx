import React from 'react';
import { Handle, Position } from '@xyflow/react';
import type { NodeProps } from '@xyflow/react';
import styles from './ClusterCard.module.scss';

interface ClusterCardData {
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
  // Дополнительные данные для связей
  strongConnections?: Array<{
    name: string;
    strength: number;
  }>;
}

interface ClusterCardProps extends NodeProps<ClusterCardData> {
  isHovered?: boolean;
  isFocused?: boolean;
}

const categoryIcons: Record<string, string> = {
  'javascript_core': '🟡',
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

export const ClusterCard: React.FC<ClusterCardProps> = ({ 
  data, 
  selected, 
  isHovered = false,
  isFocused = false 
}) => {
  const isTopCluster = data.interview_penetration > 15;
  const categoryColor = categoryColors[data.category_id] || '#999';
  const categoryIcon = categoryIcons[data.category_id] || '📝';
  
  // Расчет размеров карточки
  const cardWidth = isTopCluster ? 320 : 280;
  const cardHeight = isTopCluster ? 'auto' : 'auto';
  
  // Форматирование сложности
  const getDifficultyText = () => {
    const { junior, middle, senior } = data.difficulty_distribution;
    const parts = [];
    if (junior > 0) parts.push(`${junior.toFixed(0)}% Jun`);
    if (middle > 0) parts.push(`${middle.toFixed(0)}% Mid`);
    if (senior > 0) parts.push(`${senior.toFixed(0)}% Sen`);
    return parts.length > 0 ? parts.join(' • ') : 'Уровень не определен';
  };

  return (
    <div 
      className={`${styles.clusterCard} ${selected ? styles.selected : ''} ${isHovered ? styles.hovered : ''} ${isFocused ? styles.focused : ''} ${isTopCluster ? styles.topCluster : ''}`}
      style={{ width: cardWidth }}
    >
      {/* Handles для соединений */}
      <Handle type="source" position={Position.Top} style={{ background: categoryColor }} />
      <Handle type="source" position={Position.Right} style={{ background: categoryColor }} />
      <Handle type="source" position={Position.Bottom} style={{ background: categoryColor }} />
      <Handle type="source" position={Position.Left} style={{ background: categoryColor }} />
      <Handle type="target" position={Position.Top} style={{ background: categoryColor, top: -3 }} />
      <Handle type="target" position={Position.Right} style={{ background: categoryColor, right: -3 }} />
      <Handle type="target" position={Position.Bottom} style={{ background: categoryColor, bottom: -3 }} />
      <Handle type="target" position={Position.Left} style={{ background: categoryColor, left: -3 }} />

      {/* Заголовок с категорией */}
      <div 
        className={styles.categoryHeader}
        style={{ backgroundColor: categoryColor }}
      >
        <span className={styles.categoryIcon}>{categoryIcon}</span>
        <span className={styles.categoryName}>{data.category_name}</span>
        <span className={styles.penetrationBadge}>
          {data.interview_penetration.toFixed(1)}%
        </span>
      </div>

      {/* Основной контент */}
      <div className={styles.cardContent}>
        {/* Название кластера */}
        <h3 className={styles.clusterTitle}>
          {data.name.length > 40 ? `${data.name.substring(0, 37)}...` : data.name}
        </h3>

        {/* Статистика */}
        <div className={styles.stats}>
          <div className={styles.statItem}>
            <span className={styles.statValue}>{data.questions_count}</span>
            <span className={styles.statLabel}>вопросов</span>
          </div>
          <div className={styles.statDivider} />
          <div className={styles.statItem}>
            <span className={styles.statValue}>{data.interview_penetration.toFixed(0)}%</span>
            <span className={styles.statLabel}>интервью</span>
          </div>
        </div>

        {/* Топ компании */}
        {data.top_companies && data.top_companies.length > 0 && (
          <div className={styles.companies}>
            <div className={styles.sectionIcon}>💼</div>
            <div className={styles.companyList}>
              {data.top_companies.slice(0, 3).map((company, idx) => (
                <span key={company} className={styles.company}>
                  {company}{idx < Math.min(data.top_companies.length - 1, 2) ? ' • ' : ''}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Уровни сложности */}
        <div className={styles.difficulty}>
          <div className={styles.sectionIcon}>🎯</div>
          <div className={styles.difficultyText}>
            {getDifficultyText()}
          </div>
        </div>

        {/* Ключевые слова */}
        {data.keywords && data.keywords.length > 0 && (
          <div className={styles.keywords}>
            {data.keywords.slice(0, 4).map(keyword => (
              <span key={keyword} className={styles.keyword}>
                #{keyword}
              </span>
            ))}
            {data.keywords.length > 4 && (
              <span className={styles.keywordMore}>+{data.keywords.length - 4}</span>
            )}
          </div>
        )}

        {/* Связанные кластеры (показываем только при hover/focus) */}
        {(isHovered || isFocused) && data.strongConnections && data.strongConnections.length > 0 && (
          <div className={styles.connections}>
            <div className={styles.sectionIcon}>⚡</div>
            <div className={styles.connectionsList}>
              {data.strongConnections.slice(0, 2).map(conn => (
                <span key={conn.name} className={styles.connection}>
                  {conn.name} ({(conn.strength * 100).toFixed(0)}%)
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Индикатор важности для топ кластеров */}
      {isTopCluster && (
        <div className={styles.topBadge}>
          ⭐ ТОП
        </div>
      )}
    </div>
  );
};

export default ClusterCard;