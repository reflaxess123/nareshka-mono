import React, { useCallback, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { MarkdownContent } from '../../shared/components/MarkdownContent';
import { CodeTemplateGenerator } from '../../shared/utils/codeTemplateGenerator';
import './TopicTaskModal.scss';

interface Task {
  id: string;
  title: string;
  description: string;
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

  const handleTaskClick = async (task: Task) => {
    try {
      const response = await fetch(`/api/content/blocks/${task.id}`);
      const blockData = await response.json();

      if (blockData) {
        const templateResult = CodeTemplateGenerator.generateTemplate(
          blockData.codeContent || '',
          blockData.codeLanguage || 'javascript'
        );

        const params = new URLSearchParams({
          blockId: task.id,
          template: templateResult,
          language: blockData.codeLanguage || 'javascript',
          processed: 'true',
        });

        navigate(`/code-editor?${params.toString()}`);
      } else {
        navigate(`/code-editor?blockId=${task.id}`);
      }
    } catch (error) {
      console.error('Ошибка получения данных блока:', error);
      navigate(`/code-editor?blockId=${task.id}`);
    }
    onClose();
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
                    onClick={() => handleTaskClick(task)}
                  >
                    <div className="task-main">
                      <h4 className="task-title">{task.title}</h4>
                      {task.description && (
                        <MarkdownContent
                          content={task.description}
                          className="task-description"
                        />
                      )}
                    </div>
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
