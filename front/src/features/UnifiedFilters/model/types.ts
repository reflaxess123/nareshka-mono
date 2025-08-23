export interface UnifiedFilterState {
  search?: string;
  companies?: string[];
  has_audio?: boolean;
  categories?: string[];
  subCategories?: string[];
  clusters?: number[];
  // Дополнительные фильтры для интервью
  difficulty?: ('easy' | 'medium' | 'hard')[];
  duration?: {
    min?: number;
    max?: number;
  };
  seniority?: ('junior' | 'middle' | 'senior' | 'lead')[];
  interview_format?: ('online' | 'offline' | 'hybrid')[];
  technologies?: string[];
  // Фильтры для practice и theory
  onlyCompleted?: boolean;
  onlyUnstudied?: boolean;
}

export interface FilterSectionProps {
  title: string;
  icon?: string;
  isExpanded: boolean;
  onToggle: () => void;
  children: React.ReactNode;
  className?: string;
}

export interface UnifiedFiltersProps {
  type: 'interviews' | 'questions' | 'practice' | 'theory';
  filters: UnifiedFilterState;
  onFiltersChange: (filters: UnifiedFilterState) => void;
  resultsCount?: number;
  className?: string;
}

export interface CompanyFilterProps {
  companies: { name: string; count: number }[];
  selectedCompanies: string[];
  onSelectionChange: (companies: string[]) => void;
  isLoading?: boolean;
}

export interface AdditionalFilterProps {
  hasAudio?: boolean;
  onHasAudioChange: (value: boolean) => void;
}

export interface ActiveFilterTag {
  type: 'search' | 'company' | 'audio' | 'category' | 'cluster';
  label: string;
  value: string | number;
}

export type FilterType = 'interviews' | 'questions' | 'practice' | 'theory';