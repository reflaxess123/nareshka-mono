import { Handle, Position } from '@xyflow/react';
import React from 'react';
import type { MindMapNodeData } from '../../types/mindmap';

interface CenterNodeProps {
  data: MindMapNodeData;
}

export const CenterNode: React.FC<CenterNodeProps> = ({ data }) => {
  return (
    <div className="relative bg-gradient-to-br from-purple-500 to-purple-700 text-white rounded-full shadow-xl min-w-40 min-h-40 flex items-center justify-center border-4 border-white hover:shadow-2xl transition-all duration-300">
      {/* Handles для соединений */}
      <Handle
        type="source"
        position={Position.Top}
        className="w-4 h-4 !bg-purple-300 !border-2 !border-white"
      />
      <Handle
        type="source"
        position={Position.Bottom}
        className="w-4 h-4 !bg-purple-300 !border-2 !border-white"
      />
      <Handle
        type="source"
        position={Position.Left}
        className="w-4 h-4 !bg-purple-300 !border-2 !border-white"
      />
      <Handle
        type="source"
        position={Position.Right}
        className="w-4 h-4 !bg-purple-300 !border-2 !border-white"
      />

      <div className="text-center p-5">
        <div className="text-3xl mb-2">🧠</div>
        <div className="text-xl font-bold">{data.label}</div>
        {data.description && (
          <div className="text-sm opacity-90 mt-2">{data.description}</div>
        )}
      </div>
    </div>
  );
};
