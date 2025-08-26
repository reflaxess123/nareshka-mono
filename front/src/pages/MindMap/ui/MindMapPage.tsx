import { TechnologySwitcher } from '@/features/TechnologySwitcher';
import { useGenerateMindmapApiV2MindmapGenerateGet, useGetCategoriesApiV2InterviewCategoriesGet } from '@/shared/api/generated/api';
import { BottomNavBar } from '@/shared/components/BottomNavBar';
import type { TechnologyType } from '@/types/mindmap';
import {
  Background,
  Controls,
  type Edge,
  MiniMap,
  type Node,
  type NodeTypes,
  ReactFlow,
  useEdgesState,
  useNodesState,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import React, { useCallback, useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { TaskDetailModal } from '@/widgets/TaskDetailModal';
import { CenterNode, TopicNode } from '@/features/visualizations/MindMapNodes';
import { MindMapProgressSidebar } from '@/widgets/MindMapProgressSidebar';
import { InterviewRootNode, InterviewCategoryNode } from '@/features/visualizations/InterviewMapNodes';
import { InterviewCategorySidebar } from '@/widgets/InterviewCategorySidebar';
import { useTaskDetails } from '../../../hooks/useMindMap';
import styles from './MindMapPage.module.scss';

interface MindMapData {
  nodes: Node[];
  edges: Edge[];
  layout: string;
  total_nodes: number;
  total_edges: number;
  structure_type: string;
  active_topics: number;
  applied_filters: {
    difficulty?: string;
    topic?: string;
  };
  overall_progress?: {
    totalTasks: number;
    completedTasks: number;
    completionRate: number;
  } | null;
}

interface SelectedTopicData {
  key: string;
  title: string;
  description: string;
  color: string;
  icon: string;
}

const defaultNodeTypes: NodeTypes = {
  center: CenterNode,
  centerNode: CenterNode,
  topic: TopicNode,
  topicNode: TopicNode,
  conceptNode: TopicNode,
};

const interviewNodeTypes: NodeTypes = {
  interviewRoot: InterviewRootNode,
  interviewCategory: InterviewCategoryNode,
};

const NewMindMapPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);

  // Подавляем ResizeObserver ошибки (это известная проблема React Flow)
  useEffect(() => {
    const originalError = console.error;
    console.error = (...args) => {
      if (args[0]?.includes?.('ResizeObserver loop completed')) {
        return; // Игнорируем ResizeObserver ошибки
      }
      originalError(...args);
    };
    return () => {
      console.error = originalError;
    };
  }, []);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);
  const [selectedTopic, setSelectedTopic] = useState<SelectedTopicData | null>(
    null
  );
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [theoreticalTaskId, setTheoreticalTaskId] = useState<string | null>(
    null
  );
  const { task: theoreticalTaskDetail } = useTaskDetails(theoreticalTaskId);

  // Получаем текущую технологию из URL параметров
  const currentTechnology = (searchParams.get('tech') as TechnologyType) || 'javascript';

  console.log('🎆 Current Technology:', currentTechnology, 'is interviews?', currentTechnology === 'interviews');

  // Состояние для выбранной категории интервью
  const selectedCategoryId = searchParams.get('category');
  const [selectedCategory, setSelectedCategory] = useState<{
    id: string;
    name: string;
    questionsCount: number;
    clustersCount: number;
    percentage: number;
  } | null>(null);

  // Получаем данные категорий интервью через API
  const queryResult = useGetCategoriesApiV2InterviewCategoriesGet({
    query: {
      enabled: currentTechnology === 'interviews'
    }
  });

  console.log('🔧 Full React Query result:', {
    queryResult: Object.keys(queryResult),
    data: queryResult.data,
    isLoading: queryResult.isLoading,
    error: queryResult.error,
    isSuccess: queryResult.isSuccess,
    status: queryResult.status
  });

  const {
    data: interviewCategoriesResponse,
    isLoading: interviewCategoriesLoading,
    error: interviewCategoriesError
  } = queryResult;

  // Преобразуем данные в формат для React Flow
  const interviewsData = React.useMemo(() => {
    if (!interviewCategoriesResponse || !Array.isArray(interviewCategoriesResponse)) {
      return {
        nodes: [],
        edges: [],
        data: { categories: [], nodes: [], edges: [] },
        isLoading: interviewCategoriesLoading,
        error: interviewCategoriesError
      };
    }

    const categories = interviewCategoriesResponse;
    const totalQuestions = categories.reduce((sum, cat) => sum + (cat.questions_count || 0), 0);
    const totalClusters = categories.reduce((sum, cat) => sum + (cat.clusters_count || 0), 0);

    // Идеальное центрирование для React Flow
    // React Flow лучше всего работает с fitView, поэтому используем компактные координаты
    const centerX = 0;
    const centerY = 0;

    const rootNode = {
      id: 'root',
      type: 'interviewRoot',
      position: { x: centerX, y: centerY },
      data: {
        totalQuestions,
        totalClusters,
        totalCategories: categories.length
      }
    };

    // Оптимальное позиционирование категорий по кругу
    const categoryNodes = categories.map((category, index) => {
      // Начинаем с верхнего положения (12 часов) и двигаемся по часовой стрелке
      const angle = (2 * Math.PI * index) / categories.length - Math.PI / 2;

      // Уменьшаем радиус до комфортного расстояния
      // Минимальный радиус чтобы не налезали: ~450px
      const radius = 550;

      const x = centerX + radius * Math.cos(angle);
      const y = centerY + radius * Math.sin(angle);

      return {
        id: category.id.toString(),
        type: 'interviewCategory',
        position: { x, y },
        data: {
          id: category.id.toString(),
          name: category.name,
          questionsCount: category.questions_count || 0,
          clustersCount: category.clusters_count || 0,
          percentage: category.percentage || 0
        }
      };
    });

    const nodes = [rootNode, ...categoryNodes];

    // Создаем связи от центра к категориям
    const edges = categoryNodes.map((node, index) => ({
      id: `e${index + 1}`,
      source: 'root',
      target: node.id
    }));

    return {
      nodes,
      edges,
      data: {
        categories: categories.map(cat => ({
          id: cat.id.toString(),
          name: cat.name,
          questionsCount: cat.questions_count || 0,
          clustersCount: cat.clusters_count || 0,
          percentage: cat.percentage || 0
        })),
        nodes,
        edges
      },
      isLoading: interviewCategoriesLoading,
      error: interviewCategoriesError
    };
  }, [interviewCategoriesResponse, interviewCategoriesLoading, interviewCategoriesError]);

  // Используем generated hook для получения данных mindmap
  const {
    data: mindMapResponse,
    isLoading: mindMapLoading,
    error: mindMapError,
  } = useGenerateMindmapApiV2MindmapGenerateGet(
    currentTechnology !== 'interviews' ? {
      technology: currentTechnology,
      structure_type: 'topics',
    } : undefined,
    {
      query: {
        enabled: currentTechnology !== 'interviews'
      }
    }
  );

  const mindMapData = mindMapResponse?.data as MindMapData | undefined;

  // Выбираем данные и состояния в зависимости от режима
  const isInterviewsMode = currentTechnology === 'interviews';
  const loading = isInterviewsMode ? interviewsData.isLoading : mindMapLoading;
  const error = isInterviewsMode ? interviewsData.error : mindMapError;
  const nodeTypes = isInterviewsMode ? interviewNodeTypes : defaultNodeTypes;

  const handleTechnologyChange = useCallback((technology: TechnologyType) => {
    const newParams = new URLSearchParams(searchParams);
    newParams.set('tech', technology);
    // Сбрасываем категорию при смене технологии
    if (newParams.has('category')) {
      newParams.delete('category');
    }
    setSearchParams(newParams);
    setSelectedCategory(null);
  }, [searchParams, setSearchParams]);

  const onNodeClick = useCallback((_event: React.MouseEvent, node: Node) => {
    // Обработка клика для interviews режима
    if (currentTechnology === 'interviews') {
      if (node.type === 'interviewCategory') {
        const categoryData = {
          id: node.data.id as string,
          name: node.data.name as string,
          questionsCount: node.data.questionsCount as number,
          clustersCount: node.data.clustersCount as number,
          percentage: node.data.percentage as number
        };

        // Обновляем URL с параметром category
        const newParams = new URLSearchParams(searchParams);
        newParams.set('tech', 'interviews');
        newParams.set('category', categoryData.id);
        setSearchParams(newParams);

        setSelectedCategory(categoryData);
      }
      return;
    }

    // Обычная обработка для других технологий
    if (node.type === 'topic' && node.data.topic_key) {
      const topicData: SelectedTopicData = {
        key: node.data.topic_key as string,
        title: node.data.title as string,
        description: node.data.description as string,
        color: node.data.color as string,
        icon: node.data.icon as string,
      };
      setSelectedTopic(topicData);
      setIsSidebarOpen(true);
    }
  }, [currentTechnology, searchParams, setSearchParams]);

  const handleCloseSidebar = useCallback(() => {
    setIsSidebarOpen(false);
    setSelectedTopic(null);
  }, []);

  const handleTaskClick = useCallback((taskId: string) => {
    // Переход к редактору кода
    window.location.href = `/code-editor?blockId=${taskId}`;
  }, []);

  // Синхронизируем selectedCategory с URL параметром
  useEffect(() => {
    if (currentTechnology === 'interviews' && selectedCategoryId && interviewsData.data) {
      // Находим данные категории из nodes
      const categoryNode = interviewsData.data.nodes.find(
        (node) => node.type === 'interviewCategory' && 
        'id' in node.data && node.data.id === selectedCategoryId
      );

      if (categoryNode && categoryNode.type === 'interviewCategory' && (!selectedCategory || selectedCategory.id !== selectedCategoryId)) {
        const nodeData = categoryNode.data;
        if ('id' in nodeData && 'name' in nodeData && 'questionsCount' in nodeData && 'clustersCount' in nodeData && 'percentage' in nodeData) {
          setSelectedCategory({
            id: nodeData.id as string,
            name: nodeData.name as string,
            questionsCount: nodeData.questionsCount as number,
            clustersCount: nodeData.clustersCount as number,
            percentage: nodeData.percentage as number
          });
        }
      }
    } else if (!selectedCategoryId && selectedCategory) {
      // Если в URL нет category, но в state есть - сбрасываем
      setSelectedCategory(null);
    }
  }, [selectedCategoryId, currentTechnology, interviewsData, selectedCategory]);

  // Обновляем nodes и edges при изменении данных
  useEffect(() => {
    if (isInterviewsMode) {
      // Используем данные интервью
      if (interviewsData.nodes && interviewsData.edges) {
        setNodes(interviewsData.nodes);
        setEdges(interviewsData.edges);
      }
    } else {
      // Используем обычные mindmap данные
      if (mindMapData?.nodes && mindMapData?.edges) {
        setNodes(mindMapData.nodes);
        setEdges(mindMapData.edges);
      }
    }
  }, [mindMapData, interviewsData, isInterviewsMode, setNodes, setEdges]);

  if (loading) {
    return (
      <div
        style={{
          width: '100vw',
          height: '100vh',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          fontSize: '18px',
          color: '#666',
        }}
      >
        🔄 Загрузка MindMap...
      </div>
    );
  }

  if (error) {
    return (
      <div
        style={{
          width: '100vw',
          height: '100vh',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          fontSize: '18px',
          color: '#666',
        }}
      >
        ❌ Ошибка загрузки данных:{' '}
        {error instanceof Error ? error.message : 'Произошла ошибка'}
      </div>
    );
  }

  if (isInterviewsMode && (!interviewsData.nodes || interviewsData.nodes.length === 0)) {
    return (
      <div
        style={{
          width: '100vw',
          height: '100vh',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          fontSize: '18px',
          color: '#666',
        }}
      >
        ❌ Нет данных интервью для отображения
      </div>
    );
  }

  if (!isInterviewsMode && !mindMapData) {
    return (
      <div
        style={{
          width: '100vw',
          height: '100vh',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          fontSize: '18px',
          color: '#666',
        }}
      >
        ❌ Нет данных для отображения
      </div>
    );
  }

  return (
    <div className={styles.mindmapContainer}>
      <div className={styles.technologySwitcherWrapper}>
        <TechnologySwitcher
          currentTechnology={currentTechnology}
          onTechnologyChange={handleTechnologyChange}
        />
      </div>


      <div
        style={{
          width: isSidebarOpen ? 'calc(100% - 400px)' : '100%',
          height: '100%',
          transition: 'width 0.3s ease-in-out',
        }}
      >
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onNodeClick={onNodeClick}
          nodeTypes={nodeTypes}
          fitView
          fitViewOptions={{
            padding: 0.15, // Больше паддинга для красивого обрамления
            includeHiddenNodes: false,
            maxZoom: 1.2 // Ограничиваем авто-масштабирование
          }}
          defaultViewport={{ x: 0, y: 0, zoom: 0.9 }}
          minZoom={0.4}
          maxZoom={1.8}
          deleteKeyCode={null}
          multiSelectionKeyCode={null}
          panOnDrag={true}
          zoomOnScroll={true}
          zoomOnPinch={true}
          panOnScroll={false}
          elementsSelectable={true}
          nodesDraggable={true}
          nodesConnectable={false}
          nodesFocusable={true}
          className={styles.reactFlow}
        >
          <Background color="#f1f5f9" gap={20} />
          <div
            className={styles.controlsBottomLeft + ' ' + styles.hideOnMobile}
          >
            <Controls showInteractive={false} />
          </div>
          <div
            className={styles.miniMapBottomRight + ' ' + styles.hideOnMobile}
          >
            <MiniMap
              nodeColor={(node) => {
                const data = node.data as { color?: string };
                return (data.color as string) || '#e2e8f0';
              }}
              maskColor="rgba(0, 0, 0, 0.05)"
              pannable
              zoomable
            />
          </div>
        </ReactFlow>
      </div>

      {!isInterviewsMode && (
        <MindMapProgressSidebar
          isOpen={isSidebarOpen}
          onClose={handleCloseSidebar}
          selectedTopic={selectedTopic}
          currentTechnology={currentTechnology}
          onTaskClick={handleTaskClick}
          onTheoreticalTaskClick={setTheoreticalTaskId}
        />
      )}

      <TaskDetailModal
        isOpen={!!theoreticalTaskId}
        onClose={() => setTheoreticalTaskId(null)}
        task={theoreticalTaskDetail}
      />

      {currentTechnology === 'interviews' && selectedCategory && (
        <InterviewCategorySidebar
          isOpen={!!selectedCategory}
          onClose={() => {
            // Удаляем category из URL при закрытии sidebar
            const newParams = new URLSearchParams(searchParams);
            if (newParams.has('category')) {
              newParams.delete('category');
            }
            setSearchParams(newParams);
            // НЕ вызываем setSelectedCategory(null) здесь -
            // useEffect сам сбросит state при изменении URL
          }}
          categoryId={selectedCategory.id}
          categoryName={selectedCategory.name}
          questionsCount={selectedCategory.questionsCount}
          clustersCount={selectedCategory.clustersCount}
          percentage={selectedCategory.percentage}
        />
      )}

      <div className={styles.mobileNav}>
        <BottomNavBar />
      </div>
    </div>
  );
};

export default NewMindMapPage;
