#!/usr/bin/env python3
"""
🧪 СКРИПТ ТЕСТИРОВАНИЯ УЛУЧШЕННОГО ГЕНЕРАТОРА НА РЕАЛЬНЫХ ЗАДАЧАХ

Этот скрипт:
1. Подключается к базе данных
2. Получает все задачи с кодом
3. Тестирует новый генератор на каждой задаче
4. Выявляет проблемы и недочеты
5. Создает детальный отчет

Использование:
python test_generator_on_real_tasks.py
"""

import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# Добавляем корневую папку в Python path
sys.path.append(str(Path(__file__).parent))

try:
    from sqlalchemy import and_

    from app.shared.database.connection import get_db
    from app.shared.models.content_models import ContentBlock
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("Убедитесь, что вы запускаете скрипт из папки back/")
    sys.exit(1)


class CodeTemplateTestSuite:
    def __init__(self):
        self.results = {
            "total_tasks": 0,
            "js_tasks": 0,
            "successful": 0,
            "failed": 0,
            "issues": [],
            "statistics": {"languages": {}, "categories": {}, "common_problems": {}},
        }

        # Путь к Node.js скрипту для тестирования генератора
        self.node_test_script = (
            Path(__file__).parent.parent / "front" / "test_generator.js"
        )

    def create_node_test_script(self):
        """Создает Node.js скрипт для тестирования генератора"""
        script_content = """
const fs = require('fs');

// Импортируем генератор (симулируем ES6 импорт)
const codeContent = fs.readFileSync('./src/shared/utils/codeTemplateGenerator.ts', 'utf8');

// Простая имитация класса (без полной компиляции TypeScript)
eval(`
${codeContent.replace('export class', 'global.CodeTemplateGenerator = class')}
`);

// Функция тестирования
function testGenerator(sourceCode, language, taskId) {
    try {
        const result = global.CodeTemplateGenerator.generateTemplate(sourceCode, language);

        // Проверки качества шаблона
        const issues = [];

        // 1. Проверка на лишние скобки
        const extraBraces = (result.match(/\\}\\s*\\}/g) || []).length;
        if (extraBraces > 0) {
            issues.push(`Extra closing braces: ${extraBraces}`);
        }

        // 2. Проверка на битые структуры
        const openBraces = (result.match(/\\{/g) || []).length;
        const closeBraces = (result.match(/\\}/g) || []).length;
        if (openBraces !== closeBraces) {
            issues.push(`Mismatched braces: ${openBraces} open, ${closeBraces} close`);
        }

        // 3. Проверка на пустые шаблоны
        if (result.trim().length < 10) {
            issues.push('Template too short, possibly empty');
        }

        // 4. Проверка на наличие комментариев с задачами
        if (!result.includes('// Implement') && !result.includes('// Write')) {
            issues.push('No implementation comment found');
        }

        return {
            success: true,
            result: result,
            issues: issues,
            original_length: sourceCode.length,
            template_length: result.length
        };

    } catch (error) {
        return {
            success: false,
            error: error.message,
            issues: [`Generation failed: ${error.message}`]
        };
    }
}

// Получаем данные из stdin и обрабатываем
const input = JSON.parse(process.argv[2]);
const testResult = testGenerator(input.code, input.language, input.taskId);
console.log(JSON.stringify(testResult));
"""

        with open(self.node_test_script, "w", encoding="utf-8") as f:
            f.write(script_content)

    def test_single_task(self, task):
        """Тестирует одну задачу"""
        try:
            # Подготавливаем данные для Node.js скрипта
            test_data = {
                "code": task.codeContent,
                "language": task.codeLanguage or "javascript",
                "taskId": task.id,
            }

            # Запускаем Node.js скрипт
            result = subprocess.run(
                ["node", str(self.node_test_script)],
                input=json.dumps(test_data),
                capture_output=True,
                text=True,
                cwd=str(self.node_test_script.parent),
                timeout=10,
                check=False,
            )

            if result.returncode != 0:
                return {
                    "success": False,
                    "error": f"Node.js error: {result.stderr}",
                    "issues": ["Script execution failed"],
                }

            # Парсим результат
            return json.loads(result.stdout)

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Test timeout",
                "issues": ["Test execution timeout"],
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "issues": [f"Unexpected error: {str(e)}"],
            }

    def is_js_task(self, task):
        """Проверяет, является ли задача JS/TS/JSX"""
        if not task.codeLanguage and not task.codeContent:
            return False

        # Проверяем язык
        if task.codeLanguage:
            lang = task.codeLanguage.lower()
            if lang in ["javascript", "js", "typescript", "ts", "jsx", "tsx", "react"]:
                return True

        # Проверяем содержимое
        if task.codeContent:
            js_patterns = [
                "function ",
                "const ",
                "let ",
                "var ",
                "class ",
                "=>",
                "console.log",
                "require(",
                "import ",
                "export ",
                "useState",
                "useEffect",
            ]
            return any(pattern in task.codeContent for pattern in js_patterns)

        return False

    def run_tests(self):
        """Запускает тесты на всех задачах"""
        print("🚀 Запуск тестирования генератора на реальных задачах...")

        # Создаем Node.js скрипт
        print("📝 Создание тестового скрипта...")
        self.create_node_test_script()

        # Подключаемся к БД
        print("🔌 Подключение к базе данных...")
        session = next(get_db())

        try:
            # Получаем все задачи с кодом
            tasks = (
                session.query(ContentBlock)
                .filter(
                    and_(
                        ContentBlock.codeContent.isnot(None),
                        ContentBlock.codeContent != "",
                    )
                )
                .all()
            )

            self.results["total_tasks"] = len(tasks)
            print(f"📊 Найдено задач с кодом: {len(tasks)}")

            # Фильтруем JS/TS задачи
            js_tasks = [task for task in tasks if self.is_js_task(task)]
            self.results["js_tasks"] = len(js_tasks)
            print(f"🟨 JS/TS/JSX задач: {len(js_tasks)}")

            if len(js_tasks) == 0:
                print("❌ Не найдено JS/TS задач для тестирования")
                return

            # Тестируем каждую JS задачу
            print("\n🧪 Начинаем тестирование...")
            for i, task in enumerate(js_tasks, 1):
                print(f"\n--- Задача {i}/{len(js_tasks)} (ID: {task.id}) ---")
                print(f"Язык: {task.codeLanguage}")
                print(
                    f"Категория: {task.file.mainCategory if task.file else 'Unknown'}"
                )
                print(f"Длина кода: {len(task.codeContent)} символов")

                # Тестируем задачу
                test_result = self.test_single_task(task)

                # Обновляем статистику
                if test_result["success"]:
                    self.results["successful"] += 1
                    print("✅ Генерация успешна")

                    if test_result.get("issues"):
                        print(f"⚠️  Найдены проблемы: {len(test_result['issues'])}")
                        for issue in test_result["issues"]:
                            print(f"   - {issue}")
                else:
                    self.results["failed"] += 1
                    print(f"❌ Ошибка: {test_result.get('error', 'Unknown error')}")

                # Сохраняем проблемы
                if test_result.get("issues"):
                    self.results["issues"].append(
                        {
                            "task_id": task.id,
                            "language": task.codeLanguage,
                            "category": task.file.mainCategory
                            if task.file
                            else "Unknown",
                            "issues": test_result["issues"],
                            "original_code_length": len(task.codeContent),
                            "template_length": test_result.get("template_length", 0),
                        }
                    )

                # Обновляем статистику по языкам
                lang = task.codeLanguage or "unknown"
                self.results["statistics"]["languages"][lang] = (
                    self.results["statistics"]["languages"].get(lang, 0) + 1
                )

                # Обновляем статистику по категориям
                category = task.file.mainCategory if task.file else "unknown"
                self.results["statistics"]["categories"][category] = (
                    self.results["statistics"]["categories"].get(category, 0) + 1
                )

                # Пауза чтобы не перегружать систему
                time.sleep(0.1)

        finally:
            session.close()

        # Удаляем временный скрипт
        if self.node_test_script.exists():
            self.node_test_script.unlink()

    def generate_report(self):
        """Генерирует детальный отчет"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = Path(__file__).parent / f"GENERATOR_TEST_REPORT_{timestamp}.md"

        report = f"""# 🧪 ОТЧЕТ ТЕСТИРОВАНИЯ ГЕНЕРАТОРА ШАБЛОНОВ

