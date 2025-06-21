import {
  selectContentBlocksFilters,
  setFilters,
} from '@/entities/ContentBlock';
import {
  InfiniteTheoryCards,
  selectTheoryFilters,
  setFilters as setTheoryFilters,
  TheoryFiltersComponent,
  type TheoryFilters,
} from '@/entities/TheoryCard';
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
import { useCallback, useEffect, useState } from 'react';
import styles from './Tasks.module.scss';

type ActiveTab = 'practice' | 'theory';

const Tasks = () => {
  const { user } = useAuth();
  const { isGuest } = useRole();
  const dispatch = useAppDispatch();

  // Состояние для активного таба
  const [activeTab, setActiveTab] = useState<ActiveTab>('practice');

  // Фильтры для задач
  const contentFilters = useAppSelector(selectContentBlocksFilters);

  // Фильтры для теории
  const theoryFilters = useAppSelector(selectTheoryFilters);

  useContentCategories();

  useEffect(() => {
    if (!user) {
      console.warn('Пользователь не авторизован');
    }
  }, [user]);

  // Обработчики для задач
  const handleSearchChange = useCallback(
    (value: string) => {
      const newFilters = {
        ...contentFilters,
        q: value || undefined,
        page: 1, // Сбрасываем страницу при поиске
      };
      dispatch(setFilters(newFilters));
    },
    [dispatch, contentFilters]
  );

  const handleSortChange = useCallback(
    (sortBy: string) => {
      const newFilters = {
        ...contentFilters,
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
    [dispatch, contentFilters]
  );

  // Обработчики для теории
  const handleTheoryFiltersChange = useCallback(
    (newFilters: TheoryFilters) => {
      dispatch(setTheoryFilters(newFilters));
    },
    [dispatch]
  );

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Поиск уже применяется при onChange
  };

  const handleTabChange = (tab: ActiveTab) => {
    setActiveTab(tab);
  };

  return (
    <PageWrapper>
      <div className={styles.tasks}>
        <header className={styles.header}>
          <Text
            text={
              activeTab === 'practice'
                ? 'Задачи и упражнения'
                : 'Теория программирования'
            }
            size={TextSize.XXL}
            weight={TextWeight.MEDIUM}
            align={TextAlign.CENTER}
          />
          <Text
            text={
              activeTab === 'practice'
                ? 'Самая большая база вопросов для подготовки к собеседованиям'
                : 'Изучайте теорию с помощью интерактивных карточек'
            }
            size={TextSize.MD}
            align={TextAlign.CENTER}
            className={styles.subtitle}
          />

          {isGuest && (
            <div className={styles.guestNotice}>
              <LogIn size={20} />
              <Text
                text={`Авторизуйтесь, чтобы отслеживать прогресс ${
                  activeTab === 'practice' ? 'решения задач' : 'изучения теории'
                }`}
                size={TextSize.MD}
                align={TextAlign.CENTER}
              />
            </div>
          )}
        </header>

        {/* Поиск только для задач */}
        {activeTab === 'practice' && (
          <div className={styles.searchSection}>
            <form onSubmit={handleSearchSubmit} className={styles.searchForm}>
              <div className={styles.searchContainer}>
                <Search size={20} className={styles.searchIcon} />
                <input
                  type="text"
                  placeholder="Поиск задач"
                  value={contentFilters.q || ''}
                  onChange={(e) => handleSearchChange(e.target.value)}
                  className={styles.searchInput}
                />
              </div>
            </form>

            <div className={styles.sortContainer}>
              <label htmlFor="sort-select">Сортировка</label>
              <select
                id="sort-select"
                value={contentFilters.sortBy || 'orderInFile'}
                onChange={(e) => handleSortChange(e.target.value)}
                className={styles.sortSelect}
              >
                <option value="orderInFile">По порядку в файле</option>
                <option value="createdAt">По дате создания</option>
                <option value="updatedAt">По дате обновления</option>
                <option value="file.webdavPath">По пути файла</option>
              </select>
            </div>
          </div>
        )}

        <div className={styles.secondRow}>
          <div className={styles.tabsContainer}>
            <button
              className={`${styles.tabButton} ${
                activeTab === 'practice' ? styles.active : ''
              }`}
              onClick={() => handleTabChange('practice')}
            >
              Практика задач
            </button>
            <button
              className={`${styles.tabButton} ${
                activeTab === 'theory' ? styles.active : ''
              }`}
              onClick={() => handleTabChange('theory')}
            >
              Теория
            </button>
          </div>
        </div>

        {/* Фильтры для теории */}
        {activeTab === 'theory' && (
          <div className={styles.theoryFiltersSection}>
            <TheoryFiltersComponent
              filters={theoryFilters}
              onFiltersChange={handleTheoryFiltersChange}
            />
          </div>
        )}

        <div
          className={`${styles.mainContent} ${activeTab === 'theory' ? styles.fullWidth : ''}`}
        >
          <div className={styles.questionsSection}>
            {activeTab === 'practice' ? (
              <ContentBlocksList
                variant="default"
                className={styles.blocksList}
              />
            ) : (
              <InfiniteTheoryCards filters={theoryFilters} />
            )}
          </div>

          {activeTab === 'practice' && (
            <aside className={styles.filtersSection}>
              <div className={styles.filtersContainer}>
                <h3 className={styles.filtersTitle}>Фильтры</h3>
                <ContentFilters className={styles.filters} />
              </div>
            </aside>
          )}
        </div>
      </div>
    </PageWrapper>
  );
};

export default Tasks;
