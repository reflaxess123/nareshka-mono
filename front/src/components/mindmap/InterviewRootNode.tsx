import React from 'react';
import { Handle, Position } from '@xyflow/react';
import type { NodeProps } from '@xyflow/react';
import styles from './InterviewNodes.module.scss';

interface InterviewRootNodeData {
  totalQuestions: number;
  totalClusters: number;
  totalCategories: number;
}

export const InterviewRootNode: React.FC<NodeProps<InterviewRootNodeData>> = ({ 
  data, 
  selected 
}) => {
  return (
    <div className={`${styles.rootNode} ${selected ? styles.selected : ''}`}>
      <Handle type="source" position={Position.Top} style={{ opacity: 0 }} />
      <Handle type="source" position={Position.Right} style={{ opacity: 0 }} />
      <Handle type="source" position={Position.Bottom} style={{ opacity: 0 }} />
      <Handle type="source" position={Position.Left} style={{ opacity: 0 }} />

      <div className={styles.rootContent}>
        <div className={styles.rootHeader}>
          <span className={styles.rootIcon}>💎</span>
          <h2 className={styles.rootTitle}>База вопросов для интервью</h2>
        </div>
        
        <div className={styles.rootStats}>
          <div className={styles.statItem}>
            <span className={styles.statNumber}>
              {data.totalQuestions.toLocaleString('ru-RU')}
            </span>
            <span className={styles.statLabel}>вопросов</span>
          </div>
          <div className={styles.statItem}>
            <span className={styles.statNumber}>{data.totalClusters}</span>
            <span className={styles.statLabel}>кластеров</span>
          </div>
          <div className={styles.statItem}>
            <span className={styles.statNumber}>{data.totalCategories}</span>
            <span className={styles.statLabel}>категорий</span>
          </div>
        </div>

        <div className={styles.rootFooter}>
          <span className={styles.footerText}>
            Проанализировано из 380+ IT компаний
          </span>
        </div>
      </div>
    </div>
  );
};

export default InterviewRootNode;