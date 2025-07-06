import { TechnologySwitcher } from '@/components/TechnologySwitcher';
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

const nodeTypes: NodeTypes = {
  center: CenterNode,
  centerNode: CenterNode,
  topic: TopicNode,
  topicNode: TopicNode,
  conceptNode: TopicNode,
};

const NewMindMapPage: React.FC = () => {
  const [mindMapData, setMindMapData] = useState<MindMapData | null>(null);
  const [loading, setLoading] = useState(false);
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
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

  const fetchMindMap = useCallback(
    async (technology: TechnologyType = currentTechnology) => {
      setLoading(true);
      try {
        const params = new URLSearchParams();
        params.append('technology', technology);

        const response = await fetch(
          `/api/v2/mindmap/generate?${params.toString()}`,
          {
            credentials: 'include',
          }
        );
        const result = await response.json();

        if (result.success && result.data) {
          setMindMapData(result.data);
          setNodes(result.data.nodes);
          setEdges(result.data.edges);
        }
      } catch {
        // Игнорируем ошибки
      } finally {
        setLoading(false);
      }
    },
    [currentTechnology, setNodes, setEdges]
  );

  const handleTechnologyChange = useCallback(
    (technology: TechnologyType) => {
      setCurrentTechnology(technology);
      fetchMindMap(technology);
    },
    [fetchMindMap]
  );

  const onNodeClick = useCallback((_event: React.MouseEvent, node: Node) => {
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
  }, []);

  const handleCloseSidebar = useCallback(() => {
    setIsSidebarOpen(false);
    setSelectedTopic(null);
  }, []);

  const handleTaskClick = useCallback((taskId: string) => {
    // Переход к редактору кода
    window.location.href = `/code-editor?blockId=${taskId}`;
  }, []);

  useEffect(() => {
    fetchMindMap();
  }, [fetchMindMap]);

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

  if (!mindMapData) {
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
        ❌ Ошибка загрузки данных
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

      <MindMapProgressSidebar
        isOpen={isSidebarOpen}
        onClose={handleCloseSidebar}
        selectedTopic={selectedTopic}
        currentTechnology={currentTechnology}
        onTaskClick={handleTaskClick}
        onTheoreticalTaskClick={setTheoreticalTaskId}
      />

      <TaskDetailModal
        isOpen={!!theoreticalTaskId}
        onClose={() => setTheoreticalTaskId(null)}
        task={theoreticalTaskDetail}
      />

      <div className={styles.mobileNav}>
        <BottomNavBar />
      </div>
    </div>
  );
};

export default NewMindMapPage;
