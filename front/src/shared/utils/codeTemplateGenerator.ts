export interface TaskTemplateOptions {
  removeImplementation: boolean;
  keepComments: boolean;
  keepExamples: boolean;
  addTodoComments: boolean;
}

export interface TemplateResult {
  template: string;
  language: string;
  isProcessed: boolean; // true если была обработка, false если просто скопировано
}

/**
 * Генератор заготовок кода для задач
 * Улучшен на основе анализа 269 реальных задач
 */
export class CodeTemplateGenerator {
  private readonly JS_CATEGORIES = [
    'JS ТЕОРИЯ',
    'REACT',
    'NODE.JS',
    'TYPESCRIPT',
    'JS',
  ];

  private readonly JS_LANGUAGES = ['javascript', 'typescript', 'js', 'ts'];

  /**
   * Определяет, является ли задача JavaScript-задачей
   */
  isJavaScriptTask(block: {
    codeLanguage?: string;
    file: {
      mainCategory: string;
      subCategory: string;
    };
    codeContent?: string;
  }): boolean {
    // 1. Проверяем язык кода
    if (block.codeLanguage) {
      const lang = block.codeLanguage.toLowerCase();
      if (this.JS_LANGUAGES.includes(lang)) {
        return true;
      }
    }

    // 2. Проверяем категории файла
    const mainCat = block.file.mainCategory?.toUpperCase();
    const subCat = block.file.subCategory?.toUpperCase();

    if (
      this.JS_CATEGORIES.some(
        (cat) => mainCat?.includes(cat) || subCat?.includes(cat)
      )
    ) {
      return true;
    }

    // 3. Эвристическая проверка содержимого кода
    if (block.codeContent) {
      return this.detectJavaScriptSyntax(block.codeContent);
    }

    return false;
  }

  /**
   * Определяет JS синтаксис в коде эвристически
   */
  private detectJavaScriptSyntax(code: string): boolean {
    const jsPatterns = [
      /class\s+\w+/,
      /function\s+\w+\s*\(/,
      /const\s+\w+\s*=/,
      /let\s+\w+\s*=/,
      /=>\s*{/,
      /console\.log/,
      /require\(/,
      /import\s+.*from/,
      /export\s+(default|const|function|class)/,
    ];

    return jsPatterns.some((pattern) => pattern.test(code));
  }

  /**
   * Генерирует заготовку кода
   */
  generateTemplate(block: {
    codeContent?: string;
    codeLanguage?: string;
    file: {
      mainCategory: string;
      subCategory: string;
    };
  }): TemplateResult {
    if (!block.codeContent) {
      return {
        template: '// Код задачи не найден',
        language: block.codeLanguage || 'javascript',
        isProcessed: false,
      };
    }

    // Определяем, нужна ли обработка
    if (this.isJavaScriptTask(block)) {
      return {
        template: this.processJavaScriptCode(block.codeContent),
        language: block.codeLanguage || 'javascript',
        isProcessed: true,
      };
    } else {
      // Для не-JS задач просто копируем код
      return {
        template: block.codeContent,
        language: block.codeLanguage || 'text',
        isProcessed: false,
      };
    }
  }

  /**
   * Обрабатывает JavaScript код и создает заготовку
   * КАРДИНАЛЬНО УЛУЧШЕН на основе анализа реальных данных
   */
  private processJavaScriptCode(code: string): string {
    // ЭТАП 1: Предварительная очистка и нормализация
    const cleanedCode = this.preprocessCode(code);

    // ЭТАП 2: Умное разделение на блоки
    const parts = this.smartSplitCode(cleanedCode);

    // ЭТАП 3: Обработка каждого типа блоков
    const result: string[] = [];

    // Обрабатываем классы
    parts.classes.forEach((classCode) => {
      result.push(this.processClassAdvanced(classCode));
    });

    // Обрабатываем функции
    parts.functions.forEach((funcCode) => {
      result.push(this.processFunctionAdvanced(funcCode));
    });

    // Добавляем остальной код (импорты, комментарии)
    if (parts.other.trim()) {
      result.push(parts.other.trim());
    }

    // Добавляем примеры в конце
    if (parts.examples.length > 0) {
      result.push('');
      parts.examples.forEach((example) => {
        result.push(example.trim());
      });
    }

    return result.join('\n\n').trim();
  }

  /**
   * НОВЫЙ: Предварительная обработка кода
   * Решает проблемы с комментариями и сложным синтаксисом
   */
  private preprocessCode(code: string): string {
    let processed = code;

    // 1. Временно заменяем строки и регулярные выражения
    const stringReplacements = new Map<string, string>();
    let stringCounter = 0;

    // Заменяем строки в кавычках
    processed = processed.replace(/"[^"]*"/g, (match) => {
      const placeholder = `__STRING_${stringCounter++}__`;
      stringReplacements.set(placeholder, match);
      return placeholder;
    });

    // Заменяем строки в одинарных кавычках
    processed = processed.replace(/'[^']*'/g, (match) => {
      const placeholder = `__STRING_${stringCounter++}__`;
      stringReplacements.set(placeholder, match);
      return placeholder;
    });

