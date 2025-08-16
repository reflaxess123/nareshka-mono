import React, { useEffect, useState } from 'react';
import styles from './UniversePage.module.scss';

export const UniversePageSimple: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    console.log('UniversePage mounted');
    
    const fetchData = async () => {
      try {
        console.log('Starting fetch...');
        const response = await fetch('/api/v2/interview-universe/graph?limit=5');
        console.log('Response status:', response.status);
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        console.log('Data received:', result);
        setData(result);
      } catch (err) {
        console.error('Fetch error:', err);
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  return (
    <div className={styles.container}>
      <h1 style={{ color: 'white', padding: '20px' }}>Universe Visualization Test</h1>
      
      {loading && (
        <div style={{ color: 'white', padding: '20px' }}>
          Loading data...
        </div>
      )}
      
      {error && (
        <div style={{ color: 'red', padding: '20px' }}>
          Error: {error}
        </div>
      )}
      
      {data && (
        <div style={{ color: 'white', padding: '20px' }}>
          <p>Data loaded successfully!</p>
          <p>Nodes: {data.nodes?.length || 0}</p>
          <p>Edges: {data.edges?.length || 0}</p>
          <p>Categories: {Object.keys(data.categories || {}).length}</p>
          <pre style={{ fontSize: '12px', maxHeight: '400px', overflow: 'auto' }}>
            {JSON.stringify(data, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
};

export default UniversePageSimple;