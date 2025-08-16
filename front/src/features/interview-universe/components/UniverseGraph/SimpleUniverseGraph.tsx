import React, { useEffect } from 'react';
import Graph from 'graphology';
import { SigmaContainer, useLoadGraph, useSigma } from '@react-sigma/core';
import '@react-sigma/core/lib/style.css';
import { UniverseData } from '../../types/universe.types';
import styles from './UniverseGraph.module.scss';

interface SimpleUniverseGraphProps {
  data: UniverseData | null;
  className?: string;
}

// Simple graph content component
const SimpleGraphContent: React.FC<{ data: UniverseData }> = ({ data }) => {
  const loadGraph = useLoadGraph();
  const sigma = useSigma();

  useEffect(() => {
    console.log('Loading graph with data:', data);
    
    const graph = new Graph();

    // Add nodes with simple colors
    data.nodes.forEach((node, index) => {
      console.log('Adding node:', node.id, node.label);
      
      graph.addNode(node.id, {
        x: node.x || Math.random() * 100,
        y: node.y || Math.random() * 100,
        size: Math.max(5, node.size || 10),
        color: getColorByCategory(node.category),
        label: node.label,
      });
    });

    // Add edges
    data.edges.forEach(edge => {
      if (graph.hasNode(edge.source) && graph.hasNode(edge.target)) {
        console.log('Adding edge:', edge.source, '->', edge.target);
        graph.addEdge(edge.source, edge.target, {
          color: '#666',
          size: 1,
        });
      }
    });

    console.log('Graph stats:', {
      nodes: graph.order,
      edges: graph.size,
    });

    loadGraph(graph);
    
    // Force refresh
    setTimeout(() => {
      sigma.refresh();
    }, 100);
  }, [data, loadGraph, sigma]);

  return null;
};

// Simple color mapping
function getColorByCategory(category: string): string {
  const colors: Record<string, string> = {
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
  return colors[category] || '#9e9e9e';
}

export const SimpleUniverseGraph: React.FC<SimpleUniverseGraphProps> = ({
  data,
  className,
}) => {
  console.log('🔍 SimpleUniverseGraph render - data:', !!data);
  
  if (!data) {
    console.log('❌ No data provided to SimpleUniverseGraph');
    return (
      <div className={`${styles.container} ${className || ''}`}>
        <div className={styles.loading}>Loading graph data...</div>
      </div>
    );
  }

  console.log('✅ Rendering SimpleUniverseGraph with data:', {
    nodes: data.nodes.length,
    edges: data.edges.length,
    firstNode: data.nodes[0]?.label
  });

  return (
    <div className={`${styles.container} ${className || ''}`}>
      <SigmaContainer
        style={{ 
          height: '100%', 
          width: '100%',
          minWidth: '800px',
          minHeight: '600px'
        }}
        settings={{
          allowInvalidContainer: true,
          renderLabels: true,
          defaultNodeColor: '#999',
          defaultEdgeColor: '#666',
          labelSize: 14,
          labelWeight: 'bold',
          labelColor: { color: '#fff' },
        }}
      >
        <SimpleGraphContent data={data} />
      </SigmaContainer>
    </div>
  );
};