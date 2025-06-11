import {
  InfiniteTheoryCards,
  selectTheoryFilters,
  setFilters,
  TheoryFiltersComponent,
  type TheoryFilters,
} from '@/entities/TheoryCard';
import { PageWrapper } from '@/shared/components/PageWrapper/ui/PageWrapper';
import { useAppDispatch, useAppSelector, useRole } from '@/shared/hooks';
import { LogIn } from 'lucide-react';
import { useCallback } from 'react';
import styles from './Theory.module.scss';

const Theory = () => {
  const dispatch = useAppDispatch();
  const filters = useAppSelector(selectTheoryFilters);
  const { isGuest } = useRole();

  const handleFiltersChange = useCallback(
    (newFilters: TheoryFilters) => {
      dispatch(setFilters(newFilters));
    },
    [dispatch]
  );

  return (
    <PageWrapper>
      <div className={styles.theory}>
        <div className={styles.container}>
          <div className={styles.title}>
            <h1>Теория</h1>

            {/* Уведомление для гостей */}
            {isGuest && (
              <div className={styles.guestNotice}>
                <LogIn size={20} />
                <p>Авторизуйтесь, чтобы отслеживать прогресс изучения теории</p>
              </div>
            )}
          </div>

          <TheoryFiltersComponent
            filters={filters}
            onFiltersChange={handleFiltersChange}
          />

          <InfiniteTheoryCards filters={filters} />
        </div>
      </div>
    </PageWrapper>
  );
};

export default Theory;
