import { Handle, Position } from '@xyflow/react';
import React from 'react';
import type { MindMapNodeData } from '../../types/mindmap';

interface PathNodeProps {
  data: MindMapNodeData;
}

export const PathNode: React.FC<PathNodeProps> = ({ data }) => {
  return (
    <div
      className="relative bg-white rounded-lg shadow-lg border-3 border-yellow-200 hover:border-yellow-400 transition-all duration-200 hover:shadow-xl cursor-pointer min-w-[150px] min-h-[80px]"
      style={{ borderColor: data.difficulty_color || '#F59E0B' }}
    >
      {/* Handles для соединений */}
      <Handle
        type="target"
        position={Position.Top}
        className="w-3 h-3 !bg-yellow-400 !border !border-white"
      />
      <Handle
        type="source"
        position={Position.Bottom}
        className="w-3 h-3 !bg-yellow-400 !border !border-white"
      />
      <Handle
        type="source"
        position={Position.Left}
        className="w-3 h-3 !bg-yellow-400 !border !border-white"
      />
      <Handle
        type="source"
        position={Position.Right}
        className="w-3 h-3 !bg-yellow-400 !border !border-white"
      />

      {/* Содержимое узла */}
      <div className="p-3">
        <div className="flex items-center space-x-2 mb-2">
          <span className="text-xl">🛤️</span>
          <div
            className="text-xs font-semibold px-2 py-1 rounded-full text-white"
            style={{ backgroundColor: data.difficulty_color || '#F59E0B' }}
          >
            {data.avg_complexity}
          </div>
        </div>

        <div>
          <h3
            className="font-bold text-gray-900 text-sm leading-tight"
            title={data.full_title}
          >
            {data.label}
          </h3>
          <p className="text-xs text-gray-600 mt-1">{data.task_count} задач</p>
        </div>
      </div>
    </div>
  );
};
