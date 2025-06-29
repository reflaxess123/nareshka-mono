// Типы для новой системы mind map на основе 10 тем JavaScript

export interface TopicTask {
  id: string;
  title: string;
  complexity: number;
  time_minutes: number;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  concepts: string[];
  category: string;
}

export interface TopicInfo {
  topic_key: string;
  title: string;
  icon: string;
  color: string;
  description: string;
  task_count: number;
  total_task_count: number;
  avg_complexity: number;
  difficulty_distribution: Record<string, number>;
  top_companies: Array<{ name: string; count: number }>;
  estimated_time: number;
  difficulty_levels: TopicDifficultyLevel[];
}

export interface TopicDifficultyLevel {
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  label: string;
  full_label: string;
  parent_topic: string;
  task_count: number;
  tasks: TopicTask[];
  avg_time: number;
  color: string;
}

export interface CenterNodeData extends Record<string, unknown> {
  label: string;
  description: string;
  total_tasks: number;
  coverage: number;
  type: 'center';
}

export interface TopicNodeData extends Record<string, unknown> {
  topic_key: string;
  title: string;
  icon: string;
  color: string;
  description: string;
  task_count: number;
  total_task_count: number;
  avg_complexity: number;
  difficulty_distribution: Record<string, number>;
  top_companies: Array<{ name: string; count: number }>;
  estimated_time: number;
  difficulty_levels: TopicDifficultyLevel[];
  type: 'topic';
}

export interface DifficultyNodeData extends Record<string, unknown> {
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  label: string;
  full_label: string;
  parent_topic: string;
  task_count: number;
  tasks: TopicTask[];
  avg_time: number;
  color: string;
  type: 'difficulty';
}

export type TopicMindMapNodeData =
  | CenterNodeData
  | TopicNodeData
  | DifficultyNodeData;

export interface TopicMindMapNode {
  id: string;
  type: 'center' | 'topic' | 'difficulty';
  position: { x: number; y: number };
  data: TopicMindMapNodeData;
  selected?: boolean;
}

export interface TopicMindMapEdge {
  id: string;
  source: string;
  target: string;
  animated?: boolean;
  style?: Record<string, unknown>;
}

export interface TopicMindMapData {
  nodes: TopicMindMapNode[];
  edges: TopicMindMapEdge[];
  layout: string;
  total_nodes: number;
  total_edges: number;
  structure_type: 'topics' | 'legacy';
  topic_structure?: {
    center: CenterNodeData;
    topics: Record<string, TopicInfo>;
    total_coverage: number;
  };
}

export interface TopicMindMapResponse {
  success: boolean;
  data?: TopicMindMapData;
  error?: string;
}

// Фильтры и настройки для новой системы
export interface TopicMindMapFilters {
  structure_type: 'topics' | 'legacy';
  technology?: 'javascript' | 'react' | 'typescript';
  difficulty_filter?: 'beginner' | 'intermediate' | 'advanced';
  topic_filter?: string;
  concept_filter?: string;
}

// Константы для цветов тем
export const TOPIC_COLORS = {
  closures: '#8B5CF6',
  custom_functions: '#10B981',
  classes: '#F59E0B',
  arrays: '#EF4444',
  matrices: '#6366F1',
  objects: '#8B5CF6',
  promises: '#06B6D4',
  strings: '#84CC16',
  throttle_debounce: '#F97316',
  numbers: '#EC4899',
} as const;

// Константы для иконок тем
export const TOPIC_ICONS = {
  closures: '🔒',
  custom_functions: '⚡',
  classes: '🏗️',
  arrays: '📚',
  matrices: '🔢',
  objects: '📦',
  promises: '🔄',
  strings: '📝',
  throttle_debounce: '⏱️',
  numbers: '🔢',
} as const;

// Маппинг тем на русский язык
export const TOPIC_LABELS = {
  closures: 'Замыкания',
  custom_functions: 'Кастомные методы и функции',
  classes: 'Классы',
  arrays: 'Массивы',
  matrices: 'Матрицы',
  objects: 'Объекты',
  promises: 'Промисы',
  strings: 'Строки',
  throttle_debounce: 'Throttle & Debounce',
  numbers: 'Числа',
} as const;
