import {
  selectContentBlocksFilters,
  setFilters,
  type ContentBlocksFilters,
} from '@/entities/ContentBlock';
import { ButtonVariant } from '@/shared/components/Button/model/types';
import { Button } from '@/shared/components/Button/ui/Button';
import { Modal } from '@/shared/components/Modal';
import { SubscriptionPrompt } from '@/shared/components/SubscriptionPrompt';
import {
  translateMainCategory,
  translateSubCategory,
} from '@/shared/constants/categoryTranslations';
import { useAppDispatch, useAppSelector } from '@/shared/hooks/redux';
import {
  useCompanies,
  useContentCategories,
} from '@/shared/hooks/useContentBlocks';
import { useRole } from '@/shared/hooks/useRole';
import { ChevronDown, ChevronUp, X } from 'lucide-react';
import { useCallback, useEffect, useState } from 'react';
import styles from './ContentFilters.module.scss';

interface Category {
  name: string;
  subCategories: string[];
  totalCount: number;
  contentBlockCount: number;
  theoryQuizCount: number;
}

interface ContentFiltersProps {
  onFiltersChange?: (filters: ContentBlocksFilters) => void;
  className?: string;
}

export const ContentFilters = ({
  onFiltersChange,
  className,
}: ContentFiltersProps) => {
  const dispatch = useAppDispatch();
  const filters = useAppSelector(selectContentBlocksFilters);
  const { data: categories } = useContentCategories();
  const { canUseFilters } = useRole();

  const [showSubscriptionModal, setShowSubscriptionModal] = useState(false);

  const [expandedSections, setExpandedSections] = useState({
    topics: true,
    companies: true,
    importance: true,
    progress: true,
  });

  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const checkScreenSize = () => {
      setIsMobile(window.innerWidth <= 768);
    };

    checkScreenSize();
    window.addEventListener('resize', checkScreenSize);

    return () => window.removeEventListener('resize', checkScreenSize);
  }, []);

  useEffect(() => {
    if (isMobile) {
      setExpandedSections((prev) => ({
        ...prev,
        companies: false,
        importance: false,
      }));
    } else {
      setExpandedSections({
        topics: true,
        companies: true,
        importance: true,
        progress: true,
      });
    }
  }, [isMobile]);

  const { data: companies } = useCompanies({
    mainCategories: filters.mainCategories,
    subCategories: filters.subCategories,
  });

  const handleMainCategoryToggle = useCallback(
    (categoryName: string, checked: boolean) => {
      const currentCategories = filters.mainCategories || [];

      let newCategories: string[];
      if (checked) {
        newCategories = [...currentCategories, categoryName];
      } else {
        newCategories = currentCategories.filter((cat) => cat !== categoryName);
      }

      const newFilters = {
        ...filters,
        mainCategories: newCategories.length > 0 ? newCategories : undefined,
        subCategories: undefined,
        page: 1,
      };

      dispatch(setFilters(newFilters));
      onFiltersChange?.(newFilters);
    },
    [dispatch, filters, onFiltersChange]
  );

  const handleSubCategoryToggle = useCallback(
    (subCategoryName: string, checked: boolean) => {
      const currentSubCategories = filters.subCategories || [];

      let newSubCategories: string[];
      if (checked) {
        newSubCategories = [...currentSubCategories, subCategoryName];
      } else {
        newSubCategories = currentSubCategories.filter(
          (cat) => cat !== subCategoryName
        );
      }

      const newFilters = {
        ...filters,
        subCategories:
          newSubCategories.length > 0 ? newSubCategories : undefined,
        page: 1,
      };

      dispatch(setFilters(newFilters));
      onFiltersChange?.(newFilters);
    },
    [dispatch, filters, onFiltersChange]
  );

  const handleCompanyToggle = useCallback(
    (companyName: string, checked: boolean) => {
      if (!canUseFilters) {
        setShowSubscriptionModal(true);
        return;
      }

      const currentCompanies = filters.companies || [];

      let newCompanies: string[];
      if (checked) {
        newCompanies = [...currentCompanies, companyName];
      } else {
        newCompanies = currentCompanies.filter(
          (company) => company !== companyName
        );
      }

      const newFilters = {
        ...filters,
        companies: newCompanies.length > 0 ? newCompanies : undefined,
        page: 1,
      };

      dispatch(setFilters(newFilters));
      onFiltersChange?.(newFilters);
    },
    [dispatch, filters, onFiltersChange, canUseFilters]
  );

  const handleImportanceToggle = useCallback(
    (importance: 'low' | 'medium' | 'high', checked: boolean) => {
      const currentImportance = filters.importance || [];

      let newImportance: ('low' | 'medium' | 'high')[];
      if (checked) {
        newImportance = [...currentImportance, importance];
      } else {
        newImportance = currentImportance.filter((i) => i !== importance);
      }

      const newFilters = {
        ...filters,
        importance: newImportance.length > 0 ? newImportance : undefined,
        page: 1,
      };

      dispatch(setFilters(newFilters));
      onFiltersChange?.(newFilters);
    },
    [dispatch, filters, onFiltersChange]
  );

  const handleProgressToggle = useCallback(
    (progress: 'completed' | 'not_completed', checked: boolean) => {
      const currentProgress = filters.progress || [];

      let newProgress: ('completed' | 'not_completed')[];
      if (checked) {
        newProgress = [...currentProgress, progress];
      } else {
        newProgress = currentProgress.filter((p) => p !== progress);
      }

      const newFilters = {
        ...filters,
        progress: newProgress.length > 0 ? newProgress : undefined,
        page: 1,
      };

      dispatch(setFilters(newFilters));
      onFiltersChange?.(newFilters);
    },
    [dispatch, filters, onFiltersChange]
  );

  const handleReset = useCallback(() => {
    const resetFilters: ContentBlocksFilters = {
      page: 1,
      limit: 20,
      sortBy: 'orderInFile' as const,
      sortOrder: 'asc' as const,
      q: undefined,
      mainCategories: undefined,
      subCategories: undefined,
      onlyUnsolved: undefined,
      companies: undefined,
      importance: undefined,
      progress: undefined,
    };
    dispatch(setFilters(resetFilters));
    onFiltersChange?.(resetFilters);
  }, [dispatch, onFiltersChange]);

  const hasActiveFilters = () => {
    return !!(
      filters.q ||
      filters.onlyUnsolved ||
      filters.mainCategories?.length ||
      filters.subCategories?.length ||
      filters.companies?.length ||
      filters.importance?.length ||
      filters.progress?.length
    );
  };

  const toggleSection = (section: keyof typeof expandedSections) => {
    setExpandedSections((prev) => ({
      ...prev,
      [section]: !prev[section],
    }));
  };

  const getAvailableSubCategories = () => {
    if (!filters.mainCategories?.length || !categories?.categories) return [];

    const allSubCategories = new Set<string>();
    filters.mainCategories.forEach((mainCategory) => {
      const category = categories.categories.find(
        (cat: Category) => cat.name === mainCategory
      );
      if (category) {
        category.subCategories.forEach((sub: string) =>
          allSubCategories.add(sub)
        );
      }
    });

    return Array.from(allSubCategories);
  };

  return (
    <div className={`${styles.contentFilters} ${className || ''}`}>

      <div className={styles.filterSection}>
        <button
          className={styles.sectionHeader}
          onClick={() => toggleSection('topics')}
        >
          <span>Темы</span>
          {expandedSections.topics ? (
            <ChevronUp size={16} />
          ) : (
            <ChevronDown size={16} />
          )}
        </button>

        {expandedSections.topics && (
          <div className={styles.sectionContent}>
            <div className={styles.filterGroup}>
              <label className={styles.filterLabel}>Основные категории</label>
              <div className={styles.checkboxGroup}>
                {categories?.categories?.map((category: Category) => {
                  const translatedName = translateMainCategory(category.name);
                  const isChecked =
                    filters.mainCategories?.includes(category.name) || false;

                  return (
                    <label key={category.name} className={styles.checkboxLabel}>
                      <input
                        type="checkbox"
                        checked={isChecked}
                        onChange={(e) =>
                          handleMainCategoryToggle(
                            category.name,
                            e.target.checked
                          )
                        }
                      />
                      <span>{translatedName}</span>
                    </label>
                  );
                })}
              </div>
            </div>

            {filters.mainCategories?.length &&
              filters.mainCategories.length > 0 && (
                <div className={styles.filterGroup}>
                  <label className={styles.filterLabel}>Подкатегории</label>
                  <div className={styles.checkboxGroup}>
                    {getAvailableSubCategories().map((subCategory: string) => {
                      const translatedName = translateSubCategory(subCategory);
                      const isChecked =
                        filters.subCategories?.includes(subCategory) || false;

                      return (
                        <label
                          key={subCategory}
                          className={styles.checkboxLabel}
                        >
                          <input
                            type="checkbox"
                            checked={isChecked}
                            onChange={(e) =>
                              handleSubCategoryToggle(
                                subCategory,
                                e.target.checked
                              )
                            }
                          />
                          <span>{translatedName}</span>
                        </label>
                      );
                    })}
                  </div>
                </div>
              )}
          </div>
        )}
      </div>

      <div className={styles.filterSection}>
        <button
          className={styles.sectionHeader}
          onClick={() => toggleSection('companies')}
        >
          <span>Компании</span>
          {expandedSections.companies ? (
            <ChevronUp size={16} />
          ) : (
            <ChevronDown size={16} />
          )}
        </button>

        {expandedSections.companies && (
          <div className={styles.sectionContent}>
            <div className={styles.checkboxGroup}>
              {companies?.companies?.map(
                (company: { name: string; count: number }) => {
                  const isChecked =
                    filters.companies?.includes(company.name) || false;

                  return (
                    <label key={company.name} className={styles.checkboxLabel}>
                      <input
                        type="checkbox"
                        checked={isChecked}
                        onChange={(e) =>
                          handleCompanyToggle(company.name, e.target.checked)
                        }
                      />
                      <span>
                        {company.name} ({company.count})
                      </span>
                    </label>
                  );
                }
              )}
            </div>
          </div>
        )}
      </div>

      <div className={styles.filterSection}>
        <button
          className={styles.sectionHeader}
          onClick={() => toggleSection('importance')}
        >
          <span>Важность</span>
          {expandedSections.importance ? (
            <ChevronUp size={16} />
          ) : (
            <ChevronDown size={16} />
          )}
        </button>

        {expandedSections.importance && (
          <div className={styles.sectionContent}>
            <div className={styles.checkboxGroupHorizontal}>
              <label className={styles.checkboxLabel}>
                <input
                  type="checkbox"
                  checked={filters.importance?.includes('high') || false}
                  onChange={(e) =>
                    handleImportanceToggle('high', e.target.checked)
                  }
                />
                <span>Высокая</span>
              </label>
              <label className={styles.checkboxLabel}>
                <input
                  type="checkbox"
                  checked={filters.importance?.includes('medium') || false}
                  onChange={(e) =>
                    handleImportanceToggle('medium', e.target.checked)
                  }
                />
                <span>Средняя</span>
              </label>
              <label className={styles.checkboxLabel}>
                <input
                  type="checkbox"
                  checked={filters.importance?.includes('low') || false}
                  onChange={(e) =>
                    handleImportanceToggle('low', e.target.checked)
                  }
                />
                <span>Низкая</span>
              </label>
            </div>
          </div>
        )}
      </div>

      <div className={styles.filterSection}>
        <button
          className={styles.sectionHeader}
          onClick={() => toggleSection('progress')}
        >
          <span>Прогресс</span>
          {expandedSections.progress ? (
            <ChevronUp size={16} />
          ) : (
            <ChevronDown size={16} />
          )}
        </button>

        {expandedSections.progress && (
          <div className={styles.sectionContent}>
            <div className={styles.checkboxGroupHorizontal}>
              <label className={styles.checkboxLabel}>
                <input
                  type="checkbox"
                  checked={filters.progress?.includes('completed') || false}
                  onChange={(e) =>
                    handleProgressToggle('completed', e.target.checked)
                  }
                />
                <span>Решенные</span>
              </label>
              <label className={styles.checkboxLabel}>
                <input
                  type="checkbox"
                  checked={filters.progress?.includes('not_completed') || false}
                  onChange={(e) =>
                    handleProgressToggle('not_completed', e.target.checked)
                  }
                />
                <span>Нерешенные</span>
              </label>
            </div>
          </div>
        )}
      </div>

      <Modal
        isOpen={showSubscriptionModal}
        onClose={() => setShowSubscriptionModal(false)}
        closeOnOverlay={true}
        closeOnEsc={true}
      >
        <SubscriptionPrompt
          feature="Фильтр по компаниям"
          description="Фильтрация задач по компаниям доступна только пользователям с подпиской Нарешка+ или администраторам"
        />
      </Modal>
    </div>
  );
};
