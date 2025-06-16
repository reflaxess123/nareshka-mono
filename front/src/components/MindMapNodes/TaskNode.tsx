import { Handle, Position } from '@xyflow/react';
import React from 'react';
import './TaskNode.scss';

interface TaskNodeProps {
  data: any;
  selected?: boolean;
}

const TaskNode: React.FC<TaskNodeProps> = ({ data, selected }) => {
  const title = data.title || data.full_title || 'Задача';
  const color = data.color || '#6B7280';

  return (
    <div className={`task-node ${selected ? 'selected' : ''}`}>
      <Handle
        type="target"
        position={Position.Top}
        style={{
          background: color,
          width: '8px',
          height: '8px',
          top: '-4px',
        }}
      />

      <div className="task-content">
        <div className="task-title">{title}</div>
      </div>
    </div>
  );
};

export default TaskNode;
