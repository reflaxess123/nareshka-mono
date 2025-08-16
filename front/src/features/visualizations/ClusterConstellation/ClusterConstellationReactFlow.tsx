import React, { useEffect, useState, useCallback, useMemo } from 'react';

// Подавление ошибки ResizeObserver
const suppressResizeObserverError = () => {
  const originalError = console.error;
  console.error = (...args) => {
    const message = args[0];
    if (typeof message === 'string' && message.includes('ResizeObserver loop completed with undelivered notifications')) {
      return; // Игнорируем эту конкретную ошибку
    }
    originalError.apply(console, args);
  };
};

// Инициализируем подавление ошибки
suppressResizeObserverError();
import {
  ReactFlow,
  Node,
  Edge,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  ConnectionMode,
  NodeTypes,
  Handle,
  Position,
  NodeProps,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import styles from './ClusterConstellationReactFlow.module.scss';

interface ClusterNodeData {
  id: number;
  name: string;
  category_id: string;
  category_name: string;
  questions_count: number;
  interview_penetration: number;
  keywords: string[];
  example_question: string;
  size: number;
  top_companies: string[];
  difficulty_distribution: { junior: number; middle: number; senior: number };
  // Новые полезные поля
  rank: number;
  isTopCluster: boolean;
  difficultyLevel: 'high' | 'medium' | 'low';
  demandStatus: string;
}

interface ConstellationData {
  nodes: ClusterNodeData[];
  links: { source: number; target: number; weight: number; strength: number }[];
  categories: Record<string, string>;
  stats: any;
}

const categoryColors: Record<string, string> = {
  'javascript_core': '#f7df1e',
  'react': '#61dafb',
  'typescript': '#3178c6',
  'soft_skills': '#ff6b6b',
  'алгоритмы': '#dc143c',
  'сет': '#ff6b35',
  'верстка': '#e91e63',
  'браузеры': '#9c27b0',
  'архитектура': '#673ab7',
  'инструменты': '#3f51b5',
  'производителност': '#00bcd4',
  'тестирование': '#4caf50',
  'другое': '#9e9e9e'
};

// Импортируем компоненты для иерархической структуры
import ClusterNode from './ClusterNode';
import RootNode from './RootNode';
import CategoryNode from './CategoryNode';

// Кастомный блочный узел кластера - оптимизирован для производительности
const ClusterNodeComponent: React.FC<NodeProps<ClusterNodeData & { isHovered?: boolean; isFocused?: boolean }>> = (props) => {
  return (
    <ClusterNode 
      {...props} 
      isHovered={props.data.isHovered} 
      isFocused={props.data.isFocused}
    />
  );
};

// Компонент корневого узла
const RootNodeComponent: React.FC<NodeProps<any>> = (props) => {
  return (
    <RootNode 
      {...props} 
      isHovered={props.data.isHovered}
    />
  );
};

// Компонент узла категории
const CategoryNodeComponent: React.FC<NodeProps<any>> = (props) => {
  return (
    <CategoryNode 
      {...props} 
      isHovered={props.data.isHovered}
    />
  );
};

const nodeTypes: NodeTypes = {
  root: RootNodeComponent,
  category: CategoryNodeComponent,
  cluster: ClusterNodeComponent,
};

export const ClusterConstellationReactFlow: React.FC = () => {
  const [data, setData] = useState<ConstellationData | null>(null);
  const [selectedNode, setSelectedNode] = useState<ClusterNodeData | null>(null);
  const [hoveredNode, setHoveredNode] = useState<ClusterNodeData | null>(null);
  const [focusedNode, setFocusedNode] = useState<ClusterNodeData | null>(null);
  const [loading, setLoading] = useState(true);
  const [hoverTimeout, setHoverTimeout] = useState<NodeJS.Timeout | null>(null);
  const [clusterQuestions, setClusterQuestions] = useState<any>(null);
  const [loadingQuestions, setLoadingQuestions] = useState(false);
  // Убираем состояние раскрытия - всегда показываем иерархию
  
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  // Загрузка корректных данных категорий с правильным подсчетом кластеров
  useEffect(() => {
    // Загружаем правильную статистику и исправляем clusters_count
    Promise.all([
      fetch('/api/v2/interview-categories/').then(res => res.json()),
      // Загружаем все кластеры для правильного подсчета
      fetch('/api/v2/cluster-visualization/constellation?min_interview_count=1&limit=200').then(res => res.json())
    ])
    .then(([categories, clusterData]) => {
      console.log('Загруженные категории:', categories);
      console.log('Данные кластеров:', clusterData);
      
      // Подсчитываем реальное количество кластеров по категориям
      const clusterCounts = {};
      if (clusterData.nodes) {
        clusterData.nodes.forEach(cluster => {
          clusterCounts[cluster.category_id] = (clusterCounts[cluster.category_id] || 0) + 1;
        });
      }
      
      // Исправляем данные категорий с правильным clusters_count
      const correctedCategories = categories.map(cat => ({
        ...cat,
        clusters_count: clusterCounts[cat.id] || 0 // Используем реальный подсчет
      }));
      
      console.log('Исправленные категории:', correctedCategories);
      
      // Создаем корректные данные для визуализации
      const correctData = {
        nodes: clusterData.nodes || [],
        links: clusterData.links || [],
        categories: categories.reduce((acc, cat) => {
          acc[cat.id] = cat.name;
          return acc;
        }, {}),
        stats: { 
          total_clusters: Object.values(clusterCounts).reduce((sum, count) => sum + count, 0),
          total_questions: categories.reduce((sum, cat) => sum + (cat.questions_count || 0), 0)
        },
        // Используем исправленные данные категорий
        categoriesStats: correctedCategories
      };
      
      console.log('Финальные данные:', correctData);
      setData(correctData);
    })
    .catch(err => {
      console.error('Ошибка загрузки данных:', err);
      setData(null);
    })
    .finally(() => setLoading(false));
  }, []);
  
  // Очистка таймаутов при размонтировании
  useEffect(() => {
    return () => {
      if (hoverTimeout) clearTimeout(hoverTimeout);
    };
  }, [hoverTimeout]);

  // Улучшенное иерархическое расположение узлов
  const memoizedNodes = useMemo(() => {
    if (!data) return [];

    const flowNodes: Node[] = [];
    const centerX = 800; // Центр координат
    const centerY = 500;
    
    // Размеры корневого блока
    const rootWidth = 300;
    const rootHeight = 200;

    // 1. Создаем корневой узел в центре
    flowNodes.push({
      id: 'root',
      type: 'root',
      position: { x: centerX - rootWidth/2, y: centerY - rootHeight/2 },
      data: {
        totalQuestions: data.stats?.total_questions || 8532,
        totalClusters: data.stats?.total_clusters || 182,
        totalCategories: Object.keys(data.categories || {}).length || 13,
        isHovered: hoveredNode?.id === 'root'
      },
      draggable: false,
    });

    // 2. Используем правильные данные из categoriesStats
    const categories = (data.categoriesStats || []).map(category => ({
      id: category.id,
      name: category.name,
      questionsCount: category.questions_count || 0,
      clustersCount: category.clusters_count || 0,
      avgPenetration: category.percentage || 0,
      clusters: [], // Пока не загружаем кластеры
      isExpanded: true
    })).sort((a, b) => b.questionsCount - a.questionsCount);

    // 4. Простое равномерное размещение 13 категорий по кругу
    const categoryRadius = 520; // Увеличиваем радиус для избежания слипания
    
    categories.forEach((category, index) => {
      // Компактные размеры после упрощения контента
      const categoryWidth = 200;
      const categoryHeight = 120;
      
      // Равномерное распределение 13 категорий по кругу
      const angle = (index / categories.length) * 2 * Math.PI - Math.PI / 2;
      const x = centerX + Math.cos(angle) * categoryRadius - categoryWidth/2;
      const y = centerY + Math.sin(angle) * categoryRadius - categoryHeight/2;

      flowNodes.push({
        id: `category-${category.id}`,
        type: 'category',
        position: { x, y },
        data: {
          ...category,
          isHovered: hoveredNode?.id === `category-${category.id}`
        },
        draggable: false, // Отключаем перетаскивание
      });

      // 5. Пока не показываем кластеры - только корень и категории
      // (кластеры будут добавлены позже при клике на категорию)
    });

    return flowNodes;
  }, [data, hoveredNode, focusedNode]);

  // Создаем иерархические связи: корень → категории → кластеры
  const memoizedEdges = useMemo(() => {
    if (!data) return [];

    const flowEdges: Edge[] = [];

    // Связи от корня к категориям
    (data.categoriesStats || []).forEach(category => {
      flowEdges.push({
        id: `root-to-${category.id}`,
        source: 'root',
        target: `category-${category.id}`,
        type: 'straight',
        style: { 
          stroke: '#61dafb', 
          strokeWidth: 2,
          opacity: 0.6
        },
        animated: false,
      });
    });

    return flowEdges;
  }, [data]);

  // Обновляем узлы и связи только при изменении мемоизированных данных
  useEffect(() => {
    setNodes(memoizedNodes);
    setEdges(memoizedEdges);
  }, [memoizedNodes, memoizedEdges, setNodes, setEdges]);

  const onNodeMouseLeave = useCallback(() => {
    if (hoverTimeout) clearTimeout(hoverTimeout);
    const timeout = setTimeout(() => {
      setHoveredNode(null);
    }, 150);
    setHoverTimeout(timeout);
  }, [hoverTimeout]);
  
  // Загрузка детальной информации о кластере
  const loadClusterQuestions = useCallback(async (clusterId: number) => {
    setLoadingQuestions(true);
    try {
      const response = await fetch(`/api/v2/cluster-visualization/cluster/${clusterId}/questions`);
      const data = await response.json();
      setClusterQuestions(data);
    } catch (error) {
      console.error('Ошибка загрузки вопросов кластера:', error);
      setClusterQuestions({ error: 'Не удалось загрузить вопросы', questions: [] });
    } finally {
      setLoadingQuestions(false);
    }
  }, []);

  // Обработка клика на узел
  const onNodeClick = useCallback((event: React.MouseEvent, node: Node) => {
    event.preventDefault();
    event.stopPropagation();
    
    // Обработка клика на корневой узел
    if (node.id === 'root') {
      // Можно добавить общую статистику
      return;
    }
    
    // Обработка клика на категорию - показываем информацию о категории
    if (node.id.startsWith('category-')) {
      // Можно добавить детальную информацию о категории
      console.log('Клик на категорию:', node.data.name);
      return;
    }
    
    // Обработка клика на кластер - детальная информация
    if (focusedNode && focusedNode.id === parseInt(node.id)) {
      setFocusedNode(null);
      setSelectedNode(null);
      setClusterQuestions(null);
    } else {
      setFocusedNode(node.data);
      setSelectedNode(node.data);
      loadClusterQuestions(parseInt(node.id));
    }
  }, [focusedNode, loadClusterQuestions]);

  // Обработка hover на узел с debouncing
  const onNodeMouseEnter = useCallback((event: React.MouseEvent, node: Node) => {
    if (hoverTimeout) clearTimeout(hoverTimeout);
    setHoveredNode({ id: node.id });
  }, [hoverTimeout]);

  // Настройки MiniMap
  const miniMapNodeColor = useCallback((node: Node<ClusterNodeData>) => {
    return categoryColors[node.data.category_id] || '#999';
  }, []);

  if (loading) {
    return <div className={styles.loading}>Загрузка созвездия кластеров...</div>;
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h2>🌌 Созвездие кластеров</h2>
        <div className={styles.controls}>
        </div>
        <div className={styles.stats}>
          <span>Кластеров: {data?.stats.total_clusters}</span>
        </div>
      </div>

      <div className={styles.flowContainer}>
        <ReactFlow
          nodes={nodes.map(node => ({
            ...node,
            data: {
              ...node.data,
              isHovered: hoveredNode?.id === parseInt(node.id),
              isFocused: focusedNode?.id === parseInt(node.id),
            },
            style: {
              ...node.style,
              opacity: focusedNode && focusedNode.id !== parseInt(node.id) 
                ? (data?.links.some(link => 
                    (link.source === focusedNode.id && link.target === parseInt(node.id)) ||
                    (link.target === focusedNode.id && link.source === parseInt(node.id))
                  ) ? 0.8 : 0.3) 
                : 1,
            }
          }))}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onNodeClick={onNodeClick}
          onNodeMouseEnter={onNodeMouseEnter}
          onNodeMouseLeave={onNodeMouseLeave}
          nodeTypes={nodeTypes}
          connectionMode={ConnectionMode.Loose}
          fitView
          fitViewOptions={{ padding: 150, minZoom: 0.1, maxZoom: 1.5 }}
          minZoom={0.1}
          maxZoom={1.5}
          defaultViewport={{ x: 0, y: 0, zoom: 0.7 }}
          attributionPosition="bottom-right"
          proOptions={{ hideAttribution: true }}
        >
          <Background color="#61dafb" gap={50} size={2} />
          <Controls 
            showInteractive={false} 
            showFitView={true}
            showZoom={true}
          />
          <MiniMap
            nodeColor={miniMapNodeColor}
            maskColor="rgba(10, 14, 39, 0.8)"
            position="bottom-left"
          />
        </ReactFlow>
      </div>

      {selectedNode && (
        <div className={styles.details}>
          <button className={styles.close} onClick={() => { setSelectedNode(null); setClusterQuestions(null); }}>×</button>
          <h3>{selectedNode.name}</h3>
          <p className={styles.category}>{selectedNode.category_name}</p>
          <div className={styles.info}>
            <p><strong>Вопросов:</strong> {selectedNode.questions_count}</p>
            <p><strong>Популярность:</strong> {selectedNode.interview_penetration.toFixed(1)}%</p>
            <p><strong>Ранг по популярности:</strong> #{selectedNode.rank}</p>
            <p><strong>Статус:</strong> {selectedNode.demandStatus}</p>
            
            {selectedNode.top_companies && selectedNode.top_companies.length > 0 && (
              <>
                <p><strong>Топ компании:</strong></p>
                <div className={styles.companies}>
                  {selectedNode.top_companies.map(company => (
                    <span key={company} className={styles.company}>{company}</span>
                  ))}
                </div>
              </>
            )}
            
            <p><strong>Пример вопроса:</strong></p>
            <blockquote>{selectedNode.example_question}</blockquote>
            
            
            <p><strong>Ключевые слова:</strong></p>
            <div className={styles.keywords}>
              {selectedNode.keywords.map(k => (
                <span key={k} className={styles.keyword}>{k}</span>
              ))}
            </div>

            {/* Список всех вопросов кластера */}
            {loadingQuestions && (
              <div className={styles.questionsSection}>
                <p><strong>Загружаем все вопросы...</strong></p>
                <div className={styles.loading}>⏳ Загрузка...</div>
              </div>
            )}
            
            {clusterQuestions && (
              <div className={styles.questionsSection}>
                <p><strong>Все вопросы кластера ({clusterQuestions.total_questions}):</strong></p>
                <div className={styles.questionsList}>
                  {clusterQuestions.questions?.slice(0, 50).map((question: any, index: number) => (
                    <div key={index} className={styles.questionItem}>
                      <div className={styles.questionText}>{question.question_text}</div>
                      <div className={styles.questionMeta}>
                        {question.company && (
                          <span className={styles.questionCompany}>{question.company}</span>
                        )}
                        {question.company_name && question.company_name !== question.company && (
                          <span className={styles.questionCompany}>{question.company_name}</span>
                        )}
                        {question.position && (
                          <span className={styles.questionPosition}>{question.position}</span>
                        )}
                        {question.interview_date && (
                          <span className={styles.questionDate}>
                            {new Date(question.interview_date).toLocaleDateString('ru-RU')}
                          </span>
                        )}
                        {question.duration_minutes && (
                          <span className={styles.questionDuration}>{question.duration_minutes} мин</span>
                        )}
                      </div>
                    </div>
                  ))}
                  {clusterQuestions.questions?.length > 50 && (
                    <div className={styles.moreQuestions}>
                      ... и еще {clusterQuestions.questions.length - 50} вопросов
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      <div className={styles.legend}>
        <h4>Категории:</h4>
        <div className={styles.categories}>
          {Object.entries(categoryColors).map(([id, color]) => (
            <div key={id} className={styles.categoryItem}>
              <span className={styles.dot} style={{ backgroundColor: color }} />
              <span>{data?.categories[id] || id}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};