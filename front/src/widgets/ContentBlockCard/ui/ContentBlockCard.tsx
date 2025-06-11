import type { ContentBlock } from '@/entities/ContentBlock';
import { ContentProgress } from '@/features/ContentProgress';
import { Modal } from '@/shared/components/Modal';
import { useRole } from '@/shared/hooks';
import {
  Check,
  ChevronDown,
  ChevronUp,
  Copy,
  ExternalLink,
  Settings,
  X,
} from 'lucide-react';
import { useState } from 'react';
import { createPortal } from 'react-dom';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import styles from './ContentBlockCard.module.scss';

// Определяем размеры модального окна (копируем из Modal.tsx)
enum ModalSize {
  SM = 'sm',
  MD = 'md',
  LG = 'lg',
}

interface ContentBlockCardProps {
  block: ContentBlock;
  className?: string;
  variant?: 'default' | 'compact' | 'detailed';
}

export const ContentBlockCard = ({
  block,
  className,
  variant = 'default',
}: ContentBlockCardProps) => {
  const [isCodeExpanded, setIsCodeExpanded] = useState(!block.isCodeFoldable);
  const [copiedUrl, setCopiedUrl] = useState<string | null>(null);
  const [showEditModal, setShowEditModal] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);
  const { isAdmin } = useRole();

  // Состояние формы редактирования
  const [editData, setEditData] = useState({
    blockTitle: block.blockTitle,
    textContent: block.textContent || '',
    codeContent: block.codeContent || '',
    codeLanguage: block.codeLanguage || 'javascript',
    isCodeFoldable: block.isCodeFoldable,
    codeFoldTitle: block.codeFoldTitle || '',
    blockLevel: block.blockLevel,
  });

  const handleCopyUrl = async (url: string) => {
    try {
      await navigator.clipboard.writeText(url);
      setCopiedUrl(url);
      setTimeout(() => setCopiedUrl(null), 2000);
    } catch (error) {
      console.error('Ошибка копирования URL:', error);
    }
  };

  const handleEditContent = (e: React.MouseEvent) => {
    e.stopPropagation();
    setShowEditModal(true);
  };

  const handleSaveEdit = async () => {
    try {
      setIsUpdating(true);

      const response = await fetch(`/api/admin/content/blocks/${block.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(editData),
      });

      if (!response.ok) {
        throw new Error('Не удалось обновить блок');
      }

      // Обновляем данные блока локально
      Object.assign(block, editData);
      setShowEditModal(false);
    } catch (error) {
      console.error('Ошибка обновления блока:', error);
      alert('Не удалось обновить блок');
    } finally {
      setIsUpdating(false);
    }
  };

  const renderPathTitles = () => {
    if (block.pathTitles.length <= 1) return null;

    return (
      <div className={styles.pathTitles}>
        {block.pathTitles.slice(0, -1).map((title, index) => (
          <span key={index} className={styles.pathTitle}>
            {title}
            {index < block.pathTitles.length - 2 && (
              <span className={styles.pathSeparator}>→</span>
            )}
          </span>
        ))}
      </div>
    );
  };

  const renderCodeBlock = () => {
    if (!block.codeContent) return null;

    const shouldShowToggle = block.isCodeFoldable;
    const codeTitle = block.codeFoldTitle || 'Код';

    return (
      <div className={styles.codeBlock}>
        {shouldShowToggle && (
          <button
            onClick={() => setIsCodeExpanded(!isCodeExpanded)}
            className={styles.codeToggle}
          >
            <span>{codeTitle}</span>
            {isCodeExpanded ? (
              <ChevronUp size={16} />
            ) : (
              <ChevronDown size={16} />
            )}
          </button>
        )}

        {isCodeExpanded && (
          <div className={styles.codeContainer}>
            <SyntaxHighlighter
              language={block.codeLanguage || 'javascript'}
              style={oneDark}
              customStyle={{
                margin: 0,
                borderRadius: '6px',
                fontSize: '14px',
              }}
            >
              {block.codeContent}
            </SyntaxHighlighter>
          </div>
        )}
      </div>
    );
  };

  const renderUrls = () => {
    if (block.extractedUrls.length === 0) return null;

    return (
      <div className={styles.urls}>
        <h4 className={styles.urlsTitle}>Полезные ссылки:</h4>
        <div className={styles.urlsList}>
          {block.extractedUrls.map((url, index) => (
            <div key={index} className={styles.urlItem}>
              <a
                href={url}
                target="_blank"
                rel="noopener noreferrer"
                className={styles.urlLink}
              >
                <ExternalLink size={14} />
                {new URL(url).hostname}
              </a>
              <button
                onClick={() => handleCopyUrl(url)}
                className={styles.copyButton}
                aria-label="Копировать ссылку"
              >
                {copiedUrl === url ? <Check size={14} /> : <Copy size={14} />}
              </button>
            </div>
          ))}
        </div>
      </div>
    );
  };

  if (variant === 'compact') {
    return (
      <div
        className={`${styles.contentBlockCard} ${styles.compact} ${className || ''}`}
      >
        <div className={styles.header}>
          <h3 className={styles.title}>{block.blockTitle}</h3>
          <div className={styles.headerActions}>
            <ContentProgress
              blockId={block.id}
              currentCount={block.currentUserSolvedCount}
              variant="compact"
            />
            {isAdmin && (
              <button
                className={styles.editButton}
                onClick={handleEditContent}
                title="Редактировать контент"
                aria-label="Редактировать контент"
              >
                <Settings size={16} />
              </button>
            )}
          </div>
        </div>

        <div className={styles.meta}>
          <span className={styles.category}>
            {block.file.mainCategory} / {block.file.subCategory}
          </span>
          <span className={styles.level}>H{block.blockLevel}</span>
        </div>

        {block.textContent && (
          <p className={styles.textPreview}>
            {block.textContent.length > 100
              ? `${block.textContent.substring(0, 100)}...`
              : block.textContent}
          </p>
        )}
      </div>
    );
  }

  return (
    <>
      <article
        className={`${styles.contentBlockCard} ${styles.default} ${className || ''}`}
      >
        <header className={styles.header}>
          {renderPathTitles()}

          <div className={styles.titleRow}>
            <h2 className={styles.title}>{block.blockTitle}</h2>
            <div className={styles.titleActions}>
              <ContentProgress
                blockId={block.id}
                currentCount={block.currentUserSolvedCount}
                variant={variant === 'detailed' ? 'detailed' : 'default'}
              />
              {isAdmin && (
                <button
                  className={styles.editButton}
                  onClick={handleEditContent}
                  title="Редактировать контент"
                  aria-label="Редактировать контент"
                >
                  <Settings size={16} />
                </button>
              )}
            </div>
          </div>

          <div className={styles.meta}>
            <span className={styles.category}>
              {block.file.mainCategory} / {block.file.subCategory}
            </span>
            <span className={styles.level}>Уровень {block.blockLevel}</span>
            <span className={styles.order}>#{block.orderInFile}</span>
          </div>
        </header>

        <div className={styles.content}>
          {block.textContent && (
            <div className={styles.textContent}>
              <p>{block.textContent}</p>
            </div>
          )}

          {renderCodeBlock()}
          {renderUrls()}
        </div>

        <footer className={styles.footer}>
          <div className={styles.fileInfo}>
            <span className={styles.filePath}>{block.file.webdavPath}</span>
          </div>

          <div className={styles.timestamps}>
            <time className={styles.timestamp}>
              Создано: {new Date(block.createdAt).toLocaleDateString('ru-RU')}
            </time>
            {block.updatedAt !== block.createdAt && (
              <time className={styles.timestamp}>
                Обновлено:{' '}
                {new Date(block.updatedAt).toLocaleDateString('ru-RU')}
              </time>
            )}
          </div>
        </footer>
      </article>

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
              <h3>Редактировать блок контента</h3>
              <button
                className={styles.editModalClose}
                onClick={() => setShowEditModal(false)}
              >
                <X size={20} />
              </button>
            </div>

            <div className={styles.editModalBody}>
              <div className={styles.editFormGroup}>
                <label>Заголовок блока *</label>
                <input
                  type="text"
                  value={editData.blockTitle}
                  onChange={(e) =>
                    setEditData((prev) => ({
                      ...prev,
                      blockTitle: e.target.value,
                    }))
                  }
                  required
                />
              </div>

              <div className={styles.editFormGroup}>
                <label>Текстовое содержимое</label>
                <textarea
                  value={editData.textContent}
                  onChange={(e) =>
                    setEditData((prev) => ({
                      ...prev,
                      textContent: e.target.value,
                    }))
                  }
                  rows={4}
                />
              </div>

              <div className={styles.editFormRow}>
                <div className={styles.editFormGroup}>
                  <label>Уровень блока</label>
                  <input
                    type="number"
                    value={editData.blockLevel}
                    onChange={(e) =>
                      setEditData((prev) => ({
                        ...prev,
                        blockLevel: parseInt(e.target.value) || 1,
                      }))
                    }
                    min="1"
                    max="6"
                  />
                </div>

                <div className={styles.editFormGroup}>
                  <label>Язык кода</label>
                  <select
                    value={editData.codeLanguage}
                    onChange={(e) =>
                      setEditData((prev) => ({
                        ...prev,
                        codeLanguage: e.target.value,
                      }))
                    }
                  >
                    <option value="javascript">JavaScript</option>
                    <option value="typescript">TypeScript</option>
                    <option value="html">HTML</option>
                    <option value="css">CSS</option>
                    <option value="json">JSON</option>
                    <option value="bash">Bash</option>
                  </select>
                </div>
              </div>

              <div className={styles.editFormGroup}>
                <label>Код</label>
                <textarea
                  value={editData.codeContent}
                  onChange={(e) =>
                    setEditData((prev) => ({
                      ...prev,
                      codeContent: e.target.value,
                    }))
                  }
                  rows={8}
                  className={styles.codeTextarea}
                />
              </div>

              <div className={styles.editFormRow}>
                <div className={styles.editFormGroup}>
                  <label className={styles.checkboxLabel}>
                    <input
                      type="checkbox"
                      checked={editData.isCodeFoldable}
                      onChange={(e) =>
                        setEditData((prev) => ({
                          ...prev,
                          isCodeFoldable: e.target.checked,
                        }))
                      }
                    />
                    Код сворачиваемый
                  </label>
                </div>

                <div className={styles.editFormGroup}>
                  <label>Заголовок свертки</label>
                  <input
                    type="text"
                    value={editData.codeFoldTitle}
                    onChange={(e) =>
                      setEditData((prev) => ({
                        ...prev,
                        codeFoldTitle: e.target.value,
                      }))
                    }
                    disabled={!editData.isCodeFoldable}
                  />
                </div>
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
                disabled={isUpdating || !editData.blockTitle.trim()}
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
