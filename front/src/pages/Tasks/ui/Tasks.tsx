import {
  selectContentBlocksFilters,
  setFilters,
} from '@/entities/ContentBlock';
import { ContentFilters } from '@/features/ContentFilters';
import { PageWrapper } from '@/shared/components/PageWrapper/ui/PageWrapper';
import {
  Text,
  TextAlign,
  TextSize,
  TextWeight,
} from '@/shared/components/Text';
import { useAuth, useRole } from '@/shared/hooks';
import { useAppDispatch, useAppSelector } from '@/shared/hooks/redux';
import { useContentCategories } from '@/shared/hooks/useContentBlocks';
import { ContentBlocksList } from '@/widgets/ContentBlocksList';
import { LogIn, Search } from 'lucide-react';
import { useCallback, useEffect } from 'react';
import styles from './Tasks.module.scss';

const Tasks = () => {
  const { user } = useAuth();
  const { isGuest } = useRole();
  const dispatch = useAppDispatch();
  const filters = useAppSelector(selectContentBlocksFilters);

  useContentCategories();

  useEffect(() => {
    if (!user) {
      console.warn('Пользователь не авторизован');
    }
  }, [user]);

  const handleSearchChange = useCallback(
    (value: string) => {
      const newFilters = {
        ...filters,
        q: value || undefined,
        page: 1, // Сбрасываем страницу при поиске
      };
      dispatch(setFilters(newFilters));
    },
    [dispatch, filters]
  );

  const handleSortChange = useCallback(
    (sortBy: string) => {
      const newFilters = {
        ...filters,
        sortBy: sortBy as
          | 'orderInFile'
          | 'blockLevel'
          | 'createdAt'
          | 'updatedAt'
          | 'file.webdavPath',
        page: 1, // Сбрасываем страницу при изменении сортировки
      };
      dispatch(setFilters(newFilters));
    },
    [dispatch, filters]
  );

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Поиск уже применяется при onChange
  };

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
          <Text
            text="Самая большая база вопросов для подготовки к собеседованиям"
            size={TextSize.MD}
            align={TextAlign.CENTER}
            className={styles.subtitle}
          />

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

        <div className={styles.searchSection}>
          <form onSubmit={handleSearchSubmit} className={styles.searchForm}>
            <div className={styles.searchContainer}>
              <Search size={20} className={styles.searchIcon} />
              <input
                type="text"
                placeholder="Поиск задач"
                value={filters.q || ''}
                onChange={(e) => handleSearchChange(e.target.value)}
                className={styles.searchInput}
              />
            </div>
          </form>

          <div className={styles.sortContainer}>
            <label htmlFor="sort-select">Сортировка</label>
            <select
              id="sort-select"
              value={filters.sortBy || 'orderInFile'}
              onChange={(e) => handleSortChange(e.target.value)}
              className={styles.sortSelect}
            >
              <option value="orderInFile">По порядку</option>
              <option value="blockLevel">По уровню сложности</option>
              <option value="createdAt">По дате создания</option>
              <option value="updatedAt">По дате обновления</option>
              <option value="file.webdavPath">По пути файла</option>
            </select>
          </div>
        </div>

        <div className={styles.secondRow}>
          <div className={styles.tabsContainer}>
            <button className={`${styles.tabButton} ${styles.active}`}>
              Практика задач
            </button>
            <button className={styles.tabButton}>Теория</button>
          </div>
        </div>

        <div className={styles.mainContent}>
          <div className={styles.questionsSection}>
            <ContentBlocksList
              variant="default"
              className={styles.blocksList}
            />
          </div>

          <aside className={styles.filtersSection}>
            <div className={styles.filtersContainer}>
              <h3 className={styles.filtersTitle}>Фильтры</h3>
              <ContentFilters className={styles.filters} />
            </div>
          </aside>
        </div>
      </div>
    </PageWrapper>
  );
};

export default Tasks;
