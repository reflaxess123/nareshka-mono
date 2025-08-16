import React from 'react';
import { Handle, Position } from '@xyflow/react';
import type { NodeProps } from '@xyflow/react';
import styles from './RootNode.module.scss';

interface RootNodeData {
  totalQuestions: number;
  totalClusters: number;
  totalCategories: number;
}

interface RootNodeProps extends NodeProps<RootNodeData> {
  isHovered?: boolean;
}

export const RootNode: React.FC<RootNodeProps> = ({ 
  data, 
  selected, 
  isHovered = false 
}) => {
  return (
    <div 
      className={`${styles.rootNode} ${selected ? styles.selected : ''} ${isHovered ? styles.hovered : ''}`}
    >
      {/* Handles для соединений */}
      <Handle type="source" position={Position.Top} style={{ opacity: 0 }} />
      <Handle type="source" position={Position.Right} style={{ opacity: 0 }} />
      <Handle type="source" position={Position.Bottom} style={{ opacity: 0 }} />
      <Handle type="source" position={Position.Left} style={{ opacity: 0 }} />

      {/* Основной блок */}
      <div className={styles.block}>
        {/* Заголовок */}
        <div className={styles.header}>
          <div className={styles.icon}>📊</div>
          <div className={styles.title}>База вопросов для интервью</div>
        </div>
        
        {/* Основной контент */}
        <div className={styles.content}>
          <div className={styles.mainStat}>
            <div className={styles.mainNumber}>
              {data.totalQuestions.toLocaleString('ru-RU')}
            </div>
            <div className={styles.mainLabel}>вопросов собрано</div>
          </div>
          
          <div className={styles.additionalStats}>
            <div className={styles.statRow}>
              <span className={styles.statLabel}>Тематических кластеров:</span>
              <span className={styles.statValue}>{data.totalClusters}</span>
            </div>
            <div className={styles.statRow}>
              <span className={styles.statLabel}>Основных категорий:</span>
              <span className={styles.statValue}>{data.totalCategories}</span>
            </div>
          </div>
        </div>
        
        {/* Инструкция */}
        <div className={styles.instruction}>
          Кликните на категорию для просмотра тем
        </div>
      </div>
    </div>
  );
};

export default RootNode;