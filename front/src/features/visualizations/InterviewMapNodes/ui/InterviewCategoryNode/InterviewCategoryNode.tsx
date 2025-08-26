import React from 'react';
import { Handle, Position } from '@xyflow/react';
import './InterviewCategoryNode.scss';


const categoryColors: Record<string, string> = {
  'javascript_core': '#f7df1e',
  'react': '#61dafb',
  'typescript': '#3178c6',
  'soft_skills': '#ff6b6b',
  'алгоритмы': '#dc143c',
  'сеть': '#ff6b35',
  'верстка': '#e91e63',
  'браузеры': '#9c27b0',
  'архитектура': '#673ab7',
  'инструменты': '#3f51b5',
  'производительность': '#00bcd4',
  'тестирование': '#4caf50',
  'другое': '#9e9e9e'
};

const categoryIcons: Record<string, string> = {
  'javascript_core': '⚡',
  'react': '⚛️',
  'typescript': '🔷',
  'soft_skills': '👥',
  'алгоритмы': '🧮',
  'сеть': '🌐',
  'верстка': '🎨',
  'браузеры': '🌍',
  'архитектура': '🏗️',
  'инструменты': '🛠️',
  'производительность': '🚀',
  'тестирование': '🧪',
  'другое': '📝'
};

interface InterviewCategoryNodeData {
  id: string;
  name: string;
  questionsCount: number;
  clustersCount: number;
  percentage: number;
}

interface InterviewCategoryNodeProps {
  data: InterviewCategoryNodeData;
  selected: boolean;
}

export const InterviewCategoryNode: React.FC<InterviewCategoryNodeProps> = ({ 
  data, 
  selected 
}) => {
  const categoryColor = categoryColors[data.id] || '#10B981';
  const categoryIcon = categoryIcons[data.id] || '📝';
  
  return (
    <div className={`topic-node ${selected ? 'selected' : ''}`}>
      <Handle
        type="target"
        position={Position.Top}
        style={{
          background: categoryColor,
          width: '10px',
          height: '10px',
          top: '-5px',
        }}
      />

      <div className="topic-content">
        <div className="topic-header">
          <div
            className="topic-icon"
            style={{ backgroundColor: categoryColor }}
          >
            <span role="img" aria-label={data.name}>
              {categoryIcon}
            </span>
          </div>
          <h3 className="topic-title">{data.name}</h3>
        </div>
        
        <div className="topic-stats">
          <div className="stat">
            <div className="stat-value">{data.questionsCount.toLocaleString('ru-RU')}</div>
            <div className="stat-label">вопросов</div>
          </div>
          <div className="stat-divider"></div>
          <div className="stat">
            <div className="stat-value">{data.clustersCount}</div>
            <div className="stat-label">кластеров</div>
          </div>
        </div>
        
        <div className="topic-time">
          {data.percentage.toFixed(1)}% от всех вопросов
        </div>
      </div>
    </div>
  );
};

export default InterviewCategoryNode;