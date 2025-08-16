import { useState, useEffect, useCallback } from 'react';
import { UniverseData, FilterOptions, LoadingState } from '../types/universe.types';

interface UseGraphDataOptions {
  initialLoad?: number; // Initial number of nodes to load
  chunkSize?: number; // Number of nodes to load per chunk
  filters?: FilterOptions;
  cacheEnabled?: boolean;
}

export const useGraphData = (options: UseGraphDataOptions = {}) => {
  const {
    initialLoad = 50,
    chunkSize = 30,
    filters,
    cacheEnabled = true,
  } = options;

  const [data, setData] = useState<UniverseData | null>(null);
  const [loading, setLoading] = useState<LoadingState>({
    isLoading: true,
    loadedNodes: 0,
    totalNodes: 0,
    loadedEdges: 0,
    totalEdges: 0,
    phase: 'initial',
  });
  const [error, setError] = useState<Error | null>(null);

  // Fetch initial data
  const fetchInitialData = useCallback(async () => {
    try {
      setLoading(prev => ({ ...prev, isLoading: true, phase: 'initial' }));
      
      // Build query params
      const params = new URLSearchParams({
        limit: initialLoad.toString(),
        min_interview_count: '10',
        min_link_weight: '5',
      });

      if (filters?.categories?.length) {
        params.append('categories', filters.categories.join(','));
      }
      if (filters?.companies?.length) {
        params.append('companies', filters.companies.join(','));
      }
      if (filters?.minPenetration) {
        params.append('min_penetration', filters.minPenetration.toString());
      }

      const response = await fetch(`/api/v2/interview-universe/graph?${params}`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch universe data: ${response.statusText}`);
      }

      const result = await response.json();

      // Transform API data to our format
      const transformedData: UniverseData = {
        nodes: result.nodes.map((node: any) => ({
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
        })),
        edges: result.edges.map((edge: any) => ({
          id: `edge-${edge.source}-${edge.target}`,
          source: `cluster-${edge.source}`,
          target: `cluster-${edge.target}`,
          weight: edge.weight,
        })),
        categories: result.categories || {},
        stats: result.stats || {
          totalQuestions: 8532,
          totalClusters: 182,
          totalCategories: 13,
          totalCompanies: 380,
          avgQuestionsPerCluster: 47,
          avgInterviewPenetration: 25,
        },
      };

      setData(transformedData);
      setLoading({
        isLoading: false,
        loadedNodes: transformedData.nodes.length,
        totalNodes: result.stats?.totalClusters || 182,
        loadedEdges: transformedData.edges.length,
        totalEdges: result.stats?.totalEdges || 500,
        phase: 'complete',
      });
      
      // Cache the data if enabled
      if (cacheEnabled) {
        cacheData(transformedData);
      }
    } catch (err) {
      console.error('Error fetching universe data:', err);
      setError(err as Error);
      setLoading(prev => ({ ...prev, isLoading: false, phase: 'complete' }));
    }
  }, [initialLoad, filters, cacheEnabled]);

  // Load more nodes progressively
  const loadMoreNodes = useCallback(async () => {
    if (!data || loading.loadedNodes >= loading.totalNodes) {
      return;
    }

    try {
      setLoading(prev => ({ ...prev, isLoading: true, phase: 'layout' }));
      
      const params = new URLSearchParams({
        offset: loading.loadedNodes.toString(),
        limit: chunkSize.toString(),
        min_interview_count: '5',
      });

      const response = await fetch(`/api/v2/interview-universe/graph?${params}`);
      const result = await response.json();

      // Append new nodes and edges
      const newNodes = result.nodes.map((node: any) => ({
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
        color: '',
      }));

      const newEdges = result.edges.map((edge: any) => ({
        id: `edge-${edge.source}-${edge.target}`,
        source: `cluster-${edge.source}`,
        target: `cluster-${edge.target}`,
        weight: edge.weight,
      }));

      setData(prev => {
        if (!prev) return null;
        return {
          ...prev,
          nodes: [...prev.nodes, ...newNodes],
          edges: [...prev.edges, ...newEdges],
        };
      });

      setLoading(prev => ({
        ...prev,
        isLoading: false,
        loadedNodes: prev.loadedNodes + newNodes.length,
        loadedEdges: prev.loadedEdges + newEdges.length,
        phase: 'complete',
      }));
    } catch (err) {
      console.error('Error loading more nodes:', err);
      setError(err as Error);
      setLoading(prev => ({ ...prev, isLoading: false }));
    }
  }, [data, loading.loadedNodes, loading.totalNodes, chunkSize]);

  // Cache data in IndexedDB
  const cacheData = async (data: UniverseData) => {
    try {
      if ('indexedDB' in window) {
        // Simple cache implementation
        const cacheKey = `universe-data-${JSON.stringify(filters)}`;
        localStorage.setItem(cacheKey, JSON.stringify({
          data,
          timestamp: Date.now(),
        }));
      }
    } catch (err) {
      console.warn('Failed to cache data:', err);
    }
  };

  // Load cached data
  const loadCachedData = useCallback(() => {
    try {
      if (cacheEnabled && 'localStorage' in window) {
        const cacheKey = `universe-data-${JSON.stringify(filters)}`;
        const cached = localStorage.getItem(cacheKey);
        
        if (cached) {
          const { data, timestamp } = JSON.parse(cached);
          const age = Date.now() - timestamp;
          
          // Use cache if less than 1 hour old
          if (age < 3600000) {
            setData(data);
            setLoading({
              isLoading: false,
              loadedNodes: data.nodes.length,
              totalNodes: data.stats?.totalClusters || 182,
              loadedEdges: data.edges.length,
              totalEdges: data.stats?.totalEdges || 500,
              phase: 'complete',
            });
            return true;
          }
        }
      }
    } catch (err) {
      console.warn('Failed to load cached data:', err);
    }
    return false;
  }, [filters, cacheEnabled]);

  // Initial load
  useEffect(() => {
    const hasCache = loadCachedData();
    if (!hasCache) {
      fetchInitialData();
    }
  }, [fetchInitialData, loadCachedData]);

  return {
    data,
    loading,
    error,
    loadMoreNodes,
    refetch: fetchInitialData,
  };
};