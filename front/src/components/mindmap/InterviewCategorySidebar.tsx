import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import styles from './InterviewCategorySidebar.module.scss';

interface ClusterInfo {
  id: number;
  name: string;
  questions_count: number;
  interview_count?: number; // Количество уникальных интервью
  interview_penetration?: number; // Процент от всех интервью
  keywords: string[];
  example_question?: string;
  sample_questions?: string[];
  // Добавлено: идентификатор категории для фильтрации на клиенте
  category_id?: string;
}

interface CompanyStats {
  company: string;
  questions_count: number;
}

interface CategoryDetails {
  id: string;
  name: string;
  questions_count: number;
  clusters_count: number;
  percentage: number;
  clusters: ClusterInfo[];
  top_companies: CompanyStats[];
  sample_questions: Array<{
    id: string;
    question_text: string;
    company: string;
  }>;
}

interface InterviewCategorySidebarProps {
  isOpen: boolean;
  onClose: () => void;
  categoryId: string | null;
  categoryName: string;
  questionsCount: number;
  clustersCount: number;
  percentage: number;
}

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

export const InterviewCategorySidebar: React.FC<InterviewCategorySidebarProps> = ({
  isOpen,
  onClose,
  categoryId,
  categoryName,
  questionsCount,
  clustersCount,
  percentage
}) => {
  const [loading, setLoading] = useState(false);
  const [categoryDetails, setCategoryDetails] = useState<CategoryDetails | null>(null);
  const [expandedClusters, setExpandedClusters] = useState<Set<number>>(new Set());
  const [clusterQuestions, setClusterQuestions] = useState<Record<number, string[]>>({});

  useEffect(() => {
    if (!categoryId || !isOpen) return;

    // Сбрасываем состояние при смене категории
    setCategoryDetails(null);
    setExpandedClusters(new Set());
    setClusterQuestions({});

    const fetchCategoryDetails = async () => {
      setLoading(true);
      try {
        // Загружаем кластеры категории (бек может вернуть все узлы, поэтому фильтруем клиентом)
        const clustersRes = await fetch(
          `/api/v2/cluster-visualization/constellation?category_id=${categoryId}&limit=200`
        );
        const clustersData = await clustersRes.json();

        const allNodes: ClusterInfo[] = (clustersData?.nodes || []) as ClusterInfo[];
        const filteredNodes = allNodes.filter((n) => String(n.category_id ?? '') === String(categoryId));

        setCategoryDetails({
          id: categoryId,
          name: categoryName,
          questions_count: questionsCount,
          clusters_count: clustersCount,
          percentage,
          clusters: filteredNodes,
          top_companies: [],
          sample_questions: []
        });
      } catch (error) {
        console.error('Error fetching category details:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchCategoryDetails();
  }, [categoryId, isOpen, categoryName, clustersCount, percentage, questionsCount]);

  const toggleCluster = async (clusterId: number) => {
    setExpandedClusters(prev => {
      const newSet = new Set(prev);
      const isExpanding = !newSet.has(clusterId);
      if (isExpanding) {
        newSet.add(clusterId);
        // Загружаем вопросы для кластера при первом раскрытии
        if (!clusterQuestions[clusterId]) {
          void loadClusterQuestions(clusterId);
        }
      } else {
        newSet.delete(clusterId);
      }
      return newSet;
    });
  };

  type QuestionLike = { question_text?: string; text?: string } | string;

  const hasQuestionsField = (data: unknown): data is { questions: QuestionLike[] } => {
    return typeof data === 'object' && data !== null && Array.isArray((data as { questions?: unknown }).questions);
  };

  const isQuestionsArray = (data: unknown): data is QuestionLike[] => Array.isArray(data);

  const normalizeQuestions = (data: unknown): string[] => {
    const arr: QuestionLike[] = hasQuestionsField(data)
      ? data.questions
      : isQuestionsArray(data)
      ? data
      : [];
    return arr
      .slice(0, 10)
      .map((q) => (typeof q === 'string' ? q : (q.question_text ?? q.text ?? '')))
      .filter((q): q is string => Boolean(q));
  };

  const loadClusterQuestions = async (clusterId: number) => {
    try {
      // Попробуем загрузить вопросы для конкретного кластера
      const response = await fetch(
        `/api/v2/interview-categories/cluster/${clusterId}/questions?limit=10`
      );

      if (response.ok) {
        const data = await response.json();
        const questions = normalizeQuestions(data);

        setClusterQuestions(prev => ({
          ...prev,
          [clusterId]: questions
        }));
      }
    } catch (error) {
      console.error('Error loading cluster questions:', error);
    }
  };

  if (!isOpen) return null;

  const categoryIcon = categoryIcons[categoryId || ''] || '📝';

  return (
    <>
      <div className={styles.overlay} onClick={onClose} />
      <div className={styles.sidebar}>
        <div className={styles.header}>
          <div className={styles.headerTop}>
            <button className={styles.closeButton} onClick={onClose}>
              ✕
            </button>
          </div>

          <div className={styles.categoryInfo}>
            <div className={styles.categoryIcon}>{categoryIcon}</div>
            <h2 className={styles.categoryTitle}>{categoryName}</h2>
            <div className={styles.categoryStats}>
              <div className={styles.statBadge}>
                <span className={styles.statValue}>{questionsCount.toLocaleString('ru-RU')}</span>
                <span className={styles.statLabel}>вопросов</span>
              </div>
              <div className={styles.statBadge}>
                <span className={styles.statValue}>{clustersCount}</span>
                <span className={styles.statLabel}>кластеров</span>
              </div>
              <div className={styles.statBadge}>
                <span className={styles.statValue}>{percentage.toFixed(1)}%</span>
                <span className={styles.statLabel}>от всех</span>
              </div>
            </div>
          </div>

          {/* Ссылка на полную базу вопросов */}
          <div className={styles.viewAllLink}>
            <Link 
              to={`/questions-database?cat=${categoryId}`}
              className={styles.viewAllButton}
            >
              📋 Посмотреть все {questionsCount.toLocaleString('ru-RU')} вопросов
            </Link>
            <div className={styles.viewAllHint}>
              Перейти к полной базе данных с фильтрацией и поиском
            </div>
          </div>
        </div>


        <div className={styles.content}>
          {loading ? (
            <div className={styles.loading}>
              <div className={styles.spinner} />
              <span>Загрузка данных...</span>
            </div>
          ) : (
            <>
              {categoryDetails && (
                <div className={styles.clustersTab}>
                  <h3 className={styles.sectionTitle}>
                    Топ-20 кластеров по количеству вопросов
                  </h3>
                  <div className={styles.sectionSubtitle}>
                    Показано {Math.min(20, categoryDetails.clusters.length)} из {categoryDetails.clusters.length} кластеров
                  </div>
                  <div className={styles.clustersList}>
                    {categoryDetails.clusters
                      .sort((a, b) => b.questions_count - a.questions_count)
                      .slice(0, 20)
                      .map((cluster, index) => {
                        const isExpanded = expandedClusters.has(cluster.id);
                        const questions = clusterQuestions[cluster.id] || [];
                        return (
                          <div key={cluster.id} className={styles.clusterItem}>
                            <div
                              className={styles.clusterHeader}
                              onClick={() => toggleCluster(cluster.id)}
                              style={{ cursor: 'pointer' }}
                            >
                              <span className={styles.clusterRank}>#{index + 1}</span>
                              <h4 className={styles.clusterName}>{cluster.name}</h4>
                              <div className={styles.clusterActions}>
                                <div className={styles.clusterStats}>
                                  <span className={styles.clusterCount}>
                                    {cluster.questions_count} вопросов
                                  </span>
                                  {cluster.interview_count && (
                                    <span className={styles.interviewCount}>
                                      {cluster.interview_count} интервью
                                    </span>
                                  )}
                                </div>
                                <span className={styles.expandIcon}>
                                  {isExpanded ? '▼' : '▶'}
                                </span>
                              </div>
                            </div>

                            {isExpanded && (
                              <div className={styles.clusterContent}>
                                <div className={styles.exampleQuestions}>
                                  <span className={styles.questionsLabel}>Примеры вопросов ({cluster.questions_count} всего):</span>
                                  <div className={styles.questionsList}>
                                    {/* Сначала показываем загруженные вопросы */}
                                    {questions.length > 0 ? (
                                      questions.map((question, qIdx) => (
                                        <div key={qIdx} className={styles.questionItem}>
                                          <span className={styles.questionBullet}>•</span>
                                          <span className={styles.questionText}>
                                            {question}
                                          </span>
                                        </div>
                                      ))
                                    ) : (
                                      /* Если вопросы еще не загружены, показываем example_question */
                                      cluster.example_question ? (
                                        <div className={styles.questionItem}>
                                          <span className={styles.questionBullet}>•</span>
                                          <span className={styles.questionText}>
                                            {cluster.example_question}
                                          </span>
                                        </div>
                                      ) : (
                                        <div className={styles.noQuestions}>
                                          Загрузка вопросов...
                                        </div>
                                      )
                                    )}
                                  </div>
                                </div>
                              </div>
                            )}
                          </div>
                        );
                      })}
                  </div>
                </div>
              )}


            </>
          )}
        </div>
      </div>
    </>
  );
};

export default InterviewCategorySidebar;