    // Заменяем шаблонные строки
    processed = processed.replace(/`[^`]*`/g, (match) => {
      const placeholder = `__TEMPLATE_${stringCounter++}__`;
      stringReplacements.set(placeholder, match);
      return placeholder;
    });

    // Заменяем регулярные выражения
    processed = processed.replace(/\/[^/\n]+\/[gimuy]*/g, (match) => {
      const placeholder = `__REGEX_${stringCounter++}__`;
      stringReplacements.set(placeholder, match);
      return placeholder;
    });

    // 2. Обрабатываем комментарии более аккуратно
    // Удаляем блочные комментарии
    processed = processed.replace(/\/\*[\s\S]*?\*\//g, '');

    // Обрабатываем строчные комментарии - сохраняем только важные
    processed = processed.replace(/\/\/.*$/gm, (match) => {
      const comment = match.toLowerCase();
      // Сохраняем комментарии с примерами
      if (
        comment.includes('пример') ||
        comment.includes('example') ||
        comment.includes('использование') ||
        comment.includes('usage') ||
        comment.includes('тест') ||
        comment.includes('test')
      ) {
        return match;
      }
      // Удаляем остальные комментарии
      return '';
    });

    // 3. Восстанавливаем строки и регулярки
    for (const [placeholder, original] of stringReplacements) {
      processed = processed.replace(placeholder, original);
    }

    return processed;
  }

  /**
   * НОВЫЙ: Умное разделение кода на блоки
   * Учитывает сложные случаи из анализа
   */
  private smartSplitCode(code: string): {
    classes: string[];
    functions: string[];
    examples: string[];
    other: string;
  } {
    const result = {
      classes: [] as string[],
      functions: [] as string[],
      examples: [] as string[],
      other: '',
    };

    const lines = code.split('\n');
    let currentBlock = '';
    let blockType: 'class' | 'function' | 'example' | 'other' = 'other';
    let braceCount = 0;
    let inExample = false;
    let skipUntilBraceBalance = false;

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const trimmed = line.trim();

      // Пропускаем пустые строки в начале блоков
      if (!trimmed && !currentBlock.trim()) {
        continue;
      }

      // Проверяем начало примера
      if (this.isExampleLineAdvanced(trimmed)) {
        this.saveCurrentBlock(result, blockType, currentBlock);
        inExample = true;
        blockType = 'example';
        currentBlock = line;
        continue;
      }

      // Если в примере, продолжаем до конца файла
      if (inExample) {
        currentBlock += '\n' + line;
        continue;
      }

      // Проверяем начало класса (улучшенная логика)
      if (braceCount === 0 && this.isClassStart(trimmed)) {
        this.saveCurrentBlock(result, blockType, currentBlock);
        blockType = 'class';
        currentBlock = line;
        braceCount = this.countBraces(line).open;
        skipUntilBraceBalance = braceCount > 0;
        continue;
      }

      // Проверяем начало функции (улучшенная логика)
      if (braceCount === 0 && this.isFunctionStartAdvanced(trimmed)) {
        this.saveCurrentBlock(result, blockType, currentBlock);
        blockType = 'function';
        currentBlock = line;
        braceCount = this.countBraces(line).open;
        skipUntilBraceBalance = braceCount > 0;
        continue;
      }

      // Добавляем строку к текущему блоку
      currentBlock += (currentBlock ? '\n' : '') + line;

      // Считаем скобки для классов и функций
      if (blockType === 'class' || blockType === 'function') {
        const braces = this.countBraces(line);
        braceCount += braces.open - braces.close;

        // Если блок закончился
        if (braceCount <= 0 && skipUntilBraceBalance) {
          this.saveCurrentBlock(result, blockType, currentBlock);
          currentBlock = '';
          blockType = 'other';
          skipUntilBraceBalance = false;
        }
      }
    }

    // Добавляем последний блок
    this.saveCurrentBlock(result, blockType, currentBlock);

    return result;
  }

  /**
   * НОВЫЙ: Улучшенное определение примеров
   */
  private isExampleLineAdvanced(line: string): boolean {
    const exampleMarkers = [
      '// пример',
      '// example',
      '// использование',
      '// usage',
      '// тест',
      '// test',
      'console.log(',
      'console.error(',
      'console.warn(',
    ];

    const lowerLine = line.toLowerCase();
    return exampleMarkers.some((marker) => lowerLine.includes(marker));
  }

  /**
   * НОВЫЙ: Улучшенное определение начала класса
   */
  private isClassStart(line: string): boolean {
    // Учитываем наследование и экспорты
    return /^(export\s+)?(default\s+)?class\s+\w+(\s+extends\s+\w+)?\s*{?/.test(
      line
    );
  }

  /**
   * НОВЫЙ: Улучшенное определение начала функции
   */
  private isFunctionStartAdvanced(line: string): boolean {
    // Обычные функции
    if (/^(export\s+)?(default\s+)?function\s+\w+\s*\(/.test(line)) {
      return true;
    }

    // Стрелочные функции с const/let
    if (/^(const|let|var)\s+\w+\s*=\s*(\([^)]*\)\s*)?=>\s*{?/.test(line)) {
      return true;
    }

    // Функции как значения
    if (/^(const|let|var)\s+\w+\s*=\s*function\s*\(/.test(line)) {
      return true;
    }

    // Асинхронные функции
    if (/^(export\s+)?(default\s+)?async\s+function\s+\w+\s*\(/.test(line)) {
      return true;
    }

    return false;
  }

  /**
   * НОВЫЙ: Точный подсчет скобок
   */
  private countBraces(line: string): { open: number; close: number } {
    // Исключаем скобки в строках и комментариях
    let cleanLine = line;

    // Удаляем строки
    cleanLine = cleanLine.replace(/"[^"]*"/g, '');
    cleanLine = cleanLine.replace(/'[^']*'/g, '');
    cleanLine = cleanLine.replace(/`[^`]*`/g, '');

