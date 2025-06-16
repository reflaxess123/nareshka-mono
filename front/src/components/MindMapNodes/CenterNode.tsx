import { Handle, Position } from '@xyflow/react';
import React from 'react';
import type { CenterNodeData } from '../../types/newMindmap';
import './CenterNode.scss';

interface CenterNodeProps {
  data: CenterNodeData | Record<string, unknown>;
  selected?: boolean;
}

const CenterNode: React.FC<CenterNodeProps> = ({ data, selected }) => {
  const dataRecord = data as Record<string, unknown>;
  const title = (dataRecord.title as string) || 'JavaScript Skills';
  const description =
    (dataRecord.description as string) || 'Изучение JavaScript';

  return (
    <div className={`center-node ${selected ? 'selected' : ''}`}>
      <Handle
        type="source"
        position={Position.Top}
        style={{
          background: '#8B5CF6',
          width: '12px',
          height: '12px',
          top: '-6px',
        }}
      />
      <Handle
        type="source"
        position={Position.Right}
        style={{
          background: '#8B5CF6',
          width: '12px',
          height: '12px',
          right: '-6px',
        }}
      />
      <Handle
        type="source"
        position={Position.Bottom}
        style={{
          background: '#8B5CF6',
          width: '12px',
          height: '12px',
          bottom: '-6px',
        }}
      />
      <Handle
        type="source"
        position={Position.Left}
        style={{
          background: '#8B5CF6',
          width: '12px',
          height: '12px',
          left: '-6px',
        }}
      />

      <div className="center-content">
        <div className="center-header">
          <div className="center-icon">
            <span role="img" aria-label="JavaScript">
              ⚡
            </span>
          </div>
          <h2 className="center-title">{title}</h2>
        </div>
        <p className="center-description">{description}</p>
        <div className="center-badge">
          <span>Карта навыков JavaScript</span>
        </div>
      </div>
    </div>
  );
};

export default CenterNode;
