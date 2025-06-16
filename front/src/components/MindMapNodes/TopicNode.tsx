import { Handle, Position } from '@xyflow/react';
import React from 'react';
import './TopicNode.scss';

interface TopicNodeProps {
  data: any; // Упрощаем для отладки
  selected?: boolean;
}

const TopicNode: React.FC<TopicNodeProps> = ({ data, selected }) => {
  const getConceptIcon = (concept: string) => {
    const icons: Record<string, string> = {
      functions: '⚡',
      arrays: '📝',
      objects: '📦',
      strings: '🔤',
      classes: '🏗️',
      async: '🔄',
      regex: '🔍',
      closures: '🔒',
      custom_functions: '⚡',
      matrices: '🔢',
      promises: '🔄',
      throttle_debounce: '⏱️',
      numbers: '🔢',
    };
    return icons[concept] || data.icon || '💡';
  };

  // Определяем, какие данные у нас есть (новый или старый формат)
  const isOldFormat = data.concept !== undefined;
  const title = data.title || data.label || 'Нет названия';
  const description = data.description || '';
  const taskCount = data.task_count || 0;
  const complexity = data.avg_complexity || 0;
  const color = data.color || data.difficulty_color || '#10B981';
  const iconValue = isOldFormat
    ? getConceptIcon(data.concept)
    : data.icon || getConceptIcon(data.topic_key || '');

  return (
    <div className={`topic-node ${selected ? 'selected' : ''}`}>
      <Handle
        type="target"
        position={Position.Top}
        style={{
          background: color,
          width: '10px',
          height: '10px',
          top: '-5px',
        }}
      />
      <Handle
        type="source"
        position={Position.Bottom}
        style={{
          background: color,
          width: '10px',
          height: '10px',
          bottom: '-5px',
        }}
      />
      <Handle
        type="source"
        position={Position.Left}
        style={{
          background: color,
          width: '10px',
          height: '10px',
          left: '-5px',
        }}
      />
      <Handle
        type="source"
        position={Position.Right}
        style={{
          background: color,
          width: '10px',
          height: '10px',
          right: '-5px',
        }}
      />

      <div className="topic-content">
        <div className="topic-header">
          <div className="topic-icon" style={{ backgroundColor: color }}>
            <span role="img" aria-label={title}>
              {iconValue}
            </span>
          </div>
          <h3 className="topic-title">{title}</h3>
        </div>

        {description && <p className="topic-description">{description}</p>}

        <div className="topic-stats">
          <div className="stat">
            <div className="stat-value">{taskCount}</div>
            <div className="stat-label">Задач</div>
          </div>

          {complexity > 0 && (
            <>
              <div className="stat-divider" />
              <div className="stat">
                <div className="stat-value">{Math.round(complexity)}</div>
                <div className="stat-label">Сложность</div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default TopicNode;