    // Удаляем комментарии
    cleanLine = cleanLine.replace(/\/\/.*$/, '');
    cleanLine = cleanLine.replace(/\/\*.*?\*\//, '');

    const open = (cleanLine.match(/{/g) || []).length;
    const close = (cleanLine.match(/}/g) || []).length;

    return { open, close };
  }

  /**
   * НОВЫЙ: Сохранение блока с проверками
   */
  private saveCurrentBlock(
    result: {
      classes: string[];
      functions: string[];
      examples: string[];
      other: string;
    },
    blockType: string,
    content: string
  ) {
    const trimmedContent = content.trim();
    if (!trimmedContent) return;

    if (blockType === 'other') {
      result.other += (result.other ? '\n' : '') + trimmedContent;
    } else if (blockType === 'class') {
      result.classes.push(trimmedContent);
    } else if (blockType === 'function') {
      result.functions.push(trimmedContent);
    } else if (blockType === 'example') {
      result.examples.push(trimmedContent);
    }
  }

  /**
   * НОВЫЙ: Продвинутая обработка классов
   * Учитывает async методы, геттеры/сеттеры, статические методы
   */
  private processClassAdvanced(classCode: string): string {
    const lines = classCode.split('\n');
    const result: string[] = [];
    let insideMethod = false;
    let methodBraceCount = 0;
    let methodIndent = '';

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const trimmed = line.trim();

      // Пропускаем пустые строки
      if (!trimmed) {
        if (!insideMethod) {
          result.push(line);
        }
        continue;
      }

      // Если это начало метода (улучшенная логика)
      if (!insideMethod && this.isMethodStartAdvanced(trimmed)) {
        insideMethod = true;
        methodBraceCount = 0;
        methodIndent = line.match(/^(\s*)/)?.[1] || '    ';
        result.push(line);

        // Считаем скобки в строке объявления метода
        const braces = this.countBraces(line);
        methodBraceCount += braces.open - braces.close;

        // Если метод объявлен без открывающей скобки на той же строке
        if (braces.open === 0) {
          // Ищем открывающую скобку в следующих строках
          let j = i + 1;
          while (j < lines.length && methodBraceCount === 0) {
            const nextLine = lines[j];
            const nextBraces = this.countBraces(nextLine);
            methodBraceCount += nextBraces.open - nextBraces.close;
            if (nextBraces.open > 0) {
              result.push(nextLine); // Добавляем строку с открывающей скобкой
              i = j; // Пропускаем эту строку в основном цикле
              break;
            }
            j++;
          }
        }

        // Если метод закрыт на той же строке (однострочный)
        if (methodBraceCount <= 0 && braces.open > 0 && braces.close > 0) {
          result.push(methodIndent + '    // TODO: Implement');
          insideMethod = false;
        }
        continue;
      }

      if (insideMethod) {
        // Считаем скобки метода
        const braces = this.countBraces(line);
        methodBraceCount += braces.open - braces.close;

        // Если метод закончился (закрывающая скобка)
        if (methodBraceCount <= 0 && braces.close > 0) {
          result.push(methodIndent + '    // TODO: Implement');
          result.push(line); // Добавляем закрывающую скобку
          insideMethod = false;
          continue;
        }

        // Пропускаем все содержимое метода (не добавляем в result)
        continue;
      }

      // Обычные строки (объявление класса, поля, комментарии)
      result.push(line);
    }

