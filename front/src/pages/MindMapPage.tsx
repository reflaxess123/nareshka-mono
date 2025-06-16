import type { Connection, Node } from '@xyflow/react';
import {
  addEdge,
  Background,
  BackgroundVariant,
  Controls,
  MiniMap,
  ReactFlow,
  ReactFlowProvider,
  useEdgesState,
  useNodesState,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import React, { useCallback, useEffect, useState } from 'react';

import { CenterNode } from '../components/mindmap/CenterNode';
import { ConceptNode } from '../components/mindmap/ConceptNode';
import {
  ConceptEdge,
  DifficultyEdge,
  PathEdge,
  PrerequisiteEdge,
  TaskEdge,
} from '../components/mindmap/CustomEdges';
import { DifficultyNode } from '../components/mindmap/DifficultyNode';
import { MindMapToolbar } from '../components/mindmap/MindMapToolbar';
import { PathNode } from '../components/mindmap/PathNode';
import { TaskDetailModal } from '../components/mindmap/TaskDetailModal';
import { LoadingSpinner } from '../components/ui/LoadingSpinner';
import { useMindMapData } from '../hooks/useMindMapData';
import type { MindMapEdge, MindMapNode, TaskDetail } from '../types/mindmap';
import styles from './MindMapPage.module.scss';

const nodeTypes = {
  centerNode: CenterNode,
  conceptNode: ConceptNode,
  pathNode: PathNode,
  difficultyNode: DifficultyNode,
};

const edgeTypes = {
  conceptEdge: ConceptEdge,
  pathEdge: PathEdge,
  difficultyEdge: DifficultyEdge,
  prerequisiteEdge: PrerequisiteEdge,
  taskEdge: TaskEdge,
};

const MindMapPage: React.FC = () => {
  const [nodes, setNodes, onNodesChange] = useNodesState<MindMapNode>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<MindMapEdge>([]);
  const [selectedTask, setSelectedTask] = useState<TaskDetail | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const [difficultyFilter, setDifficultyFilter] = useState<string>('');
  const [conceptFilter, setConceptFilter] = useState<string>('');

  const { data, isLoading, error, refetch } = useMindMapData(
    difficultyFilter,
    conceptFilter
  );

  useEffect(() => {
    console.log('📊 MindMap data received:', data);
    if (data?.data) {
      console.log(
        '📍 Setting nodes:',
        data.data.nodes.length,
        'edges:',
        data.data.edges.length
      );
      console.log('📍 Nodes sample:', data.data.nodes.slice(0, 2));
      console.log('📍 Edges sample:', data.data.edges.slice(0, 2));
      setNodes(data.data.nodes);
      setEdges(data.data.edges);
    } else {
      console.log('⚠️ No data received or data.data is undefined');
    }
  }, [data, setNodes, setEdges]);

  useEffect(() => {
    console.log(
      '🔄 Current state - nodes:',
      nodes.length,
      'edges:',
      edges.length
    );
  }, [nodes, edges]);

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  const onNodeClick = useCallback(
    async (_event: React.MouseEvent, node: Node) => {
      console.log('Node clicked:', node);

      if (node.data?.task_id) {
        try {
          const response = await fetch(
            `/api/mindmap/task/${node.data.task_id}`
          );
          const taskData = await response.json();

          if (taskData.success) {
            setSelectedTask(taskData.task);
            setIsModalOpen(true);
          }
        } catch (error) {
          console.error('Ошибка загрузки задачи:', error);
        }
      }
    },
    []
  );

  const handleDifficultyFilter = (difficulty: string) => {
    setDifficultyFilter(difficulty === difficultyFilter ? '' : difficulty);
  };

  const handleConceptFilter = (concept: string) => {
    setConceptFilter(concept === conceptFilter ? '' : concept);
  };

  const handleResetFilters = () => {
    setDifficultyFilter('');
    setConceptFilter('');
  };

  if (isLoading) {
    return (
      <div className={styles.loadingContainer}>
        <LoadingSpinner size="large" />
        <span className={styles.loadingText}>
          Генерируем интеллектуальную карту обучения...
        </span>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.errorContainer}>
        <div className={styles.errorTitle}>Ошибка загрузки MindMap</div>
        <div className={styles.errorText}>{error.message}</div>
        <button onClick={() => refetch()} className={styles.retryButton}>
          Попробовать снова
        </button>
      </div>
    );
  }

  if (!isLoading && (!data || !data.data || data.data.nodes.length === 0)) {
    return (
      <div className={styles.emptyContainer}>
        <div className={styles.emptyTitle}>Нет данных для отображения</div>
        <div className={styles.emptyText}>
          Данные mindmap не загружены или пусты.
          {data
            ? `Получено ${data.data?.nodes?.length || 0} узлов`
            : 'Нет ответа от сервера'}
        </div>
        <button onClick={() => refetch()} className={styles.retryButton}>
          Перезагрузить
        </button>
      </div>
    );
  }

  return (
    <div className={styles.mindmapContainer}>
      <div className={styles.header}>
        <div className={styles.headerContent}>
          <div className={styles.headerFlex}>
            <div className={styles.headerLeft}>
              <div className={styles.headerInfo}>
                <div className={styles.logo}>JS</div>
                <div className={styles.titleContainer}>
                  <h1 className={styles.title}>Карта изучения</h1>
                  <p className={styles.subtitle}>
                    {data?.metadata?.total_tasks || 0} интерактивных задач
                  </p>
                </div>
              </div>
            </div>

            <MindMapToolbar
              difficultyFilter={difficultyFilter}
              conceptFilter={conceptFilter}
              onDifficultyFilter={handleDifficultyFilter}
              onConceptFilter={handleConceptFilter}
              onResetFilters={handleResetFilters}
              totalTasks={data?.metadata?.total_tasks || 0}
            />
          </div>
        </div>
      </div>

      <div className={styles.flowCanvas}>
        <ReactFlowProvider>
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onNodeClick={onNodeClick}
            nodeTypes={nodeTypes}
            edgeTypes={edgeTypes}
            fitView
            fitViewOptions={{
              padding: 0.05,
              includeHiddenNodes: false,
            }}
            defaultViewport={{ x: 0, y: 0, zoom: 1.2 }}
            minZoom={0.3}
            maxZoom={3}
            attributionPosition="bottom-left"
            className={styles.reactFlow}
          >
            <Background
              variant={BackgroundVariant.Dots}
              gap={20}
              size={2}
              color="#e2e8f0"
            />

            <Controls
              position="bottom-right"
              showInteractive={false}
              showFitView={true}
              showZoom={true}
            />

            <MiniMap
              position="bottom-left"
              nodeColor={(node) => {
                switch (node.type) {
                  case 'centerNode':
                    return '#8B5CF6';
                  case 'conceptNode':
                    return '#10B981';
                  case 'pathNode':
                    return '#F59E0B';
                  case 'difficultyNode':
                    return '#EF4444';
                  default:
                    return '#6B7280';
                }
              }}
              maskColor="rgba(255, 255, 255, 0.6)"
              style={{
                backgroundColor: '#f8fafc',
              }}
            />
          </ReactFlow>
        </ReactFlowProvider>
      </div>

      <TaskDetailModal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          setSelectedTask(null);
        }}
        task={selectedTask}
      />

      <div className={styles.legend}>
        <div className={styles.legendItems}>
          <div className={styles.legendItem}>
            <div className={`${styles.legendDot} ${styles.purple}`}></div>
            <span className={styles.legendText}>Центр</span>
          </div>
          <div className={styles.legendItem}>
            <div className={`${styles.legendDot} ${styles.green}`}></div>
            <span className={styles.legendText}>Концепции</span>
          </div>
          <div className={styles.legendItem}>
            <div className={`${styles.legendDot} ${styles.yellow}`}></div>
            <span className={styles.legendText}>Пути</span>
          </div>
          <div className={styles.legendItem}>
            <div className={`${styles.legendDot} ${styles.red}`}></div>
            <span className={styles.legendText}>Уровни</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MindMapPage;
