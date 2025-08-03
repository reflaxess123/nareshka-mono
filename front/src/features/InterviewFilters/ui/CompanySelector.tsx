import React, { useState, useEffect, useRef } from 'react';
import styles from './CompanySelector.module.scss';

interface CompanySelectorProps {
  companies: string[];
  selectedCompanies: string[];
  onSelectionChange: (companies: string[]) => void;
}

// Топ-10 самых популярных компаний (по данным из БД)
const TOP_COMPANIES = [
  'Яндекс',
  'Сбер', 
  'Т-Банк',
  'Иннотех',
  'Альфа-Банк',
  'Linked Helper',
  'Северсталь',
  'IT-One',
  'iFellow',
  'РСХБ-Интех'
];

export const CompanySelector: React.FC<CompanySelectorProps> = ({
  companies,
  selectedCompanies,
  onSelectionChange
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [filteredCompanies, setFilteredCompanies] = useState<string[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Фильтрация компаний по поисковому запросу
  useEffect(() => {
    if (searchTerm.trim() === '') {
      setFilteredCompanies([]);
    } else {
      const filtered = companies
        .filter(company => 
          company.toLowerCase().includes(searchTerm.toLowerCase()) &&
          !selectedCompanies.includes(company)
        )
        .slice(0, 10); // Показываем максимум 10 результатов
      setFilteredCompanies(filtered);
    }
  }, [searchTerm, companies, selectedCompanies]);

  // Закрытие dropdown при клике вне компонента
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleCompanySelect = (company: string) => {
    if (!selectedCompanies.includes(company)) {
      onSelectionChange([...selectedCompanies, company]);
    }
    setSearchTerm('');
    setIsDropdownOpen(false);
    inputRef.current?.focus();
  };

  const handleCompanyRemove = (company: string) => {
    onSelectionChange(selectedCompanies.filter(c => c !== company));
  };

  const handleClearAll = () => {
    onSelectionChange([]);
    setSearchTerm('');
  };

  const handleInputFocus = () => {
    setIsDropdownOpen(true);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
    setIsDropdownOpen(true);
  };

  // Популярные компании, которые еще не выбраны
  const availableTopCompanies = TOP_COMPANIES.filter(
    company => companies.includes(company) && !selectedCompanies.includes(company)
  );

  return (
    <div className={styles.container}>
      {/* Быстрые кнопки популярных компаний */}
      {availableTopCompanies.length > 0 && (
        <div className={styles.quickButtons}>
          <span className={styles.quickLabel}>🔥 Популярные:</span>
          <div className={styles.buttonGroup}>
            {availableTopCompanies.slice(0, 6).map(company => (
              <button
                key={company}
                className={styles.quickButton}
                onClick={() => handleCompanySelect(company)}
              >
                {company}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Поиск компаний */}
      <div className={styles.searchSection} ref={dropdownRef}>
        <div className={styles.searchInput}>
          <input
            ref={inputRef}
            type="text"
            placeholder="🔍 Поиск компании..."
            value={searchTerm}
            onChange={handleInputChange}
            onFocus={handleInputFocus}
            className={styles.input}
          />
        </div>

        {/* Dropdown с результатами поиска */}
        {isDropdownOpen && filteredCompanies.length > 0 && (
          <div className={styles.dropdown}>
            {filteredCompanies.map(company => (
              <button
                key={company}
                className={styles.dropdownItem}
                onClick={() => handleCompanySelect(company)}
              >
                {company}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Выбранные компании */}
      {selectedCompanies.length > 0 && (
        <div className={styles.selectedSection}>
          <div className={styles.selectedHeader}>
            <span className={styles.selectedLabel}>
              ✅ Выбрано ({selectedCompanies.length}):
            </span>
            <button 
              className={styles.clearAllButton}
              onClick={handleClearAll}
            >
              Очистить все
            </button>
          </div>
          <div className={styles.selectedTags}>
            {selectedCompanies.map(company => (
              <span key={company} className={styles.selectedTag}>
                {company}
                <button
                  className={styles.removeButton}
                  onClick={() => handleCompanyRemove(company)}
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};