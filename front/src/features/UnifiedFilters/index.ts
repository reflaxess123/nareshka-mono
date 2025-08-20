export { UnifiedFilters } from './ui/UnifiedFilters';
export { FilterSection } from './ui/FilterSection';
export { CompanyFilter } from './ui/CompanyFilter';
export { AdditionalFilter } from './ui/AdditionalFilter';
export { ActiveFilterTags } from './ui/ActiveFilterTags';

export type {
  UnifiedFilterState,
  UnifiedFiltersProps,
  FilterSectionProps,
  CompanyFilterProps,
  AdditionalFilterProps,
  ActiveFilterTag,
  FilterType,
} from './model/types';

export {
  createEmptyFilters,
  hasActiveFilters,
  generateFilterTags,
  removeFilterTag,
  adaptToInterviewFilters,
  adaptFromInterviewFilters,
  debounce,
} from './model/utils';