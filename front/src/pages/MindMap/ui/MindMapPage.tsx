import { TechnologySwitcher } from '@/components/TechnologySwitcher';
import { useGenerateMindmapApiV2MindmapGenerateGet } from '@/shared/api/generated/api';
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
import { TaskDetailModal } from '../../../components/mindmap/TaskDetailModal';
import CenterNode from '../../../components/MindMapNodes/CenterNode';
import MindMapProgressSidebar from '../../../components/MindMapNodes/MindMapProgressSidebar';
import TopicNode from '../../../components/MindMapNodes/TopicNode';
import InterviewRootNode from '../../../components/mindmap/InterviewRootNode';
import InterviewCategoryNode from '../../../components/mindmap/InterviewCategoryNode';
import InterviewCategorySidebar from '../../../components/mindmap/InterviewCategorySidebar';
import { useTaskDetails } from '../../../hooks/useMindMap';
import { useInterviewsVisualization } from '../../../hooks/useInterviewsVisualization';
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
  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);
  const [selectedTopic, setSelectedTopic] = useState<SelectedTopicData | null>(
    null
  );
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [currentTechnology, setCurrentTechnology] =
    useState<TechnologyType>('javascript');
  const [theoreticalTaskId, setTheoreticalTaskId] = useState<string | null>(
    null
  );
  const { task: theoreticalTaskDetail } = useTaskDetails(theoreticalTaskId);

  // Состояние для выбранной категории интервью
  const [selectedCategory, setSelectedCategory] = useState<{
    id: string;
    name: string;
    questionsCount: number;
    clustersCount: number;
    percentage: number;
  } | null>(null);

  // Используем хук для данных интервью
  const interviewsData = useInterviewsVisualization();

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

  const mindMapData = mindMapResponse?.data as unknown as MindMapData | null;

  // Выбираем данные и состояния в зависимости от режима
  const isInterviewsMode = currentTechnology === 'interviews';
  const loading = isInterviewsMode ? interviewsData.isLoading : mindMapLoading;
  const error = isInterviewsMode ? interviewsData.error : mindMapError;
  const nodeTypes = isInterviewsMode ? interviewNodeTypes : defaultNodeTypes;

  const handleTechnologyChange = useCallback((technology: TechnologyType) => {
    setCurrentTechnology(technology);
    setSelectedCategory(null); // Сбрасываем выбранную категорию при смене технологии
    // Хук автоматически обновится при изменении параметров
  }, []);

  const onNodeClick = useCallback((_event: React.MouseEvent, node: Node) => {
    // Обработка клика для interviews режима
    if (currentTechnology === 'interviews') {
      if (node.type === 'interviewCategory') {
        setSelectedCategory({
          id: node.data.id as string,
          name: node.data.name as string,
          questionsCount: node.data.questionsCount as number,
          clustersCount: node.data.clustersCount as number,
          percentage: node.data.percentage as number
        });
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
  }, [currentTechnology]);

  const handleCloseSidebar = useCallback(() => {
    setIsSidebarOpen(false);
    setSelectedTopic(null);
  }, []);

  const handleTaskClick = useCallback((taskId: string) => {
    // Переход к редактору кода
    window.location.href = `/code-editor?blockId=${taskId}`;
  }, []);

  // Обновляем nodes и edges при изменении данных
  useEffect(() => {
    if (isInterviewsMode) {
      // Используем данные интервью
      if (interviewsData.data) {
        setNodes(interviewsData.data.nodes);
        setEdges(interviewsData.data.edges);
      }
    } else {
      // Используем обычные mindmap данные
      if (mindMapData?.nodes && mindMapData?.edges) {
        setNodes(mindMapData.nodes);
        setEdges(mindMapData.edges);
      }
    }
  }, [mindMapData, interviewsData.data, isInterviewsMode, setNodes, setEdges]);

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
          fitViewOptions={{ padding: 0.1, includeHiddenNodes: false }}
          defaultViewport={{ x: 0, y: 0, zoom: 0.8 }}
          minZoom={0.3}
          maxZoom={2}
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
                const data = node.data as Record<string, unknown>;
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
          onClose={() => setSelectedCategory(null)}
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