    return result.join('\n');
  }

  /**
   * НОВЫЙ: Улучшенное определение начала метода
   */
  private isMethodStartAdvanced(line: string): boolean {
    const trimmed = line.trim();

    // Пропускаем комментарии и пустые строки
    if (trimmed.startsWith('//') || trimmed.startsWith('/*') || !trimmed) {
      return false;
    }

    // Пропускаем объявления полей класса
    if (/^\w+\s*[=:;]/.test(trimmed)) {
      return false;
    }

    // Конструктор
    if (/^constructor\s*\(/.test(trimmed)) {
      return true;
    }

    // Обычные методы (имя + скобки, но не function)
    if (
      /^\w+\s*\([^)]*\)\s*{?/.test(trimmed) &&
      !trimmed.includes('function') &&
      !trimmed.includes('=')
    ) {
      return true;
    }

    // Асинхронные методы
    if (/^async\s+\w+\s*\([^)]*\)\s*{?/.test(trimmed)) {
      return true;
    }

    // Статические методы
    if (/^static\s+(async\s+)?\w+\s*\([^)]*\)\s*{?/.test(trimmed)) {
      return true;
    }

    // Геттеры и сеттеры
    if (/^(get|set)\s+\w+\s*\([^)]*\)\s*{?/.test(trimmed)) {
      return true;
    }

    return false;
  }

  /**
   * НОВЫЙ: Продвинутая обработка функций
   * Учитывает async функции, стрелочные функции, экспорты
   */
  private processFunctionAdvanced(funcCode: string): string {
    const lines = funcCode.split('\n');

    // Для простых функций - используем старую логику
    if (lines.length <= 3) {
      const firstLine = lines[0];
      const lastLine = lines[lines.length - 1];
      return `${firstLine}\n  // TODO: Implement function\n${lastLine}`;
    }

    // Для сложных функций - более умная обработка
    const result: string[] = [];
    let braceCount = 0;
    let foundOpenBrace = false;

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const braces = this.countBraces(line);

      if (i === 0) {
        // Первая строка - всегда добавляем
        result.push(line);
        braceCount += braces.open - braces.close;
        if (braces.open > 0) foundOpenBrace = true;
        continue;
      }

      braceCount += braces.open - braces.close;

      // Если это последняя строка или функция закончилась
      if (i === lines.length - 1 || (braceCount <= 0 && foundOpenBrace)) {
        if (!result.some((l) => l.includes('// TODO'))) {
          result.push('  // TODO: Implement function');
        }
        result.push(line);
        break;
      }

      // Пропускаем содержимое функции
    }

    return result.join('\n');
  }
}

// Экспортируем экземпляр для использования
export const codeTemplateGenerator = new CodeTemplateGenerator();
