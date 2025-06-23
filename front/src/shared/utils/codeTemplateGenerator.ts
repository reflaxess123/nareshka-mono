/**
 * 🚀 УЛУЧШЕННЫЙ ГЕНЕРАТОР ШАБЛОНОВ КОДА
 *
 * Поддерживает только JavaScript, TypeScript и React (JSX)
 *
 * Решает проблемы оригинального генератора:
 * ✅ Правильно парсит скобки, игнорируя строки и комментарии
 * ✅ Обрабатывает вложенные функции и структуры
 * ✅ Поддерживает современный JS/TS/JSX синтаксис
 * ✅ Обрабатывает все типы функций (стрелочные, методы, async)
 * ✅ Сохраняет структуру кода и комментарии
 */

interface ParsedToken {
  type: 'string' | 'comment' | 'brace_open' | 'brace_close' | 'other';
  value: string;
  line: number;
  column: number;
}

interface FunctionInfo {
  startLine: number;
  endLine: number;
  signature: string;
  type: 'function' | 'arrow' | 'method' | 'async';
  indentation: string;
}

export class CodeTemplateGenerator {
  /**
   * 🎯 ГЛАВНАЯ ФУНКЦИЯ: Генерирует шаблон кода
   */
  static generateTemplate(sourceCode: string, language: string): string {
    const generator = new CodeTemplateGenerator();
    return generator.processCode(sourceCode, language);
  }

