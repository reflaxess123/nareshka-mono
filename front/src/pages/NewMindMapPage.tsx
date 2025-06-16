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
import CenterNode from '../components/MindMapNodes/CenterNode';
import TaskNode from '../components/MindMapNodes/TaskNode';
import TopicNode from '../components/MindMapNodes/TopicNode';
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
  task: TaskNode,
};

const NewMindMapPage: React.FC = () => {
  const [mindMapData, setMindMapData] = useState<MindMapData | null>(null);
  const [loading, setLoading] = useState(false);
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  const fetchMindMap = useCallback(async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/mindmap/generate');
      const result = await response.json();
      console.log('Received mind map data:', result);

      if (result.success && result.data) {
        setMindMapData(result.data);
        setNodes(result.data.nodes);
        setEdges(result.data.edges);
      } else {
        console.error('API returned error:', result.error);
      }
    } catch (error) {
      console.error('Error fetching mind map:', error);
    } finally {
      setLoading(false);
    }
  }, [setNodes, setEdges]);

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
        }}
      >
        Генерируем mind map...
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
        }}
      >
        Не удалось загрузить mind map
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
                  <h1 className={styles.title}>JavaScript Skills Map</h1>
                  <p className={styles.subtitle}>
                    {mindMapData?.total_nodes || 0} узлов •{' '}
                    {mindMapData?.active_topics || 0} активных тем
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className={styles.flowCanvas}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          nodeTypes={nodeTypes}
          fitView
          defaultViewport={{ x: 0, y: 0, zoom: 0.5 }}
          minZoom={0.2}
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
          <Controls showInteractive={false} />
          <MiniMap
            nodeColor={(node) => {
              const data = node.data as Record<string, unknown>;
              return (data.color as string) || '#e2e8f0';
            }}
            maskColor="rgba(0, 0, 0, 0.05)"
            pannable
            zoomable
          />
        </ReactFlow>
      </div>

      <div className={styles.legend}>
        <div className={styles.legendItems}>
          <div className={styles.legendItem}>
            <div className={`${styles.legendDot} ${styles.purple}`}></div>
            <span className={styles.legendText}>Центр</span>
          </div>
          <div className={styles.legendItem}>
            <div className={`${styles.legendDot} ${styles.green}`}></div>
            <span className={styles.legendText}>Темы</span>
          </div>
          <div className={styles.legendItem}>
            <div className={`${styles.legendDot} ${styles.yellow}`}></div>
            <span className={styles.legendText}>Задачи</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NewMindMapPage;
