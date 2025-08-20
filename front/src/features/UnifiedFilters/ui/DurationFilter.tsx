import React, { useState, useEffect } from 'react';
import { Clock } from 'lucide-react';
import styles from './DurationFilter.module.scss';

interface DurationFilterProps {
  selectedDuration: { min?: number; max?: number; };
  onSelectionChange: (duration: { min?: number; max?: number; }) => void;
}

// Предустановленные диапазоны на основе данных из базы
const DURATION_PRESETS = [
  { label: 'До 30 мин', min: 0, max: 30 },
  { label: '30-60 мин', min: 30, max: 60 },
  { label: '1-2 часа', min: 60, max: 120 },
  { label: 'Больше 2 часов', min: 120, max: undefined },
];

export const DurationFilter: React.FC<DurationFilterProps> = ({
  selectedDuration,
  onSelectionChange,
}) => {
  const [customMode, setCustomMode] = useState(false);
  const [minValue, setMinValue] = useState(selectedDuration.min?.toString() || '');
  const [maxValue, setMaxValue] = useState(selectedDuration.max?.toString() || '');

  useEffect(() => {
    setMinValue(selectedDuration.min?.toString() || '');
    setMaxValue(selectedDuration.max?.toString() || '');
  }, [selectedDuration]);

  const handlePresetClick = (preset: typeof DURATION_PRESETS[0]) => {
    const duration = { min: preset.min, max: preset.max };
    onSelectionChange(duration);
    setCustomMode(false);
  };

  const handleCustomApply = () => {
    const min = minValue ? parseInt(minValue, 10) : undefined;
    const max = maxValue ? parseInt(maxValue, 10) : undefined;
    
    if (min !== undefined && max !== undefined && min > max) {
      return; // Не применяем если min > max
    }
    
    onSelectionChange({ min, max });
  };

  const handleClear = () => {
    onSelectionChange({});
    setMinValue('');
    setMaxValue('');
    setCustomMode(false);
  };

  const isPresetActive = (preset: typeof DURATION_PRESETS[0]) => {
    return selectedDuration.min === preset.min && selectedDuration.max === preset.max;
  };

  const hasActiveFilter = selectedDuration.min !== undefined || selectedDuration.max !== undefined;

  return (
    <div className={styles.durationFilter}>
      {/* Предустановленные диапазоны */}
      <div className={styles.presetGroup}>
        {DURATION_PRESETS.map((preset, index) => (
          <button
            key={index}
            className={`${styles.presetButton} ${isPresetActive(preset) ? styles.active : ''}`}
            onClick={() => handlePresetClick(preset)}
          >
            <Clock size={14} className={styles.icon} />
            {preset.label}
          </button>
        ))}
      </div>

      {/* Кастомный диапазон */}
      <div className={styles.customSection}>
        <button
          className={`${styles.customToggle} ${customMode ? styles.active : ''}`}
          onClick={() => setCustomMode(!customMode)}
        >
          Кастомный диапазон
        </button>

        {customMode && (
          <div className={styles.customInputs}>
            <div className={styles.inputGroup}>
              <label className={styles.inputLabel}>От (мин)</label>
              <input
                type="number"
                min="0"
                max="300"
                value={minValue}
                onChange={(e) => setMinValue(e.target.value)}
                className={styles.durationInput}
                placeholder="0"
              />
            </div>
            
            <div className={styles.inputGroup}>
              <label className={styles.inputLabel}>До (мин)</label>
              <input
                type="number"
                min="0"
                max="300"
                value={maxValue}
                onChange={(e) => setMaxValue(e.target.value)}
                className={styles.durationInput}
                placeholder="∞"
              />
            </div>
            
            <button
              onClick={handleCustomApply}
              className={styles.applyButton}
              disabled={!minValue && !maxValue}
            >
              Применить
            </button>
          </div>
        )}
      </div>

      {/* Очистить фильтр */}
      {hasActiveFilter && (
        <button onClick={handleClear} className={styles.clearButton}>
          Очистить
        </button>
      )}

      {/* Информация о текущем фильтре */}
      {hasActiveFilter && (
        <div className={styles.currentFilter}>
          <Clock size={12} className={styles.icon} />
          {selectedDuration.min !== undefined && selectedDuration.max !== undefined
            ? `${selectedDuration.min}-${selectedDuration.max} мин`
            : selectedDuration.min !== undefined
            ? `От ${selectedDuration.min} мин`
            : `До ${selectedDuration.max} мин`}
        </div>
      )}
    </div>
  );
};