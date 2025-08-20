import React from 'react';
import styles from './SourceFilter.module.scss';

interface SourceFilterProps {
  selectedSources: string[];
  onSelectionChange: (sources: string[]) => void;
}

const SOURCE_OPTIONS = [
  { value: 'telegram', label: '📱 Telegram', count: 1060 },
  { value: 'llm_report', label: '🤖 AI отчёты', count: 98 },
];

export const SourceFilter: React.FC<SourceFilterProps> = ({
  selectedSources,
  onSelectionChange,
}) => {
  const handleSourceToggle = (source: string, checked: boolean) => {
    const newSelected = checked
      ? [...selectedSources, source]
      : selectedSources.filter(s => s !== source);
    
    onSelectionChange(newSelected);
  };

  return (
    <div className={styles.sourceFilter}>
      <div className={styles.checkboxGroup}>
        {SOURCE_OPTIONS.map(option => {
          const isChecked = selectedSources.includes(option.value);
          
          return (
            <label key={option.value} className={styles.checkboxLabel}>
              <input
                type="checkbox"
                checked={isChecked}
                onChange={(e) => handleSourceToggle(option.value, e.target.checked)}
                className={styles.checkbox}
              />
              <span className={styles.labelText}>
                {option.label}
                <span className={styles.count}>({option.count})</span>
              </span>
            </label>
          );
        })}
      </div>
    </div>
  );
};