import React, { useState, useCallback, useEffect } from 'react';
import { useDebounce } from '../../hooks/useDebounce';
import styles from './InterviewSearch.module.scss';

interface SearchResult {
  id: string;
  question_text: string;
  company: string;
  category_name: string;
  cluster_name?: string;
  matched_keywords?: string[];
}

interface InterviewSearchProps {
  onResultSelect?: (result: SearchResult) => void;
  onSearchStateChange?: (isSearching: boolean) => void;
}

export const InterviewSearch: React.FC<InterviewSearchProps> = ({ 
  onResultSelect,
  onSearchStateChange 
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(0);
  
  const debouncedQuery = useDebounce(searchQuery, 300);

  const handleSearch = useCallback(async (query: string) => {
    if (query.length < 3) {
      setResults([]);
      setIsOpen(false);
      return;
    }

    setIsLoading(true);
    onSearchStateChange?.(true);

    try {
      const response = await fetch(
        `/api/v2/interview-categories/search/questions?query=${encodeURIComponent(query)}&limit=20`
      );
      
      if (!response.ok) {
        throw new Error('Search failed');
      }

      const data = await response.json();
      setResults(data.results || []);
      setIsOpen(true);
    } catch (error) {
      console.error('Search error:', error);
      setResults([]);
    } finally {
      setIsLoading(false);
      onSearchStateChange?.(false);
    }
  }, [onSearchStateChange]);

  useEffect(() => {
    handleSearch(debouncedQuery);
  }, [debouncedQuery, handleSearch]);

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (!isOpen || results.length === 0) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex(prev => (prev + 1) % results.length);
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex(prev => (prev - 1 + results.length) % results.length);
        break;
      case 'Enter':
        e.preventDefault();
        if (results[selectedIndex]) {
          onResultSelect?.(results[selectedIndex]);
          setIsOpen(false);
          setSearchQuery('');
        }
        break;
      case 'Escape':
        setIsOpen(false);
        break;
    }
  }, [isOpen, results, selectedIndex, onResultSelect]);

  const highlightMatch = (text: string, query: string) => {
    const parts = text.split(new RegExp(`(${query})`, 'gi'));
    return parts.map((part, index) => 
      part.toLowerCase() === query.toLowerCase() ? 
        <mark key={index} className={styles.highlight}>{part}</mark> : part
    );
  };

  return (
    <div className={styles.searchContainer}>
      <div className={styles.searchInputWrapper}>
        <svg 
          className={styles.searchIcon} 
          width="20" 
          height="20" 
          viewBox="0 0 20 20"
        >
          <path 
            d="M14.386 14.386l4.0877 4.0877-4.0877-4.0877c-2.9418 2.9419-7.7115 2.9419-10.6533 0-2.9419-2.9418-2.9419-7.7115 0-10.6533 2.9418-2.9419 7.7115-2.9419 10.6533 0 2.9419 2.9418 2.9419 7.7115 0 10.6533z" 
            stroke="currentColor" 
            fill="none" 
            strokeWidth="2"
          />
        </svg>
        
        <input
          type="text"
          className={styles.searchInput}
          placeholder="Поиск по 8,532 вопросам..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          onKeyDown={handleKeyDown}
        />
        
        {isLoading && (
          <div className={styles.loadingSpinner}>
            <div className={styles.spinner} />
          </div>
        )}
        
        {searchQuery && !isLoading && (
          <button 
            className={styles.clearButton}
            onClick={() => {
              setSearchQuery('');
              setResults([]);
              setIsOpen(false);
            }}
          >
            ✕
          </button>
        )}
      </div>

      {isOpen && results.length > 0 && (
        <div className={styles.resultsDropdown}>
          <div className={styles.resultsHeader}>
            Найдено: {results.length} вопросов
          </div>
          
          <div className={styles.resultsList}>
            {results.map((result, index) => (
              <div
                key={result.id}
                className={`${styles.resultItem} ${index === selectedIndex ? styles.selected : ''}`}
                onClick={() => {
                  onResultSelect?.(result);
                  setIsOpen(false);
                  setSearchQuery('');
                }}
                onMouseEnter={() => setSelectedIndex(index)}
              >
                <div className={styles.resultQuestion}>
                  {highlightMatch(result.question_text, searchQuery)}
                </div>
                
                <div className={styles.resultMeta}>
                  <span className={styles.resultCompany}>
                    {result.company}
                  </span>
                  <span className={styles.resultCategory}>
                    {result.category_name}
                  </span>
                  {result.cluster_name && (
                    <span className={styles.resultCluster}>
                      {result.cluster_name}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {isOpen && searchQuery.length >= 3 && results.length === 0 && !isLoading && (
        <div className={styles.noResults}>
          <div className={styles.noResultsIcon}>🔍</div>
          <div className={styles.noResultsText}>
            Ничего не найдено по запросу "{searchQuery}"
          </div>
          <div className={styles.noResultsHint}>
            Попробуйте изменить поисковый запрос
          </div>
        </div>
      )}
    </div>
  );
};

export default InterviewSearch;