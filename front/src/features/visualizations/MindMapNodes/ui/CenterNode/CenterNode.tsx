import { Handle, Position } from '@xyflow/react';
import React from 'react';
import styles from './CenterNode.module.scss';

interface CenterNodeData {
  title: string;
  description: string;
  icon?: string;
  color?: string;
  technology?: string;
  overallProgress?: {
    totalTasks: number;
    completedTasks: number;
    completionRate: number;
  } | null;
}

interface CenterNodeProps {
  data: CenterNodeData;
  selected: boolean;
}

const CenterNode: React.FC<CenterNodeProps> = ({ data, selected }) => {
  const title = data.title || 'JavaScript Skills';
  const description = data.description || 'Изучение JavaScript';
  const icon = data.icon || '⚡';
  const color = data.color || '#F7DF1E';
  const technology = data.technology || 'javascript';
  const overallProgress = data.overallProgress;

  return (
    <div className={`${styles.centerNode} ${selected ? styles.selected : ''}`}>
      <Handle
        type="source"
        position={Position.Top}
        style={{
          background: color,
          width: '12px',
          height: '12px',
          top: '-6px',
        }}
      />
      <Handle
        type="source"
        position={Position.Right}
        style={{
          background: color,
          width: '12px',
          height: '12px',
          right: '-6px',
        }}
      />
      <Handle
        type="source"
        position={Position.Bottom}
        style={{
          background: color,
          width: '12px',
          height: '12px',
          bottom: '-6px',
        }}
      />
      <Handle
        type="source"
        position={Position.Left}
        style={{
          background: color,
          width: '12px',
          height: '12px',
          left: '-6px',
        }}
      />

      <div className={styles.centerContent}>
        <div className={styles.centerHeader}>
          <div className={styles.centerIcon}>
            <span role="img" aria-label={technology}>
              {icon}
            </span>
          </div>
          <h2 className={styles.centerTitle}>{title}</h2>
        </div>
        <p className={styles.centerDescription}>{description}</p>

        {/* Отображение общего прогресса */}
        {overallProgress && (
          <div className={styles.centerProgress}>
            <div className={styles.progressText}>
              {overallProgress.completedTasks}/{overallProgress.totalTasks}{' '}
              задач
            </div>
            <div className={styles.progressPercentage}>
              {Math.round(overallProgress.completionRate)}%
            </div>
            <div className={styles.progressBar}>
              <div
                className={styles.progressFill}
                style={{
                  width: `${Math.min(overallProgress.completionRate, 100)}%`,
                }}
              />
            </div>
          </div>
        )}

        <div className={styles.centerBadge}>
          <span>Карта навыков {title.replace(' Skills', '')}</span>
        </div>
      </div>
    </div>
  );
};

export default CenterNode;
