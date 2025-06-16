import { Handle, Position } from '@xyflow/react';
import React from 'react';
import './MoreNode.scss';

interface MoreNodeProps {
  data: any;
  selected?: boolean;
}

const MoreNode: React.FC<MoreNodeProps> = ({ data, selected }) => {
  const title = data.title || '+ еще';
  const color = data.color || '#6B7280';

  return (
    <div className={`more-node ${selected ? 'selected' : ''}`}>
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

      <div className="more-content">
        <div className="more-title">{title}</div>
      </div>
    </div>
  );
};

export default MoreNode;
