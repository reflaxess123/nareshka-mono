import React, { useCallback, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './TopicTaskModal.scss';

interface Task {
  id: string;
  title: string;
  description: string;
  complexity_score: number;
  target_skill_level: string;
  estimated_time_minutes: number;
  programming_concepts: string[];
  js_features_used: string[];
}

interface Topic {
  key: string;
  title: string;
  icon: string;
  color: string;
  description: string;
}

interface TopicTaskModalProps {
  isOpen: boolean;
  onClose: () => void;
  topicKey: string | null;
}

const TopicTaskModal: React.FC<TopicTaskModalProps> = ({
  isOpen,
  onClose,
  topicKey,
}) => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [topic, setTopic] = useState<Topic | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [error, setError] = useState<string | null>(null);

  const fetchTopicTasks = useCallback(async () => {
    if (!topicKey) return;

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`/api/mindmap/topic/${topicKey}/tasks`);
      const result = await response.json();

      if (result.success) {
        setTopic(result.topic);
        setTasks(result.tasks);
      } else {
        setError('Ошибка загрузки задач');
      }
    } catch {
      setError('Ошибка сети');
    } finally {
      setLoading(false);
    }
  }, [topicKey]);

  useEffect(() => {
    if (isOpen && topicKey) {
      fetchTopicTasks();
    }
  }, [isOpen, topicKey, fetchTopicTasks]);

  const handleTaskClick = (taskId: string) => {
    navigate(`/code-editor?blockId=${taskId}`);
    onClose();
  };

  const getDifficultyColor = (level: string) => {
    switch (level) {
      case 'beginner':
        return '#10B981';
      case 'intermediate':
        return '#F59E0B';
      case 'advanced':
        return '#EF4444';
      default:
        return '#6B7280';
    }
  };

  const getDifficultyLabel = (level: string) => {
    switch (level) {
      case 'beginner':
        return 'Начальный';
      case 'intermediate':
        return 'Средний';
      case 'advanced':
        return 'Продвинутый';
      default:
        return 'Неизвестно';
    }
  };

  if (!isOpen) return null;

  return (
    <div className="topic-task-modal-overlay" onClick={onClose}>
      <div className="topic-task-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          {topic && (
            <div className="topic-info">
              <div
                className="topic-icon"
                style={{ backgroundColor: topic.color }}
              >
                {topic.icon}
              </div>
              <div className="topic-details">
                <h2 className="topic-title">{topic.title}</h2>
                <p className="topic-description">{topic.description}</p>
              </div>
            </div>
          )}
          <button className="close-button" onClick={onClose}>
            ✕
          </button>
        </div>

        <div className="modal-content">
          {loading && (
            <div className="loading-state">
              <div className="spinner">🔄</div>
              <p>Загрузка задач...</p>
            </div>
          )}

          {error && (
            <div className="error-state">
              <p>❌ {error}</p>
              <button onClick={fetchTopicTasks} className="retry-button">
                Повторить
              </button>
            </div>
          )}

          {!loading && !error && (
            <>
              <div className="tasks-header">
                <h3>Задачи ({tasks.length})</h3>
                <p>Кликните на задачу чтобы перейти в редактор кода</p>
              </div>

              <div className="tasks-list">
                {tasks.map((task) => (
                  <div
                    key={task.id}
                    className="task-item"
                    onClick={() => handleTaskClick(task.id)}
                  >
                    <div className="task-main">
                      <h4 className="task-title">{task.title}</h4>
                      {task.description && (
                        <p className="task-description">{task.description}</p>
                      )}
                    </div>

                    <div className="task-meta">
                      <div
                        className="difficulty-badge"
                        style={{
                          backgroundColor: getDifficultyColor(
                            task.target_skill_level
                          ),
                        }}
                      >
                        {getDifficultyLabel(task.target_skill_level)}
                      </div>

                      <div className="task-stats">
                        <span className="complexity">
                          Сложность: {task.complexity_score}/10
                        </span>
                        <span className="time">
                          ~{task.estimated_time_minutes} мин
                        </span>
                      </div>
                    </div>

                    {task.programming_concepts.length > 0 && (
                      <div className="task-concepts">
                        {task.programming_concepts
                          .slice(0, 3)
                          .map((concept) => (
                            <span key={concept} className="concept-tag">
                              {concept}
                            </span>
                          ))}
                        {task.programming_concepts.length > 3 && (
                          <span className="concept-tag more">
                            +{task.programming_concepts.length - 3}
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                ))}

                {tasks.length === 0 && (
                  <div className="empty-state">
                    <p>В этой группе пока нет задач</p>
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default TopicTaskModal;
