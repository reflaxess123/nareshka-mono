import { useEffect, useState } from 'react';
import type { Node, Edge } from '@xyflow/react';

interface CategoryData {
  id: string;
  name: string;
  questions_count: number;
  clusters_count: number;
  percentage: number;
}

interface ClusterData {
  nodes: Array<{
    id: number;
    name: string;
    category_id: string;
    category_name: string;
    questions_count: number;
  }>;
  links: Array<{
    source: number;
    target: number;
    weight: number;
  }>;
}

export const useInterviewsVisualization = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [data, setData] = useState<{ nodes: Node[]; edges: Edge[] } | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Загружаем данные категорий и кластеров параллельно
        const [categoriesRes, clustersRes] = await Promise.all([
          fetch('/api/v2/interview-categories/'),
          fetch('/api/v2/cluster-visualization/constellation?min_interview_count=1&limit=200')
        ]);

        if (!categoriesRes.ok || !clustersRes.ok) {
          throw new Error('Failed to fetch interview data');
        }

        const categories: CategoryData[] = await categoriesRes.json();
        const clusterData: ClusterData = await clustersRes.json();

        // Подсчитываем реальное количество кластеров по категориям
        const clusterCounts: Record<string, number> = {};
        if (clusterData.nodes) {
          clusterData.nodes.forEach(cluster => {
            clusterCounts[cluster.category_id] = (clusterCounts[cluster.category_id] || 0) + 1;
          });
        }

        // Исправляем данные категорий с правильным clusters_count
        const correctedCategories = categories.map(cat => ({
          ...cat,
          clusters_count: clusterCounts[cat.id] || 0
        }));

        // Трансформируем данные в формат ReactFlow
        const nodes: Node[] = [];
        const edges: Edge[] = [];

        const centerX = 800;
        const centerY = 500;
        const rootWidth = 300;
        const rootHeight = 200;

        // Создаем корневой узел
        nodes.push({
          id: 'interviews-root',
          type: 'interviewRoot',
          position: { x: centerX - rootWidth/2, y: centerY - rootHeight/2 },
          data: {
            totalQuestions: categories.reduce((sum, cat) => sum + cat.questions_count, 0),
            totalClusters: Object.values(clusterCounts).reduce((sum, count) => sum + count, 0),
            totalCategories: categories.length
          },
          draggable: false,
        });

        // Создаем узлы категорий
        const categoryRadius = 520;
        const sortedCategories = correctedCategories
          .sort((a, b) => b.questions_count - a.questions_count);

        sortedCategories.forEach((category, index) => {
          const categoryWidth = 200;
          const categoryHeight = 120;
          
          // Равномерное распределение по кругу
          const angle = (index / sortedCategories.length) * 2 * Math.PI - Math.PI / 2;
          const x = centerX + Math.cos(angle) * categoryRadius - categoryWidth/2;
          const y = centerY + Math.sin(angle) * categoryRadius - categoryHeight/2;

          nodes.push({
            id: `category-${category.id}`,
            type: 'interviewCategory',
            position: { x, y },
            data: {
              id: category.id,
              name: category.name,
              questionsCount: category.questions_count,
              clustersCount: category.clusters_count,
              percentage: category.percentage
            },
            draggable: false,
          });

          // Создаем связь от корня к категории
          edges.push({
            id: `root-to-${category.id}`,
            source: 'interviews-root',
            target: `category-${category.id}`,
            type: 'straight',
            style: { 
              stroke: '#61dafb', 
              strokeWidth: 2,
              opacity: 0.6
            },
            animated: false,
          });
        });

        setData({ nodes, edges });
        setError(null);
      } catch (err) {
        console.error('Error loading interviews visualization:', err);
        setError(err instanceof Error ? err : new Error('Unknown error'));
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  return {
    data,
    loading,
    error,
    isLoading: loading
  };
};