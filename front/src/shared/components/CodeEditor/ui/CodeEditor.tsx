import { Editor } from '@monaco-editor/react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  CheckCircle,
  Copy,
  Loader2,
  Play,
  Save,
  Settings,
  XCircle,
} from 'lucide-react';
import type { editor } from 'monaco-editor';
import { useCallback, useEffect, useRef, useState } from 'react';

import type {
  CodeExecutionRequest,
  CodeExecutionResponse,
} from '@/shared/api/code-editor';
import { codeEditorApi, codeEditorKeys } from '@/shared/api/code-editor';
import { useTheme } from '@/shared/context';
import styles from './CodeEditor.module.scss';

// Types
export interface CodeEditorProps {
  blockId?: string;
  initialCode?: string;
  initialLanguage?: string;
  onCodeChange?: (code: string) => void;
  onExecutionComplete?: (result: CodeExecutionResponse) => void;
  height?: string;
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

// Language Selector Component
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

// Code Execution Panel Component
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

// Main Code Editor Component
export const CodeEditor = ({
  blockId,
  initialCode = '',
  initialLanguage = 'PYTHON',
  onCodeChange,
  onExecutionComplete,
  height = '400px',
  readOnly = false,
  className = '',
}: CodeEditorProps) => {
  const { theme } = useTheme();
  const [code, setCode] = useState(initialCode);
  const [language, setLanguage] = useState(initialLanguage);
  const [stdin, setStdin] = useState('');
  const [currentExecution, setCurrentExecution] =
    useState<CodeExecutionResponse>();
  const [isExecuting, setIsExecuting] = useState(false);
  const [showSettings, setShowSettings] = useState(false);

  const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null);
  const queryClient = useQueryClient();

  // Load saved solution if blockId is provided
  const { data: solutions } = useQuery({
    queryKey: codeEditorKeys.blockSolutions(blockId || ''),
    queryFn: () =>
      blockId ? codeEditorApi.getBlockSolutions(blockId) : Promise.resolve([]),
    enabled: !!blockId,
  });

  // Save solution mutation
  const saveSolutionMutation = useMutation({
    mutationFn: codeEditorApi.saveSolution,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: codeEditorKeys.solutions() });
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

  // Update language when initialLanguage prop changes
  useEffect(() => {
    setLanguage(initialLanguage);
  }, [initialLanguage]);

  // Update code when initialCode prop changes
  useEffect(() => {
    setCode(initialCode);
  }, [initialCode]);

  // Load saved solution when data is available
  useEffect(() => {
    if (solutions && solutions.length > 0) {
      const savedSolution = solutions.find(
        (s) => s.supportedLanguage.language === language
      );
      if (savedSolution) {
        setCode(savedSolution.sourceCode);
      }
    }
  }, [solutions, language]);

  // Handle code changes
  const handleCodeChange = useCallback(
    (value: string | undefined) => {
      const newCode = value || '';
      setCode(newCode);
      onCodeChange?.(newCode);
    },
    [onCodeChange]
  );

  // Handle language change
  const handleLanguageChange = useCallback(
    (newLanguage: string) => {
      setLanguage(newLanguage);

      // Try to load saved solution for the new language
      if (solutions) {
        const savedSolution = solutions.find(
          (s) => s.supportedLanguage.language === newLanguage
        );
        if (savedSolution) {
          setCode(savedSolution.sourceCode);
        } else {
          // Set default code template for the language
          setCode(getDefaultCodeTemplate(newLanguage));
        }
      }
    },
    [solutions]
  );

  // Execute code
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

  // Save solution
  const handleSaveSolution = useCallback(() => {
    if (!blockId || !code.trim()) return;

    saveSolutionMutation.mutate({
      blockId,
      language,
      sourceCode: code,
      isCompleted: false,
    });
  }, [blockId, language, code, saveSolutionMutation]);

  // Monaco editor configuration
  const editorOptions: editor.IStandaloneEditorConstructionOptions = {
    minimap: { enabled: false },
    fontSize: 14,
    lineNumbers: 'on',
    roundedSelection: false,
    scrollBeyondLastLine: false,
    readOnly,
    automaticLayout: true,
    theme: theme === 'dark' ? 'vs-dark' : 'vs-light',
    wordWrap: 'on',
    tabSize: 2,
    insertSpaces: true,
    scrollbar: {
      verticalScrollbarSize: 8,
      horizontalScrollbarSize: 8,
    },
  };

  return (
    <div className={`${styles.codeEditorContainer} ${className}`}>
      {/* Editor Toolbar */}
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

          <button
            onClick={() => setShowSettings(!showSettings)}
            className={`${styles.toolbarButton} ${styles.settingsButton}`}
            title="Settings"
          >
            <Settings className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Settings Panel */}
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

      {/* Monaco Editor */}
      <div className={styles.editorWrapper} style={{ height }}>
        <Editor
          height="100%"
          language={getMonacoLanguage(language)}
          value={code}
          options={editorOptions}
          onChange={handleCodeChange}
          onMount={(editor) => {
            editorRef.current = editor;
          }}
        />
      </div>

      {/* Execution Results */}
      {(isExecuting || executeCodeMutation.isPending || currentExecution) && (
        <CodeExecutionPanel
          execution={currentExecution}
          isLoading={isExecuting || executeCodeMutation.isPending}
          onClear={() => setCurrentExecution(undefined)}
        />
      )}
    </div>
  );
};

// Helper functions
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
