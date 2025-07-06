import type { ContentBlock } from '@/entities/ContentBlock';
import { ContentProgress } from '@/features/ContentProgress';
import { Button, ButtonVariant } from '@/shared/components/Button';
import { MarkdownContent } from '@/shared/components/MarkdownContent';
import { Modal } from '@/shared/components/Modal';
import { Text } from '@/shared/components/Text';
import { useRole } from '@/shared/hooks';
import { CodeTemplateGenerator } from '@/shared/utils/codeTemplateGenerator';
import {
  Check,
  ChevronDown,
  ChevronUp,
  Copy,
  ExternalLink,
  Settings,
  Terminal,
  X,
} from 'lucide-react';
import { forwardRef, useState } from 'react';
import { createPortal } from 'react-dom';
import { useNavigate } from 'react-router-dom';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import styles from './ContentBlockCard.module.scss';

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

export const ContentBlockCard = forwardRef<HTMLElement, ContentBlockCardProps>(
  ({ block, variant = 'default', className = '' }, ref) => {
    const [isCodeExpanded, setIsCodeExpanded] = useState(!block.isCodeFoldable);
    const [isAnswerExpanded, setIsAnswerExpanded] = useState(false);
    const [copiedUrl, setCopiedUrl] = useState<string | null>(null);
    const [showEditModal, setShowEditModal] = useState(false);
    const [isUpdating, setIsUpdating] = useState(false);
    const { isAdmin } = useRole();
    const navigate = useNavigate();

    const [editData, setEditData] = useState({
      title: block.title,
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

        const response = await fetch(
          `/api/v2/admin/content/blocks/${block.id}`,
          {
            method: 'PUT',
            headers: {
              'Content-Type': 'application/json',
            },
            credentials: 'include',
            body: JSON.stringify(editData),
          }
        );

        if (!response.ok) {
          throw new Error('Не удалось обновить блок');
        }

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
      if (!block.pathTitles || block.pathTitles.length <= 1) return null;

      return (
        <div className={styles.pathTitles}>
          {block.pathTitles.slice(0, -1).map((title, index) => (
            <span key={index} className={styles.pathTitle}>
              {title}
              {index < (block.pathTitles?.length || 0) - 2 && (
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
      if (!block.extractedUrls || block.extractedUrls.length === 0) return null;

      const hasMarkdownTable =
        block.textContent?.includes('|') && block.textContent?.includes('---');
      if (hasMarkdownTable) return null;

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

    const handleTryInEditor = () => {
      const templateResult = CodeTemplateGenerator.generateTemplate(
        block.codeContent || '',
        block.codeLanguage || 'javascript'
      );

      const params = new URLSearchParams({
        blockId: block.id,
        template: templateResult,
        language: block.codeLanguage || 'javascript',
        processed: 'true',
      });

      navigate(`/code-editor?${params.toString()}`);
    };

    const shouldShowEditorButton = (): boolean => {
      if (!block.codeContent || !block.codeContent.trim()) {
        return false;
      }

      const language = block.codeLanguage?.toLowerCase();
      if (
        language === 'react' ||
        language === 'jsx' ||
        language === 'tsx' ||
        language === 'typescript' ||
        language === 'ts'
      ) {
        return false;
      }

      return true;
    };

    if (variant === 'compact') {
      return (
        <div
          className={`${styles.contentBlockCard} ${styles.compact} ${className || ''}`}
        >
          <div className={styles.header}>
            <h3 className={styles.title}>{block.title}</h3>
            <div className={styles.headerActions}>
              <ContentProgress
                blockId={block.id}
                currentCount={block.currentUserSolvedCount || 0}
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
              {block.file
                ? `${block.file.mainCategory} / ${block.file.subCategory}`
                : `${block.category} / ${block.subCategory}`}
            </span>
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
          ref={ref}
        >
          <header className={styles.header}>
            {renderPathTitles()}

            <div className={styles.titleRow}>
              <h2 className={styles.title}>{block.title}</h2>
              <div className={styles.titleActions}>
                <ContentProgress
                  blockId={block.id}
                  currentCount={block.currentUserSolvedCount || 0}
                  variant="default"
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
                {block.file
                  ? `${block.file.mainCategory} / ${block.file.subCategory}`
                  : `${block.category} / ${block.subCategory}`}
              </span>
              {block.companies && block.companies.length > 0 && (
                <div className={styles.companies}>
                  <span className={styles.companiesLabel}>Компании:</span>
                  <div className={styles.companiesTags}>
                    {block.companies.map((company, index) => (
                      <span key={index} className={styles.companyTag}>
                        {company}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </header>

          <div className={styles.content}>
            {block.textContent && (
              <div className={styles.textContent}>
                {block.type === 'theory_quiz' ? (
                  <div
                    dangerouslySetInnerHTML={{ __html: block.textContent }}
                  />
                ) : (
                  <MarkdownContent
                    content={block.textContent}
                    extractedUrls={block.extractedUrls || []}
                  />
                )}
              </div>
            )}

            {block.type === 'theory_quiz' && block.answerBlock && (
              <div className={styles.quizAnswer}>
                <button
                  className={styles.answerToggle}
                  onClick={() => setIsAnswerExpanded(!isAnswerExpanded)}
                >
                  <span className={styles.answerTitle}>💡 Ответ</span>
                  {isAnswerExpanded ? (
                    <ChevronUp size={16} />
                  ) : (
                    <ChevronDown size={16} />
                  )}
                </button>

                {isAnswerExpanded && (
                  <div
                    className={styles.answerContent}
                    dangerouslySetInnerHTML={{ __html: block.answerBlock }}
                  />
                )}
              </div>
            )}

            {renderCodeBlock()}
            {renderUrls()}

            {shouldShowEditorButton() && (
              <div className={styles.editorButtonContainer}>
                <Button
                  onClick={handleTryInEditor}
                  variant={ButtonVariant.PRIMARY}
                  className={styles.tryEditorButton}
                  title={
                    CodeTemplateGenerator.isJavaScriptTask(block)
                      ? 'Попробовать решить в редакторе (будет создана заготовка)'
                      : 'Открыть в редакторе (код будет скопирован как есть)'
                  }
                >
                  <Terminal size={16} color="var(--text-primary)" />
                  <Text text="Попробовать решить в редакторе" />
                  {CodeTemplateGenerator.isJavaScriptTask(block) && (
                    <span className={styles.jsLabel}>JS</span>
                  )}
                </Button>
              </div>
            )}
          </div>

          {(block.textContent ||
            block.codeContent ||
            (block.extractedUrls && block.extractedUrls.length > 0)) && (
            <button
              className={styles.expandButton}
              onClick={() => setIsCodeExpanded(!isCodeExpanded)}
              aria-label={isCodeExpanded ? 'Свернуть' : 'Развернуть'}
            >
              {isCodeExpanded ? (
                <ChevronUp size={20} />
              ) : (
                <ChevronDown size={20} />
              )}
            </button>
          )}

          {isAdmin && (
            <footer className={styles.footer}>
              <div className={styles.fileInfo}>
                <span className={styles.filePath}>
                  {block.file ? block.file.webdavPath : 'Theory Quiz (no file)'}
                </span>
              </div>

              <div className={styles.timestamps}>
                <time className={styles.timestamp}>
                  Создано:{' '}
                  {new Date(block.createdAt).toLocaleDateString('ru-RU')}
                </time>
                {block.updatedAt !== block.createdAt && (
                  <time className={styles.timestamp}>
                    Обновлено:{' '}
                    {new Date(block.updatedAt).toLocaleDateString('ru-RU')}
                  </time>
                )}
              </div>
            </footer>
          )}
        </article>

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
                    value={editData.title}
                    onChange={(e) =>
                      setEditData((prev) => ({
                        ...prev,
                        title: e.target.value,
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
                      value={editData.blockLevel || 0}
                      onChange={(e) =>
                        setEditData((prev) => ({
                          ...prev,
                          blockLevel: parseInt(e.target.value),
                        }))
                      }
                      className={styles.editModalInput}
                      placeholder="Уровень заголовка"
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
                        checked={editData.isCodeFoldable || false}
                        onChange={(e) =>
                          setEditData((prev) => ({
                            ...prev,
                            isCodeFoldable: e.target.checked,
                          }))
                        }
                        className={styles.editModalCheckbox}
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
                  disabled={isUpdating || !editData.title.trim()}
                >
                  {isUpdating ? 'Сохранение...' : 'Сохранить'}
                </button>
              </div>
            </Modal>,
            document.body
          )}
      </>
    );
  }
);
