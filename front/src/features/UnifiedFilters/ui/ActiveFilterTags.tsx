import React from 'react';
import { X } from 'lucide-react';
import type { ActiveFilterTag } from '../model/types';
import styles from './ActiveFilterTags.module.scss';

interface ActiveFilterTagsProps {
  tags: ActiveFilterTag[];
  onRemoveTag: (tag: ActiveFilterTag) => void;
  onClearAll: () => void;
  className?: string;
}

export const ActiveFilterTags: React.FC<ActiveFilterTagsProps> = ({
  tags,
  onRemoveTag,
  onClearAll,
  className,
}) => {
  if (tags.length === 0) {
    return null;
  }

  return (
    <div className={`${styles.activeFilterTags} ${className || ''}`}>
      <div className={styles.tagsContainer}>
        <div className={styles.tags}>
          {tags.map((tag, index) => (
            <span 
              key={`${tag.type}-${tag.value}-${index}`} 
              className={styles.tag}
            >
              <span className={styles.tagLabel}>{tag.label}</span>
              <button
                onClick={() => onRemoveTag(tag)}
                className={styles.removeButton}
                aria-label={`Удалить фильтр ${tag.label}`}
              >
                <X size={12} />
              </button>
            </span>
          ))}
        </div>
        
        <button 
          onClick={onClearAll} 
          className={styles.clearAllButton}
        >
          Очистить всё
        </button>
      </div>
    </div>
  );
};