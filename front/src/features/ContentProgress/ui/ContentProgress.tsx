import {
  ButtonSize,
  ButtonVariant,
} from '@/shared/components/Button/model/types';
import { Button } from '@/shared/components/Button/ui/Button';
import { useRole } from '@/shared/hooks';
import { useUpdateProgress } from '@/shared/hooks/useContentBlocks';
import { Check, LogIn, Minus, Plus, X } from 'lucide-react';
import styles from './ContentProgress.module.scss';

interface ContentProgressProps {
  blockId: string;
  currentCount: number;
  className?: string;
  variant?: 'default' | 'compact' | 'detailed';
}

export const ContentProgress = ({
  blockId,
  currentCount,
  className,
  variant = 'default',
}: ContentProgressProps) => {
  const updateProgressMutation = useUpdateProgress();
  const { isGuest } = useRole();

  const handleIncrement = async () => {
    if (updateProgressMutation.isPending) return;

    try {
      await updateProgressMutation.mutateAsync({
        blockId,
        action: 'increment',
      });
    } catch (error) {
      console.error('Ошибка увеличения прогресса:', error);
    }
  };

  const handleDecrement = async () => {
    if (updateProgressMutation.isPending || currentCount <= 0) return;

    try {
      await updateProgressMutation.mutateAsync({
        blockId,
        action: 'decrement',
      });
    } catch (error) {
      console.error('Ошибка уменьшения прогресса:', error);
    }
  };

  // Для гостей показываем приглашение к авторизации
  if (isGuest) {
    if (variant === 'compact') {
      return (
        <div
          className={`${styles.contentProgress} ${styles.guestCompact} ${className || ''}`}
        >
          <div className={styles.guestButton}>
            <LogIn size={16} />
          </div>
        </div>
      );
    }

    if (variant === 'detailed') {
      return (
        <div
          className={`${styles.contentProgress} ${styles.guestDetailed} ${className || ''}`}
        >
          <div className={styles.guestInfo}>
            <span className={styles.guestText}>
              Войдите для отслеживания прогресса
            </span>
          </div>
        </div>
      );
    }

    // Default variant для гостей
    return (
      <div
        className={`${styles.contentProgress} ${styles.guestDefault} ${className || ''}`}
      >
        <Button
          size={ButtonSize.SM}
          variant={ButtonVariant.GHOST}
          leftIcon={<LogIn size={16} />}
        >
          Войти для прогресса
        </Button>
      </div>
    );
  }

  if (variant === 'compact') {
    return (
      <div
        className={`${styles.contentProgress} ${styles.compact} ${className || ''}`}
      >
        <button
          onClick={handleIncrement}
          disabled={updateProgressMutation.isPending}
          className={`${styles.compactButton} ${styles.increment}`}
          aria-label="Отметить как решено"
        >
          <Plus size={16} />
        </button>

        {currentCount > 0 && (
          <>
            <span className={styles.count}>{currentCount}</span>
            <button
              onClick={handleDecrement}
              disabled={updateProgressMutation.isPending}
              className={`${styles.compactButton} ${styles.decrement}`}
              aria-label="Убрать отметку"
            >
              <Minus size={16} />
            </button>
          </>
        )}
      </div>
    );
  }

  if (variant === 'detailed') {
    return (
      <div
        className={`${styles.contentProgress} ${styles.detailed} ${className || ''}`}
      >
        <div className={styles.progressInfo}>
          <span className={styles.label}>Решений:</span>
          <span className={styles.count}>{currentCount}</span>
        </div>

        <div className={styles.actions}>
          <Button
            onClick={handleIncrement}
            disabled={updateProgressMutation.isPending}
            size={ButtonSize.SM}
            variant={ButtonVariant.PRIMARY}
            leftIcon={<Check size={16} />}
          >
            Решено
          </Button>

          {currentCount > 0 && (
            <Button
              onClick={handleDecrement}
              disabled={updateProgressMutation.isPending}
              size={ButtonSize.SM}
              variant={ButtonVariant.GHOST}
              leftIcon={<X size={16} />}
            >
              Отменить
            </Button>
          )}
        </div>
      </div>
    );
  }

  // Default variant
  return (
    <div
      className={`${styles.contentProgress} ${styles.default} ${className || ''}`}
    >
      <Button
        onClick={handleIncrement}
        disabled={updateProgressMutation.isPending}
        size={ButtonSize.SM}
        variant={
          currentCount > 0 ? ButtonVariant.SECONDARY : ButtonVariant.PRIMARY
        }
        leftIcon={<Check size={16} />}
      >
        {currentCount > 0 ? `Решено (${currentCount})` : 'Решено'}
      </Button>

      {currentCount > 0 && (
        <Button
          onClick={handleDecrement}
          disabled={updateProgressMutation.isPending}
          size={ButtonSize.SM}
          variant={ButtonVariant.GHOST}
          leftIcon={<X size={16} />}
        >
          Отменить
        </Button>
      )}
    </div>
  );
};
