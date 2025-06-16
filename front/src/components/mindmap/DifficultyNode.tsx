import { Handle, Position } from '@xyflow/react';
import React from 'react';
import type { MindMapNodeData } from '../../types/mindmap';

interface DifficultyNodeProps {
  data: MindMapNodeData;
}

export const DifficultyNode: React.FC<DifficultyNodeProps> = ({ data }) => {
  const getDifficultyIcon = (level: string) => {
    const icons: Record<string, string> = {
      beginner: '🌱',
      intermediate: '🚀',
      advanced: '⚡',
    };
    return icons[level.toLowerCase()] || '🎯';
  };

  const getDifficultyGradient = (level: string) => {
    const gradients: Record<string, string> = {
      beginner: 'from-green-400 to-green-600',
      intermediate: 'from-blue-400 to-blue-600',
      advanced: 'from-red-400 to-red-600',
    };
    return gradients[level.toLowerCase()] || 'from-gray-400 to-gray-600';
  };

  return (
    <div
      className={`relative bg-gradient-to-br ${getDifficultyGradient(data.label)} text-white rounded-xl shadow-lg hover:shadow-xl transition-all duration-200 cursor-pointer min-w-[130px] min-h-[90px]`}
    >
      {/* Handles для соединений */}
      <Handle
        type="target"
        position={Position.Top}
        className="w-3 h-3 !bg-white !border-2 !border-current"
        style={{ color: data.difficulty_color }}
      />
      <Handle
        type="source"
        position={Position.Bottom}
        className="w-3 h-3 !bg-white !border-2 !border-current"
        style={{ color: data.difficulty_color }}
      />
      <Handle
        type="source"
        position={Position.Left}
        className="w-3 h-3 !bg-white !border-2 !border-current"
        style={{ color: data.difficulty_color }}
      />
      <Handle
        type="source"
        position={Position.Right}
        className="w-3 h-3 !bg-white !border-2 !border-current"
        style={{ color: data.difficulty_color }}
      />

      {/* Содержимое узла */}
      <div className="p-4 text-center">
        <div className="text-2xl mb-2">{getDifficultyIcon(data.label)}</div>
        <h3 className="font-bold text-base">{data.label}</h3>
        <div className="text-sm mt-1 opacity-90">
          {data.task_count} задач ({data.percentage}%)
        </div>
      </div>
    </div>
  );
};
