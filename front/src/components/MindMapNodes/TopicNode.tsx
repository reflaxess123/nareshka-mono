import { Handle, Position } from '@xyflow/react';
import React from 'react';
import './TopicNode.scss';

interface TopicNodeProps {
  data: {
    title?: string;
    description?: string;
    color?: string;
    icon?: string;
    topic_key?: string;
  };
  selected?: boolean;
}

const TopicNode: React.FC<TopicNodeProps> = ({ data, selected }) => {
  const title = data.title || 'Нет названия';
  const description = data.description || '';
  const color = data.color || '#10B981';
  const icon = data.icon || '💡';

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
              {icon}
            </span>
          </div>
          <h3 className="topic-title">{title}</h3>
        </div>
        {description && <p className="topic-description">{description}</p>}
      </div>
    </div>
  );
};

export default TopicNode;
