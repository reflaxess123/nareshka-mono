import { Editor } from '@monaco-editor/react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  CheckCircle,
  Copy,
  Loader2,
  Play,
  Save,
  Settings,
  TestTube,
  XCircle,
} from 'lucide-react';
import type { editor } from 'monaco-editor';
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { toast } from 'react-toastify';

import type {
  CodeExecutionRequest,
  CodeExecutionResponse,
} from '@/shared/api/code-editor';
import { codeEditorApi, codeEditorKeys } from '@/shared/api/code-editor';
import { useTheme } from '@/shared/context';
import { useProgressTracking } from '@/shared/hooks/useProgressTracking';
import styles from './CodeEditor.module.scss';

// Types for validation result
interface TestResult {
  testCaseId?: string;
  testName?: string;
  passed: boolean;
  isPublic: boolean;
  input?: string;
  expectedOutput?: string;
  actualOutput?: string;
  error?: string;
}

interface ValidationResult {
  allTestsPassed: boolean;
  passedTests?: number;
  totalTests?: number;
  error?: string;
  testsResults?: TestResult[];
}

// Constants for localStorage keys
const VALIDATION_WARNING_KEY = 'nareshka_validation_warning_shown';

export interface CodeEditorProps {
  blockId?: string;
  initialCode?: string;
  initialLanguage?: string;
  onCodeChange?: (code: string) => void;
  onExecutionComplete?: (result: CodeExecutionResponse) => void;
  readOnly?: boolean;
  className?: string;
}

export interface CodeExecutionPanelProps {
  execution?: CodeExecutionResponse;
  isLoading?: boolean;
  onClear?: () => void;
}

export interface LanguageSelectorProps {
  selectedLanguage: string;
  onLanguageChange: (language: string) => void;
  className?: string;
}

export const LanguageSelector = ({
  selectedLanguage,
  onLanguageChange,
  className = '',
}: LanguageSelectorProps) => {
  const { data: languages = [], isLoading } = useQuery({
    queryKey: codeEditorKeys.languages(),
    queryFn: codeEditorApi.getSupportedLanguages,
  });

  if (isLoading) {
    return (
      <div className={`${styles.languageSelector} ${className}`}>
        <Loader2 className="w-4 h-4 animate-spin" />
        <span>Loading languages...</span>
      </div>
    );
  }

  return (
    <select
      value={selectedLanguage}
      onChange={(e) => onLanguageChange(e.target.value)}
      className={`${styles.languageSelector} ${className}`}
    >
      {languages.map((lang) => (
        <option key={lang.id} value={lang.language}>
          {lang.name} {lang.version}
        </option>
      ))}
    </select>
  );
};

