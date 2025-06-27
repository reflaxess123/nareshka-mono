import { CheckCircle, Circle, Clock, X } from 'lucide-react';
import React, { useEffect, useState } from 'react';
import './MindMapProgressSidebar.scss';

interface Task {
  id: string;
  title: string;
  description?: string;
  hasCode: boolean;
  progress?: {
    solvedCount: number;
    isCompleted: boolean;
  } | null;
}

interface TopicData {
  key: string;
  title: string;
  icon: string;
  color: string;
  description: string;
}

interface TopicResponse {
  success: boolean;
  topic: TopicData;
  tasks: Task[];
  stats?: {
    totalTasks: number;
    completedTasks: number;
    completionRate: number;
  } | null;
}

interface MindMapProgressSidebarProps {
  isOpen: boolean;
  onClose: () => void;
  selectedTopic: {
    key: string;
    title: string;
    description: string;
    color: string;
    icon: string;
  } | null;
  onTaskClick?: (taskId: string) => void;
}

const MindMapProgressSidebar: React.FC<MindMapProgressSidebarProps> = ({
  isOpen,
  onClose,
  selectedTopic,
  onTaskClick,
}) => {
  const [topicData, setTopicData] = useState<TopicResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (selectedTopic && isOpen) {
      fetchTopicProgress();
    }
  }, [selectedTopic, isOpen]);

  const fetchTopicProgress = async () => {
    if (!selectedTopic) return;

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `/api/mindmap/topic/${selectedTopic.key}/tasks`,
        {
          credentials: 'include',
        }
      );

      if (!response.ok) {
        throw new Error('Ошибка загрузки данных о прогрессе');
      }

      const data = await response.json();
      console.log('Topic progress data:', data); // Для отладки
      setTopicData(data);
    } catch (err) {
      console.error('Error fetching topic progress:', err);
      setError(err instanceof Error ? err.message : 'Произошла ошибка');
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (task: Task) => {
    if (!task.progress)
      return <Circle className="status-not-started" size={16} />;
    if (task.progress.isCompleted)
      return <CheckCircle className="status-completed" size={16} />;
    if (task.progress.solvedCount > 0)
      return <Clock className="status-in-progress" size={16} />;
    return <Circle className="status-not-started" size={16} />;
  };

  const getStatusText = (task: Task) => {
    if (!task.progress) return 'Не начато';
    if (task.progress.isCompleted) return 'Решено';
    if (task.progress.solvedCount > 0) return 'В процессе';
    return 'Не начато';
  };

  const handleTaskClick = (task: Task) => {
    if (
      task.hasCode &&
      onTaskClick &&
      (!task.progress || !task.progress.isCompleted)
    ) {
      onTaskClick(task.id);
    }
  };

  return (
    <div className={`mindmap-progress-sidebar ${isOpen ? 'open' : ''}`}>
      <div className="sidebar-content">
        <div className="sidebar-header">
          <div className="header-title">
            <h2>Детали прогресса</h2>
          </div>
          <button className="close-button" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        {!selectedTopic ? (
          <div className="empty-selection">
            <div className="empty-icon">🎯</div>
            <h3>Выберите категорию</h3>
            <p>
              Кликните на любую категорию на карте знаний, чтобы увидеть
              детальную информацию о прогрессе и списке задач.
            </p>
          </div>
        ) : (
          <div className="topic-section">
            {loading && (
              <div className="loading-state">
                <div className="spinner">⏳</div>
                <p>Загрузка данных о прогрессе...</p>
              </div>
            )}

            {error && (
              <div className="error-state">
                <p>Ошибка: {error}</p>
                <button className="retry-button" onClick={fetchTopicProgress}>
                  Повторить
                </button>
              </div>
            )}

            {!loading && !error && (
              <>
                <div className="topic-info">
                  <div className="topic-header">
                    <div
                      className="topic-icon"
                      style={{ backgroundColor: selectedTopic.color }}
                    >
                      <span>{selectedTopic.icon}</span>
                    </div>
                    <div className="topic-details">
                      <h3 className="topic-title">{selectedTopic.title}</h3>
                      <p className="topic-description">
                        {selectedTopic.description}
                      </p>
                    </div>
                  </div>

                  {topicData?.stats ? (
                    <div className="topic-progress">
                      <div className="progress-stats">
                        <span className="stat">
                          {topicData.stats.completedTasks}/
                          {topicData.stats.totalTasks} задач
                        </span>
                        <span className="percentage">
                          {Math.round(topicData.stats.completionRate)}%
                        </span>
                      </div>
                    </div>
                  ) : (
                    <div className="topic-progress">
                      <div className="progress-stats">
                        <span className="stat">
                          {topicData
                            ? `0/${topicData.tasks.filter((t) => t.hasCode).length} задач`
                            : 'Загрузка...'}
                        </span>
                        <span className="percentage">0%</span>
                      </div>
                    </div>
                  )}
                </div>

                {topicData && (
                  <div className="tasks-section">
                    <div className="tasks-header">
                      <h4>
                        Задачи (
                        {topicData.tasks.filter((t) => t.hasCode).length})
                      </h4>
                      <p>Кликните на задачу чтобы перейти в редактор кода</p>
                    </div>

                    <div className="tasks-list">
                      {topicData.tasks.filter((t) => t.hasCode).length > 0 ? (
                        topicData.tasks
                          .filter((task) => task.hasCode)
                          .map((task) => (
                            <div
                              key={task.id}
                              className={`task-item ${
                                task.hasCode &&
                                (!task.progress || !task.progress.isCompleted)
                                  ? 'clickable'
                                  : 'disabled'
                              } ${task.progress?.isCompleted ? 'completed' : ''}`}
                              onClick={() => handleTaskClick(task)}
                            >
                              <div className="task-header">
                                <div className="task-status">
                                  {getStatusIcon(task)}
                                </div>
                                <div className="task-main">
                                  <h5 className="task-title">{task.title}</h5>
                                  <div className="task-status-text">
                                    {getStatusText(task)}
                                  </div>
                                </div>
                                {task.progress &&
                                  task.progress.solvedCount > 0 && (
                                    <div className="solve-count">
                                      {task.progress.solvedCount}
                                    </div>
                                  )}
                              </div>
                              {task.description && (
                                <div className="task-description">
                                  {task.description}
                                </div>
                              )}
                              {task.progress?.isCompleted && (
                                <div className="task-note">
                                  Задача уже решена
                                </div>
                              )}
                              {!task.hasCode && (
                                <div className="task-note">
                                  Теоретическая задача
                                </div>
                              )}
                            </div>
                          ))
                      ) : (
                        <div className="empty-state">
                          <p>Задачи с кодом не найдены</p>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default MindMapProgressSidebar;
