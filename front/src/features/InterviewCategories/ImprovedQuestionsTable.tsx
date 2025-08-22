import React, { useState, useCallback } from 'react';
import { Copy, Users, Tag, FileText, Hash } from 'lucide-react';
import styles from './ImprovedQuestionsTable.module.scss';

interface Question {
  id: string;
  question_text: string;
  company?: string;
  topic_name?: string;
  cluster_id?: number;
  category_id?: string;
  interview_id?: string;
}

interface ImprovedQuestionsTableProps {
  questions: Question[];
  currentPage: number;
  itemsPerPage: number;
  onQuestionSelect: (question: Question) => void;
  onShowSameInterview: (interviewId: string) => void;
  interviewCounts: Record<string, number>;
}

export const ImprovedQuestionsTable: React.FC<ImprovedQuestionsTableProps> = ({
  questions,
  currentPage,
  itemsPerPage,
  onQuestionSelect,
  onShowSameInterview,
  interviewCounts
}) => {
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [hoveredRow, setHoveredRow] = useState<string | null>(null);

  const handleCopyQuestion = useCallback(async (question: Question) => {
    try {
      await navigator.clipboard.writeText(question.question_text);
      setCopiedId(question.id);
      setTimeout(() => setCopiedId(null), 2000);
      onQuestionSelect(question);
    } catch (err) {
      console.error('Ошибка копирования:', err);
    }
  }, [onQuestionSelect]);

  const formatInterviewName = useCallback((interviewId: string) => {
    if (!interviewId) return '';
    // Преобразуем interview_sber_frontend_2 в "Сбер Frontend #3"
    const parts = interviewId.replace('interview_', '').split('_');
    const number = parts[parts.length - 1];
    const isNumber = !isNaN(parseInt(number));
    
    if (isNumber) {
      const companyAndRole = parts.slice(0, -1).join(' ');
      const formatted = companyAndRole.charAt(0).toUpperCase() + companyAndRole.slice(1);
      return `${formatted} #${parseInt(number) + 1}`;
    }
    
    return parts.join(' ').charAt(0).toUpperCase() + parts.join(' ').slice(1);
  }, []);

  const getCategoryColor = useCallback((categoryId: string) => {
    const colors: Record<string, string> = {
      'javascript_core': '#f7df1e',
      'react': '#61dafb',
      'typescript': '#3178c6',
      'soft_skills': '#10b981',
      'network': '#8b5cf6',
      'algorithms': '#ef4444',
      'layout': '#f97316',
      'tools': '#6b7280',
      'performance': '#eab308',
      'browsers': '#06b6d4',
      'testing': '#ec4899',
      'architecture': '#6366f1',
      'other': '#9ca3af'
    };
    return colors[categoryId] || '#9ca3af';
  }, []);

  const getCategoryName = useCallback((categoryId: string) => {
    const names: Record<string, string> = {
      'javascript_core': 'JavaScript',
      'react': 'React',
      'typescript': 'TypeScript',
      'soft_skills': 'Soft Skills',
      'network': 'Сеть',
      'algorithms': 'Алгоритмы',
      'layout': 'Верстка',
      'tools': 'Инструменты',
      'performance': 'Производительность',
      'browsers': 'Браузеры',
      'testing': 'Тестирование',
      'architecture': 'Архитектура',
      'other': 'Другое'
    };
    return names[categoryId] || categoryId;
  }, []);


  return (
    <div className={styles.improvedTable}>
      {questions.map((question, index) => {
        const globalIndex = ((currentPage - 1) * itemsPerPage) + index + 1;
        const isHovered = hoveredRow === question.id;
        const isCopied = copiedId === question.id;

        return (
          <div
            key={question.id}
            className={`${styles.questionRow} ${isHovered ? styles.hovered : ''} ${isCopied ? styles.copied : ''}`}
            onMouseEnter={() => setHoveredRow(question.id)}
            onMouseLeave={() => setHoveredRow(null)}
          >
            {/* Основная строка */}
            <div className={styles.mainRow} onClick={() => handleCopyQuestion(question)}>
              <div className={styles.leftSection}>
                <span className={styles.index}>
                  <Hash size={12} />
                  {globalIndex}
                </span>
              </div>

              <div className={styles.questionContent}>
                <div className={styles.questionText}>
                  {question.question_text}
                </div>
                
                <div className={styles.inlineMetadata}>
                  {question.company && (
                    <span className={styles.companyBadge}>
                      <Users size={10} />
                      {question.company}
                    </span>
                  )}
                  {question.category_id && (
                    <span 
                      className={styles.categoryBadge}
                      style={{ 
                        backgroundColor: `${getCategoryColor(question.category_id)}15`,
                        borderColor: getCategoryColor(question.category_id)
                      }}
                    >
                      <Tag size={10} />
                      {getCategoryName(question.category_id)}
                    </span>
                  )}
                  {question.interview_id && (
                    <button
                      className={styles.interviewBadge}
                      onClick={(e) => {
                        e.stopPropagation();
                        onShowSameInterview(question.interview_id!);
                      }}
                    >
                      <FileText size={10} />
                      <span className={styles.interviewText}>
                        {formatInterviewName(question.interview_id)}
                        {interviewCounts[question.interview_id] > 1 && (
                          <span className={styles.interviewCount}>
                            {' '}• {interviewCounts[question.interview_id]} вопр
                          </span>
                        )}
                      </span>
                    </button>
                  )}
                </div>
              </div>

              <div className={styles.rightSection}>
                <div className={styles.copyIndicator}>
                  {isCopied ? (
                    <span className={styles.copiedText}>✓</span>
                  ) : (
                    <Copy size={14} className={styles.copyIcon} />
                  )}
                </div>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};