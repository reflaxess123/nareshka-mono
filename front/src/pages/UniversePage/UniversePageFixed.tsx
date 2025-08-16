import React, { useEffect, useState } from 'react';
import { SimpleUniverseGraph } from '../../features/interview-universe/components/UniverseGraph/SimpleUniverseGraph';
import { UniverseData } from '../../features/interview-universe/types/universe.types';
import styles from './UniversePage.module.scss';

export const UniversePageFixed: React.FC = () => {
  const [data, setData] = useState<UniverseData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        console.log('Fetching universe data...');
        const response = await fetch('/api/v2/interview-universe/graph?limit=50');
        
        if (!response.ok) {
          throw new Error(`Failed to fetch universe data: ${response.statusText}`);
        }

        const apiData = await response.json();
        console.log('Raw API data:', apiData);

        // Transform API data to our format
        const transformedData: UniverseData = {
          nodes: apiData.nodes.map((node: any) => ({
            id: `cluster-${node.id}`,
            label: node.name,
            clusterId: node.id,
            category: node.category_id,
            questionsCount: node.questions_count,
            interviewPenetration: node.interview_penetration,
            keywords: node.keywords || [],
            exampleQuestion: node.example_question,
            topCompanies: node.top_companies || [],
            difficultyDistribution: node.difficulty_distribution || {
              junior: 0,
              middle: 0,
              senior: 0,
            },
            size: Math.sqrt(node.questions_count) * 2,
            color: '', // Will be set by category colors
            x: node.x || Math.random() * 1000,
            y: node.y || Math.random() * 1000,
          })),
          edges: apiData.edges.map((edge: any) => ({
            id: `edge-${edge.source}-${edge.target}`,
            source: `cluster-${edge.source}`,
            target: `cluster-${edge.target}`,
            weight: edge.weight,
          })),
          categories: apiData.categories || {},
          stats: apiData.stats || {
            totalQuestions: 8532,
            totalClusters: 182,
            totalCategories: 13,
            totalCompanies: 380,
            avgQuestionsPerCluster: 47,
            avgInterviewPenetration: 25,
          },
        };

        console.log('✅ Transformed data:', transformedData);
        console.log('📊 Data summary:', {
          nodesCount: transformedData.nodes.length,
          edgesCount: transformedData.edges.length,
          firstNode: transformedData.nodes[0],
          firstEdge: transformedData.edges[0]
        });
        setData(transformedData);
      } catch (err) {
        console.error('Error fetching universe data:', err);
        setError(err as Error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleNodeClick = (node: any) => {
    console.log('Node clicked:', node);
  };

  const handleNodeHover = (node: any) => {
    console.log('Node hovered:', node);
  };

  if (error) {
    return (
      <div className={styles.errorContainer}>
        <h2>Error loading universe data</h2>
        <p>{error.message}</p>
      </div>
    );
  }

  console.log('🎨 Rendering UniversePage. Loading:', loading, 'Data:', !!data, 'Error:', !!error);

  return (
    <div className={styles.container}>
      {data && (
        <SimpleUniverseGraph
          data={data}
          className={styles.graph}
        />
      )}
      {loading && (
        <div className={styles.loadingOverlay}>
          <div className={styles.loadingContent}>
            <div className={styles.spinner} />
            <p>Loading universe visualization...</p>
          </div>
        </div>
      )}
      {!loading && !data && !error && (
        <div style={{color: 'white', padding: '20px'}}>
          ⚠️ No data available
        </div>
      )}
    </div>
  );
};

export default UniversePageFixed;