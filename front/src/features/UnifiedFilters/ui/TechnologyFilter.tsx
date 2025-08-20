import React, { useState, useMemo } from 'react';
import { Search } from 'lucide-react';
import styles from './TechnologyFilter.module.scss';

interface TechnologyFilterProps {
  technologies: string[];
  selectedTechnologies: string[];
  onSelectionChange: (technologies: string[]) => void;
  isLoading?: boolean;
}

// Популярные технологии для интервью
const POPULAR_TECHNOLOGIES = [
  'JavaScript', 'TypeScript', 'React', 'Vue.js', 'Angular',
  'Node.js', 'Python', 'Java', 'PHP', 'C#',
  'HTML', 'CSS', 'SCSS', 'Git', 'Docker',
  'MongoDB', 'PostgreSQL', 'Redis', 'GraphQL', 'REST API'
];

export const TechnologyFilter: React.FC<TechnologyFilterProps> = ({
  technologies,
  selectedTechnologies,
  onSelectionChange,
  isLoading = false,
}) => {
  const [searchTerm, setSearchTerm] = useState('');

  // Объединяем популярные технологии с теми, что пришли с сервера
  const allTechnologies = useMemo(() => {
    const techSet = new Set([...POPULAR_TECHNOLOGIES, ...technologies]);
    return Array.from(techSet).sort();
  }, [technologies]);

  const filteredTechnologies = useMemo(() => {
    if (!searchTerm) return allTechnologies;
    return allTechnologies.filter(tech =>
      tech.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [allTechnologies, searchTerm]);

  const handleTechnologyToggle = (technology: string, checked: boolean) => {
    const newSelected = checked
      ? [...selectedTechnologies, technology]
      : selectedTechnologies.filter(name => name !== technology);
    
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
    <div className={styles.technologyFilter}>
      {/* Поиск */}
      <div className={styles.searchInputWrapper}>
        <Search size={16} className={styles.searchIcon} />
        <input
          type="text"
          placeholder="Поиск технологий..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className={styles.searchInput}
        />
      </div>

      {/* Список технологий */}
      <div className={styles.checkboxGroup}>
        {filteredTechnologies.length === 0 && searchTerm ? (
          <div className={styles.noResults}>
            Технологии не найдены
          </div>
        ) : (
          filteredTechnologies.map(technology => {
            const isChecked = selectedTechnologies.includes(technology);
            const isPopular = POPULAR_TECHNOLOGIES.includes(technology);
            
            return (
              <label 
                key={technology} 
                className={`${styles.checkboxLabel} ${isPopular ? styles.popular : ''}`}
              >
                <input
                  type="checkbox"
                  checked={isChecked}
                  onChange={(e) => handleTechnologyToggle(technology, e.target.checked)}
                  className={styles.checkbox}
                />
                <span className={styles.labelText}>
                  {isPopular && <span className={styles.popularBadge}>🔥</span>}
                  {technology}
                </span>
              </label>
            );
          })
        )}
      </div>

      {/* Информация о выбранных */}
      {selectedTechnologies.length > 0 && (
        <div className={styles.selectedInfo}>
          Выбрано: {selectedTechnologies.length}
        </div>
      )}
    </div>
  );
};