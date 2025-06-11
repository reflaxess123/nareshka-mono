import { ContentFilters } from '@/features/ContentFilters';
import { PageWrapper } from '@/shared/components/PageWrapper/ui/PageWrapper';
import {
  Text,
  TextAlign,
  TextSize,
  TextWeight,
} from '@/shared/components/Text';
import { useAuth, useRole } from '@/shared/hooks';
import { useContentCategories } from '@/shared/hooks/useContentBlocks';
import { ContentBlocksList } from '@/widgets/ContentBlocksList';
import { LogIn } from 'lucide-react';
import { useEffect } from 'react';
import styles from './Tasks.module.scss';

const Tasks = () => {
  const { user } = useAuth();
  const { isGuest } = useRole();

  // Загружаем категории при монтировании
  useContentCategories();

  useEffect(() => {
    // Проверяем авторизацию пользователя
    if (!user) {
      console.warn('Пользователь не авторизован');
    }
  }, [user]);

  return (
    <PageWrapper>
      <div className={styles.tasks}>
        <header className={styles.header}>
          <Text
            text="Задачи и упражнения"
            size={TextSize.XXL}
            weight={TextWeight.MEDIUM}
            align={TextAlign.CENTER}
          />

          {/* Уведомление для гостей */}
          {isGuest && (
            <div className={styles.guestNotice}>
              <LogIn size={20} />
              <Text
                text="Авторизуйтесь, чтобы отслеживать прогресс решения задач"
                size={TextSize.MD}
                align={TextAlign.CENTER}
              />
            </div>
          )}
        </header>

        <div className={styles.content}>
          {/* Фильтры */}
          <div className={styles.filtersSection}>
            <ContentFilters className={styles.filters} />
          </div>

          {/* Список контент-блоков */}
          <div className={styles.blocksSection}>
            <ContentBlocksList
              variant="default"
              className={styles.blocksList}
            />
          </div>
        </div>
      </div>
    </PageWrapper>
  );
};

export default Tasks;
