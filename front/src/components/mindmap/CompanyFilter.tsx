import React, { useState, useEffect, useCallback } from 'react';
import styles from './CompanyFilter.module.scss';

interface Company {
  name: string;
  questions_count: number;
}

interface CompanyFilterProps {
  onFilterChange: (selectedCompanies: string[]) => void;
  className?: string;
}

export const CompanyFilter: React.FC<CompanyFilterProps> = ({ 
  onFilterChange, 
  className 
}) => {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [selectedCompanies, setSelectedCompanies] = useState<string[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);

  // Загружаем список компаний
  useEffect(() => {
    const fetchCompanies = async () => {
      setLoading(true);
      try {
        const response = await fetch('/api/v2/interviews/companies/list');
        const data = await response.json();
        
        // API возвращает массив строк, преобразуем в объекты
        const companiesData: Company[] = (data.companies || []).map((name: string) => ({
          name,
          questions_count: 0 // Количество вопросов неизвестно из этого API
        }));
        
        // Сортируем по алфавиту, так как нет данных о количестве вопросов
        const sortedCompanies = companiesData.sort((a, b) => 
          a.name.localeCompare(b.name, 'ru')
        );
        
        setCompanies(sortedCompanies);
      } catch (error) {
        console.error('Error fetching companies:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchCompanies();
  }, []);

  // Фильтруем компании по поисковому запросу
  const filteredCompanies = companies.filter(company =>
    company.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Известные компании для быстрого выбора
  const popularCompanyNames = ['Яндекс', 'Сбер', 'Т-Банк', 'Альфа-Банк', 'Avito'];
  const topCompanies = companies.filter(c => 
    popularCompanyNames.includes(c.name)
  ).slice(0, 5);

  const handleCompanyToggle = useCallback((companyName: string) => {
    setSelectedCompanies(prev => {
      const newSelection = prev.includes(companyName)
        ? prev.filter(c => c !== companyName)
        : [...prev, companyName];
      
      // Вызываем callback с обновленным списком
      onFilterChange(newSelection);
      return newSelection;
    });
  }, [onFilterChange]);

  const handleSelectAll = useCallback(() => {
    if (selectedCompanies.length === companies.length) {
      setSelectedCompanies([]);
      onFilterChange([]);
    } else {
      const allCompanyNames = companies.map(c => c.name);
      setSelectedCompanies(allCompanyNames);
      onFilterChange(allCompanyNames);
    }
  }, [companies, selectedCompanies.length, onFilterChange]);

  const handleClearSelection = useCallback(() => {
    setSelectedCompanies([]);
    onFilterChange([]);
  }, [onFilterChange]);

  return (
    <div className={`${styles.companyFilter} ${className || ''}`}>
      <button 
        className={styles.filterButton}
        onClick={() => setIsOpen(!isOpen)}
      >
        <span className={styles.filterIcon}>🏢</span>
        <span className={styles.filterLabel}>
          Компании
          {selectedCompanies.length > 0 && (
            <span className={styles.selectedCount}>
              ({selectedCompanies.length})
            </span>
          )}
        </span>
        <span className={styles.dropdownIcon}>
          {isOpen ? '▼' : '▶'}
        </span>
      </button>

      {isOpen && (
        <div className={styles.dropdown}>
          <div className={styles.dropdownHeader}>
            <input
              type="text"
              className={styles.searchInput}
              placeholder="Поиск компаний..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              onClick={(e) => e.stopPropagation()}
            />
            
            <div className={styles.headerActions}>
              <button 
                className={styles.actionButton}
                onClick={handleSelectAll}
              >
                {selectedCompanies.length === companies.length ? 'Снять все' : 'Выбрать все'}
              </button>
              {selectedCompanies.length > 0 && (
                <button 
                  className={styles.actionButton}
                  onClick={handleClearSelection}
                >
                  Очистить
                </button>
              )}
            </div>
          </div>

          {!searchTerm && topCompanies.length > 0 && (
            <div className={styles.topCompanies}>
              <div className={styles.sectionTitle}>Топ компании</div>
              <div className={styles.quickSelect}>
                {topCompanies.map(company => (
                  <button
                    key={company.name}
                    className={`${styles.quickCompany} ${
                      selectedCompanies.includes(company.name) ? styles.selected : ''
                    }`}
                    onClick={() => handleCompanyToggle(company.name)}
                  >
                    <span className={styles.companyName}>{company.name}</span>
                  </button>
                ))}
              </div>
            </div>
          )}

          <div className={styles.companiesList}>
            {loading ? (
              <div className={styles.loading}>
                <div className={styles.spinner} />
                <span>Загрузка компаний...</span>
              </div>
            ) : (
              <>
                {searchTerm && (
                  <div className={styles.sectionTitle}>
                    Результаты поиска ({filteredCompanies.length})
                  </div>
                )}
                {!searchTerm && (
                  <div className={styles.sectionTitle}>
                    Все компании ({companies.length})
                  </div>
                )}
                
                <div className={styles.scrollableList}>
                  {filteredCompanies.map(company => (
                    <label 
                      key={company.name}
                      className={styles.companyItem}
                    >
                      <input
                        type="checkbox"
                        className={styles.checkbox}
                        checked={selectedCompanies.includes(company.name)}
                        onChange={() => handleCompanyToggle(company.name)}
                      />
                      <span className={styles.companyInfo}>
                        <span className={styles.companyName}>
                          {company.name}
                        </span>
                      </span>
                    </label>
                  ))}
                </div>
              </>
            )}
          </div>

          {selectedCompanies.length > 0 && (
            <div className={styles.dropdownFooter}>
              <div className={styles.selectionSummary}>
                Выбрано {selectedCompanies.length} из {companies.length} компаний
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default CompanyFilter;