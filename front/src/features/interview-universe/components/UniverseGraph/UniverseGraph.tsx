import React, { useEffect, useRef, useState, useMemo, useCallback } from 'react';
import Graph from 'graphology';
import Sigma from 'sigma';
import { SigmaContainer, useLoadGraph, useRegisterEvents, useSigma } from '@react-sigma/core';
import '@react-sigma/core/lib/style.css';
import ForceAtlas2Layout from 'graphology-layout-forceatlas2/worker';
import { circular } from 'graphology-layout';
import { 
  UniverseData, 
  UniverseNode, 
  UniverseEdge,
  FilterOptions,
  LayoutOptions,
  InteractionState,
  SigmaNodeAttributes
} from '../../types/universe.types';
import styles from './UniverseGraph.module.scss';

interface UniverseGraphProps {
  data: UniverseData | null;
  filters?: FilterOptions;
  layout?: LayoutOptions;
  onNodeClick?: (node: UniverseNode) => void;
  onNodeHover?: (node: UniverseNode | null) => void;
  className?: string;
}

// Category color mapping
const CATEGORY_COLORS: Record<string, string> = {
  'javascript_core': '#f7df1e',
  'react': '#61dafb',
  'typescript': '#3178c6',
  'soft_skills': '#ff6b6b',
  'алгоритмы': '#dc143c',
  'сеть': '#ff6b35',
  'верстка': '#e91e63',
  'браузеры': '#9c27b0',
  'архитектура': '#673ab7',
  'инструменты': '#3f51b5',
  'производительность': '#00bcd4',
  'тестирование': '#4caf50',
  'другое': '#9e9e9e'
};

// Inner component that has access to Sigma instance
const GraphContent: React.FC<{
  data: UniverseData;
  filters?: FilterOptions;
  layout?: LayoutOptions;
  onNodeClick?: (node: UniverseNode) => void;
  onNodeHover?: (node: UniverseNode | null) => void;
}> = ({ data, filters, layout = { type: 'forceatlas2' }, onNodeClick, onNodeHover }) => {
  const sigma = useSigma();
  const loadGraph = useLoadGraph();
  const registerEvents = useRegisterEvents();
  const [hoveredNode, setHoveredNode] = useState<string | null>(null);
  const layoutWorkerRef = useRef<any>(null);

  // Build and load the graph
  useEffect(() => {
    const graph = new Graph();

    // Apply filters
    const filteredNodes = data.nodes.filter(node => {
      if (filters?.categories && !filters.categories.includes(node.category)) {
        return false;
      }
      if (filters?.minQuestionsCount && node.questionsCount < filters.minQuestionsCount) {
        return false;
      }
      if (filters?.maxQuestionsCount && node.questionsCount > filters.maxQuestionsCount) {
        return false;
      }
      if (filters?.minPenetration && node.interviewPenetration < filters.minPenetration) {
        return false;
      }
      return true;
    });

    const nodeIds = new Set(filteredNodes.map(n => n.id));
    const filteredEdges = data.edges.filter(edge => 
      nodeIds.has(edge.source) && nodeIds.has(edge.target)
    );

    // Add nodes to graph
    filteredNodes.forEach(node => {
      const size = Math.sqrt(node.questionsCount) * 2; // Size based on questions count
      
      graph.addNode(node.id, {
        ...node,
        x: node.x || Math.random() * 1000,
        y: node.y || Math.random() * 1000,
        size,
        color: CATEGORY_COLORS[node.category] || '#9e9e9e',
        label: node.label,
        borderColor: '#ffffff',
        borderWidth: hoveredNode === node.id ? 3 : 1,
        type: 'circle',
      } as SigmaNodeAttributes);
    });

    // Add edges to graph
    filteredEdges.forEach(edge => {
      graph.addEdge(edge.source, edge.target, {
        size: Math.log(edge.weight + 1) * 0.5,
        color: '#cccccc44',
        type: 'line',
      });
    });

    // Load the graph
    loadGraph(graph);

    // Apply layout
    if (layout.type === 'forceatlas2') {
      applyForceAtlas2Layout(graph, layout.settings);
    } else if (layout.type === 'circular') {
      circular.assign(graph);
      sigma.refresh();
    }

    return () => {
      if (layoutWorkerRef.current) {
        layoutWorkerRef.current.kill();
        layoutWorkerRef.current = null;
      }
    };
  }, [data, filters, layout, loadGraph, sigma, hoveredNode]);

  // Apply ForceAtlas2 layout
  const applyForceAtlas2Layout = useCallback((graph: Graph, settings?: any) => {
    if (layoutWorkerRef.current) {
      layoutWorkerRef.current.kill();
    }

    const sensibleSettings = {
      iterations: 100,
      settings: {
        gravity: settings?.gravity ?? 1,
        scalingRatio: settings?.scalingRatio ?? 10,
        strongGravityMode: settings?.strongGravityMode ?? false,
        barnesHutOptimize: settings?.barnesHutOptimize ?? true,
        barnesHutTheta: settings?.barnesHutTheta ?? 0.5,
        edgeWeightInfluence: settings?.edgeWeightInfluence ?? 1,
        slowDown: settings?.slowDown ?? 1,
      }
    };

    layoutWorkerRef.current = new ForceAtlas2Layout(graph, sensibleSettings);
    
    layoutWorkerRef.current.start();
    
    // Stop layout after some time for performance
    setTimeout(() => {
      if (layoutWorkerRef.current) {
        layoutWorkerRef.current.stop();
        sigma.refresh();
      }
    }, 5000);
  }, [sigma]);

  // Register events
  useEffect(() => {
    registerEvents({
      clickNode: (event) => {
        const nodeData = sigma.getGraph().getNodeAttributes(event.node) as UniverseNode;
        if (onNodeClick) {
          onNodeClick(nodeData);
        }
      },
      enterNode: (event) => {
        setHoveredNode(event.node);
        const nodeData = sigma.getGraph().getNodeAttributes(event.node) as UniverseNode;
        
        // Highlight hovered node and connected edges
        sigma.getGraph().setNodeAttribute(event.node, 'highlighted', true);
        sigma.getGraph().neighbors(event.node).forEach(neighbor => {
          sigma.getGraph().setNodeAttribute(neighbor, 'highlighted', true);
        });
        
        if (onNodeHover) {
          onNodeHover(nodeData);
        }
        
        sigma.refresh();
      },
      leaveNode: () => {
        if (hoveredNode) {
          // Reset highlights
          sigma.getGraph().forEachNode(node => {
            sigma.getGraph().setNodeAttribute(node, 'highlighted', false);
          });
        }
        
        setHoveredNode(null);
        if (onNodeHover) {
          onNodeHover(null);
        }
        
        sigma.refresh();
      },
    });
  }, [registerEvents, sigma, onNodeClick, onNodeHover, hoveredNode]);

  // Update node states based on hover
  useEffect(() => {
    const graph = sigma.getGraph();
    
    graph.forEachNode((node) => {
      const isHovered = node === hoveredNode;
      const isNeighbor = hoveredNode && graph.hasEdge(hoveredNode, node);
      
      if (hoveredNode && !isHovered && !isNeighbor) {
        graph.updateNodeAttribute(node, 'color', (color) => color + '33'); // Add transparency
      } else {
        const originalColor = CATEGORY_COLORS[graph.getNodeAttribute(node, 'category')] || '#9e9e9e';
        graph.setNodeAttribute(node, 'color', originalColor);
      }
      
      graph.setNodeAttribute(node, 'borderWidth', isHovered ? 3 : 1);
    });

    graph.forEachEdge((edge) => {
      const [source, target] = graph.extremities(edge);
      const isConnected = hoveredNode && (source === hoveredNode || target === hoveredNode);
      
      graph.setEdgeAttribute(edge, 'color', isConnected ? '#ffffff88' : '#cccccc44');
      graph.setEdgeAttribute(edge, 'size', isConnected ? 2 : 1);
    });

    sigma.refresh();
  }, [hoveredNode, sigma]);

  return null;
};

