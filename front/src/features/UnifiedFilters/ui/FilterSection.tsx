import React from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';
import type { FilterSectionProps } from '../model/types';
import styles from './FilterSection.module.scss';

export const FilterSection: React.FC<FilterSectionProps> = ({
  title,
  icon,
  isExpanded,
  onToggle,
  children,
  className,
}) => {
  return (
    <div className={`${styles.filterSection} ${className || ''}`}>
      <button
        className={styles.sectionHeader}
        onClick={onToggle}
        aria-expanded={isExpanded}
      >
        <span className={styles.title}>
          {icon && <span className={styles.icon}>{icon}</span>}
          {title}
        </span>
        {isExpanded ? (
          <ChevronUp size={16} className={styles.chevron} />
        ) : (
          <ChevronDown size={16} className={styles.chevron} />
        )}
      </button>

      {isExpanded && (
        <div className={styles.sectionContent}>
          {children}
        </div>
      )}
    </div>
  );
};