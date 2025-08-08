import { apiInstance } from './base';

export type TopicRow = {
  cluster_id: string;
  cluster_label: string;
  count: string;
  companies?: string;
  first_seen?: string;
  last_seen?: string;
};

export type CompanyProfileRow = {
  company: string;
  rank: string;
  cluster_id: string;
  cluster_label: string;
  count: string;
  share?: string;
};

export type TrendRow = { month: string; cluster_label: string; count: string };
export type CooccurrenceRow = {
  cluster_label_a: string;
  cluster_label_b: string;
  count: string;
};
export type DuplicateRow = {
  row_id_1: string;
  row_id_2: string;
  sim_embed: string;
  sim_char: string;
  id_1: string;
  question_text_1: string;
  company_1: string;
  date_1: string;
  id_2: string;
  question_text_2: string;
  company_2: string;
  date_2: string;
};

export type HeatmapResponse = {
  companies: string[];
  topics: string[];
  values: number[][];
};

export type QuestionFrequencyRow = {
  question_text: string;
  total_count: number;
  companies: { company: string; count: number }[];
};

export type CompanyQuestionsRow = {
  company: string;
  total_questions: number;
  items: { question_text: string; count: number }[];
};

export const AnalyticsAPI = {
  getTopics: (limit = 100) =>
    apiInstance
      .get<TopicRow[]>(`/api/v2/analytics/topics`, { params: { limit } })
      .then((r) => r.data),
  getCompanyProfiles: (company?: string, top = 10) =>
    apiInstance
      .get<
        CompanyProfileRow[]
      >(`/api/v2/analytics/company-profiles`, { params: { company, top } })
      .then((r) => r.data),
  getTrends: () =>
    apiInstance.get<TrendRow[]>(`/api/v2/analytics/trends`).then((r) => r.data),
  getCooccurrence: (limit = 500) =>
    apiInstance
      .get<
        CooccurrenceRow[]
      >(`/api/v2/analytics/cooccurrence`, { params: { limit } })
      .then((r) => r.data),
  getDuplicates: (limit = 500) =>
    apiInstance
      .get<
        DuplicateRow[]
      >(`/api/v2/analytics/duplicates`, { params: { limit } })
      .then((r) => r.data),
  getHeatmap: (normalization: 'none' | 'row' | 'col' = 'row') =>
    apiInstance
      .get<HeatmapResponse>(`/api/v2/analytics/heatmap`, {
        params: { normalization },
      })
      .then((r) => r.data),
  // New endpoints
  getQuestionsFrequencies: (
    params: {
      min_count?: number;
      limit?: number;
      question_contains?: string;
    } = {}
  ) =>
    apiInstance
      .get<
        QuestionFrequencyRow[]
      >(`/api/v2/analytics/questions-frequencies`, { params })
      .then((r) => r.data),
  getTopQuestions: (params: { limit?: number; min_count?: number } = {}) =>
    apiInstance
      .get<
        QuestionFrequencyRow[]
      >(`/api/v2/analytics/top-questions`, { params })
      .then((r) => r.data),
  getCompaniesQuestions: (
    params: {
      company?: string;
      min_count?: number;
      limit_per_company?: number;
    } = {}
  ) =>
    apiInstance
      .get<
        CompanyQuestionsRow[]
      >(`/api/v2/analytics/companies-questions`, { params })
      .then((r) => r.data),
};