export const CodeExecutionPanel = ({
  execution,
  isLoading = false,
  onClear,
}: CodeExecutionPanelProps) => {
  const [copied, setCopied] = useState<'stdout' | 'stderr' | ''>('');

  const handleCopy = (text: string | undefined, type: 'stdout' | 'stderr') => {
    if (!text) return;
    navigator.clipboard.writeText(text);
    setCopied(type);
    const timer = setTimeout(() => setCopied(''), 2000);
    return () => clearTimeout(timer);
  };

  const getStatusIcon = () => {
    if (
      isLoading ||
      execution?.status === 'PENDING' ||
      execution?.status === 'RUNNING'
    ) {
      return <Loader2 className="w-4 h-4 animate-spin text-blue-500" />;
    }
    if (execution?.status === 'SUCCESS') {
      return <CheckCircle className="w-4 h-4 text-green-500" />;
    }
    return <XCircle className="w-4 h-4 text-red-500" />;
  };

  const getStatusText = () => {
    if (isLoading) return 'Executing...';
    if (!execution) return '';

    switch (execution.status) {
      case 'PENDING':
        return 'Queued for execution';
      case 'RUNNING':
        return 'Running...';
      case 'SUCCESS':
        return `Completed in ${execution.executionTimeMs}ms`;
      case 'ERROR':
        return 'Execution failed';
      case 'TIMEOUT':
        return 'Execution timed out';
      case 'MEMORY_LIMIT':
        return 'Memory limit exceeded';
      default:
        return execution.status;
    }
  };

  return (
    <div className={styles.codeExecutionPanel}>
      <div className={styles.executionHeader}>
        <div className={styles.executionStatus}>
          {getStatusIcon()}
          <span>{getStatusText()}</span>
        </div>
        {onClear && (
          <button onClick={onClear} className={styles.clearButton}>
            Clear
          </button>
        )}
      </div>

      {execution?.stdout && (
        <div className={styles.executionOutput}>
          <div className={styles.outputHeader}>
            <h4>Output</h4>
            <button
              onClick={() => handleCopy(execution.stdout, 'stdout')}
              className={styles.copyButton}
            >
              {copied === 'stdout' ? (
                <CheckCircle size={14} />
              ) : (
                <Copy size={14} />
              )}
              <span>{copied === 'stdout' ? 'Copied!' : 'Copy'}</span>
            </button>
          </div>
          <pre className={styles.outputContent}>{execution.stdout}</pre>
        </div>
      )}

      {execution?.stderr && (
        <div className={styles.executionError}>
          <div className={styles.outputHeader}>
            <h4>Error</h4>
            <button
              onClick={() => handleCopy(execution.stderr, 'stderr')}
              className={styles.copyButton}
            >
              {copied === 'stderr' ? (
                <CheckCircle size={14} />
              ) : (
                <Copy size={14} />
              )}
              <span>{copied === 'stderr' ? 'Copied!' : 'Copy'}</span>
            </button>
          </div>
          <pre className={styles.errorContent}>{execution.stderr}</pre>
        </div>
      )}

      {execution?.errorMessage && (
        <div className={styles.executionError}>
          <div className={styles.outputHeader}>
            <h4>Error Message</h4>
          </div>
          <p className={styles.errorMessage}>{execution.errorMessage}</p>
        </div>
      )}

      {execution?.status === 'SUCCESS' && execution.executionTimeMs && (
        <div className={styles.executionStats}>
          <span>Time: {execution.executionTimeMs}ms</span>
          {execution.memoryUsedMB && (
            <span>Memory: {execution.memoryUsedMB}MB</span>
          )}
        </div>
      )}
    </div>
  );
};

