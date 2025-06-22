import { ProgressBar } from '@/shared/components/ProgressBar';
import { Handle, Position } from '@xyflow/react';
import { AlertTriangle, CheckCircle2, Clock, Play } from 'lucide-react';
import React from 'react';
import './ProgressTopicNode.scss';

interface ProgressTopicNodeData {
  title?: string;
  description?: string;
  color?: string;
  icon?: string;
  topic_key?: string;
  mainCategory?: string;
  subCategory?: string;
  totalTasks?: number;
  completedTasks?: number;
  attemptedTasks?: number;
  completionRate?: number;
  averageAttempts?: number;
  totalTimeSpent?: number;
  status?: 'not_started' | 'in_progress' | 'completed' | 'struggling';
  lastActivity?: string;
}

interface ProgressTopicNodeProps {
  data: ProgressTopicNodeData;
  selected?: boolean;
}

const ProgressTopicNode: React.FC<ProgressTopicNodeProps> = ({
  data,
  selected,
}) => {
  const title = data.title || data.mainCategory || 'Нет названия';
  const description = data.description || data.subCategory || '';
  const icon = data.icon || '💡';

  // Определяем цвет на основе прогресса
  const getProgressColor = () => {
    if (!data.status || data.status === 'not_started') return '#94a3b8'; // серый
    if (data.status === 'completed') return '#10b981'; // зеленый
    if (data.status === 'struggling') return '#f59e0b'; // оранжевый
    if (data.status === 'in_progress') return '#3b82f6'; // синий
    return data.color || '#10B981';
  };

  const progressColor = getProgressColor();
  const completionRate = data.completionRate || 0;
  const totalTasks = data.totalTasks || 0;
  const completedTasks = data.completedTasks || 0;

  const getStatusIcon = () => {
    switch (data.status) {
      case 'completed':
        return <CheckCircle2 size={16} className="status-icon completed" />;
      case 'struggling':
        return <AlertTriangle size={16} className="status-icon struggling" />;
      case 'in_progress':
        return <Clock size={16} className="status-icon in-progress" />;
      case 'not_started':
        return <Play size={16} className="status-icon not-started" />;
      default:
        return null;
    }
  };

  const formatTime = (minutes: number) => {
    if (minutes < 60) return `${minutes}м`;
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = minutes % 60;
    return `${hours}ч ${remainingMinutes}м`;
  };

  return (
    <div
      className={`progress-topic-node ${selected ? 'selected' : ''} ${data.status || 'not-started'}`}
    >
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
          <div className="topic-title-section">
            <h3 className="topic-title">{title}</h3>
            {getStatusIcon()}
          </div>
        </div>

        {description && <p className="topic-description">{description}</p>}

        {/* Прогресс-бар */}
        {totalTasks > 0 && (
          <div className="progress-section">
            <ProgressBar
              percentage={completionRate}
              status={data.status}
              size="small"
              showLabel={false}
            />
            <div className="progress-stats">
              <span className="task-count">
                {completedTasks}/{totalTasks}
              </span>
              <span className="completion-rate">
                {Math.round(completionRate)}%
              </span>
            </div>
          </div>
        )}

        {/* Дополнительная статистика */}
        {(data.averageAttempts || data.totalTimeSpent) && (
          <div className="topic-stats">
            {data.averageAttempts && (
              <div className="stat">
                <div className="stat-value">
                  {Math.round(data.averageAttempts)}
                </div>
                <div className="stat-label">попыток</div>
              </div>
            )}

            {data.totalTimeSpent && data.totalTimeSpent > 0 && (
              <>
                <div className="stat-divider"></div>
                <div className="stat">
                  <div className="stat-value">
                    {formatTime(data.totalTimeSpent)}
                  </div>
                  <div className="stat-label">время</div>
                </div>
              </>
            )}
          </div>
        )}

        {/* Индикатор последней активности */}
        {data.lastActivity && (
          <div className="last-activity">
            <Clock size={12} />
            <span>
              {new Date(data.lastActivity).toLocaleDateString('ru-RU')}
            </span>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProgressTopicNode;
