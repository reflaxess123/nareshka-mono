import React, { useState, useMemo } from 'react';
import { Search } from 'lucide-react';
import type { CompanyFilterProps } from '../model/types';
import styles from './CompanyFilter.module.scss';

export const CompanyFilter: React.FC<CompanyFilterProps> = ({
  companies,
  selectedCompanies,
  onSelectionChange,
  isLoading = false,
}) => {
  const [searchTerm, setSearchTerm] = useState('');

  const filteredCompanies = useMemo(() => {
    if (!searchTerm) return companies;
    return companies.filter(company =>
      company.name.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [companies, searchTerm]);

  const handleCompanyToggle = (companyName: string, checked: boolean) => {
    const newSelected = checked
      ? [...selectedCompanies, companyName]
      : selectedCompanies.filter(name => name !== companyName);
    
    onSelectionChange(newSelected);
  };

  if (isLoading) {
    return (
      <div className={styles.loading}>
        <div className={styles.skeleton}></div>
        <div className={styles.skeleton}></div>
        <div className={styles.skeleton}></div>
      </div>
    );
  }

  return (
    <div className={styles.companyFilter}>
      {/* Поиск */}
      <div className={styles.searchInputWrapper}>
        <Search size={16} className={styles.searchIcon} />
        <input
          type="text"
          placeholder="Поиск компаний..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className={styles.searchInput}
        />
      </div>

      {/* Список компаний */}
      <div className={styles.checkboxGroup}>
        {filteredCompanies.length === 0 && searchTerm ? (
          <div className={styles.noResults}>
            Компании не найдены
          </div>
        ) : (
          filteredCompanies.map(company => {
            const isChecked = selectedCompanies.includes(company.name);
            return (
              <label key={company.name} className={styles.checkboxLabel}>
                <input
                  type="checkbox"
                  checked={isChecked}
                  onChange={(e) => handleCompanyToggle(company.name, e.target.checked)}
                  className={styles.checkbox}
                />
                <span className={styles.labelText}>
                  {company.name}
                  <span className={styles.count}>({company.count})</span>
                </span>
              </label>
            );
          })
        )}
      </div>

      {/* Информация о выбранных */}
      {selectedCompanies.length > 0 && (
        <div className={styles.selectedInfo}>
          Выбрано: {selectedCompanies.length}
        </div>
      )}
    </div>
  );
};