export const CodeEditor = ({
  blockId,
  initialCode = '',
  initialLanguage = 'PYTHON',
  onCodeChange,
  onExecutionComplete,
  readOnly = false,
  className = '',
}: CodeEditorProps) => {
  const { theme } = useTheme();
  const [code, setCode] = useState(initialCode);
  const [language, setLanguage] = useState(initialLanguage);
  const [stdin, setStdin] = useState('');
  const [currentExecution, setCurrentExecution] =
    useState<CodeExecutionResponse>();
  const [validationResult, setValidationResult] = useState<ValidationResult>();
  const [isExecuting, setIsExecuting] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [codeOverridden, setCodeOverridden] = useState(false);

  const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null);
  const queryClient = useQueryClient();

  const { validateSolution, isValidating } = useProgressTracking({
    showToasts: true,
  });

  const { data: solutions } = useQuery({
    queryKey: codeEditorKeys.blockSolutions(blockId || ''),
    queryFn: () =>
      blockId ? codeEditorApi.getBlockSolutions(blockId) : Promise.resolve([]),
    enabled: !!blockId,
  });

  const saveSolutionMutation = useMutation({
    mutationFn: codeEditorApi.saveSolution,
    onSuccess: () => {
      // Show success notification
      toast.success('💾 Решение успешно сохранено!', {
        position: 'top-right',
        autoClose: 3000,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
      });

      // Invalidate queries to refresh data
      queryClient.invalidateQueries({ queryKey: codeEditorKeys.solutions() });
    },
    onError: (error) => {
      // Show error notification
      toast.error('❌ Не удалось сохранить решение', {
        position: 'top-right',
        autoClose: 5000,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
      });
      console.error('Save solution error:', error);
    },
  });

  const executeCodeMutation = useMutation({
    mutationFn: codeEditorApi.executeCode,
    onSuccess: async (execution) => {
      setIsExecuting(true);
      try {
        const finalResult = await codeEditorApi.pollExecutionResult(
          execution.id,
          (updatedResult) => {
            setCurrentExecution(updatedResult);
          }
        );
        setCurrentExecution(finalResult);
        onExecutionComplete?.(finalResult);
      } catch (error) {
        console.error('Execution polling failed:', error);
      } finally {
        setIsExecuting(false);
      }
    },
    onError: (error) => {
      console.error('Code execution failed:', error);
      setIsExecuting(false);
    },
  });

  useEffect(() => {
    setLanguage(initialLanguage);
  }, [initialLanguage]);

  useEffect(() => {
    if (initialCode !== code) {
      setCode(initialCode);
      setCodeOverridden(true);
    }
  }, [initialCode]);

  useEffect(() => {
    if (solutions && solutions.length > 0 && !codeOverridden) {
      const validSolutions = solutions.filter((s) => s && s.supportedLanguage);
      const savedSolution = validSolutions.find(
        (s) => s.supportedLanguage.language === language
      );
      if (savedSolution) {
        setCode(savedSolution.sourceCode);
      }
    }
  }, [solutions, language, codeOverridden]);

  const handleCodeChange = useCallback(
    (value: string | undefined) => {
      const newCode = value || '';
      setCode(newCode);
      setCodeOverridden(false);
      onCodeChange?.(newCode);
    },
    [onCodeChange]
  );

  const handleLanguageChange = useCallback(
    (newLanguage: string) => {
      setLanguage(newLanguage);

      if (solutions && !codeOverridden) {
        const validSolutions = solutions.filter(
          (s) => s && s.supportedLanguage
        );
        const savedSolution = validSolutions.find(
          (s) => s.supportedLanguage.language === newLanguage
        );
        if (savedSolution) {
          setCode(savedSolution.sourceCode);
        } else {
          setCode(getDefaultCodeTemplate(newLanguage));
        }
      }
    },
    [solutions, codeOverridden]
  );

  const handleExecuteCode = useCallback(() => {
    if (!code.trim()) return;

    const request: CodeExecutionRequest = {
      sourceCode: code,
      language,
      stdin: stdin || undefined,
      blockId,
    };

    executeCodeMutation.mutate(request);
  }, [code, language, stdin, blockId, executeCodeMutation]);

  const handleSaveSolution = useCallback(() => {
    if (!blockId || !code.trim()) return;

    saveSolutionMutation.mutate({
      blockId,
      language,
      sourceCode: code,
      isCompleted: false,
    });
  }, [blockId, language, code, saveSolutionMutation]);

  const handleValidateSolution = useCallback(() => {
    if (!blockId || !code.trim()) return;

    const hasSeenWarning = localStorage.getItem(VALIDATION_WARNING_KEY);

    if (!hasSeenWarning) {
      // Show warning toast
      toast.warning(
        '⚠️ Внимание! Валидация через тест-кейсы — экспериментальная функция и может допускать ошибки.',
        {
          position: 'top-center',
          autoClose: 8000,
          hideProgressBar: false,
          closeOnClick: true,
          pauseOnHover: true,
          draggable: true,
        }
      );

      localStorage.setItem(VALIDATION_WARNING_KEY, 'true');
    }

    validateSolution(
      {
        blockId,
        sourceCode: code,
        language,
      },
      {
        onSuccess: (result) => {
          setValidationResult(result);

          // Show additional notification for successful solution increment
          if (result.allTestsPassed) {
            toast.success(
              '🎯 Счетчик решений увеличен! Задача засчитана как решенная.',
              {
                position: 'top-right',
                autoClose: 4000,
                hideProgressBar: false,
                closeOnClick: true,
                pauseOnHover: true,
                draggable: true,
              }
            );
          }
        },
        onError: (error) => {
          console.error('❌ Validation failed:', error);
          setValidationResult({
            error: 'Validation failed: ' + error.message,
            allTestsPassed: false,
          });
        },
      }
    );
  }, [blockId, code, language, validateSolution]);

  const monacoTheme = theme === 'dark' ? 'vs-dark' : 'vs-light';

  const editorOptions: editor.IStandaloneEditorConstructionOptions = {
    minimap: { enabled: false },
    fontSize: 14,
    lineNumbers: 'on',
    roundedSelection: false,
    scrollBeyondLastLine: false,
    readOnly,
    automaticLayout: true,
    theme: monacoTheme,
    wordWrap: 'on',
    tabSize: 2,
    insertSpaces: true,
    scrollbar: {
      verticalScrollbarSize: 8,
      horizontalScrollbarSize: 8,
    },
  };

  useEffect(() => {
    if (editorRef.current) {
      const monacoTheme = theme === 'dark' ? 'vs-dark' : 'vs-light';
      editorRef.current.updateOptions({ theme: monacoTheme });
    }
  }, [theme]);

  const lineHeight = 22;
  const minLines = 5;
  const maxLines = 30;
  const codeLines = useMemo(() => code.split('\n').length, [code]);
  const editorHeight =
    Math.min(Math.max(codeLines, minLines), maxLines) * lineHeight; // +8px на паддинги/toolbar

  return (
    <div className={`${styles.codeEditorContainer} ${className}`}>
      <div className={styles.editorToolbar}>
        <div className={styles.toolbarLeft}>
          <LanguageSelector
            selectedLanguage={language}
            onLanguageChange={handleLanguageChange}
            className={styles.toolbarLanguage}
          />
        </div>

        <div className={styles.toolbarRight}>
          {blockId && (
            <button
              onClick={handleSaveSolution}
              disabled={saveSolutionMutation.isPending || !code.trim()}
              className={`${styles.toolbarButton} ${styles.saveButton}`}
              title="Save Solution"
            >
              <Save className="w-4 h-4" />
            </button>
          )}

          <button
            onClick={handleExecuteCode}
            disabled={
              isExecuting || executeCodeMutation.isPending || !code.trim()
            }
            className={`${styles.toolbarButton} ${styles.executeButton}`}
            title="Run Code"
          >
            {isExecuting || executeCodeMutation.isPending ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Play className="w-4 h-4" />
            )}
          </button>

          {blockId && (
            <button
              onClick={handleValidateSolution}
              disabled={isValidating || !code.trim()}
              className={`${styles.toolbarButton} ${styles.validateButton}`}
              title="Validate Solution Against Test Cases"
            >
              {isValidating ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <TestTube className="w-4 h-4" />
              )}
            </button>
          )}

          <button
            onClick={() => setShowSettings(!showSettings)}
            className={`${styles.toolbarButton} ${styles.settingsButton}`}
            title="Settings"
          >
            <Settings className="w-4 h-4" />
          </button>
        </div>
      </div>

      {showSettings && (
        <div className={styles.settingsPanel}>
          <div className={styles.settingGroup}>
            <label htmlFor="stdin-input">Input (stdin):</label>
            <textarea
              id="stdin-input"
              value={stdin}
              onChange={(e) => setStdin(e.target.value)}
              placeholder="Enter input for your program..."
              className={styles.stdinInput}
              rows={3}
            />
          </div>
        </div>
      )}

      <div className={styles.editorWrapper}>
        <Editor
          height={editorHeight}
          language={getMonacoLanguage(language)}
          value={code}
          options={editorOptions}
          onChange={handleCodeChange}
          onMount={(editor) => {
            editorRef.current = editor;
            const currentTheme = theme === 'dark' ? 'vs-dark' : 'vs-light';
            editor.updateOptions({ theme: currentTheme });
          }}
        />
      </div>

      {(isExecuting || executeCodeMutation.isPending || currentExecution) && (
        <CodeExecutionPanel
          execution={currentExecution}
          isLoading={isExecuting || executeCodeMutation.isPending}
          onClear={() => setCurrentExecution(undefined)}
        />
      )}

      {validationResult && (
        <div className={styles.validationPanel}>
          <div className={styles.validationHeader}>
            <div className={styles.validationStatus}>
              {validationResult.allTestsPassed ? (
                <CheckCircle className="w-4 h-4 text-green-500" />
              ) : (
                <XCircle className="w-4 h-4 text-red-500" />
              )}
              <span>
                {validationResult.allTestsPassed
                  ? `✅ All tests passed! (${validationResult.passedTests || 0}/${validationResult.totalTests || 0})`
                  : `❌ Tests failed: ${validationResult.passedTests || 0}/${validationResult.totalTests || 0}`}
              </span>
            </div>
            <button
              onClick={() => setValidationResult(undefined)}
              className={styles.clearButton}
            >
              Clear
            </button>
          </div>

          {validationResult.error && (
            <div className={styles.validationError}>
              <h4>Error:</h4>
              <p>{validationResult.error}</p>
            </div>
          )}

          {validationResult.testsResults && (
            <div className={styles.testResults}>
              <h4>Test Results:</h4>
              {validationResult.testsResults.map(
                (test: TestResult, index: number) => (
                  <div
                    key={test.testCaseId || index}
                    className={`${styles.testResult} ${
                      test.passed ? styles.testPassed : styles.testFailed
                    }`}
                  >
                    <div className={styles.testName}>
                      {test.passed ? '✅' : '❌'}{' '}
                      {test.testName || `Test ${index + 1}`}
                    </div>
                    {test.isPublic && (
                      <div className={styles.testDetails}>
                        {test.input && (
                          <div>
                            <strong>Input:</strong> {test.input}
                          </div>
                        )}
                        <div>
                          <strong>Expected:</strong> {test.expectedOutput}
                        </div>
                        {test.actualOutput && (
                          <div>
                            <strong>Actual:</strong> {test.actualOutput}
                          </div>
                        )}
                        {test.error && (
                          <div className={styles.testError}>
                            <strong>Error:</strong> {test.error}
                          </div>
                        )}
                      </div>
                    )}
                    {!test.isPublic && (
                      <div className={styles.testDetails}>
                        <em>Hidden test case</em>
                      </div>
                    )}
                  </div>
                )
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

function getMonacoLanguage(language: string): string {
  const languageMap: Record<string, string> = {
    PYTHON: 'python',
    JAVASCRIPT: 'javascript',
    TYPESCRIPT: 'typescript',
    JAVA: 'java',
    CPP: 'cpp',
    C: 'c',
    GO: 'go',
    RUST: 'rust',
    PHP: 'php',
    RUBY: 'ruby',
  };
  return languageMap[language] || 'plaintext';
}

function getDefaultCodeTemplate(language: string): string {
  const templates: Record<string, string> = {
    PYTHON: '# Write your Python code here\nprint("Hello, World!")',
    JAVASCRIPT:
      '// Write your JavaScript code here\nconsole.log("Hello, World!");',
    TYPESCRIPT:
      '// Write your TypeScript code here\nconsole.log("Hello, World!");',
    JAVA: 'public class Main {\n    public static void main(String[] args) {\n        System.out.println("Hello, World!");\n    }\n}',
    CPP: '#include <iostream>\nusing namespace std;\n\nint main() {\n    cout << "Hello, World!" << endl;\n    return 0;\n}',
    C: '#include <stdio.h>\n\nint main() {\n    printf("Hello, World!\\n");\n    return 0;\n}',
    GO: 'package main\n\nimport "fmt"\n\nfunc main() {\n    fmt.Println("Hello, World!")\n}',
    RUST: 'fn main() {\n    println!("Hello, World!");\n}',
    PHP: '<?php\necho "Hello, World!\\n";\n?>',
    RUBY: 'puts "Hello, World!"',
  };
  return templates[language] || '// Write your code here';
}
