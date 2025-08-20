import type { UnifiedFilterState, ActiveFilterTag } from './types';

export const createEmptyFilters = (): UnifiedFilterState => ({
  search: undefined,
  companies: undefined,
  has_audio: undefined,
  categories: undefined,
  clusters: undefined,
  difficulty: undefined,
  duration: undefined,
});

export const hasActiveFilters = (filters: UnifiedFilterState): boolean => {
  return !!(
    filters.search ||
    filters.companies?.length ||
    filters.has_audio ||
    filters.categories?.length ||
    filters.clusters?.length ||
    filters.difficulty?.length ||
    filters.duration?.min ||
    filters.duration?.max
  );
};

export const generateFilterTags = (filters: UnifiedFilterState): ActiveFilterTag[] => {
  const tags: ActiveFilterTag[] = [];

  if (filters.search) {
    tags.push({ 
      type: 'search', 
      label: `🔍 "${filters.search}"`, 
      value: filters.search 
    });
  }

  filters.companies?.forEach(company => {
    tags.push({ 
      type: 'company', 
      label: `🏢 ${company}`, 
      value: company 
    });
  });

  if (filters.has_audio) {
    tags.push({ 
      type: 'audio', 
      label: '🎵 С аудио/видео', 
      value: 'has_audio' 
    });
  }

  filters.categories?.forEach(category => {
    tags.push({ 
      type: 'category', 
      label: `📁 ${category}`, 
      value: category 
    });
  });

  filters.clusters?.forEach(cluster => {
    tags.push({ 
      type: 'cluster', 
      label: `🏷️ Кластер ${cluster}`, 
      value: cluster 
    });
  });

  return tags;
};

export const removeFilterTag = (
  filters: UnifiedFilterState, 
  tag: ActiveFilterTag
): UnifiedFilterState => {
  const newFilters = { ...filters };

  switch (tag.type) {
    case 'search':
      newFilters.search = undefined;
      break;
    case 'company':
      newFilters.companies = newFilters.companies?.filter(c => c !== tag.value);
      if (newFilters.companies?.length === 0) {
        newFilters.companies = undefined;
      }
      break;
    case 'audio':
      newFilters.has_audio = undefined;
      break;
    case 'category':
      newFilters.categories = newFilters.categories?.filter(c => c !== tag.value);
      if (newFilters.categories?.length === 0) {
        newFilters.categories = undefined;
      }
      break;
    case 'cluster':
      newFilters.clusters = newFilters.clusters?.filter(c => c !== tag.value);
      if (newFilters.clusters?.length === 0) {
        newFilters.clusters = undefined;
      }
      break;
  }

  return newFilters;
};

// Адаптеры для существующих API
export const adaptToInterviewFilters = (filters: UnifiedFilterState) => ({
  companies: filters.companies,
  search: filters.search,
  has_audio: filters.has_audio,
});

export const adaptFromInterviewFilters = (filters: {
  companies?: string[];
  search?: string;
  has_audio?: boolean;
}): UnifiedFilterState => ({
  companies: filters.companies,
  search: filters.search,
  has_audio: filters.has_audio,
});

export const debounce = <T extends (...args: unknown[]) => unknown>(
  func: T,
  wait: number
): ((...args: Parameters<T>) => void) => {
  let timeout: NodeJS.Timeout;
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
};