  /**
   * Проверяет, является ли задача JavaScript/TypeScript (сохранен для совместимости)
   */
  static isJavaScriptTask(block: {
    codeLanguage?: string;
    file: { mainCategory: string; subCategory: string };
    codeContent?: string;
  }): boolean {
    // Проверяем язык кода
    if (block.codeLanguage) {
      const lang = block.codeLanguage.toLowerCase();
      return (
        lang === 'javascript' ||
        lang === 'js' ||
        lang === 'typescript' ||
        lang === 'ts' ||
        lang === 'jsx' ||
        lang === 'tsx' ||
        lang === 'react'
      );
    }

    // Проверяем категорию
    if (
      block.file?.mainCategory?.toLowerCase().includes('javascript') ||
      block.file?.subCategory?.toLowerCase().includes('javascript') ||
      block.file?.mainCategory?.toLowerCase().includes('react') ||
      block.file?.subCategory?.toLowerCase().includes('react')
    ) {
      return true;
    }

    // Проверяем содержимое кода на JS синтаксис
    if (block.codeContent) {
      const jsPatterns = [
        /function\s+\w+/,
        /const\s+\w+\s*=/,
        /let\s+\w+\s*=/,
        /var\s+\w+\s*=/,
        /class\s+\w+/,
        /=>\s*{/,
        /console\.log/,
        /require\(/,
        /import\s+/,
        /export\s+/,
        /<[A-Z]\w*/, // JSX компоненты
        /useState/,
        /useEffect/,
      ];

      return jsPatterns.some((pattern) => pattern.test(block.codeContent!));
    }

    return false;
  }

  /**
   * 📋 Основной метод обработки кода
   */
  processCode(sourceCode: string, language: string): string {
    if (!sourceCode || !sourceCode.trim()) {
      return this.getDefaultTemplate(language);
    }

    try {
      const lang = language.toLowerCase();
      if (
        [
          'javascript',
          'js',
          'typescript',
          'ts',
          'jsx',
          'tsx',
          'react',
        ].includes(lang)
      ) {
        return this.processJavaScript(sourceCode);
      }

      // Для неподдерживаемых языков возвращаем оригинальный код
      console.warn(
        `Language ${language} not supported, returning original code`
      );
      return sourceCode;
    } catch (error) {
      console.warn(
        'Template generation failed, returning original code:',
        error
      );
      return sourceCode;
    }
  }

  /**
   * 🔧 ОБРАБОТКА JAVASCRIPT/TYPESCRIPT/JSX (УЛУЧШЕННАЯ ВЕРСИЯ)
   */
  private processJavaScript(code: string): string {
    const lines = code.split('\n');
    const tokens = this.tokenize(code);

    // Находим все функции в коде
    const functions = this.findJavaScriptFunctions(lines, tokens);

    // Если функции не найдены, возвращаем дефолтный шаблон
    if (functions.length === 0) {
      return this.getDefaultTemplate('javascript');
    }

    // Обрабатываем функции, заменяя их содержимое на шаблоны
    const template = this.replaceFunctionBodies(lines, functions);

    // Валидируем результат
    const validation = this.validateResult(template);

    if (!validation.isValid) {
      console.warn('Проблемы с генерацией шаблона:', validation.issues);

      // Если критические ошибки со скобками, используем fallback
      if (validation.issues.some((issue) => issue.includes('скобок'))) {
        return this.createSimpleFallbackTemplate(code);
      }
    }

    return template;
  }

  /**
   * 🛡️ ПРОСТОЙ FALLBACK ШАБЛОН
   */
  private createSimpleFallbackTemplate(code: string): string {
    const lines = code.split('\n');
    const firstLine = lines[0] || '';

    // Пытаемся извлечь сигнатуру первой функции
    const funcMatch = firstLine.match(
      /^(\s*)(async\s+)?(function\s+\w+|const\s+\w+\s*=|class\s+\w+|\w+\s*\()/
    );

    if (funcMatch) {
      const indentation = funcMatch[1] || '';

      // Определяем тип функции для правильного шаблона
      if (firstLine.includes('class ')) {
        return firstLine.replace(
          /\{.*/,
          '{\n' + indentation + '  // Implement class\n' + indentation + '}'
        );
      } else if (firstLine.includes('function ') || firstLine.includes('(')) {
        return firstLine.replace(
          /\{.*/,
          '{\n' + indentation + '  // Implement function\n' + indentation + '}'
        );
      }
    }

    // Если ничего не получилось, возвращаем базовый шаблон
    return this.getDefaultTemplate('javascript');
  }

  /**
   * 🔍 ТОКЕНИЗАЦИЯ: Разбивает код на токены с учетом строк и комментариев
   */
  private tokenize(code: string): ParsedToken[] {
    const tokens: ParsedToken[] = [];
    const lines = code.split('\n');

    for (let lineNum = 0; lineNum < lines.length; lineNum++) {
      const line = lines[lineNum];
      let col = 0;

      while (col < line.length) {
        const char = line[col];

        // Обработка строк в двойных кавычках
        if (char === '"') {
          const [token, newCol] = this.parseString(line, col, '"', lineNum);
          tokens.push(token);
          col = newCol;
          continue;
        }

        // Обработка строк в одинарных кавычках
        if (char === "'") {
          const [token, newCol] = this.parseString(line, col, "'", lineNum);
          tokens.push(token);
          col = newCol;
          continue;
        }

        // Обработка шаблонных литералов
        if (char === '`') {
          const [token, newCol] = this.parseString(line, col, '`', lineNum);
          tokens.push(token);
          col = newCol;
          continue;
        }

        // Обработка однострочных комментариев
        if (char === '/' && col + 1 < line.length && line[col + 1] === '/') {
          tokens.push({
            type: 'comment',
            value: line.substring(col),
            line: lineNum,
            column: col,
          });
          break; // Остальная часть строки - комментарий
        }

        // Обработка многострочных комментариев
        if (char === '/' && col + 1 < line.length && line[col + 1] === '*') {
          const [token, newCol, shouldBreak] = this.parseMultilineComment(
            lines,
            lineNum,
            col
          );
          tokens.push(token);
          if (shouldBreak) break;
          col = newCol;
          continue;
        }

        // Обработка фигурных скобок
        if (char === '{') {
          tokens.push({
            type: 'brace_open',
            value: char,
            line: lineNum,
            column: col,
          });
          col++;
          continue;
        }

        if (char === '}') {
          tokens.push({
            type: 'brace_close',
            value: char,
            line: lineNum,
            column: col,
          });
          col++;
          continue;
        }

        // Прочие символы
        tokens.push({
          type: 'other',
          value: char,
          line: lineNum,
          column: col,
        });
        col++;
      }
    }

    return tokens;
  }

  /**
   * 📝 ПАРСИНГ СТРОК
   */
  private parseString(
    line: string,
    startCol: number,
    quote: string,
    lineNum: number
  ): [ParsedToken, number] {
    let col = startCol + 1; // Пропускаем открывающую кавычку
    let value = quote;

    while (col < line.length) {
      const char = line[col];

      if (char === '\\') {
        // Экранированный символ
        value += char;
        col++;
        if (col < line.length) {
          value += line[col];
          col++;
        }
        continue;
      }

      value += char;

      if (char === quote) {
        // Конец строки
        col++;
        break;
      }

      col++;
    }

    return [
      {
        type: 'string',
        value,
        line: lineNum,
        column: startCol,
      },
      col,
    ];
  }

  /**
   * 💬 ПАРСИНГ МНОГОСТРОЧНЫХ КОММЕНТАРИЕВ
   */
  private parseMultilineComment(
    lines: string[],
    startLine: number,
    startCol: number
  ): [ParsedToken, number, boolean] {
    let lineNum = startLine;
    let col = startCol + 2; // Пропускаем /*
    let value = '/*';

    while (lineNum < lines.length) {
      const line = lines[lineNum];

      while (col < line.length) {
        const char = line[col];
        value += char;

        if (char === '*' && col + 1 < line.length && line[col + 1] === '/') {
          value += '/';
          col += 2; // Пропускаем */
          return [
            {
              type: 'comment',
              value,
              line: startLine,
              column: startCol,
            },
            col,
            false,
          ];
        }

        col++;
      }

      lineNum++;
      col = 0;
      if (lineNum < lines.length) {
        value += '\n';
      }
    }

    // Комментарий не закрыт
    return [
      {
        type: 'comment',
        value,
        line: startLine,
        column: startCol,
      },
      col,
      true,
    ];
  }

  /**
   * 🔍 ПОИСК ФУНКЦИЙ В JAVASCRIPT/TYPESCRIPT
   */
  private findJavaScriptFunctions(
    lines: string[],
    tokens: ParsedToken[]
  ): FunctionInfo[] {
    const functions: FunctionInfo[] = [];

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const funcMatch = this.matchFunction(line);

      if (funcMatch) {
        const endLine = this.findFunctionEnd(lines, tokens, i);

        if (endLine > i) {
          functions.push({
            startLine: i,
            endLine,
            signature: funcMatch.signature,
            type: funcMatch.type,
            indentation: funcMatch.indentation,
          });
        }
      }
    }

    return functions;
  }

  /**
   * 🎯 РАСПОЗНАВАНИЕ ФУНКЦИЙ (УЛУЧШЕННАЯ ВЕРСИЯ)
   */
  private matchFunction(line: string): {
    signature: string;
    type: 'function' | 'arrow' | 'method' | 'async';
    indentation: string;
  } | null {
    const trimmed = line.trim();

    // Получаем отступы
    const indentMatch = line.match(/^(\s*)/);
    const indentation = indentMatch ? indentMatch[1] : '';

    // Исключаем строки, которые не могут быть функциями
    if (
      trimmed.startsWith('//') ||
      trimmed.startsWith('/*') ||
      trimmed.startsWith('*') ||
      trimmed.includes('return ') ||
      trimmed.startsWith('if') ||
      trimmed.startsWith('for') ||
      trimmed.startsWith('while') ||
      trimmed.startsWith('switch') ||
      trimmed.startsWith('else') ||
      trimmed.startsWith('catch') ||
      trimmed.startsWith('try') ||
      !line.includes('{')
    ) {
      return null;
    }

    // 1. Function declarations
    const funcDeclaration = line.match(
      /^(\s*)(async\s+)?function\s+(\w+)\s*\([^)]*\)\s*\{/
    );
    if (funcDeclaration) {
      return {
        signature: line,
        type: funcDeclaration[2] ? 'async' : 'function',
        indentation,
      };
    }

    // 2. Arrow functions (улучшенная версия)
    const arrowFunc = line.match(
      /^(\s*)(const|let|var)\s+(\w+)\s*=\s*(async\s+)?(\([^)]*\)|\w+)\s*=>\s*\{/
    );
    if (arrowFunc) {
      return {
        signature: line,
        type: arrowFunc[4] ? 'async' : 'arrow',
        indentation,
      };
    }

    // 3. Class methods (улучшенная проверка)
    const classMethod = line.match(
      /^(\s*)(static\s+)?(async\s+)?(\w+)\s*\([^)]*\)\s*\{/
    );
    if (classMethod) {
      return {
        signature: line,
        type: classMethod[3] ? 'async' : 'method',
        indentation,
      };
    }

    // 4. Object methods
    const objectMethod = line.match(
      /^(\s*)(\w+):\s*(async\s+)?function\s*\([^)]*\)\s*\{/
    );
    if (objectMethod) {
      return {
        signature: line,
        type: objectMethod[3] ? 'async' : 'method',
        indentation,
      };
    }

    // 5. Object method shorthand
    const objectMethodShorthand = line.match(
      /^(\s*)(async\s+)?(\w+)\s*\([^)]*\)\s*\{/
    );
    if (objectMethodShorthand && !trimmed.includes('class ')) {
      return {
        signature: line,
        type: objectMethodShorthand[2] ? 'async' : 'method',
        indentation,
      };
    }

    // 6. Anonymous function assignments
    const anonFunc = line.match(
      /^(\s*)(const|let|var)\s+(\w+)\s*=\s*(async\s+)?function\s*\([^)]*\)\s*\{/
    );
    if (anonFunc) {
      return {
        signature: line,
        type: anonFunc[4] ? 'async' : 'function',
        indentation,
      };
    }

    return null;
  }

  /**
   * 🔍 ПОИСК КОНЦА ФУНКЦИИ (ИСПРАВЛЕННАЯ ВЕРСИЯ)
   */
  private findFunctionEnd(
    lines: string[],
    tokens: ParsedToken[],
    startLine: number
  ): number {
    let braceCount = 0;
    let foundFirstBrace = false;

    // Найдем все токены начиная со startLine
    const relevantTokens = tokens.filter((token) => token.line >= startLine);

    for (const token of relevantTokens) {
      // Учитываем только скобки в коде (не в строках и комментариях)
      if (token.type === 'brace_open') {
        braceCount++;
        foundFirstBrace = true;
      } else if (token.type === 'brace_close') {
        braceCount--;

        // Если нашли соответствующую закрывающую скобку
        if (foundFirstBrace && braceCount === 0) {
          return token.line;
        }
      }
    }

    // Если токенизация не помогла, используем fallback
    return this.findFunctionEndFallback(lines, startLine);
  }

  /**
   * 🔧 FALLBACK МЕТОД ПОИСКА КОНЦА ФУНКЦИИ
   */
  private findFunctionEndFallback(lines: string[], startLine: number): number {
    let braceCount = 0;
    let foundFirstBrace = false;

    for (let i = startLine; i < lines.length; i++) {
      const line = lines[i];
      let inString = false;
      let stringChar = '';
      let inComment = false;

      for (let j = 0; j < line.length; j++) {
        const char = line[j];
        const nextChar = line[j + 1];

        // Обработка однострочных комментариев
        if (!inString && char === '/' && nextChar === '/') {
          inComment = true;
          break; // Остальная часть строки - комментарий
        }

        // Обработка строк
        if (
          !inComment &&
          !inString &&
          (char === '"' || char === "'" || char === '`')
        ) {
          inString = true;
          stringChar = char;
        } else if (inString && char === stringChar && line[j - 1] !== '\\') {
          inString = false;
          stringChar = '';
        }

        // Считаем скобки только вне строк и комментариев
        if (!inString && !inComment) {
          if (char === '{') {
            braceCount++;
            foundFirstBrace = true;
          } else if (char === '}') {
            braceCount--;

            if (foundFirstBrace && braceCount === 0) {
              return i;
            }
          }
        }
      }
    }

    return startLine; // Если не нашли конец
  }

  /**
   * 🔄 ЗАМЕНА ТЕЛА ФУНКЦИЙ НА ШАБЛОНЫ (ИСПРАВЛЕННАЯ ВЕРСИЯ)
   */
  private replaceFunctionBodies(
    lines: string[],
    functions: FunctionInfo[]
  ): string {
    const result = [...lines];

    // Обрабатываем функции в обратном порядке, чтобы не сбить индексы
    functions
      .sort((a, b) => b.startLine - a.startLine)
      .forEach((func) => {
        // Проверяем корректность границ функции
        if (func.endLine <= func.startLine || func.endLine >= result.length) {
          console.warn(
            `Некорректные границы функции: ${func.startLine}-${func.endLine}`
          );
          return;
        }

        const commentLine = func.indentation + '  // Implement function';

        // Получаем первую строку функции (с сигнатурой)
        const functionSignature = result[func.startLine];

        // Находим позицию открывающей скобки
        const openBraceIndex = functionSignature.indexOf('{');

        if (openBraceIndex === -1) {
          console.warn(
            `Не найдена открывающая скобка в функции на строке ${func.startLine}`
          );
          return;
        }

        // Создаем новую строку с сигнатурой и комментарием
        const signatureWithComment =
          functionSignature.substring(0, openBraceIndex + 1) +
          '\n' +
          commentLine +
          '\n' +
          func.indentation +
          '}';

        // Заменяем всю функцию на новый шаблон
        const linesToRemove = func.endLine - func.startLine;
        result.splice(func.startLine, linesToRemove + 1, signatureWithComment);
      });

    return result.join('\n');
  }

  /**
   * ✅ ВАЛИДАЦИЯ РЕЗУЛЬТАТА
   */
  private validateResult(template: string): {
    isValid: boolean;
    issues: string[];
  } {
    const issues: string[] = [];

    // Проверка соответствия скобок
    const openBraces = (template.match(/\{/g) || []).length;
    const closeBraces = (template.match(/\}/g) || []).length;

    if (openBraces !== closeBraces) {
      issues.push(
        `Несоответствие скобок: ${openBraces} открывающих, ${closeBraces} закрывающих`
      );
    }

    // Проверка на наличие комментариев
    if (!template.includes('// Implement')) {
      issues.push('Отсутствуют комментарии для реализации');
    }

    // Проверка на наличие подряд идущих скобок (признак ошибки)
    if (template.includes('}}') || template.includes('{ }')) {
      issues.push('Найдены подозрительные комбинации скобок');
    }

    return {
      isValid: issues.length === 0,
      issues,
    };
  }

  /**
   * 📝 ШАБЛОН ПО УМОЛЧАНИЮ
   */
  private getDefaultTemplate(language: string): string {
    const lang = language.toLowerCase();

    if (
      ['javascript', 'js', 'typescript', 'ts', 'jsx', 'tsx', 'react'].includes(
        lang
      )
    ) {
      return `function solution() {
  // Implement your solution here
  return null;
}`;
    }

    return '// Write your code here';
  }
}
