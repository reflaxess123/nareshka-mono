import React from 'react';

interface MindMapToolbarProps {
  difficultyFilter: string;
  conceptFilter: string;
  onDifficultyFilter: (difficulty: string) => void;
  onConceptFilter: (concept: string) => void;
  onResetFilters: () => void;
  totalTasks: number;
}

export const MindMapToolbar: React.FC<MindMapToolbarProps> = ({
  difficultyFilter,
  conceptFilter,
  onDifficultyFilter,
  onConceptFilter,
  onResetFilters,
  totalTasks,
}) => {
  const difficulties = [
    { value: 'beginner', label: '🌱 Beginner', color: 'bg-green-500' },
    { value: 'intermediate', label: '🚀 Intermediate', color: 'bg-blue-500' },
    { value: 'advanced', label: '⚡ Advanced', color: 'bg-red-500' },
  ];

  const concepts = [
    { value: 'functions', label: '⚡ Functions' },
    { value: 'arrays', label: '📝 Arrays' },
    { value: 'objects', label: '📦 Objects' },
    { value: 'strings', label: '🔤 Strings' },
    { value: 'classes', label: '🏗️ Classes' },
    { value: 'async', label: '🔄 Async' },
  ];

  return (
    <div className="flex items-center space-x-4">
      {/* Фильтр по сложности */}
      <div className="flex items-center space-x-2">
        <span className="text-sm font-medium text-gray-700">Сложность:</span>
        <div className="flex space-x-1">
          {difficulties.map((diff) => (
            <button
              key={diff.value}
              onClick={() => onDifficultyFilter(diff.value)}
              className={`px-3 py-1 rounded-full text-xs font-medium transition-all ${
                difficultyFilter === diff.value
                  ? `${diff.color} text-white shadow-md`
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {diff.label}
            </button>
          ))}
        </div>
      </div>

      {/* Фильтр по концепциям */}
      <div className="flex items-center space-x-2">
        <span className="text-sm font-medium text-gray-700">Концепция:</span>
        <select
          value={conceptFilter}
          onChange={(e) => onConceptFilter(e.target.value)}
          className="px-3 py-1 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">Все концепции</option>
          {concepts.map((concept) => (
            <option key={concept.value} value={concept.value}>
              {concept.label}
            </option>
          ))}
        </select>
      </div>

      {/* Кнопка сброса */}
      {(difficultyFilter || conceptFilter) && (
        <button
          onClick={onResetFilters}
          className="px-3 py-1 bg-gray-500 text-white rounded-md text-xs hover:bg-gray-600 transition-colors"
        >
          Сбросить
        </button>
      )}

      {/* Счетчик задач */}
      <div className="text-sm text-gray-500 border-l border-gray-300 pl-4">
        {totalTasks} задач
      </div>
    </div>
  );
};