**Дата тестирования:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## 📊 ОБЩАЯ СТАТИСТИКА

- **Всего задач с кодом:** {self.results['total_tasks']}
- **JS/TS/JSX задач:** {self.results['js_tasks']}
- **Успешно обработано:** {self.results['successful']}
- **Ошибок генерации:** {self.results['failed']}
- **Процент успеха:** {(self.results['successful'] / max(1, self.results['js_tasks']) * 100):.1f}%

## 🎯 СТАТИСТИКА ПО ЯЗЫКАМ

"""

        for lang, count in sorted(self.results["statistics"]["languages"].items()):
            report += f"- **{lang}:** {count} задач\n"

        report += """

## 📂 СТАТИСТИКА ПО КАТЕГОРИЯМ

"""

        for category, count in sorted(self.results["statistics"]["categories"].items()):
            report += f"- **{category}:** {count} задач\n"

        report += f"""

## ⚠️ НАЙДЕННЫЕ ПРОБЛЕМЫ

**Всего задач с проблемами:** {len(self.results['issues'])}

"""

        if self.results["issues"]:
            # Группируем проблемы по типам
            problem_types = {}
            for issue_data in self.results["issues"]:
                for issue in issue_data["issues"]:
                    problem_types[issue] = problem_types.get(issue, 0) + 1

            report += "### 🔢 Частота проблем:\n\n"
            for problem, count in sorted(
                problem_types.items(), key=lambda x: x[1], reverse=True
            ):
                report += f"- **{problem}:** {count} раз\n"

            report += "\n### 📋 Детальный список проблем:\n\n"

            for i, issue_data in enumerate(self.results["issues"], 1):
                report += f"""
