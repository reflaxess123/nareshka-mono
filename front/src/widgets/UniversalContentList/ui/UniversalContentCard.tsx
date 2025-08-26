import React, { useCallback, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Mic, 
  Building2, 
  BookOpen, 
  CheckCircle, 
  Code,
  Clock,
  Brain,
  ExternalLink,
  PlayCircle,
  FileText
} from 'lucide-react';
import type { UniversalContentItem } from '@/shared/types/learning';
import { CONTENT_TYPE_CONFIG } from '@/shared/types/learning';
import { useLearningStore } from '@/pages/Learning/model/learningStore';
import styles from './UniversalContentCard.module.scss';

interface UniversalContentCardProps {
  item: UniversalContentItem;
  viewMode: 'cards' | 'list' | 'compact';
  interviewCounts?: Record<string, number>;
}

export const UniversalContentCard: React.FC<UniversalContentCardProps> = ({ 
  item, 
  viewMode,
  interviewCounts = {}
}) => {
  const navigate = useNavigate();
  const config = CONTENT_TYPE_CONFIG[item.type];
  const { updateFilters } = useLearningStore();
  
  const [showAnswer, setShowAnswer] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
  const previewTimerRef = useRef<NodeJS.Timeout | null>(null);

  // Получаем прогресс из localStorage для практики
  const getProgress = () => {
    if (item.type !== 'practice') return false;
    const progress = localStorage.getItem('practice_progress');
    if (!progress) return false;
    try {
      const progressData = JSON.parse(progress);
      return progressData[item.id] === true;
    } catch {
      return false;
    }
  };

  const isCompleted = getProgress();
  
  // Функция для получения полного контента
  const getFullContent = () => {
    if (item.type === 'interviews') {
      const originalData = item.metadata.originalData;
      return item.metadata.fullContent || (originalData && 'content' in originalData ? originalData.content as string : '') || '';
    }
    if (item.type === 'practice') {
      return item.metadata.textContent || '';
    }
    return '';
  };

  // Показывать превью только для интервью и практики
  const canShowPreview = (item.type === 'interviews' || item.type === 'practice') && getFullContent();

  // Обработчики превью с задержкой
  const handleMouseEnter = useCallback(() => {
    if (!canShowPreview) return;
    previewTimerRef.current = setTimeout(() => {
      setShowPreview(true);
    }, 500);
  }, [canShowPreview]);

  const handleMouseLeave = useCallback(() => {
    if (previewTimerRef.current) {
      clearTimeout(previewTimerRef.current);
      previewTimerRef.current = null;
    }
    setShowPreview(false);
  }, []);

  // Обработчик клика на карточку
  const handleCardClick = useCallback(() => {
    switch (item.type) {
      case 'interviews':
        navigate(`/interviews/${item.id}`);
        break;
      case 'questions':
        // Копируем вопрос в буфер обмена
        navigator.clipboard.writeText(item.title);
        break;
      case 'practice':
        navigate(`/code-editor?blockId=${item.id}`);
        break;
      case 'theory':
        // Для теории - переключаем показ ответа вместо навигации
        setShowAnswer(prev => !prev);
        break;
    }
  }, [item, navigate]);

  // Обработчик клика на интервью-тег для вопросов
  const handleInterviewTagClick = useCallback((e: React.MouseEvent, interviewId: string) => {
    e.stopPropagation();
    updateFilters({
      categories: [],
      clusters: [],
      companies: [],
      search: `interview:${interviewId}`
    });
  }, [updateFilters]);

  // Рендер иконок в зависимости от типа
  const renderTypeIcon = () => {
    switch (item.type) {
      case 'interviews':
        return item.hasAudio ? <Mic size={16} /> : <Building2 size={16} />;
      case 'questions':
        return <Brain size={16} />;
      case 'practice':
        return <Code size={16} />;
      case 'theory':
        return <BookOpen size={16} />;
    }
  };

  // Рендер дополнительной информации
  const renderMetaInfo = () => {
    const metaItems = [];

    if (item.company) {
      metaItems.push(
        <span key="company" className={styles.metaItem}>
          <Building2 size={14} />
          {item.company}
        </span>
      );
    }

    if (item.category) {
      metaItems.push(
        <span key="category" className={styles.metaItem}>
          📁 {item.category}
        </span>
      );
    }

    if (item.subCategory) {
      metaItems.push(
        <span key="subcategory" className={styles.metaItem}>
          📂 {item.subCategory}
        </span>
      );
    }

    // Значки сложности отключены
    // if (item.difficulty) {
    //   ...
    // }

    // Дополнительная информация для интервью
    if (item.type === 'interviews') {
      if (item.metadata?.duration) {
        metaItems.push(
          <span key="duration" className={styles.metaItem}>
            <Clock size={14} />
            {item.metadata.duration} мин
          </span>
        );
      }
      
      const technologies = item.metadata.technologies;
      if (technologies && technologies.length > 0) {
        metaItems.push(
          <span key="tech" className={styles.metaItem}>
            <Code size={14} />
            {technologies.slice(0, 2).join(', ')}
            {technologies.length > 2 ? '...' : ''}
          </span>
        );
      }
    }
    
    // Дополнительная информация для практики - убираем тег языка программирования
    // if (item.type === 'practice' && item.codeLanguage) {
    //   metaItems.push(
    //     <span key="language" className={styles.metaItem}>
    //       <Code2 size={14} />
    //       {item.codeLanguage.toUpperCase()}
    //     </span>
    //   );
    // }
    
    // Дополнительная информация для теории
    if (item.type === 'theory' && item.metadata?.cardType) {
      metaItems.push(
        <span key="cardtype" className={styles.metaItem}>
          📚 {item.metadata.cardType}
        </span>
      );
    }

    if (item.isCompleted || isCompleted) {
      metaItems.push(
        <span key="completed" className={styles.completed}>
          <CheckCircle size={14} />
          {item.type === 'practice' ? 'Решено' : 'Изучено'}
        </span>
      );
    }

    if (item.hasAudio) {
      metaItems.push(
        <span key="audio" className={styles.hasAudio}>
          <PlayCircle size={14} />
          Есть аудио/видео запись
        </span>
      );
    }

    return metaItems;
  };

  // Компактный вид
  if (viewMode === 'compact') {
    return (
      <div 
        className={`${styles.cardCompact} ${styles[item.type]}`}
        onClick={handleCardClick}
      >
        <div className={styles.compactLeft}>
          <span className={styles.typeIcon}>{renderTypeIcon()}</span>
          <span className={styles.title}>{item.title}</span>
        </div>
        <div className={styles.compactRight}>
          {renderMetaInfo()}
        </div>
      </div>
    );
  }

  // Вид списком
  if (viewMode === 'list') {
    return (
      <div 
        className={`${styles.cardList} ${styles[item.type]}`}
        onClick={handleCardClick}
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
      >
        <div className={styles.listLeft}>
          <div className={styles.typeIndicator} style={{ backgroundColor: config.color }}>
            {renderTypeIcon()}
          </div>
          <div className={styles.listContent}>
            <h3 className={styles.title}>{item.title}</h3>
            {item.type === 'theory' && showAnswer ? (
              <div className={styles.theoryAnswer}>
                <p className={styles.answerLabel}>Ответ:</p>
                <div 
                  className={styles.answerContent}
                  dangerouslySetInnerHTML={{ __html: item.metadata?.answerBlock || 'Нет ответа' }}
                />
              </div>
            ) : (
              item.description && (
                <p className={styles.description}>{item.description}</p>
              )
            )}
            <div className={styles.meta}>
              {renderMetaInfo()}
            </div>
            {/* Интервью-теги для вопросов */}
            {item.type === 'questions' && item.metadata.interviewInfo ? (() => {
              const interviewInfo = item.metadata.interviewInfo;
              if (!interviewInfo || !interviewInfo.id || !interviewInfo.formattedName) return null;
              return (
                <div className={styles.interviewTag}>
                  <button
                    className={styles.interviewBadge}
                    onClick={(e) => handleInterviewTagClick(e, interviewInfo.id)}
                    title={`Показать все вопросы из ${interviewInfo.formattedName}`}
                  >
                    <FileText size={12} />
                    <span>
                      {interviewInfo.formattedName}
                      {interviewCounts[interviewInfo.id] > 1 && (
                        <span className={styles.interviewCount}>
                          {' '}• {interviewCounts[interviewInfo.id]} вопр
                        </span>
                      )}
                    </span>
                  </button>
                </div>
              );
            })() : null}
          </div>
        </div>
        <div className={styles.listActions}>
          {item.type === 'interviews' && (
            <button className={styles.actionBtn}>
              <ExternalLink size={16} />
            </button>
          )}
        </div>
        
        {/* Превью контента при наведении */}
        {showPreview && canShowPreview && (
          <div className={styles.contentPreview}>
            <div className={styles.previewContent}>
              <div className={styles.previewHeader}>
                {item.type === 'interviews' ? '📄 Полное интервью' : '💻 Полное описание задачи'}
              </div>
              <div className={styles.previewText}>
{String(getFullContent() || '')}
              </div>
            </div>
          </div>
        )}
      </div>
    );
  }

  // Вид карточками (по умолчанию)
  return (
    <div 
      className={`${styles.card} ${styles[item.type]}`}
      onClick={handleCardClick}
    >
      <div className={styles.cardHeader}>
        <div 
          className={styles.typeLabel}
          style={{ backgroundColor: config.color }}
        >
          {renderTypeIcon()}
          <span>{config.label}</span>
        </div>
        {item.hasAudio && (
          <span className={styles.audioBadge}>
            <Mic size={14} />
          </span>
        )}
        {item.isCompleted && (
          <span className={styles.completedBadge}>
            <CheckCircle size={14} />
          </span>
        )}
      </div>

      <div className={styles.cardBody}>
        <h3 className={styles.title}>{item.title}</h3>
        
        {item.description && (
          <p className={styles.description}>
            {item.description.length > 150 
              ? `${item.description.substring(0, 150)}...` 
              : item.description}
          </p>
        )}

        <div className={styles.meta}>
          {renderMetaInfo()}
        </div>

        {item.tags && item.tags.length > 0 && (
          <div className={styles.tags}>
            {item.tags.slice(0, 3).map(tag => (
              <span key={tag} className={styles.tag}>
                #{tag}
              </span>
            ))}
            {item.tags.length > 3 && (
              <span className={styles.moreTag}>
                +{item.tags.length - 3}
              </span>
            )}
          </div>
        )}
      </div>

      <div className={styles.cardFooter}>
        <button 
          className={styles.primaryAction}
          onClick={(e) => {
            e.stopPropagation();
            handleCardClick();
          }}
        >
          {item.type === 'interviews' && 'Читать'}
          {item.type === 'questions' && 'Копировать'}
          {item.type === 'practice' && 'Решать'}
          {item.type === 'theory' && 'Изучать'}
        </button>
      </div>
    </div>
  );
};