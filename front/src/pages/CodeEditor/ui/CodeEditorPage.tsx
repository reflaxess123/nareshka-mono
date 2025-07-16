import { ContentProgress } from '@/features/ContentProgress';
import { contentApi } from '@/shared/api/content';
import { Button, ButtonVariant } from '@/shared/components/Button';
import { CodeEditor } from '@/shared/components/CodeEditor';
import { MarkdownContent } from '@/shared/components/MarkdownContent';
import { useRole } from '@/shared/hooks';
import { contentQueryKeys } from '@/shared/hooks/useContentBlocks';
import { useProgressTracking } from '@/shared/hooks/useProgressTracking';
import { CodeTemplateGenerator } from '@/shared/utils/codeTemplateGenerator';
import { useQuery } from '@tanstack/react-query';
import { ArrowLeft, Code, Code2, Eye } from 'lucide-react';
import { useCallback, useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import './CodeEditorPage.scss';

export const CodeEditorPage = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { isGuest } = useRole();

  const blockId = searchParams.get('blockId');
  const templateFromUrl = searchParams.get('template');
  const languageFromUrl = searchParams.get('language');
  const processedFromUrl = searchParams.get('processed') === 'true';

  const [initialCode, setInitialCode] = useState<string>('');
  const [language, setLanguage] = useState<
    'JAVASCRIPT' | 'TYPESCRIPT' | 'PYTHON'
  >('JAVASCRIPT');
  const [isResizing, setIsResizing] = useState(false);
  const [leftPanelWidth, setLeftPanelWidth] = useState(50);
  const [templateKey, setTemplateKey] = useState(0);

  const { getTestCases, isLoadingTests } = useProgressTracking({
    showToasts: true,
  });

  const {
    data: block,
    isLoading,
    error,
  } = useQuery({
    queryKey: contentQueryKeys.block(blockId || ''),
    queryFn: async () => {
      if (!blockId) return null;
      try {
        return await contentApi.getBlock(blockId);
      } catch (err) {
        console.error('Error loading block:', err);
        return null;
      }
    },
    enabled: !!blockId,
  });

  useEffect(() => {
    if (blockId && block && block.codeContent && !isLoadingTests) {
      console.log(
        '🤖 Автоматически запускаем генерацию тест-кейсов для задачи:',
        blockId
      );

      // ✅ УБРАНО: уведомление о генерации тест-кейсов
      // Тихо загружаем тест-кейсы в фоне без уведомлений
      getTestCases(blockId);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [blockId, block?.id]); // Убрали getTestCases и isLoadingTests из зависимостей

  const determineLanguageFromBlock = (block: {
    codeLanguage?: string | null;
    file?: {
      mainCategory: string;
      subCategory: string;
    } | null;
    codeContent?: string | null;
  }): string => {
    const isJSTask = CodeTemplateGenerator.isJavaScriptTask(block);

    if (isJSTask) {
      const codeLanguage = block.codeLanguage?.toLowerCase();
      if (codeLanguage === 'typescript' || codeLanguage === 'ts') {
        return 'TYPESCRIPT';
      }
      return 'JAVASCRIPT';
    }

    if (block.codeLanguage) {
      const lang = block.codeLanguage.toLowerCase();
      const languageMap: Record<string, string> = {
        python: 'PYTHON',
        py: 'PYTHON',
        javascript: 'JAVASCRIPT',
        js: 'JAVASCRIPT',
        typescript: 'TYPESCRIPT',
        ts: 'TYPESCRIPT',
        java: 'JAVA',
        cpp: 'CPP',
        'c++': 'CPP',
        c: 'C',
        go: 'GO',
        rust: 'RUST',
        php: 'PHP',
        ruby: 'RUBY',
        rb: 'RUBY',
      };

      if (languageMap[lang]) {
        return languageMap[lang];
      }
    }

    return 'JAVASCRIPT';
  };

  useEffect(() => {
    if (templateFromUrl && languageFromUrl) {
      const decodedTemplate = decodeURIComponent(templateFromUrl);
      if (initialCode !== decodedTemplate) {
        setInitialCode(decodedTemplate);
        setLanguage(
          languageFromUrl.toUpperCase() as
            | 'JAVASCRIPT'
            | 'TYPESCRIPT'
            | 'PYTHON'
        );
      }
      return;
    }

    if (blockId && !isLoading) {
      if (block && block.codeContent) {
        const templateResult = CodeTemplateGenerator.generateTemplate(
          block.codeContent || '',
          block.codeLanguage || 'javascript'
        );
        const detectedLanguage = determineLanguageFromBlock(block);

        setInitialCode(templateResult);
        setLanguage(detectedLanguage as 'JAVASCRIPT' | 'TYPESCRIPT' | 'PYTHON');
      }
      return;
    }

    if (!blockId && !initialCode) {
      setInitialCode(`// Добро пожаловать в редактор кода Nareshka!
// Чаще всего наши задачи на JavaScript, поэтому он выбран по умолчанию

function fibonacci(n) {
    if (n <= 1) {
        return n;
    }
    return fibonacci(n - 1) + fibonacci(n - 2);
}

// Вычисляем первые 10 чисел Фибоначчи
for (let i = 0; i < 10; i++) {
    console.log(\`F(\${i}) = \${fibonacci(i)}\`);
}
`);
      setLanguage('JAVASCRIPT');
    }
  }, [
    block,
    isLoading,
    templateFromUrl,
    languageFromUrl,
    processedFromUrl,
    blockId,
    initialCode,
  ]);

  const handleBackToTasks = () => {
    navigate('/tasks');
  };

  const handleResetToOriginal = () => {
    if (block?.codeContent) {
      const detectedLanguage = determineLanguageFromBlock(block);

      setInitialCode(block.codeContent);
      setLanguage(detectedLanguage as 'JAVASCRIPT' | 'TYPESCRIPT' | 'PYTHON');
      setTemplateKey((prev) => prev + 1);

      const newSearchParams = new URLSearchParams(searchParams);
      newSearchParams.set('template', encodeURIComponent(block.codeContent));
      newSearchParams.set('language', detectedLanguage);
      newSearchParams.set('processed', 'false');
      navigate(`?${newSearchParams.toString()}`, { replace: true });
    }
  };

  const handleGenerateTemplate = () => {
    if (block) {
      const templateResult = CodeTemplateGenerator.generateTemplate(
        block.codeContent || '',
        block.codeLanguage || 'javascript'
      );
      const detectedLanguage = determineLanguageFromBlock(block);

      setInitialCode(templateResult);
      setLanguage(detectedLanguage as 'JAVASCRIPT' | 'TYPESCRIPT' | 'PYTHON');
      setTemplateKey((prev) => prev + 1);

      const newSearchParams = new URLSearchParams(searchParams);
      newSearchParams.set('template', encodeURIComponent(templateResult));
      newSearchParams.set('language', detectedLanguage);
      newSearchParams.set('processed', 'true');
      navigate(`?${newSearchParams.toString()}`, { replace: true });
    }
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    setIsResizing(true);
    e.preventDefault();
  };

  const handleMouseMove = useCallback(
    (e: MouseEvent) => {
      if (!isResizing) return;

      const newWidth = (e.clientX / window.innerWidth) * 100;
      if (newWidth >= 25 && newWidth <= 75) {
        setLeftPanelWidth(newWidth);
      }
    },
    [isResizing]
  );

  const handleMouseUp = () => {
    setIsResizing(false);
  };

  useEffect(() => {
    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [isResizing, handleMouseMove]);

  const isTaskMode = !!blockId;
  const isJSTask = block
    ? CodeTemplateGenerator.isJavaScriptTask(block)
    : false;

  if (isTaskMode && isLoading) {
    return (
      <div className="code-editor-page loading">
        <div className="loading-spinner">
          <Code2 className="animate-spin" size={32} />
          <p>Загрузка задачи...</p>
        </div>
      </div>
    );
  }

  if (isTaskMode && (error || !block)) {
    return (
      <div className="code-editor-page error">
        <div className="error-container">
          <h1>❌ Задача не найдена</h1>
          <p>Задача с ID {blockId} не существует или была удалена.</p>
          <Button onClick={handleBackToTasks} variant={ButtonVariant.PRIMARY}>
            <ArrowLeft size={16} />
            Вернуться к задачам
          </Button>
        </div>
      </div>
    );
  }

  const normalizedLanguage = (() => {
    switch (language as string) {
      case 'JS':
        return 'JAVASCRIPT';
      case 'TS':
        return 'TYPESCRIPT';
      case 'PY':
        return 'PYTHON';
      default:
        return language;
    }
  })();

  return (
    <div className="code-editor-page">
      <div className="compact-header">
        <div className="header-left">
          <Button
            onClick={handleBackToTasks}
            variant={ButtonVariant.GHOST}
            className="back-button"
          >
            <ArrowLeft size={16} />
            Назад
          </Button>

          {isTaskMode && block && (
            <>
              <span className="task-title">{block.title}</span>
              <div className="task-badges">
                {isJSTask && <span className="language-badge">JavaScript</span>}
              </div>
            </>
          )}
        </div>

        <div className="header-right">
          {isTaskMode && block && !isGuest && (
            <>
              <div className="progress-container">
                <span className="progress-label">Прогресс:</span>
                <ContentProgress
                  blockId={block.id}
                  currentCount={block.currentUserSolvedCount || 0}
                  variant="default"
                />
              </div>

              <div className="header-divider" />
            </>
          )}

          {isTaskMode && isJSTask && (
            <div className="template-container">
              <span className="template-label">Шаблоны:</span>
              <div className="template-buttons">
                <button
                  onClick={handleGenerateTemplate}
                  className="template-btn"
                >
                  <Code size={16} />
                  Заготовка
                </button>
                <button
                  onClick={handleResetToOriginal}
                  className="solution-btn"
                >
                  <Eye size={16} />
                  Решение
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="split-layout">
        <div className="left-panel" style={{ width: `${leftPanelWidth}%` }}>
          {isTaskMode ? (
            <div className="panel-content">
              <h3>📋 Описание задачи</h3>
              {block?.textContent && (
                <MarkdownContent content={block.textContent} />
              )}

              {/* ✅ УБРАНО: блок AI тест-кейсов */}
            </div>
          ) : (
            <div className="panel-content">
              <div className="welcome-content">
                <h2>🚀 Редактор кода Nareshka</h2>
                <p>
                  Добро пожаловать в онлайн-редактор кода! Здесь вы можете
                  решать задачи по программированию и улучшать свои навыки.
                </p>
              </div>

              {/* ✅ УБРАНО: блок AI тест-кейсов */}
            </div>
          )}
        </div>

        <div className="resizer" onMouseDown={handleMouseDown} />

        <div
          className="right-panel"
          style={{ width: `${100 - leftPanelWidth}%` }}
        >
          <div className="editor-wrapper">
            <CodeEditor
              key={`${blockId}-${normalizedLanguage}-${templateKey}`}
              blockId={blockId || undefined}
              initialCode={initialCode}
              initialLanguage={
                normalizedLanguage as 'JAVASCRIPT' | 'TYPESCRIPT' | 'PYTHON'
              }
            />
          </div>
        </div>
      </div>
    </div>
  );
};
