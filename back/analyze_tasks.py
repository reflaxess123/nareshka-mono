#!/usr/bin/env python3

import logging
import re
from collections import defaultdict
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from app.config import settings
from app.models import ContentBlock, ContentFile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def analyze_tasks():
    """Максимально подробный анализ задач в базе данных"""
    
    # Подключение к базе данных
    db_url = settings.database_url
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        logger.info("🔍 МАКСИМАЛЬНО ПОДРОБНЫЙ АНАЛИЗ ЗАДАЧ В БАЗЕ ДАННЫХ...")
        
        # Получаем все блоки с кодом
        blocks = db.query(ContentBlock).filter(
            ContentBlock.codeContent.isnot(None),
            ContentBlock.codeContent != ""
        ).all()
        
        logger.info(f"📊 Найдено блоков с кодом: {len(blocks)}")
        
        # Расширенная статистика
        languages = defaultdict(int)
        categories = defaultdict(int)
        js_tasks = []
        non_js_tasks = []
        problematic_cases = []
        
        # Анализируем каждый блок максимально подробно
        for block in blocks:
            # Базовая статистика
            lang = block.codeLanguage or "unknown"
            languages[lang] += 1
            
            if block.file:
                cat_key = f"{block.file.mainCategory} / {block.file.subCategory}"
                categories[cat_key] += 1
            
            # Определяем JS задачи
            is_js = is_javascript_task(block)
            if is_js:
                js_tasks.append(block)
            else:
                non_js_tasks.append(block)
            
            # ГЛУБОКИЙ АНАЛИЗ ПРОБЛЕМНЫХ СЛУЧАЕВ
            if is_js:
                problems = analyze_code_complexity(block)
                if problems['total_score'] > 0:
                    problematic_cases.append((block, problems))
        
        # Выводим базовую статистику
        print_basic_stats(languages, categories, js_tasks, non_js_tasks)
        
        # Анализируем примеры разных типов задач
        analyze_task_examples(js_tasks, non_js_tasks)
        
        # КРИТИЧЕСКИЙ АНАЛИЗ ПРОБЛЕМНЫХ СЛУЧАЕВ
        analyze_problematic_cases(problematic_cases)
        
        # Анализ паттернов кода
        analyze_code_patterns(js_tasks)
        
        # Тестирование нашего генератора на реальных данных
        test_generator_on_real_data(js_tasks[:10])
        
        logger.info(f"\n✅ АНАЛИЗ ЗАВЕРШЕН. Проблемных случаев: {len(problematic_cases)}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка при анализе: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

def analyze_code_complexity(block):
    """Максимально подробный анализ сложности кода"""
    code = block.codeContent
    problems = {
        'issues': [],
        'total_score': 0,
        'categories': defaultdict(int)
    }
    
    # 1. СТРУКТУРНАЯ СЛОЖНОСТЬ
    class_count = len(re.findall(r'\bclass\s+\w+', code))
    function_count = len(re.findall(r'\bfunction\s+\w+', code))
    arrow_function_count = len(re.findall(r'=>', code))
    method_count = len(re.findall(r'^\s*\w+\s*\([^)]*\)\s*{', code, re.MULTILINE))
    
    if class_count > 1:
        problems['issues'].append(f"Множественные классы ({class_count})")
        problems['total_score'] += class_count * 2
        problems['categories']['multiple_classes'] += class_count
    
    if function_count > 3:
        problems['issues'].append(f"Много функций ({function_count})")
        problems['total_score'] += function_count
        problems['categories']['many_functions'] += function_count
    
    if method_count > 5:
        problems['issues'].append(f"Много методов ({method_count})")
        problems['total_score'] += method_count
        problems['categories']['many_methods'] += method_count
    
    # 2. ВЛОЖЕННОСТЬ И СКОБКИ
    brace_count = code.count('{')
    max_nesting = calculate_max_nesting(code)
    
    if brace_count > 15:
        problems['issues'].append(f"Высокая вложенность ({brace_count} скобок)")
        problems['total_score'] += 3
        problems['categories']['high_nesting'] += 1
    
    if max_nesting > 4:
        problems['issues'].append(f"Глубокая вложенность ({max_nesting} уровней)")
        problems['total_score'] += max_nesting
        problems['categories']['deep_nesting'] += 1
    
    # 3. АСИНХРОННОСТЬ И ПРОМИСЫ
    async_patterns = [
        r'\basync\s+function',
        r'\bawait\s+',
        r'\bPromise\.',
        r'\.then\(',
        r'\.catch\(',
        r'\.finally\('
    ]
    
    async_count = sum(len(re.findall(pattern, code)) for pattern in async_patterns)
    if async_count > 0:
        problems['issues'].append(f"Асинхронный код ({async_count} паттернов)")
        problems['total_score'] += async_count * 2
        problems['categories']['async_code'] += async_count
    
    # 4. МОДУЛЬНАЯ СИСТЕМА
    module_patterns = [
        r'\bimport\s+',
        r'\bexport\s+',
        r'\brequire\(',
        r'\bmodule\.exports',
        r'\bexports\.'
    ]
    
    module_count = sum(len(re.findall(pattern, code)) for pattern in module_patterns)
    if module_count > 0:
        problems['issues'].append(f"Модульная система ({module_count} импортов/экспортов)")
        problems['total_score'] += module_count
        problems['categories']['modules'] += module_count
    
    # 5. СЛОЖНЫЕ JS КОНЦЕПЦИИ
    advanced_patterns = [
        (r'\bprototype\.', 'prototype'),
        (r'\bthis\.', 'this'),
        (r'\.bind\(', 'bind'),
        (r'\.call\(', 'call'),
        (r'\.apply\(', 'apply'),
        (r'\bconstructor\s*\(', 'constructor'),
        (r'\bsuper\(', 'super'),
        (r'\bextends\s+', 'extends'),
        (r'\bstatic\s+', 'static'),
        (r'\bget\s+\w+\s*\(', 'getter'),
        (r'\bset\s+\w+\s*\(', 'setter'),
        (r'\byield\s+', 'generator'),
        (r'\bfunction\*', 'generator'),
        (r'Symbol\.', 'symbols'),
        (r'Proxy\(', 'proxy'),
        (r'Reflect\.', 'reflect')
    ]
    
    advanced_features = []
    for pattern, name in advanced_patterns:
        count = len(re.findall(pattern, code))
        if count > 0:
            advanced_features.append(f"{name}({count})")
            problems['total_score'] += count * 2
            problems['categories']['advanced_js'] += count
    
    if advanced_features:
        problems['issues'].append(f"Продвинутые JS концепции: {', '.join(advanced_features)}")
    
    # 6. РЕГУЛЯРНЫЕ ВЫРАЖЕНИЯ И СТРОКИ
    regex_count = len(re.findall(r'/[^/\n]+/[gimuy]*', code))
    template_literal_count = len(re.findall(r'`[^`]*`', code))
    
    if regex_count > 0:
        problems['issues'].append(f"Регулярные выражения ({regex_count})")
        problems['total_score'] += regex_count * 2
        problems['categories']['regex'] += regex_count
    
    if template_literal_count > 2:
        problems['issues'].append(f"Шаблонные строки ({template_literal_count})")
        problems['total_score'] += template_literal_count
        problems['categories']['templates'] += template_literal_count
    
    # 7. ОБРАБОТКА ОШИБОК
    error_handling = [
        r'\btry\s*{',
        r'\bcatch\s*\(',
        r'\bfinally\s*{',
        r'\bthrow\s+',
        r'new\s+Error\('
    ]
    
    error_count = sum(len(re.findall(pattern, code)) for pattern in error_handling)
    if error_count > 0:
        problems['issues'].append(f"Обработка ошибок ({error_count} блоков)")
        problems['total_score'] += error_count
        problems['categories']['error_handling'] += error_count
    
    # 8. РАЗМЕР И СЛОЖНОСТЬ
    lines = code.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    
    if len(non_empty_lines) > 50:
        problems['issues'].append(f"Длинный код ({len(non_empty_lines)} строк)")
        problems['total_score'] += len(non_empty_lines) // 10
        problems['categories']['long_code'] += 1
    
    # 9. СПЕЦИФИЧЕСКИЕ ПАТТЕРНЫ, КОТОРЫЕ СЛОЖНО ПАРСИТЬ
    tricky_patterns = [
        (r'{\s*\[.*\]:', 'computed_properties'),
        (r'\.\.\.', 'spread_operator'),
        (r'\?\?', 'nullish_coalescing'),
        (r'\?\.', 'optional_chaining'),
        (r'=>\s*{', 'arrow_functions_with_body'),
        (r'=>\s*\(', 'arrow_functions_with_parens'),
        (r'function\s*\*', 'generator_functions'),
        (r'\bclass\s+\w+\s+extends', 'class_inheritance'),
        (r'super\s*\(', 'super_calls'),
        (r'#\w+', 'private_fields')
    ]
    
    tricky_features = []
    for pattern, name in tricky_patterns:
        count = len(re.findall(pattern, code))
        if count > 0:
            tricky_features.append(f"{name}({count})")
            problems['total_score'] += count * 3  # Высокий вес для сложных паттернов
            problems['categories']['tricky_syntax'] += count
    
    if tricky_features:
        problems['issues'].append(f"Сложный синтаксис: {', '.join(tricky_features)}")
    
    # 10. ПРОБЛЕМЫ ПАРСИНГА НАШЕГО ГЕНЕРАТОРА
    parsing_issues = []
    
    # Вложенные классы
    if re.search(r'class\s+\w+[^}]*class\s+\w+', code):
        parsing_issues.append("nested_classes")
        problems['total_score'] += 5
    
    # Методы с комплексными сигнатурами
    complex_methods = re.findall(r'\w+\s*\([^)]{20,}\)\s*{', code)
    if complex_methods:
        parsing_issues.append(f"complex_method_signatures({len(complex_methods)})")
        problems['total_score'] += len(complex_methods) * 2
    
    # Функции внутри методов
    if re.search(r'{\s*[^}]*function\s+\w+', code):
        parsing_issues.append("nested_functions")
        problems['total_score'] += 3
    
    # Комментарии внутри кода (могут сломать парсинг)
    inline_comments = len(re.findall(r'//.*$', code, re.MULTILINE))
    block_comments = len(re.findall(r'/\*.*?\*/', code, re.DOTALL))
    
    if inline_comments > 10 or block_comments > 3:
        parsing_issues.append(f"many_comments({inline_comments + block_comments})")
        problems['total_score'] += 1
    
    if parsing_issues:
        problems['issues'].append(f"Проблемы парсинга: {', '.join(parsing_issues)}")
        problems['categories']['parsing_issues'] += len(parsing_issues)
    
    return problems

def calculate_max_nesting(code):
    """Вычисляет максимальную глубину вложенности"""
    max_depth = 0
    current_depth = 0
    
    for char in code:
        if char == '{':
            current_depth += 1
            max_depth = max(max_depth, current_depth)
        elif char == '}':
            current_depth = max(0, current_depth - 1)
    
    return max_depth

def print_basic_stats(languages, categories, js_tasks, non_js_tasks):
    """Выводит базовую статистику"""
    logger.info("\n📈 СТАТИСТИКА ПО ЯЗЫКАМ:")
    for lang, count in sorted(languages.items(), key=lambda x: x[1], reverse=True):
        logger.info(f"  {lang}: {count} задач")
    
    logger.info("\n📈 СТАТИСТИКА ПО КАТЕГОРИЯМ:")
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        logger.info(f"  {cat}: {count} задач")
    
    logger.info(f"\n🎯 JavaScript задач: {len(js_tasks)}")
    logger.info(f"🎯 Не-JavaScript задач: {len(non_js_tasks)}")

def analyze_task_examples(js_tasks, non_js_tasks):
    """Анализирует примеры задач"""
    logger.info("\n🔬 ПРИМЕРЫ JAVASCRIPT ЗАДАЧ:")
    for i, block in enumerate(js_tasks[:3]):
        logger.info(f"\n--- JS Задача {i+1}: {block.blockTitle} ---")
        logger.info(f"ID: {block.id}")
        logger.info(f"Категория: {block.file.mainCategory} / {block.file.subCategory}")
        logger.info(f"Язык: {block.codeLanguage}")
        logger.info(f"Длина кода: {len(block.codeContent)} символов")
        
        # Показываем структуру кода
        code_lines = block.codeContent.split('\n')
        logger.info(f"Строк кода: {len(code_lines)}")
        logger.info("Первые 15 строк:")
        for j, line in enumerate(code_lines[:15]):
            logger.info(f"  {j+1:2d}: {line}")
        if len(code_lines) > 15:
            logger.info("  ...")

def analyze_problematic_cases(problematic_cases):
    """Анализирует проблемные случаи"""
    logger.info(f"\n🚨 ПРОБЛЕМНЫЕ СЛУЧАИ ({len(problematic_cases)}):")
    
    # Сортируем по сложности
    problematic_cases.sort(key=lambda x: x[1]['total_score'], reverse=True)
    
    # Статистика по типам проблем
    problem_stats = defaultdict(int)
    for _, problems in problematic_cases:
        for category, count in problems['categories'].items():
            problem_stats[category] += count
    
    logger.info("\n📊 СТАТИСТИКА ПРОБЛЕМ:")
    for problem_type, count in sorted(problem_stats.items(), key=lambda x: x[1], reverse=True):
        logger.info(f"  {problem_type}: {count} случаев")
    
    # Топ самых сложных случаев
    logger.info("\n🔥 ТОП-5 САМЫХ СЛОЖНЫХ СЛУЧАЕВ:")
    for i, (block, problems) in enumerate(problematic_cases[:5]):
        logger.info(f"\n--- Сложный случай {i+1} (сложность: {problems['total_score']}) ---")
        logger.info(f"ID: {block.id}")
        logger.info(f"Задача: {block.blockTitle}")
        logger.info(f"Категория: {block.file.mainCategory} / {block.file.subCategory}")
        logger.info(f"Проблемы: {'; '.join(problems['issues'])}")
        logger.info(f"Длина: {len(block.codeContent)} символов")
        
        # Показываем проблемные части кода
        logger.info("Проблемные паттерны в коде:")
        show_problematic_patterns(block.codeContent)

def show_problematic_patterns(code):
    """Показывает проблемные паттерны в коде"""
    lines = code.split('\n')
    
    # Ищем сложные строки
    for i, line in enumerate(lines):
        if any(pattern in line for pattern in ['class ', 'function ', '=>', 'async ', 'await ']):
            logger.info(f"  {i+1:2d}: {line.strip()}")

def analyze_code_patterns(js_tasks):
    """Анализирует паттерны кода"""
    logger.info("\n🔍 АНАЛИЗ ПАТТЕРНОВ КОДА:")
    
    patterns = {
        'classes_with_inheritance': 0,
        'classes_with_static_methods': 0,
        'classes_with_getters_setters': 0,
        'arrow_functions': 0,
        'async_functions': 0,
        'generator_functions': 0,
        'destructuring': 0,
        'spread_operator': 0,
        'template_literals': 0,
        'modules': 0
    }
    
    for block in js_tasks:
        code = block.codeContent
        
        if re.search(r'class\s+\w+\s+extends', code):
            patterns['classes_with_inheritance'] += 1
        
        if re.search(r'static\s+\w+', code):
            patterns['classes_with_static_methods'] += 1
        
        if re.search(r'get\s+\w+\s*\(|set\s+\w+\s*\(', code):
            patterns['classes_with_getters_setters'] += 1
        
        if '=>' in code:
            patterns['arrow_functions'] += 1
        
        if 'async ' in code or 'await ' in code:
            patterns['async_functions'] += 1
        
        if 'function*' in code or 'yield ' in code:
            patterns['generator_functions'] += 1
        
        if re.search(r'{\s*\w+\s*}|{\s*\w+:', code):
            patterns['destructuring'] += 1
        
        if '...' in code:
            patterns['spread_operator'] += 1
        
        if '`' in code:
            patterns['template_literals'] += 1
        
        if 'import ' in code or 'export ' in code:
            patterns['modules'] += 1
    
    for pattern, count in patterns.items():
        if count > 0:
            logger.info(f"  {pattern}: {count} задач")

def test_generator_on_real_data(sample_tasks):
    """Тестирует наш генератор на реальных данных"""
    logger.info(f"\n🧪 ТЕСТИРОВАНИЕ ГЕНЕРАТОРА НА {len(sample_tasks)} РЕАЛЬНЫХ ЗАДАЧАХ:")
    
    # Имитируем работу генератора (без импорта фронтенд кода)
    for i, block in enumerate(sample_tasks):
        logger.info(f"\n--- Тест {i+1}: {block.blockTitle} ---")
        
        # Проверяем, как наш генератор определит эту задачу
        is_js = is_javascript_task(block)
        logger.info(f"Определена как JS: {is_js}")
        
        if is_js:
            # Анализируем, что может пойти не так при генерации шаблона
            potential_issues = []
            code = block.codeContent
            
            # Проверяем сложности парсинга
            if code.count('class') > 1:
                potential_issues.append("Множественные классы")
            
            if re.search(r'class[^{]*{[^}]*class', code):
                potential_issues.append("Вложенные классы")
            
            if code.count('{') != code.count('}'):
                potential_issues.append("Несбалансированные скобки")
            
            if re.search(r'//.*{|}', code):
                potential_issues.append("Скобки в комментариях")
            
            if '/*' in code and '*/' in code:
                potential_issues.append("Блочные комментарии")
            
            if potential_issues:
                logger.info(f"⚠️  Потенциальные проблемы: {', '.join(potential_issues)}")
            else:
                logger.info("✅ Должен обработаться корректно")

def is_javascript_task(block):
    """Определяет, является ли задача JavaScript задачей (копия логики с фронтенда)"""
    JS_CATEGORIES = ['JS ТЕОРИЯ', 'REACT', 'NODE.JS', 'TYPESCRIPT', 'JS']
    JS_LANGUAGES = ['javascript', 'typescript', 'js', 'ts']
    
    # 1. Проверяем язык кода
    if block.codeLanguage:
        lang = block.codeLanguage.lower()
        if lang in JS_LANGUAGES:
            return True
    
    # 2. Проверяем категории файла
    if block.file:
        main_cat = block.file.mainCategory.upper() if block.file.mainCategory else ""
        sub_cat = block.file.subCategory.upper() if block.file.subCategory else ""
        
        if any(cat in main_cat or cat in sub_cat for cat in JS_CATEGORIES):
            return True
    
    # 3. Эвристическая проверка содержимого кода
    if block.codeContent:
        js_patterns = [
            r'class\s+\w+',
            r'function\s+\w+\s*\(',
            r'const\s+\w+\s*=',
            r'let\s+\w+\s*=',
            r'=>\s*{',
            r'console\.log',
            r'require\(',
            r'import\s+.*from',
            r'export\s+(default|const|function|class)'
        ]
        return any(re.search(pattern, block.codeContent) for pattern in js_patterns)
    
    return False

if __name__ == "__main__":
    analyze_tasks() 