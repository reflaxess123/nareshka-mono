import React from 'react';
import { MarkdownContent } from '../../shared/components/MarkdownContent';
import type { TaskDetail } from '../../types/mindmap';

interface TaskDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  task: TaskDetail | null;
}

export const TaskDetailModal: React.FC<TaskDetailModalProps> = ({
  isOpen,
  onClose,
  task,
}) => {
  if (!isOpen || !task) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Overlay */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="flex min-h-full items-center justify-center p-4">
        <div className="relative bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b">
            <div>
              <h2 className="text-xl font-bold text-gray-900">{task.title}</h2>
              <p className="text-sm text-gray-600">
                {task.category} / {task.subcategory}
              </p>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <svg
                className="w-6 h-6"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>

          {/* Content */}
          <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Left column */}
              <div className="space-y-4">
                {/* Description */}
                {task.text_content && (
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-2">
                      📝 Описание
                    </h3>
                    <div
                      className="bg-gray-50 rounded-lg p-4 text-sm text-gray-700"
                      style={{ whiteSpace: 'pre-line' }}
                    >
                      <MarkdownContent content={task.text_content} />
                    </div>
                  </div>
                )}

                {/* Concepts */}
                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">
                    💡 Концепции
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {task.programming_concepts.map((concept, index) => (
                      <span
                        key={index}
                        className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"
                      >
                        {concept}
                      </span>
                    ))}
                  </div>
                </div>

                {/* JS Features */}
                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">
                    ⚡ JS Фичи
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {task.js_features_used.map((feature, index) => (
                      <span
                        key={index}
                        className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full"
                      >
                        {feature}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Stats */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-purple-50 rounded-lg p-3">
                    <div className="text-sm text-purple-600 font-medium">
                      Сложность
                    </div>
                    <div className="text-lg font-bold text-purple-900">
                      {task.complexity_score}/10
                    </div>
                  </div>
                  <div className="bg-orange-50 rounded-lg p-3">
                    <div className="text-sm text-orange-600 font-medium">
                      Время
                    </div>
                    <div className="text-lg font-bold text-orange-900">
                      {task.estimated_time_minutes} мин
                    </div>
                  </div>
                </div>
              </div>

              {/* Right column - Code */}
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">
                  💻 Код ({task.code_lines} строк)
                </h3>
                <div className="bg-gray-900 rounded-lg p-4 overflow-x-auto">
                  <pre className="text-sm text-gray-100">
                    <code>{task.code_content}</code>
                  </pre>
                </div>
              </div>
            </div>

            {/* Path */}
            {task.path_titles.length > 0 && (
              <div className="mt-6 pt-6 border-t">
                <h3 className="font-semibold text-gray-900 mb-2">
                  🛤️ Путь обучения
                </h3>
                <div className="text-sm text-gray-600">
                  {task.path_titles.join(' → ')}
                </div>
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="px-6 py-4 border-t bg-gray-50">
            <div className="flex justify-between items-center text-sm text-gray-600">
              <div>
                Уровень:{' '}
                <span className="font-medium">{task.target_skill_level}</span>
              </div>
              <div>
                Тип:{' '}
                <span className="font-medium">{task.pedagogical_type}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
