// Types for Interview Universe visualization with Sigma.js

export interface UniverseNode {
  id: string;
  label: string;
  x?: number;
  y?: number;
  size: number;
  color: string;
  category: string;
  clusterId: number;
  questionsCount: number;
  interviewPenetration: number;
  keywords: string[];
  exampleQuestion?: string;
  topCompanies: string[];
  difficultyDistribution: {
    junior: number;
    middle: number;
    senior: number;
  };
  // Visual properties
  borderColor?: string;
  borderWidth?: number;
  opacity?: number;
  highlighted?: boolean;
  hidden?: boolean;
}

export interface UniverseEdge {
  id: string;
  source: string;
  target: string;
  weight: number;
  size?: number;
  color?: string;
  type?: 'line' | 'arrow' | 'curve';
  hidden?: boolean;
}

export interface UniverseData {
  nodes: UniverseNode[];
  edges: UniverseEdge[];
  categories: Record<string, CategoryInfo>;
  stats: UniverseStats;
}

export interface CategoryInfo {
  id: string;
  name: string;
  color: string;
  questionsCount: number;
  clustersCount: number;
  percentage: number;
}

export interface UniverseStats {
  totalQuestions: number;
  totalClusters: number;
  totalCategories: number;
  totalCompanies: number;
  avgQuestionsPerCluster: number;
  avgInterviewPenetration: number;
}

export interface FilterOptions {
  categories?: string[];
  companies?: string[];
  minQuestionsCount?: number;
  maxQuestionsCount?: number;
  minPenetration?: number;
  difficulty?: ('junior' | 'middle' | 'senior')[];
}

export interface LayoutOptions {
  type: 'forceatlas2' | 'circular' | 'random' | 'grid';
  settings?: {
    gravity?: number;
    scalingRatio?: number;
    strongGravityMode?: boolean;
    barnesHutOptimize?: boolean;
    barnesHutTheta?: number;
    edgeWeightInfluence?: number;
    slowDown?: number;
  };
}

export interface ViewMode {
  type: 'galaxy' | 'network' | 'heatmap' | 'timeline' | 'company';
  settings?: Record<string, any>;
}

export interface InteractionState {
  hoveredNode: string | null;
  selectedNodes: string[];
  focusedNode: string | null;
  highlightedEdges: string[];
  searchQuery: string;
  zoomLevel: number;
  panPosition: { x: number; y: number };
}

export interface ClusterDetails {
  id: number;
  name: string;
  category: string;
  questionsCount: number;
  questions?: QuestionInfo[];
  relatedClusters: RelatedCluster[];
  topCompanies: CompanyStats[];
  trendData?: TrendPoint[];
}

export interface QuestionInfo {
  id: string;
  text: string;
  company: string;
  date?: string;
  difficulty?: 'junior' | 'middle' | 'senior';
}

export interface RelatedCluster {
  id: number;
  name: string;
  sharedQuestions: number;
  correlation: number;
}

export interface CompanyStats {
  name: string;
  count: number;
  percentage: number;
}

export interface TrendPoint {
  date: string;
  count: number;
  penetration: number;
}

// Sigma specific types
export interface SigmaNodeAttributes extends UniverseNode {
  x: number;
  y: number;
  type?: 'circle' | 'square' | 'diamond';
  icon?: string;
  image?: string;
}

export interface SigmaEdgeAttributes {
  size: number;
  color: string;
  type?: 'line' | 'arrow' | 'curve';
  hidden?: boolean;
}

// Performance optimization types
export interface LoadingState {
  isLoading: boolean;
  loadedNodes: number;
  totalNodes: number;
  loadedEdges: number;
  totalEdges: number;
  phase: 'initial' | 'layout' | 'rendering' | 'complete';
}

export interface CacheConfig {
  enabled: boolean;
  ttl: number; // Time to live in seconds
  maxSize: number; // Max cache size in MB
  storage: 'memory' | 'indexeddb' | 'localstorage';
}