import { CodeEditor } from '@/shared/components/CodeEditor';
import { PageWrapper } from '@/shared/components/PageWrapper/ui/PageWrapper';
import { motion } from 'framer-motion';
import './CodeEditorPage.scss';

export const CodeEditorPage = () => {
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
            <div className="header-text">
              <h1>🚀 Редактор кода</h1>
            </div>
          </div>
        </motion.div>

        <motion.div
          className="editor-section"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
        >
          <div className="editor-container">
            <CodeEditor
              initialCode={`# Добро пожаловать в редактор кода Nareshka!
# Попробуйте выполнить этот код

def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Вычисляем первые 10 чисел Фибоначчи
for i in range(10):
    print(f"F({i}) = {fibonacci(i)}")
`}
              initialLanguage="PYTHON"
              height="600px"
            />
          </div>
        </motion.div>
      </div>
    </PageWrapper>
  );
};
