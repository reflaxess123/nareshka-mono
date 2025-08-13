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

// Импортируем новый круглый компонент
import CircularClusterNode from './CircularClusterNode';

// Кастомный круглый узел кластера - оптимизирован для производительности
const ClusterNode: React.FC<NodeProps<ClusterNodeData & { isHovered?: boolean; isFocused?: boolean }>> = (props) => {
  return (
    <CircularClusterNode 
      {...props} 
      isHovered={props.data.isHovered} 
      isFocused={props.data.isFocused}
    />
  );
};

const nodeTypes: NodeTypes = {
  cluster: ClusterNode,
};

export const ClusterConstellationReactFlow: React.FC = () => {
  const [data, setData] = useState<ConstellationData | null>(null);
  const [selectedNode, setSelectedNode] = useState<ClusterNodeData | null>(null);
  const [hoveredNode, setHoveredNode] = useState<ClusterNodeData | null>(null);
  const [focusedNode, setFocusedNode] = useState<ClusterNodeData | null>(null);
  const [loading, setLoading] = useState(true);
  const [hoverTimeout, setHoverTimeout] = useState<NodeJS.Timeout | null>(null);
  const [showLegend, setShowLegend] = useState(true);
  const [clusterQuestions, setClusterQuestions] = useState<any>(null);
  const [loadingQuestions, setLoadingQuestions] = useState(false);
  
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  // Загрузка данных - ТОЛЬКО топ кластеры для производительности
  useEffect(() => {
    // Загружаем только самые важные кластеры с высокими порогами
    fetch('/api/v2/cluster-visualization/constellation?min_interview_count=50&min_link_weight=15&limit=20')
      .then(res => res.json())
      .then(data => {
        // Ограничиваем количество узлов для производительности
        const limitedData = {
          ...data,
          nodes: data.nodes?.slice(0, 20) || [], // Максимум 20 узлов
          links: data.links?.filter(link => 
            data.nodes?.slice(0, 20).find(n => n.id === link.source) &&
            data.nodes?.slice(0, 20).find(n => n.id === link.target)
          ).slice(0, 15) || [] // Максимум 15 связей
        };
        setData(limitedData);
      })
      .catch(err => {
        console.error('Ошибка загрузки данных:', err);
        // Fallback - загружаем с еще более строгими ограничениями
        fetch('/api/v2/cluster-visualization/constellation?min_interview_count=100&limit=10')
          .then(res => res.json())
          .then(setData);
      })
      .finally(() => setLoading(false));
  }, []);
  
  // Очистка таймаутов при размонтировании
  useEffect(() => {
    return () => {
      if (hoverTimeout) clearTimeout(hoverTimeout);
    };
  }, [hoverTimeout]);

  // Мемоизированные узлы для предотвращения пересчета позиций
  const memoizedNodes = useMemo(() => {
    if (!data) return [];

    // Сортируем по популярности
    const sortedNodes = [...data.nodes].sort((a, b) => b.interview_penetration - a.interview_penetration);
    
    // Группируем узлы по категориям для более организованного расположения
    const nodesByCategory = sortedNodes.reduce((acc, node) => {
      if (!acc[node.category_id]) acc[node.category_id] = [];
      acc[node.category_id].push(node);
      return acc;
    }, {} as Record<string, typeof sortedNodes>);
    
    // Создаем узлы с оптимальным расположением для производительности
    const flowNodes: Node<ClusterNodeData>[] = [];
    const nodeSize = 180; // Уменьшенный размер для круглых узлов
    const minDistance = 220; // Минимальное расстояние между узлами
    
    // Размещаем все узлы по спирали для лучшей читаемости
    const centerX = 800; // Увеличен для лучшего использования ширины экрана
    const centerY = 350; // Слегка поднят для учета отступа от хедера
    
    sortedNodes.forEach((node, index) => {
      // Спиральное размещение с увеличивающимся радиусом
      const angle = index * (2 * Math.PI / 3.618); // Золотое сечение для равномерности
      const radius = 150 + index * 80; // Увеличивающийся радиус
      const x = centerX + Math.cos(angle) * radius;
      const y = centerY + Math.sin(angle) * radius;
      
      // Добавляем полезную информацию для отображения на узле
      const nodeData = {
        ...node,
        // Ранг по популярности (топ-5 помечаем как важные)
        rank: index + 1,
        isTopCluster: index < 5,
        // Уровень сложности на основе проникновения
        difficultyLevel: node.interview_penetration > 8 ? 'high' : 
                        node.interview_penetration > 6 ? 'medium' : 'low',
        // Статус востребованности
        demandStatus: node.interview_penetration > 9 ? 'Очень востребован' :
                     node.interview_penetration > 7 ? 'Востребован' :
                     node.interview_penetration > 5 ? 'Умеренно востребован' : 'Нишевая тема'
      };

      flowNodes.push({
        id: node.id.toString(),
        type: 'cluster',
        position: { x, y },
        data: nodeData,
        draggable: true,
      });
    });
    
    // Удаляем сложную логику категорий - теперь все узлы размещаются по спирали
    
    return flowNodes;
  }, [data]);

  // Убираем связи - возвращаем пустой массив
  const memoizedEdges = useMemo(() => {
    return [];
  }, []);

  // Обновляем узлы и связи только при изменении мемоизированных данных
  useEffect(() => {
    setNodes(memoizedNodes);
    setEdges(memoizedEdges);
  }, [memoizedNodes, memoizedEdges, setNodes, setEdges]);

  // Обработка hover на узел с debouncing
  const onNodeMouseEnter = useCallback((event: React.MouseEvent, node: Node<ClusterNodeData>) => {
    if (hoverTimeout) clearTimeout(hoverTimeout);
    setHoveredNode(node.data);
  }, [hoverTimeout]);
  
  const onNodeMouseLeave = useCallback(() => {
    if (hoverTimeout) clearTimeout(hoverTimeout);
    const timeout = setTimeout(() => {
      setHoveredNode(null);
    }, 150); // Небольшая задержка
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

  // Обработка клика на узел - режим фокусировки с загрузкой вопросов
  const onNodeClick = useCallback((event: React.MouseEvent, node: Node<ClusterNodeData>) => {
    event.preventDefault();
    event.stopPropagation();
    
    if (focusedNode && focusedNode.id === node.data.id) {
      // Если уже сфокусирован - убираем фокус
      setFocusedNode(null);
      setSelectedNode(null);
      setClusterQuestions(null);
    } else {
      // Фокусируемся на узле и загружаем вопросы
      setFocusedNode(node.data);
      setSelectedNode(node.data);
      loadClusterQuestions(node.data.id);
    }
  }, [focusedNode, loadClusterQuestions]);

  // Сброс позиций
  const resetLayout = useCallback(() => {
    if (!data) return;
    
    const sortedNodes = [...data.nodes].sort((a, b) => b.interview_penetration - a.interview_penetration);
    
    // Группируем узлы по категориям
    const nodesByCategory = sortedNodes.reduce((acc, node) => {
      if (!acc[node.category_id]) acc[node.category_id] = [];
      acc[node.category_id].push(node);
      return acc;
    }, {} as Record<string, typeof sortedNodes>);
    
    const resetNodes: Node<ClusterNodeData>[] = [];
    const cardWidth = 320;
    const cardHeight = 250;
    const spacing = 40;
    
    // Размещаем топ-5 узлов в центре
    sortedNodes.slice(0, 5).forEach((node, index) => {
      const angle = (index / 5) * 2 * Math.PI - Math.PI / 2;
      const radius = 300;
      const x = 800 + Math.cos(angle) * radius;
      const y = 450 + Math.sin(angle) * radius;
      
      const strongConnections = data?.links
        ?.filter(link => 
          link.source === node.id || link.target === node.id
        )
        ?.sort((a, b) => b.strength - a.strength)
        ?.slice(0, 3)
        ?.map(link => {
          const connectedNodeId = link.source === node.id ? link.target : link.source;
          const connectedNode = sortedNodes.find(n => n.id === connectedNodeId);
          return connectedNode ? {
            name: connectedNode.name.length > 20 ? connectedNode.name.substring(0, 17) + '...' : connectedNode.name,
            strength: link.strength
          } : null;
        })
        ?.filter(Boolean) || [];
      
      resetNodes.push({
        id: node.id.toString(),
        type: 'cluster',
        position: { x, y },
        data: {
          ...node,
          strongConnections
        },
        draggable: true,
      });
    });
    
    // Размещаем остальные узлы по категориям
    const categories = Object.keys(nodesByCategory);
    
    categories.forEach((categoryId, catIndex) => {
      const categoryNodes = nodesByCategory[categoryId].filter(n => 
        !sortedNodes.slice(0, 5).includes(n)
      );
      
      if (categoryNodes.length === 0) return;
      
      const sectorAngle = (2 * Math.PI) / categories.length;
      const baseSectorAngle = catIndex * sectorAngle;
      
      categoryNodes.forEach((node, nodeIndex) => {
        const layerIndex = Math.floor(nodeIndex / 3);
        const positionInLayer = nodeIndex % 3;
        const radius = 600 + layerIndex * (cardHeight + spacing);
        const angleOffset = (positionInLayer - 1) * 0.15;
        const angle = baseSectorAngle + angleOffset;
        const x = 800 + Math.cos(angle) * radius;
        const y = 450 + Math.sin(angle) * radius;
        
        const strongConnections = data?.links
          ?.filter(link => 
            link.source === node.id || link.target === node.id
          )
          ?.sort((a, b) => b.strength - a.strength)
          ?.slice(0, 3)
          ?.map(link => {
            const connectedNodeId = link.source === node.id ? link.target : link.source;
            const connectedNode = sortedNodes.find(n => n.id === connectedNodeId);
            return connectedNode ? {
              name: connectedNode.name.length > 20 ? connectedNode.name.substring(0, 17) + '...' : connectedNode.name,
              strength: link.strength
            } : null;
          })
          ?.filter(Boolean) || [];
        
        resetNodes.push({
          id: node.id.toString(),
          type: 'cluster',
          position: { x, y },
          data: {
            ...node,
            strongConnections
          },
          draggable: true,
        });
      });
    });
    
    setNodes(resetNodes);
  }, [data, setNodes]);

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
          <button className={styles.resetButton} onClick={resetLayout}>
            🔄 Сбросить расположение
          </button>
          <button 
            className={styles.resetButton} 
            onClick={() => setShowLegend(!showLegend)}
            style={{ background: showLegend ? 'rgba(76, 175, 80, 0.2)' : 'rgba(97, 218, 251, 0.1)', borderColor: showLegend ? '#4caf50' : '#61dafb', color: showLegend ? '#4caf50' : '#61dafb' }}
          >
            {showLegend ? '👁️ Скрыть легенду' : '👁️ Показать легенду'}
          </button>
          {focusedNode && (
            <button 
              className={styles.resetButton} 
              onClick={() => { setFocusedNode(null); setSelectedNode(null); }}
              style={{ background: 'rgba(255, 193, 7, 0.2)', borderColor: '#ffc107', color: '#ffc107' }}
            >
              ✕ Убрать фокус
            </button>
          )}
          <div className={styles.info}>
            {focusedNode 
              ? `Фокус: ${focusedNode.name}` 
              : 'Кликните на кластер для детальной информации'}
          </div>
        </div>
        <div className={styles.stats}>
          <span>Кластеров: {data?.stats.total_clusters}</span>
          <span>Связей: {data?.stats.total_links}</span>
          <span>Средняя популярность: {data?.stats.avg_penetration.toFixed(1)}%</span>
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
          fitViewOptions={{ padding: 100, minZoom: 0.1, maxZoom: 2 }}
          minZoom={0.1}
          maxZoom={2}
          defaultViewport={{ x: 0, y: 0, zoom: 0.8 }}
          attributionPosition="bottom-right"
          proOptions={{ hideAttribution: true }}
        >
          <Background color="#61dafb" gap={50} size={2} />
          <Controls showInteractive={false} />
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

      {showLegend && (
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
          
          <h4 style={{ marginTop: '15px' }}>Важность тем:</h4>
          <div className={styles.connections}>
            <div className={styles.connectionType}>
              <span>⭐</span>
              <span>Топ-5 самых популярных</span>
            </div>
            <div className={styles.connectionType}>
              <span>#1-5</span>
              <span>Очень востребованы (&gt;9%)</span>
            </div>
            <div className={styles.connectionType}>
              <span>#6-12</span>
              <span>Востребованы (7-9%)</span>
            </div>
            <div className={styles.connectionType}>
              <span>#13+</span>
              <span>Нишевые темы (&lt;7%)</span>
            </div>
          </div>
          
          <div className={styles.tips}>
            <h4>Управление:</h4>
            <div className={styles.tip}>• Кликните - детали кластера</div>
            <div className={styles.tip}>• Наведите - краткая информация</div>
            <div className={styles.tip}>• Колесо - масштабирование</div>
            <div className={styles.tip}>• Перетаскивайте для перемещения</div>
          </div>
        </div>
      )}
    </div>
  );
};