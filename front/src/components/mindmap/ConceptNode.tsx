import { Handle, Position } from '@xyflow/react';
import React from 'react';
import type { MindMapNodeData } from '../../types/mindmap';

interface ConceptNodeProps {
  data: MindMapNodeData;
}

export const ConceptNode: React.FC<ConceptNodeProps> = ({ data }) => {
  const getConceptIcon = (concept: string) => {
    const icons: Record<string, string> = {
      functions: '⚡',
      arrays: '📝',
      objects: '📦',
      strings: '🔤',
      classes: '🏗️',
      async: '🔄',
      regex: '🔍',
    };
    return icons[concept] || '💡';
  };

  return (
    <div
      className="relative bg-white rounded-lg shadow-lg border-3 border-green-200 hover:border-green-400 transition-all duration-200 hover:shadow-xl cursor-pointer min-w-[140px] min-h-[100px]"
      style={{ borderColor: data.difficulty_color || '#10B981' }}
    >
      {/* Handles для соединений */}
      <Handle
        type="target"
        position={Position.Top}
        className="w-3 h-3 !bg-green-400 !border !border-white"
      />
      <Handle
        type="source"
        position={Position.Bottom}
        className="w-3 h-3 !bg-green-400 !border !border-white"
      />
      <Handle
        type="source"
        position={Position.Left}
        className="w-3 h-3 !bg-green-400 !border !border-white"
      />
      <Handle
        type="source"
        position={Position.Right}
        className="w-3 h-3 !bg-green-400 !border !border-white"
      />

      {/* Содержимое узла */}
      <div className="p-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-2xl">{getConceptIcon(data.concept || '')}</span>
          <div
            className="text-xs font-semibold px-2 py-1 rounded-full text-white"
            style={{ backgroundColor: data.difficulty_color || '#10B981' }}
          >
            {data.avg_complexity}
          </div>
        </div>

        <div className="text-center">
          <h3 className="font-bold text-gray-900 text-base">{data.label}</h3>
          <p className="text-sm text-gray-600 mt-1">{data.task_count} задач</p>
        </div>
      </div>
    </div>
  );
};
