/**
 * Генератор шаблонов кода для различных языков программирования
 * Очищает реализации функций/методов, оставляя только сигнатуры
 */
export class CodeTemplateGenerator {
  /**
   * Генерирует шаблон кода на основе исходного кода
   */
  static generateTemplate(sourceCode: string, language: string): string {
    const generator = new CodeTemplateGenerator();
    return generator.processCode(sourceCode, language);
  }

  /**
   * Проверяет, является ли задача JavaScript/TypeScript
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
        lang === 'ts'
      );
    }

    // Проверяем категорию
    if (
      block.file?.mainCategory?.toLowerCase().includes('javascript') ||
      block.file?.subCategory?.toLowerCase().includes('javascript')
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
      ];

      return jsPatterns.some((pattern) => pattern.test(block.codeContent!));
    }

    return false;
  }

  /**
   * Основной метод обработки кода
   */
  processCode(sourceCode: string, language: string): string {
    if (!sourceCode || !sourceCode.trim()) {
      return this.getDefaultTemplate(language);
    }

    try {
      switch (language.toLowerCase()) {
        case 'javascript':
        case 'js':
          return this.processJavaScript(sourceCode);
        case 'typescript':
        case 'ts':
          return this.processTypeScript(sourceCode);
        case 'python':
          return this.processPython(sourceCode);
        case 'java':
          return this.processJava(sourceCode);
        case 'cpp':
        case 'c++':
          return this.processCpp(sourceCode);
        case 'c':
          return this.processC(sourceCode);
        default:
          return sourceCode;
      }
    } catch (error) {
      console.warn(
        'Template generation failed, returning original code:',
        error
      );
      return sourceCode;
    }
  }

  private processJavaScript(code: string): string {
    let result = code;

    // Обрабатываем классы
    result = this.processClasses(result);

    // Обрабатываем функции
    result = this.processFunctions(result);

    // Обрабатываем стрелочные функции
    result = this.processArrowFunctions(result);

    return result;
  }

  private processTypeScript(code: string): string {
    // TypeScript обрабатывается так же как JavaScript
    return this.processJavaScript(code);
  }

  private processPython(code: string): string {
    const lines = code.split('\n');
    const result: string[] = [];
    let inFunction = false;
    let functionIndent = '';

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];

      // Определяем начало функции/метода
      if (line.trim().startsWith('def ')) {
        inFunction = true;
        functionIndent = line.match(/^(\s*)/)?.[1] || '';
        result.push(line);
        result.push(functionIndent + '    pass');
        continue;
      }

      // Проверяем конец функции
      if (inFunction) {
        const currentIndent = line.match(/^(\s*)/)?.[1] || '';
        if (line.trim() && currentIndent.length <= functionIndent.length) {
          inFunction = false;
          result.push(line);
        }
        continue;
      }

