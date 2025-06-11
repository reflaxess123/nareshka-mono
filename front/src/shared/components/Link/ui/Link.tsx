import { clsx } from 'clsx';
import { useNavigate } from 'react-router-dom';
import styles from './Link.module.scss';

type LinkProps = {
  text: string;
  className?: string;
  icon?: React.ReactNode;
  hoverExpand?: boolean;
  isParentHovered?: boolean;
  to?: string;
  onClick?: () => void;
  size?: 'small' | 'medium' | 'large';
  variant?: 'default' | 'sidebar';
};

export const Link = ({
  text,
  className,
  icon,
  hoverExpand,
  isParentHovered,
  to,
  onClick,
  size = 'medium',
  variant = 'default',
}: LinkProps) => {
  const navigate = useNavigate();

  return (
    <div
      className={clsx(styles.link, className, {
        [styles.hoverExpand]: hoverExpand,
        [styles.sidebar]: variant === 'sidebar',
      })}
      onClick={() => {
        if (onClick) {
          onClick();
        } else {
          navigate(to ?? '');
        }
      }}
    >
      {icon && <div className={styles.icon}>{icon}</div>}
      {text && (
        <div
          className={clsx(styles.text, {
            [styles.parentHoveredText]: isParentHovered,
            [styles.small]: size === 'small',
            [styles.medium]: size === 'medium',
            [styles.large]: size === 'large',
          })}
        >
          {text}
        </div>
      )}
    </div>
  );
};
