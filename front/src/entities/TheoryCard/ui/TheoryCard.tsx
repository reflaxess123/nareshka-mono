import { Modal } from '@/shared/components/Modal';
import { useRole } from '@/shared/hooks';
import { Settings, X } from 'lucide-react';
import { useState } from 'react';
import { createPortal } from 'react-dom';
import { useUpdateProgress } from '../model/queries';
import type { TheoryCard as TheoryCardType } from '../model/types';
import { CATEGORY_ICONS, PROGRESS_COLORS } from '../model/types';
import styles from './TheoryCard.module.scss';

interface TheoryCardProps {
  card: TheoryCardType;
}

// Определяем размеры модального окна (копируем из Modal.tsx)
enum ModalSize {
  SM = 'sm',
  MD = 'md',
  LG = 'lg',
}

export const TheoryCard = ({ card }: TheoryCardProps) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);
  const updateProgressMutation = useUpdateProgress();
  const { isGuest, isAdmin } = useRole();

  // Состояние формы редактирования
  const [editData, setEditData] = useState({
    questionBlock: card.questionBlock,
    answerBlock: card.answerBlock,
    category: card.category,
    subCategory: card.subCategory || '',
    tags: card.tags,
    orderIndex: card.orderIndex,
    cardType: card.cardType,
    deck: card.deck,
  });

  const handleCardClick = () => {
    setIsExpanded(!isExpanded);
  };

  const handleProgressUpdate = (action: 'increment' | 'decrement') => {
    updateProgressMutation.mutate({
      cardId: card.id,
      data: { action },
    });
  };

  const handleEditTheory = (e: React.MouseEvent) => {
    e.stopPropagation();
    setShowEditModal(true);
  };

  const handleSaveEdit = async () => {
    try {
      setIsUpdating(true);

      const response = await fetch(`/api/admin/theory/cards/${card.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(editData),
      });

      if (!response.ok) {
        throw new Error('Не удалось обновить карточку');
      }

      // Обновляем данные карточки локально
      Object.assign(card, editData);
      setShowEditModal(false);
    } finally {
      setIsUpdating(false);
    }
  };

  // Получаем иконку для категории
  const categoryIcon = CATEGORY_ICONS[card.category] || CATEGORY_ICONS.DEFAULT;

  // Определяем уровень прогресса (только для авторизованных пользователей)
  const getProgressLevel = (count: number | null | undefined) => {
    const safeCount = count ?? 0;
    if (safeCount === 0)
      return {
        level: 'Не изучено',
        color: PROGRESS_COLORS.NOT_STUDIED,
        emoji: '🔴',
      };
    if (safeCount <= 2)
      return {
        level: 'Начальный',
        color: PROGRESS_COLORS.BEGINNER,
        emoji: '🟡',
      };
    if (safeCount <= 5)
      return {
        level: 'Средний',
        color: PROGRESS_COLORS.INTERMEDIATE,
        emoji: '🔵',
      };
    return { level: 'Изучено', color: PROGRESS_COLORS.STUDIED, emoji: '🟢' };
  };

  const progressInfo = !isGuest
    ? getProgressLevel(card.progress?.solvedCount)
    : null;

  return (
    <>
      <div
        className={`${styles.theoryCard} ${isExpanded ? styles.expanded : ''}`}
        onClick={handleCardClick}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ' ') {
            handleCardClick();
          }
        }}
      >
        <div className={styles.cardHeader}>
          <div className={styles.categoryInfo}>
            <div
              className={styles.categoryIcon}
              style={{ color: categoryIcon.color }}
            >
              {categoryIcon.icon}
            </div>
            <div className={styles.categoryText}>
              <span className={styles.category}>{card.category}</span>
              {card.subCategory && (
                <span className={styles.subCategory}>{card.subCategory}</span>
              )}
            </div>
          </div>

          <div className={styles.headerRight}>
            {/* Прогресс - только для авторизованных пользователей */}
            {!isGuest && progressInfo && (
              <div className={styles.progressInfo}>
                <span className={styles.progressEmoji}>
                  {progressInfo.emoji}
                </span>
                <span className={styles.progressCount}>
                  {card.progress?.solvedCount ?? 0}
                </span>
                <span
                  className={styles.progressLevel}
                  style={{ color: progressInfo.color }}
                >
                  {progressInfo.level}
                </span>
              </div>
            )}

            {/* Для гостей показываем приглашение к авторизации */}
            {isGuest && (
              <div className={styles.guestInfo}>
                <span className={styles.guestText}>
                  Войдите для отслеживания прогресса
                </span>
              </div>
            )}

            {/* Кнопка редактирования для администраторов */}
            {isAdmin && (
              <button
                className={styles.editButton}
                onClick={handleEditTheory}
                title="Редактировать теорию"
                aria-label="Редактировать теорию"
              >
                <Settings size={16} />
              </button>
            )}

            <div className={styles.expandIcon}>{isExpanded ? '−' : '+'}</div>
          </div>
        </div>

        <div className={styles.question}>
          <div dangerouslySetInnerHTML={{ __html: card.questionBlock }} />
        </div>

        {isExpanded && (
          <div className={styles.additionalInfo}>
            <div className={styles.answerSection}>
              <h4 className={styles.answerTitle}>💡 Ответ:</h4>
              <div
                className={styles.answerContent}
                dangerouslySetInnerHTML={{ __html: card.answerBlock }}
              />
            </div>

            {/* Кнопки прогресса - только для авторизованных пользователей */}
            {!isGuest && (
              <div className={styles.progressButtons}>
                <button
                  className={styles.progressButton}
                  onClick={(e) => {
                    e.stopPropagation();
                    handleProgressUpdate('increment');
                  }}
                  disabled={updateProgressMutation.isPending}
                >
                  ✅ Изучил
                </button>
                {(card.progress?.solvedCount ?? 0) > 0 && (
                  <button
                    className={styles.progressButton}
                    onClick={(e) => {
                      e.stopPropagation();
                      handleProgressUpdate('decrement');
                    }}
                    disabled={updateProgressMutation.isPending}
                  >
                    ↩️ Отменить
                  </button>
                )}
              </div>
            )}

            {/* Приглашение для гостей */}
            {isGuest && (
              <div className={styles.guestPrompt}>
                <p>🔐 Авторизуйтесь, чтобы отслеживать прогресс изучения</p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Модальное окно редактирования - рендерится через Portal */}
      {showEditModal &&
        createPortal(
          <Modal
            isOpen={showEditModal}
            onClose={() => setShowEditModal(false)}
            size={ModalSize.LG}
            closeOnOverlay={true}
            closeOnEsc={true}
          >
            <div className={styles.editModalHeader}>
              <h3>Редактировать карточку теории</h3>
              <button
                className={styles.editModalClose}
                onClick={() => setShowEditModal(false)}
              >
                <X size={20} />
              </button>
            </div>

            <div className={styles.editModalBody}>
              <div className={styles.editFormRow}>
                <div className={styles.editFormGroup}>
                  <label>Категория *</label>
                  <input
                    type="text"
                    value={editData.category}
                    onChange={(e) =>
                      setEditData((prev) => ({
                        ...prev,
                        category: e.target.value,
                      }))
                    }
                    required
                  />
                </div>

                <div className={styles.editFormGroup}>
                  <label>Подкатегория</label>
                  <input
                    type="text"
                    value={editData.subCategory}
                    onChange={(e) =>
                      setEditData((prev) => ({
                        ...prev,
                        subCategory: e.target.value,
                      }))
                    }
                  />
                </div>
              </div>

              <div className={styles.editFormRow}>
                <div className={styles.editFormGroup}>
                  <label>Тип карточки</label>
                  <select
                    value={editData.cardType}
                    onChange={(e) =>
                      setEditData((prev) => ({
                        ...prev,
                        cardType: e.target.value,
                      }))
                    }
                  >
                    <option value="Простая">Простая</option>
                    <option value="Обращение">Обращение</option>
                    <option value="Базовая (и обращение)">
                      Базовая (и обращение)
                    </option>
                    <option value="Пропуск">Пропуск</option>
                  </select>
                </div>

                <div className={styles.editFormGroup}>
                  <label>Порядковый номер</label>
                  <input
                    type="number"
                    value={editData.orderIndex}
                    onChange={(e) =>
                      setEditData((prev) => ({
                        ...prev,
                        orderIndex: parseInt(e.target.value) || 0,
                      }))
                    }
                    min="0"
                  />
                </div>
              </div>

              <div className={styles.editFormGroup}>
                <label>Колода</label>
                <input
                  type="text"
                  value={editData.deck}
                  onChange={(e) =>
                    setEditData((prev) => ({ ...prev, deck: e.target.value }))
                  }
                />
              </div>

              <div className={styles.editFormGroup}>
                <label>Вопрос *</label>
                <textarea
                  value={editData.questionBlock}
                  onChange={(e) =>
                    setEditData((prev) => ({
                      ...prev,
                      questionBlock: e.target.value,
                    }))
                  }
                  rows={6}
                  className={styles.htmlTextarea}
                  placeholder="HTML содержимое вопроса"
                  required
                />
              </div>

              <div className={styles.editFormGroup}>
                <label>Ответ *</label>
                <textarea
                  value={editData.answerBlock}
                  onChange={(e) =>
                    setEditData((prev) => ({
                      ...prev,
                      answerBlock: e.target.value,
                    }))
                  }
                  rows={6}
                  className={styles.htmlTextarea}
                  placeholder="HTML содержимое ответа"
                  required
                />
              </div>

              <div className={styles.editFormGroup}>
                <label>Теги (через запятую)</label>
                <input
                  type="text"
                  value={editData.tags.join(', ')}
                  onChange={(e) =>
                    setEditData((prev) => ({
                      ...prev,
                      tags: e.target.value
                        .split(',')
                        .map((tag) => tag.trim())
                        .filter(Boolean),
                    }))
                  }
                  placeholder="javascript, variables, basic"
                />
              </div>
            </div>

            <div className={styles.editModalFooter}>
              <button
                className={styles.editModalCancel}
                onClick={() => setShowEditModal(false)}
                disabled={isUpdating}
              >
                Отмена
              </button>
              <button
                className={styles.editModalSave}
                onClick={handleSaveEdit}
                disabled={
                  isUpdating ||
                  !editData.questionBlock.trim() ||
                  !editData.answerBlock.trim() ||
                  !editData.category.trim()
                }
              >
                {isUpdating ? 'Сохранение...' : 'Сохранить'}
              </button>
            </div>
          </Modal>,
          document.body
        )}
    </>
  );
};
