import { Button, ButtonVariant } from '@/shared/components/Button';
import { Crown, Star } from 'lucide-react';
import styles from './SubscriptionPrompt.module.scss';

interface SubscriptionPromptProps {
  feature: string;
  description?: string;
  className?: string;
}

export const SubscriptionPrompt = ({
  feature,
  description = 'Эта функция доступна только пользователям с подпиской Нарешка+',
  className = '',
}: SubscriptionPromptProps) => {
  const handleUpgrade = () => {
    console.log('Переход на страницу подписки');
  };

  return (
    <div className={`${styles.subscriptionPrompt} ${className}`}>
      <div className={styles.iconContainer}>
        <Crown className={styles.crownIcon} size={24} />
        <Star className={styles.starIcon} size={16} />
      </div>

      <div className={styles.content}>
        <h3 className={styles.title}>{feature} доступно в Нарешка+</h3>

        <p className={styles.description}>{description}</p>

        <div className={styles.features}>
          <div className={styles.feature}>
            <Crown size={16} />
            <span>Фильтры по компаниям</span>
          </div>
          <div className={styles.feature}>
            <Crown size={16} />
            <span>Расширенные фильтры</span>
          </div>
          <div className={styles.feature}>
            <Crown size={16} />
            <span>Статистика решений</span>
          </div>
        </div>

        <Button
          onClick={handleUpgrade}
          variant={ButtonVariant.PRIMARY}
          className={styles.upgradeButton}
        >
          <Crown size={16} />
          Получить Нарешка+
        </Button>
      </div>
    </div>
  );
};