// Main component wrapper
export const UniverseGraph: React.FC<UniverseGraphProps> = ({
  data,
  filters,
  layout,
  onNodeClick,
  onNodeHover,
  className,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [containerReady, setContainerReady] = useState(false);

  useEffect(() => {
    // Ensure container has dimensions before rendering Sigma
    const checkContainer = () => {
      if (containerRef.current) {
        const rect = containerRef.current.getBoundingClientRect();
        if (rect.width > 0 && rect.height > 0) {
          setContainerReady(true);
        }
      }
    };

    // Check immediately
    checkContainer();
    
    // Check again after DOM updates
    const timer = setTimeout(checkContainer, 100);
    
    // Also check on window resize
    window.addEventListener('resize', checkContainer);
    
    return () => {
      clearTimeout(timer);
      window.removeEventListener('resize', checkContainer);
    };
  }, []);

  if (!data) {
    return (
      <div ref={containerRef} className={`${styles.container} ${className || ''}`}>
        <div className={styles.loading}>Loading universe data...</div>
      </div>
    );
  }

  if (!containerReady) {
    return (
      <div ref={containerRef} className={`${styles.container} ${className || ''}`}>
        <div className={styles.loading}>Initializing visualization...</div>
      </div>
    );
  }

  return (
    <div ref={containerRef} className={`${styles.container} ${className || ''}`}>
      <SigmaContainer
        style={{ height: '100%', width: '100%' }}
        settings={{
          allowInvalidContainer: true,
          renderLabels: true,
          labelFont: '"Inter", sans-serif',
          labelSize: 12,
          labelWeight: '600',
          labelColor: { color: '#ffffff' },
          defaultNodeType: 'circle',
          defaultEdgeType: 'line',
          nodeReducer: (node, attrs) => {
            // Reducer to handle node rendering states
            const isHighlighted = attrs.highlighted;
            return {
              ...attrs,
              size: isHighlighted ? attrs.size * 1.2 : attrs.size,
              zIndex: isHighlighted ? 1 : 0,
            };
          },
        }}
      >
        <GraphContent
          data={data}
          filters={filters}
          layout={layout}
          onNodeClick={onNodeClick}
          onNodeHover={onNodeHover}
        />
      </SigmaContainer>
    </div>
  );
};