#### Задача {i} (ID: {issue_data['task_id']})
- **Язык:** {issue_data['language']}
- **Категория:** {issue_data['category']}
- **Длина оригинального кода:** {issue_data['original_code_length']} символов
- **Длина шаблона:** {issue_data['template_length']} символов
- **Проблемы:**
"""
                for issue in issue_data["issues"]:
                    report += f"  - {issue}\n"
        else:
            report += "✅ **Проблем не обнаружено!**\n"

        report += """

## 🎯 РЕКОМЕНДАЦИИ

"""

        if self.results["failed"] > 0:
            report += f"### ❌ Критические проблемы ({self.results['failed']} задач)\n"
            report += "- Необходимо исправить ошибки генерации\n"
            report += "- Проверить обработку специфических языковых конструкций\n\n"

        if len(self.results["issues"]) > 0:
            report += f"### ⚠️ Проблемы качества ({len(self.results['issues'])} задач)\n"
            report += "- Улучшить алгоритм парсинга функций\n"
            report += "- Добавить дополнительные проверки целостности\n"
            report += "- Оптимизировать обработку edge cases\n\n"

        if self.results["successful"] == self.results["js_tasks"]:
            report += "### ✅ Отличные результаты!\n"
            report += "- Генератор успешно обрабатывает все JS/TS задачи\n"
            report += "- Можно переходить к продуктивному использованию\n\n"

        report += f"""
## 📈 ВЫВОДЫ

- **Готовность к продакшену:** {'✅ Да' if self.results['failed'] == 0 and len(self.results['issues']) < self.results['js_tasks'] * 0.1 else '❌ Требуются доработки'}
- **Основные проблемы:** {', '.join(list({issue for issue_data in self.results['issues'] for issue in issue_data['issues']})[:3]) if self.results['issues'] else 'Не обнаружены'}
- **Следующие шаги:** {'Мониторинг в продакшене' if self.results['failed'] == 0 else 'Исправление найденных проблем'}

---
*Отчет сгенерирован автоматически {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""

        # Сохраняем отчет
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"\n📄 Отчет сохранен: {report_file}")

        # Также сохраняем JSON с сырыми данными
        json_file = report_file.with_suffix(".json")
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)

        print(f"📊 Сырые данные: {json_file}")


def main():
    print("🧪 ТЕСТИРОВАНИЕ УЛУЧШЕННОГО ГЕНЕРАТОРА ШАБЛОНОВ")
    print("=" * 50)

    # Проверяем наличие Node.js
    try:
        subprocess.run(["node", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Node.js не найден. Установите Node.js для запуска тестов.")
        sys.exit(1)

    # Запускаем тесты
    test_suite = CodeTemplateTestSuite()
    test_suite.run_tests()
    test_suite.generate_report()

    print("\n🎉 Тестирование завершено!")
    print(f"✅ Успешно: {test_suite.results['successful']}")
    print(f"❌ Ошибок: {test_suite.results['failed']}")
    print(f"⚠️  Проблем: {len(test_suite.results['issues'])}")


if __name__ == "__main__":
    main()