      // Обычные строки
      if (!inFunction) {
        result.push(line);
      }
    }

    return result.join('\n');
  }

  private processJava(code: string): string {
    let result = code;

    // Обрабатываем методы в классах
    result = this.processJavaClasses(result);

    return result;
  }

  private processCpp(code: string): string {
    let result = code;

    // Обрабатываем функции и методы
    result = this.processCppFunctions(result);

    return result;
  }

  private processC(code: string): string {
    return this.processCppFunctions(code);
  }

  private processClasses(code: string): string {
    const classRegex = /class\s+\w+(?:\s+extends\s+\w+)?\s*\{[\s\S]*?\}/g;

    return code.replace(classRegex, (classMatch) => {
      return this.processClassAdvanced(classMatch);
    });
  }

  private processFunctions(code: string): string {
    const functionRegex =
      /(?:async\s+)?function\s+\w+\s*\([^)]*\)\s*\{[\s\S]*?\}/g;

    return code.replace(functionRegex, (funcMatch) => {
      return this.processFunctionAdvanced(funcMatch);
    });
  }

  private processArrowFunctions(code: string): string {
    // Простые стрелочные функции
    const simpleArrowRegex = /(\w+\s*=\s*\([^)]*\)\s*=>\s*)\{[\s\S]*?\}/g;

    return code.replace(simpleArrowRegex, (_, signature) => {
      return `${signature}{\n  // Implement function\n}`;
    });
  }

  private processClassAdvanced(classCode: string): string {
    const lines = classCode.split('\n');
    const result: string[] = [];
    let insideMethod = false;
    let methodBraceCount = 0;
    let methodIndent = '';

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];

      // Проверяем начало метода
      if (this.isMethodDeclaration(line) && !insideMethod) {
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
          result.push(methodIndent + '    // Implement');
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
          result.push(methodIndent + '    // Implement');
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
   * Продвинутая обработка функций
   * Учитывает async функции, стрелочные функции, экспорты
   */
  private processFunctionAdvanced(funcCode: string): string {
    const lines = funcCode.split('\n');

    // Для простых функций - используем старую логику
    if (lines.length <= 3) {
      const firstLine = lines[0];
      const lastLine = lines[lines.length - 1];
      return `${firstLine}\n  // Implement function\n${lastLine}`;
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
        if (!result.some((l) => l.includes('// Implement'))) {
          result.push('  // Implement function');
        }
        result.push(line);
        break;
      }

      // Пропускаем содержимое функции
    }

    return result.join('\n');
  }

  private processJavaClasses(code: string): string {
    // Упрощенная обработка Java классов
    const methodRegex =
      /((?:public|private|protected|static|\s)*\w+\s+\w+\s*\([^)]*\)\s*\{)[\s\S]*?(\})/g;

    return code.replace(methodRegex, (_, opening, closing) => {
      return `${opening}\n        // Implement method\n    ${closing}`;
    });
  }

  private processCppFunctions(code: string): string {
    // Упрощенная обработка C/C++ функций
    const functionRegex = /(\w+\s+\w+\s*\([^)]*\)\s*\{)[\s\S]*?(\})/g;

    return code.replace(functionRegex, (_, opening, closing) => {
      return `${opening}\n    // Implement function\n${closing}`;
    });
  }

  private isMethodDeclaration(line: string): boolean {
    const trimmed = line.trim();

    // JavaScript/TypeScript методы
    const patterns = [
      /^\w+\s*\(/, // methodName(
      /^async\s+\w+\s*\(/, // async methodName(
      /^static\s+\w+\s*\(/, // static methodName(
      /^get\s+\w+\s*\(/, // get propertyName(
      /^set\s+\w+\s*\(/, // set propertyName(
    ];

    return patterns.some((pattern) => pattern.test(trimmed));
  }

  private countBraces(line: string): { open: number; close: number } {
    // Исключаем скобки в строках и комментариях
    const cleanLine = line
      .replace(/"[^"]*"/g, '')
      .replace(/'[^']*'/g, '')
      .replace(/\/\/.*$/, '');

    const open = (cleanLine.match(/\{/g) || []).length;
    const close = (cleanLine.match(/\}/g) || []).length;

    return { open, close };
  }

  private getDefaultTemplate(language: string): string {
    switch (language.toLowerCase()) {
      case 'javascript':
      case 'js':
        return 'function solution() {\n  // Implement your solution here\n}';
      case 'typescript':
      case 'ts':
        return 'function solution(): any {\n  // Implement your solution here\n}';
      case 'python':
        return 'def solution():\n    # Implement your solution here\n    pass';
      case 'java':
        return 'public class Solution {\n    public void solution() {\n        // Implement your solution here\n    }\n}';
      case 'cpp':
      case 'c++':
        return '#include <iostream>\n\nint main() {\n    // Implement your solution here\n    return 0;\n}';
      case 'c':
        return '#include <stdio.h>\n\nint main() {\n    // Implement your solution here\n    return 0;\n}';
      default:
        return '// Implement your solution here';
    }
  }
}
