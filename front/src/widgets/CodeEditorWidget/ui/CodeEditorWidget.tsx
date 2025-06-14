import { useQuery } from '@tanstack/react-query';
import { AnimatePresence, motion } from 'framer-motion';
import { BarChart3, ChevronDown, ChevronUp, Code, History } from 'lucide-react';
import { useCallback, useState } from 'react';

import type { CodeExecutionResponse } from '@/shared/api/code-editor';
import { codeEditorApi, codeEditorKeys } from '@/shared/api/code-editor';
import { CodeEditor } from '@/shared/components/CodeEditor';

export interface CodeEditorWidgetProps {
  blockId: string;
  blockTitle: string;
  codeContent?: string;
  codeLanguage?: string;
  className?: string;
}

export const CodeEditorWidget = ({
  blockId,
  blockTitle,
  codeContent,
  codeLanguage = 'PYTHON',
  className = '',
}: CodeEditorWidgetProps) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [showStats, setShowStats] = useState(false);

  // Загружаем решения пользователя для этого блока
  const { data: solutions = [] } = useQuery({
    queryKey: codeEditorKeys.blockSolutions(blockId),
    queryFn: () => codeEditorApi.getBlockSolutions(blockId),
    enabled: isExpanded,
  });

  // Загружаем историю выполнений
  const { data: executions = [] } = useQuery({
    queryKey: codeEditorKeys.executions(),
    queryFn: () => codeEditorApi.getUserExecutions({ blockId, limit: 10 }),
    enabled: showHistory,
  });

  // Загружаем статистику
  const { data: stats } = useQuery({
    queryKey: codeEditorKeys.stats(),
    queryFn: codeEditorApi.getExecutionStats,
    enabled: showStats,
  });

  const handleExecutionComplete = useCallback(
    (result: CodeExecutionResponse) => {
      console.log('Code execution completed:', result);
      // Можно добавить уведомления или другую логику
    },
    []
  );

  const toggleExpanded = () => {
    setIsExpanded(!isExpanded);
  };

  const hasSolutions = solutions.length > 0;
  const latestSolution = solutions[0];

  return (
    <div className={`code-editor-widget ${className}`}>
      {/* Widget Header */}
      <div className="widget-header" onClick={toggleExpanded}>
        <div className="header-left">
          <Code className="w-5 h-5 text-blue-500" />
          <h3 className="widget-title">{blockTitle}</h3>
          {hasSolutions && (
            <span className="solution-badge">
              {solutions.length} решени{solutions.length > 1 ? 'я' : 'е'}
            </span>
          )}
        </div>

        <div className="header-right">
          <button
            className="expand-button"
            aria-label={
              isExpanded ? 'Свернуть редактор' : 'Развернуть редактор'
            }
          >
            {isExpanded ? (
              <ChevronUp className="w-5 h-5" />
            ) : (
              <ChevronDown className="w-5 h-5" />
            )}
          </button>
        </div>
      </div>

      {/* Widget Content */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            className="widget-content"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3, ease: 'easeInOut' }}
          >
            {/* Action Bar */}
            <div className="action-bar">
              <div className="action-left">
                {latestSolution && (
                  <div className="solution-info">
                    <span className="solution-language">
                      {latestSolution.supportedLanguage.name}
                    </span>
                    <span className="solution-stats">
                      {latestSolution.executionCount} запусков,
                      {latestSolution.successfulExecutions} успешных
                    </span>
                  </div>
                )}
              </div>

              <div className="action-right">
                <button
                  onClick={() => setShowHistory(!showHistory)}
                  className={`action-button ${showHistory ? 'active' : ''}`}
                  title="История выполнений"
                >
                  <History className="w-4 h-4" />
                  История
                </button>

                <button
                  onClick={() => setShowStats(!showStats)}
                  className={`action-button ${showStats ? 'active' : ''}`}
                  title="Статистика"
                >
                  <BarChart3 className="w-4 h-4" />
                  Статистика
                </button>
              </div>
            </div>

            {/* Code Editor */}
            <div className="editor-container">
              <CodeEditor
                blockId={blockId}
                initialCode={codeContent || latestSolution?.sourceCode}
                initialLanguage={codeLanguage}
                onExecutionComplete={handleExecutionComplete}
                height="500px"
              />
            </div>

            {/* History Panel */}
            <AnimatePresence>
              {showHistory && (
                <motion.div
                  className="history-panel"
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.2 }}
                >
                  <h4 className="panel-title">История выполнений</h4>

                  {executions.length === 0 ? (
                    <div className="empty-state">
                      <p>Пока нет истории выполнений для этого блока</p>
                    </div>
                  ) : (
                    <div className="execution-list">
                      {executions.slice(0, 5).map((execution) => (
                        <div key={execution.id} className="execution-item">
                          <div className="execution-header">
                            <span
                              className={`status-badge ${execution.status.toLowerCase()}`}
                            >
                              {execution.status}
                            </span>
                            <span className="execution-time">
                              {new Date(execution.createdAt).toLocaleString()}
                            </span>
                          </div>

                          {execution.executionTimeMs && (
                            <div className="execution-details">
                              <span>Время: {execution.executionTimeMs}ms</span>
                              {execution.memoryUsedMB && (
                                <span>Память: {execution.memoryUsedMB}MB</span>
                              )}
                            </div>
                          )}

                          {execution.errorMessage && (
                            <div className="execution-error">
                              {execution.errorMessage}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </motion.div>
              )}
            </AnimatePresence>

            {/* Stats Panel */}
            <AnimatePresence>
              {showStats && stats && (
                <motion.div
                  className="stats-panel"
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: 'auto', opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.2 }}
                >
                  <h4 className="panel-title">Статистика выполнения кода</h4>

                  <div className="stats-grid">
                    <div className="stat-item">
                      <div className="stat-value">{stats.totalExecutions}</div>
                      <div className="stat-label">Всего запусков</div>
                    </div>

                    <div className="stat-item">
                      <div className="stat-value">
                        {stats.successfulExecutions}
                      </div>
                      <div className="stat-label">Успешных</div>
                    </div>

                    <div className="stat-item">
                      <div className="stat-value">
                        {Math.round(stats.averageExecutionTime)}ms
                      </div>
                      <div className="stat-label">Среднее время</div>
                    </div>

                    <div className="stat-item">
                      <div className="stat-value">
                        {stats.totalExecutions > 0
                          ? Math.round(
                              (stats.successfulExecutions /
                                stats.totalExecutions) *
                                100
                            )
                          : 0}
                        %
                      </div>
                      <div className="stat-label">Успешность</div>
                    </div>
                  </div>

                  {stats.languageStats.length > 0 && (
                    <div className="language-stats">
                      <h5>Статистика по языкам:</h5>
                      <div className="language-list">
                        {stats.languageStats.map((langStat) => (
                          <div
                            key={langStat.language}
                            className="language-stat-item"
                          >
                            <span className="language-name">
                              {langStat.name}
                            </span>
                            <span className="language-count">
                              {langStat.executions} запусков
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
