import { Handle, Position } from '@xyflow/react';
import React from 'react';
import type { DifficultyNodeData } from '../../types/newMindmap';
import './DifficultyNode.scss';

interface DifficultyNodeProps {
  data: DifficultyNodeData | Record<string, unknown>;
  selected?: boolean;
}

const DifficultyNode: React.FC<DifficultyNodeProps> = ({ data, selected }) => {
  const getDifficultyIcon = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner':
        return '🌱';
      case 'intermediate':
        return '⚡';
      case 'advanced':
        return '🔥';
      default:
        return '⭐';
    }
  };

  // Поддерживаем и новый и старый формат данных
  const difficulty = (data as Record<string, string>).difficulty || 'beginner';
  const label =
    (data as Record<string, string>).label ||
    (data as Record<string, string>).difficulty_name ||
    difficulty;
  const fullLabel = (data as Record<string, string>).full_label || label;
  const taskCount = (data as Record<string, number>).task_count || 0;
  const avgTime = (data as Record<string, number>).avg_time || 0;
  const color =
    (data as Record<string, string>).color ||
    (data as Record<string, string>).difficulty_color ||
    '#F59E0B';

  return (
    <div
      className={`difficulty-node ${selected ? 'selected' : ''} difficulty-${difficulty}`}
    >
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

      <div className="difficulty-content">
        <div className="difficulty-header">
          <div className="difficulty-icon" style={{ backgroundColor: color }}>
            <span role="img" aria-label={difficulty}>
              {getDifficultyIcon(difficulty)}
            </span>
          </div>
          <h4 className="difficulty-title">{fullLabel}</h4>
        </div>

        <div className="difficulty-stats">
          <div className="stat">
            <div className="stat-value">{taskCount}</div>
            <div className="stat-label">Задач</div>
          </div>

          {avgTime > 0 && (
            <>
              <div className="stat-divider" />
              <div className="stat">
                <div className="stat-value">{avgTime}</div>
                <div className="stat-label">мин</div>
              </div>
            </>
          )}
        </div>

        <div className="difficulty-badge">
          <span>{label}</span>
        </div>
      </div>
    </div>
  );
};

export default DifficultyNode;
