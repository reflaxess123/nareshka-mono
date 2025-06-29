import { useTechnologies } from '@/hooks/useTechnologies';
import type { TechnologyType } from '@/types/mindmap';
import React from 'react';
import styles from './TechnologySwitcher.module.scss';

interface TechnologySwitcherProps {
  currentTechnology: TechnologyType;
  onTechnologyChange: (technology: TechnologyType) => void;
  className?: string;
}

export const TechnologySwitcher: React.FC<TechnologySwitcherProps> = ({
  currentTechnology,
  onTechnologyChange,
  className = '',
}) => {
  const { data: technologiesData, isLoading } = useTechnologies();

  if (isLoading || !technologiesData?.success) {
    return (
      <div className={`${styles.switcher} ${className}`}>
        <div className={styles.loading}>Загрузка...</div>
      </div>
    );
  }

  const { technologies, configs } = technologiesData.data;

  return (
    <div className={`${styles.switcher} ${className}`}>
      <div className={styles.switcherContainer}>
        {technologies.map((tech) => {
          const config = configs[tech];
          const isActive = currentTechnology === tech;

          return (
            <button
              key={tech}
              className={`${styles.switcherButton} ${isActive ? styles.active : ''}`}
              onClick={() => onTechnologyChange(tech)}
              style={
                {
                  '--tech-color': config.color,
                } as React.CSSProperties
              }
              title={config.description}
            >
              <span
                className={styles.switcherIcon}
                role="img"
                aria-label={config.title}
              >
                {config.icon}
              </span>
              <span className={styles.switcherLabel}>{config.title}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
};
