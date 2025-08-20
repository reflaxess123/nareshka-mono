import React, { useState, useMemo } from 'react';
import { Search } from 'lucide-react';
import styles from './PositionFilter.module.scss';

interface PositionFilterProps {
  selectedPositions: string[];
  onSelectionChange: (positions: string[]) => void;
  isLoading?: boolean;
}

// Популярные позиции на основе данных из базы
const POPULAR_POSITIONS = [
  'Frontend разработчик',
  'Backend разработчик', 
  'Fullstack разработчик',
  'React разработчик',
  'Vue разработчик',
  'Angular разработчик',
  'Node.js разработчик',
  'JavaScript разработчик',
  'TypeScript разработчик',
  'Senior Frontend разработчик',
  'Middle Frontend разработчик',
  'Junior Frontend разработчик',
];

export const PositionFilter: React.FC<PositionFilterProps> = ({
  selectedPositions,
  onSelectionChange,
  isLoading = false,
}) => {
  const [searchTerm, setSearchTerm] = useState('');

  const filteredPositions = useMemo(() => {
    if (!searchTerm) return POPULAR_POSITIONS;
    return POPULAR_POSITIONS.filter(position =>
      position.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [searchTerm]);

  const handlePositionToggle = (position: string, checked: boolean) => {
    const newSelected = checked
      ? [...selectedPositions, position]
      : selectedPositions.filter(name => name !== position);
    
    onSelectionChange(newSelected);
  };

  if (isLoading) {
    return (
      <div className={styles.loading}>
        <div className={styles.skeleton}></div>
        <div className={styles.skeleton}></div>
        <div className={styles.skeleton}></div>
      </div>
    );
  }

  return (
    <div className={styles.positionFilter}>
      {/* Поиск */}
      <div className={styles.searchInputWrapper}>
        <Search size={16} className={styles.searchIcon} />
        <input
          type="text"
          placeholder="Поиск позиций..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className={styles.searchInput}
        />
      </div>

      {/* Список позиций */}
      <div className={styles.checkboxGroup}>
        {filteredPositions.length === 0 && searchTerm ? (
          <div className={styles.noResults}>
            Позиции не найдены
          </div>
        ) : (
          filteredPositions.map(position => {
            const isChecked = selectedPositions.includes(position);
            
            return (
              <label key={position} className={styles.checkboxLabel}>
                <input
                  type="checkbox"
                  checked={isChecked}
                  onChange={(e) => handlePositionToggle(position, e.target.checked)}
                  className={styles.checkbox}
                />
                <span className={styles.labelText}>
                  {position}
                </span>
              </label>
            );
          })
        )}
      </div>

      {/* Информация о выбранных */}
      {selectedPositions.length > 0 && (
        <div className={styles.selectedInfo}>
          Выбрано: {selectedPositions.length}
        </div>
      )}
    </div>
  );
};