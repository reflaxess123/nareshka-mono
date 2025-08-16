import React from 'react';
import { UniverseGraph } from '../../features/interview-universe/components/UniverseGraph/UniverseGraph';
import { useGraphData } from '../../features/interview-universe/hooks/useGraphData';
import styles from './UniversePage.module.scss';

export const UniversePage: React.FC = () => {
  const { data, loading, error, loadMoreNodes } = useGraphData({
    initialLoad: 50,
    chunkSize: 30,
  });

  const handleNodeClick = (node: any) => {
    console.log('Node clicked:', node);
    // TODO: Show node details panel
  };

  const handleNodeHover = (node: any) => {
    console.log('Node hovered:', node);
    // TODO: Show tooltip
  };

  if (error) {
    return (
      <div className={styles.errorContainer}>
        <h2>Error loading universe data</h2>
        <p>{error.message}</p>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <UniverseGraph
        data={data}
        onNodeClick={handleNodeClick}
        onNodeHover={handleNodeHover}
        className={styles.graph}
      />
      {loading.isLoading && (
        <div className={styles.loadingOverlay}>
          <div className={styles.loadingContent}>
            <div className={styles.spinner} />
            <p>Loading universe... {loading.loadedNodes}/{loading.totalNodes} nodes</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default UniversePage;