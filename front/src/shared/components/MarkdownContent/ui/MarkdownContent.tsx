import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import styles from './MarkdownContent.module.scss';

interface MarkdownContentProps {
  content: string;
  className?: string;
  extractedUrls?: string[];
}

// Функция для обработки markdown-таблиц с подстановкой ссылок
const processTableWithLinks = (
  content: string,
  extractedUrls: string[] = []
): string => {
  if (
    !content.includes('|') ||
    !content.includes('---') ||
    extractedUrls.length === 0
  ) {
    return content;
  }

  let urlIndex = 0;
  const linkKeywords = [
    'пустой',
    'пустая версия',
    'empty',
    'blank',
    'готовый',
    'готовая версия',
    'ready',
    'complete',
    'решение',
  ];

  // Разбиваем контент на строки
  const lines = content.split('\n');
  let isHeaderProcessed = false;

  return lines
    .map((line) => {
      if (line.includes('---')) {
        isHeaderProcessed = true;
        return line;
      }

      // Если это строка таблицы (содержит |) и мы уже прошли заголовки
      if (line.includes('|') && isHeaderProcessed) {
        // Разбиваем строку на ячейки
        const cells = line.split('|').map((cell) => cell.trim());

        // Обрабатываем каждую ячейку
        const processedCells = cells.map((cell) => {
          // Проверяем, содержит ли ячейка ключевые слова для ссылок
          const lowerCell = cell.toLowerCase();
          const hasLinkKeyword = linkKeywords.some((keyword) =>
            lowerCell.includes(keyword.toLowerCase())
          );

          // Если ячейка содержит ключевое слово и есть доступные ссылки
          if (hasLinkKeyword && urlIndex < extractedUrls.length) {
            const url = extractedUrls[urlIndex];
            urlIndex++;

            // Создаем markdown-ссылку
            return `[${cell}](${url})`;
          }

          return cell;
        });

        return processedCells.join('|');
      }

      return line;
    })
    .join('\n');
};

export const MarkdownContent: React.FC<MarkdownContentProps> = ({
  content,
  className = '',
  extractedUrls = [],
}) => {
  const hasMarkdownTable = content.includes('|') && content.includes('---');

  if (hasMarkdownTable) {
    // Обрабатываем контент, подставляя ссылки в таблицу
    const processedContent = processTableWithLinks(content, extractedUrls);

    return (
      <div className={`${styles.markdownContent} ${className}`}>
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          components={{
            table: ({ children }) => (
              <table className={styles.table}>{children}</table>
            ),
            thead: ({ children }) => (
              <thead className={styles.thead}>{children}</thead>
            ),
            tbody: ({ children }) => (
              <tbody className={styles.tbody}>{children}</tbody>
            ),
            tr: ({ children }) => <tr className={styles.tr}>{children}</tr>,
            th: ({ children }) => <th className={styles.th}>{children}</th>,
            td: ({ children }) => <td className={styles.td}>{children}</td>,
            p: ({ children }) => <p className={styles.paragraph}>{children}</p>,
            a: ({ children, href }) => (
              <a
                className={styles.link}
                href={href}
                target="_blank"
                rel="noopener noreferrer"
              >
                {children}
              </a>
            ),
          }}
        >
          {processedContent}
        </ReactMarkdown>
      </div>
    );
  }

  return <div className={`${styles.textContent} ${className}`}>{content}</div>;
};
