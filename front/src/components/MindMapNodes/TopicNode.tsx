import { Handle, Position } from '@xyflow/react';
import React from 'react';
import './TopicNode.scss';

interface TopicNodeData {
  title: string;
  description?: string;
  color: string;
  icon: string;
  progress?: {
    totalTasks: number;
    completedTasks: number;
    completionRate: number;
    status: string;
  } | null;
}

interface TopicNodeProps {
  data: TopicNodeData;
  selected: boolean;
}

const TopicNode: React.FC<TopicNodeProps> = ({ data, selected }) => {
  const title = data.title || 'Нет названия';
  const description = data.description || '';
  const color = data.color || '#10B981';
  const icon = data.icon || '💡';
  const progress = data.progress;

  const getProgressColor = () => {
    if (!progress) return color;
    if (progress.status === 'completed') return '#10b981'; // зеленый
    if (progress.status === 'in_progress') return '#3b82f6'; // синий
    return '#94a3b8'; // серый для not_started
  };

  const progressColor = getProgressColor();

  return (
    <div className={`topic-node ${selected ? 'selected' : ''}`}>
      <Handle
        type="target"
        position={Position.Top}
        style={{
          background: progressColor,
          width: '10px',
          height: '10px',
          top: '-5px',
        }}
      />
      <Handle
        type="source"
        position={Position.Bottom}
        style={{
          background: progressColor,
          width: '10px',
          height: '10px',
          bottom: '-5px',
        }}
      />
      <Handle
        type="source"
        position={Position.Left}
        style={{
          background: progressColor,
          width: '10px',
          height: '10px',
          left: '-5px',
        }}
      />
      <Handle
        type="source"
        position={Position.Right}
        style={{
          background: progressColor,
          width: '10px',
          height: '10px',
          right: '-5px',
        }}
      />

      <div className="topic-content">
        <div className="topic-header">
          <div
            className="topic-icon"
            style={{ backgroundColor: progressColor }}
          >
            <span role="img" aria-label={title}>
              {icon}
            </span>
          </div>
          <h3 className="topic-title">{title}</h3>
        </div>
        {description && <p className="topic-description">{description}</p>}

        {/* Отображение прогресса */}
        {progress && (
          <div className="topic-progress">
            <div className="progress-text">
              {progress.completedTasks}/{progress.totalTasks}
            </div>
            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{
                  width: `${Math.min(progress.completionRate, 100)}%`,
                  backgroundColor: progressColor,
                }}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default TopicNode;
