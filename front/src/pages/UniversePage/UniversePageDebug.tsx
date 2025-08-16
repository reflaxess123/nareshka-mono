import React, { useEffect, useState } from 'react';
import styles from './UniversePage.module.scss';

export const UniversePageDebug: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/v2/interview-universe/graph?limit=5')
      .then(res => res.json())
      .then(data => {
        console.log('✅ Data loaded:', data);
        setData(data);
        setLoading(false);
      })
      .catch(err => {
        console.error('❌ Error:', err);
        setLoading(false);
      });
  }, []);

  return (
    <div style={{ 
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: '#0a0a0a',
      color: 'white',
      padding: '20px',
      overflow: 'auto'
    }}>
      <h1>Universe Debug Page</h1>
      
      {loading && <div>Loading...</div>}
      
      {data && (
        <div>
          <h2>✅ Data Loaded Successfully</h2>
          <p><strong>Nodes:</strong> {data.nodes?.length || 0}</p>
          <p><strong>Edges:</strong> {data.edges?.length || 0}</p>
          <p><strong>Categories:</strong> {Object.keys(data.categories || {}).length}</p>
          
          <h3>Nodes Preview:</h3>
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: '10px',
            marginTop: '10px'
          }}>
            {data.nodes?.slice(0, 6).map((node: any, i: number) => (
              <div key={i} style={{
                background: '#1a1a1a',
                padding: '10px',
                borderRadius: '8px',
                border: '1px solid #333'
              }}>
                <h4 style={{ color: '#61dafb', margin: '0 0 8px 0' }}>
                  {node.name}
                </h4>
                <p style={{ margin: '4px 0', fontSize: '14px' }}>
                  <strong>Category:</strong> {node.category_name}
                </p>
                <p style={{ margin: '4px 0', fontSize: '14px' }}>
                  <strong>Questions:</strong> {node.questions_count}
                </p>
                <p style={{ margin: '4px 0', fontSize: '14px' }}>
                  <strong>Companies:</strong> {node.top_companies?.join(', ') || 'None'}
                </p>
                <p style={{ margin: '4px 0', fontSize: '12px', color: '#888' }}>
                  {node.example_question?.substring(0, 100)}...
                </p>
              </div>
            ))}
          </div>
          
          <h3 style={{ marginTop: '30px' }}>Network Connections:</h3>
          <div style={{ marginTop: '10px' }}>
            {data.edges?.slice(0, 10).map((edge: any, i: number) => (
              <div key={i} style={{
                background: '#1a1a1a',
                padding: '8px',
                margin: '4px 0',
                borderRadius: '4px',
                fontSize: '14px'
              }}>
                Node {edge.source} ↔ Node {edge.target} (Weight: {edge.weight})
              </div>
            ))}
          </div>
          
          <div style={{ marginTop: '40px', padding: '20px', background: '#1a4a1a', borderRadius: '8px' }}>
            <h3>🎯 Next Steps:</h3>
            <p>1. Data is loading correctly ✅</p>
            <p>2. We have {data.nodes?.length} nodes and {data.edges?.length} connections</p>
            <p>3. Ready to implement proper Sigma.js visualization</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default UniversePageDebug;