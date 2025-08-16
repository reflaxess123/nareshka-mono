import type { Edge, Node } from '@xyflow/react';

// Базовые типы данных
export interface TaskDetail {
  id: string;
  title: string;
  category: string;
  subcategory: string;
  path_titles: string[];
  text_content: string;
  code_content: string;
  code_language: string;
  code_lines: number;
  complexity_score: number;
  difficulty_factors: string[];
  programming_concepts: string[];
  js_features_used: string[];
  keywords: string[];
  similar_tasks: string[];
  prerequisite_concepts: string[];
  estimated_time_minutes: number;
  target_skill_level: string;
  path_depth: number;
  order_in_file: number;
  pedagogical_type: string;
  text_complexity: number;
  user_success_rate: number;
  avg_solve_time: number;
}

// Типы узлов для React Flow (legacy)
export interface MindMapNodeData extends Record<string, unknown> {
  label: string;
  description?: string;
  type: 'center' | 'concept' | 'path' | 'difficulty' | 'task';

  // Для концепций
  concept?: string;
  task_count?: number;
  avg_complexity?: number;
  difficulty_color?: string;

  // Для путей обучения
  full_title?: string;

  // Для уровней сложности
  percentage?: number;

  // Для задач
  task_id?: string;
  task?: TaskDetail;
}

export interface LegacyMindMapNode extends Node {
  data: MindMapNodeData;
}

export interface LegacyMindMapEdge extends Edge {
  type?:
    | 'conceptEdge'
    | 'pathEdge'
    | 'difficultyEdge'
    | 'prerequisiteEdge'
    | 'taskEdge';
}

// Основные типы для новой системы mind map
export interface Task {
  id: string;
  title: string;
  complexity: number;
  time_minutes: number;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  concepts: string[];
  category: string;
}

export interface TopicData {
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
  difficulty_levels: DifficultyLevelData[];
}

export interface DifficultyLevelData {
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  label: string;
  full_label: string;
  parent_topic: string;
  task_count: number;
  tasks: Task[];
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

export interface TopicNodeData extends TopicData, Record<string, unknown> {
  type: 'topic';
}

export interface DifficultyNodeData
  extends DifficultyLevelData,
    Record<string, unknown> {
  type: 'difficulty';
}

export type NodeData = CenterNodeData | TopicNodeData | DifficultyNodeData;

export interface MindMapNode extends Node {
  id: string;
  type: 'center' | 'topic' | 'difficulty';
  position: { x: number; y: number };
  data: NodeData;
}

export interface MindMapEdge extends Edge {
  id: string;
  source: string;
  target: string;
  animated?: boolean;
  style?: Record<string, unknown>;
}

export interface MindMapData {
  nodes: MindMapNode[];
  edges: MindMapEdge[];
  layout: string;
  total_nodes: number;
  total_edges: number;
  structure_type: 'topics' | 'legacy';
  active_topics?: number;
  applied_filters?: {
    difficulty?: string;
    topic?: string;
  };
  topic_structure?: {
    center: CenterNodeData;
    topics: Record<string, TopicData>;
    total_coverage: number;
  };
}

export interface MindMapResponse {
  success: boolean;
  data?: MindMapData;
  error?: string;
  metadata?: {
    total_tasks: number;
    generated_at: string;
    filters_applied: {
      difficulty?: string;
      concept?: string;
    };
  };
}

export interface TaskDetailResponse {
  success: boolean;
  task: TaskDetail;
  related_tasks: Array<{
    id: string;
    title: string;
    complexity_score: number;
    target_skill_level: string;
  }>;
}

// Фильтры и настройки
export interface MindMapFilters {
  structure_type?: 'topics' | 'legacy';
  difficulty?: 'beginner' | 'intermediate' | 'advanced';
  difficulty_filter?: 'beginner' | 'intermediate' | 'advanced';
  topic_filter?: string;
  concept?: string;
  concept_filter?: string;
  topic?: string;
}

export interface MindMapSettings {
  showAnimations: boolean;
  showMiniMap: boolean;
  showBackground: boolean;
  layoutType: 'hierarchy' | 'radial' | 'force';
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

// Добавляем типы для технологий
export type TechnologyType = 'javascript' | 'react' | 'typescript' | 'interviews';

export interface TechnologyConfig {
  title: string;
  description: string;
  icon: string;
  color: string;
}

export interface TechnologiesResponse {
  success: boolean;
  data: {
    technologies: TechnologyType[];
    configs: Record<TechnologyType, TechnologyConfig>;
  };
}
