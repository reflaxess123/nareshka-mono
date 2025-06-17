import { contentApi } from '@/shared/api/content';
import { Button, ButtonVariant } from '@/shared/components/Button';
import { CodeEditor } from '@/shared/components/CodeEditor';
import { MarkdownContent } from '@/shared/components/MarkdownContent';
import { PageWrapper } from '@/shared/components/PageWrapper/ui/PageWrapper';
import { codeTemplateGenerator } from '@/shared/utils/codeTemplateGenerator';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { ArrowLeft, CheckCircle, Code2, Info } from 'lucide-react';
import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import './CodeEditorPage.scss';

export const CodeEditorPage = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const blockId = searchParams.get('blockId');
  const templateFromUrl = searchParams.get('template');
  const languageFromUrl = searchParams.get('language');
  const processedFromUrl = searchParams.get('processed') === 'true';

  const [initialCode, setInitialCode] = useState('');
  const [language, setLanguage] = useState(() => {
    if (languageFromUrl) {
      return languageFromUrl.toUpperCase() as
        | 'JAVASCRIPT'
        | 'TYPESCRIPT'
        | 'PYTHON';
    }
    return 'JAVASCRIPT';
  });
  const [isTemplateGenerated, setIsTemplateGenerated] = useState(false);

  const {
    data: block,
    isLoading,
    error,
  } = useQuery({
    queryKey: ['content-block', blockId],
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

  const determineLanguageFromBlock = (block: {
    codeLanguage?: string;
    file: {
      mainCategory: string;
      subCategory: string;
    };
    codeContent?: string;
  }): string => {
    const isJSTask = codeTemplateGenerator.isJavaScriptTask(block);

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
        setIsTemplateGenerated(processedFromUrl);
      }
      return;
    }

    if (blockId && !isLoading) {
      if (block && block.codeContent) {
        const templateResult = codeTemplateGenerator.generateTemplate(block);
        const detectedLanguage = determineLanguageFromBlock(block);

        setInitialCode(templateResult.template);
        setLanguage(detectedLanguage as 'JAVASCRIPT' | 'TYPESCRIPT' | 'PYTHON');
        setIsTemplateGenerated(templateResult.isProcessed);
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
      setIsTemplateGenerated(false);
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
      setIsTemplateGenerated(false);

      const newSearchParams = new URLSearchParams(searchParams);
      newSearchParams.set('template', encodeURIComponent(block.codeContent));
      newSearchParams.set('language', detectedLanguage);
      newSearchParams.set('processed', 'false');
      navigate(`?${newSearchParams.toString()}`, { replace: true });
    }
  };

  const handleGenerateTemplate = () => {
    if (block) {
      const templateResult = codeTemplateGenerator.generateTemplate(block);
      const detectedLanguage = determineLanguageFromBlock(block);

      setInitialCode(templateResult.template);
      setLanguage(detectedLanguage as 'JAVASCRIPT' | 'TYPESCRIPT' | 'PYTHON');
      setIsTemplateGenerated(templateResult.isProcessed);

      const newSearchParams = new URLSearchParams(searchParams);
      newSearchParams.set(
        'template',
        encodeURIComponent(templateResult.template)
      );
      newSearchParams.set('language', detectedLanguage);
      newSearchParams.set('processed', templateResult.isProcessed.toString());
      navigate(`?${newSearchParams.toString()}`, { replace: true });
    }
  };

  const isTaskMode = !!blockId;
  const isJSTask = block
    ? codeTemplateGenerator.isJavaScriptTask(block)
    : false;

  if (isTaskMode && isLoading) {
    return (
      <PageWrapper>
        <div className="code-editor-page loading">
          <div className="loading-spinner">
            <Code2 className="animate-spin" size={32} />
            <p>Загрузка задачи...</p>
          </div>
        </div>
      </PageWrapper>
    );
  }

  if (isTaskMode && (error || !block)) {
    return (
      <PageWrapper>
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
      </PageWrapper>
    );
  }

  // Нормализуем язык для корректной работы с CodeEditor
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
    <PageWrapper>
      <div className="code-editor-page">
        <motion.div
          className="page-header"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <div className="header-content">
            <div className="header-left">
              {isTaskMode ? (
                <Button
                  onClick={handleBackToTasks}
                  variant={ButtonVariant.GHOST}
                  className="back-button"
                >
                  <ArrowLeft size={16} />
                  Назад к задачам
                </Button>
              ) : (
                <div className="header-text">
                  <h1>🚀 Редактор кода</h1>
                </div>
              )}
            </div>

            {isTaskMode && block && (
              <div className="header-center">
                <h1 className="task-title">{block.blockTitle}</h1>
                <div className="task-meta">
                  <span className="category">
                    {block.file.mainCategory} / {block.file.subCategory}
                  </span>
                  <span className="level">Уровень {block.blockLevel}</span>
                  {isJSTask && <span className="js-badge">JavaScript</span>}
                </div>
              </div>
            )}

            {isTaskMode && isJSTask && (
              <div className="header-right">
                <div className="template-controls">
                  <Button
                    onClick={handleGenerateTemplate}
                    variant={ButtonVariant.SECONDARY}
                    title="Создать заготовку кода"
                  >
                    <Code2 size={16} />
                    Заготовка
                  </Button>
                  <Button
                    onClick={handleResetToOriginal}
                    variant={ButtonVariant.GHOST}
                    title="Показать полное решение"
                  >
                    Полное решение
                  </Button>
                </div>
              </div>
            )}
          </div>

          {isTaskMode && isJSTask && (
            <div
              className={`template-status ${isTemplateGenerated ? 'template' : 'original'}`}
            >
              <div className="status-content">
                {isTemplateGenerated ? (
                  <>
                    <CheckCircle size={16} className="status-icon" />
                    <span>
                      Отображается заготовка кода - реализуйте недостающие части
                    </span>
                  </>
                ) : (
                  <>
                    <Info size={16} className="status-icon" />
                    <span>Отображается полное решение задачи</span>
                  </>
                )}
              </div>
            </div>
          )}
        </motion.div>

        {isTaskMode && block?.textContent && (
          <motion.div
            className="task-description"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
          >
            <h3>📋 Описание задачи</h3>
            <MarkdownContent content={block.textContent} />
          </motion.div>
        )}

        <motion.div
          className="editor-section"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <div className="editor-container">
            <CodeEditor
              key={`${blockId}-${isTemplateGenerated}-${initialCode.length}`}
              blockId={blockId || undefined}
              initialCode={initialCode}
              initialLanguage={
                normalizedLanguage as 'JAVASCRIPT' | 'TYPESCRIPT' | 'PYTHON'
              }
              // height="600px"
            />
          </div>
        </motion.div>
      </div>
    </PageWrapper>
  );
};
