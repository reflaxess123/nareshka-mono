import React from 'react';
import type { AdditionalFilterProps } from '../model/types';
import styles from './AdditionalFilter.module.scss';

export const AdditionalFilter: React.FC<AdditionalFilterProps> = ({
  hasAudio,
  onHasAudioChange,
}) => {
  return (
    <div className={styles.additionalFilter}>
      <div className={styles.filterGroup}>
        <label className={styles.checkboxLabel}>
          <input
            type="checkbox"
            checked={hasAudio || false}
            onChange={(e) => onHasAudioChange(e.target.checked)}
            className={styles.checkbox}
          />
          <span className={styles.labelText}>
            <span className={styles.icon}>🎵</span>
            Только с аудио/видео записью
          </span>
        </label>
      </div>
    </div>
  );
};