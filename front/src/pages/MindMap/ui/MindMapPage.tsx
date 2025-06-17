import { BottomNavBar } from '@/shared/components/BottomNavBar';
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
import CenterNode from '../../../components/MindMapNodes/CenterNode';
import TopicNode from '../../../components/MindMapNodes/TopicNode';
import TopicTaskModal from '../../../components/MindMapNodes/TopicTaskModal';
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
  const [selectedTopic, setSelectedTopic] = useState<string | null>(null);
  const [isTopicModalOpen, setIsTopicModalOpen] = useState(false);

  const fetchMindMap = useCallback(async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/mindmap/generate');
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
  }, [setNodes, setEdges]);

  const onNodeClick = useCallback((_event: React.MouseEvent, node: Node) => {
    if (node.type === 'topic' && node.data.topic_key) {
      setSelectedTopic(node.data.topic_key as string);
      setIsTopicModalOpen(true);
    }
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
      <div style={{ width: '100%', height: '100%' }}>
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

      <TopicTaskModal
        isOpen={isTopicModalOpen}
        onClose={() => {
          setIsTopicModalOpen(false);
          setSelectedTopic(null);
        }}
        topicKey={selectedTopic}
      />
      <div className={styles.mobileNav}>
        <BottomNavBar />
      </div>
    </div>
  );
};

export default NewMindMapPage;
