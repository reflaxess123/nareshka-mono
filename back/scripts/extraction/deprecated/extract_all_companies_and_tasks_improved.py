import re
import os
import json
from collections import defaultdict

# Список известных компаний из наших предыдущих анализов
KNOWN_COMPANIES = {
    'яндекс', 'сбер', 'тинкофф', 'тинкоф', 'лемма', 'wb', 'иннотех', 'отп', 'отп банк', 
    'газпром', 'газпромбанк', 'profsoft', 'altenar', 'it-one', 'сбертех', 'альфа', 
    'альфабанк', 'альфа-банк', 'вк', 'автомакон', 'мойсклад', 'цезио', 'qugo', 'ibs', 
    'росбанк', 'ооо мобайлдевелопмент', 'сибур', 'гк т1', 'билайн', 'kotelov', 'втб',
    'unisender', 'озон', 'поле.рф', 'artw', 'авито', 'realweb', 'itfb', 'киберлаб', 
    'portalbilet', 'marpla', 'росгосстрах', 'right line', 'quantum art', 'аласкар технологии',
    'селекти', 'промсвязьбанк', 'сбердевайсы', 'funbox', 'цум', 'it baltic', 'сберкорус',
    'рутуб', 'евротехклимат', 'luxsoft', 'tilda', 'антара', 'финам', 'баланс платформа',
    'лаб касп', 'яндекс такси', 'click2money', 'kts', 'premium it solution', 'moex',
    'eesee', 'дом.рф', 'лига цифровой экономики', 'яндекс про', 'coding team', 'ютэир',
    'goinvest', 'yandex.pay', 'yandex.multitrack', 'баум', 'кокос.group', 'сквад',
    'точка банк', 'vision', 'sbertech', 'онлайн школа тетрика', 'сфера', 'yandex',
    'mail.ru', 'kaspersky', 'райфайзен', 'tele2', 'теле2', 'рсхб', 'рсхб-интех',
    'техзор', 'урбантех', 'datsteam', 'dats team', 'unybrands', 'мтс', 'northflank',
    'кьюго', 'кодинг тим', 'стрим телеком', 'stream telecom', 'баум', 'realtime',
    'кликтумани', 'click to money', 'техническая поддержка', 'холдинг', 'бфт',
    'ivi', 'расчетные решения', 'сбер для экспертов', 'почта россии', 'совкомбанк',
    'северсталь', 'касперский', 'нетология', 'skillbox', 'geekbrains', 'hexlet'
}

EXCLUSION_PATTERN = r"""^(то есть|нельзя|без|написать|часто|решено|раз|встречалось?|попадалось?|в целом|
пример|задача|задачи|решение|решения|как|надо|нужно|какой|какие|описание|смысл|что|чтобы|если|или|проверка|ошибка|ошибки|тест|тесты|шаблон|шаблоны|объект|массив|строка|число|функция|классы|хуки|поля|типы|асинхронность|промисы|колбэки|замыкания|рекурсия|алгоритмы|структуры|данные|сервер|клиент|фронтенд|бэкенд|api|база данных|бд|ооп|паттерны|архитектура|дизайн|система|команда|собеседование|вопрос|ответ|практика|теория|статья|глава|часть|часто|просто|сложно|для|от|с|из|в|на|по|за|при|до|после|со|путь|для|ключ|значение|код|кода|текст|текста|компонент|компоненты|виджет|виджеты|страница|страницы|модель|модели|слайс|слайсы|хук|хуки|стили|константы|утилиты|контекст|роутер|провайдер|редакс|redux|react|js|ts|python|sql|html|css|json|yaml|xml|git|docker|linux|windows|macos|api|ui|ux|npm|yarn|webpack|vite|babel|eslint|prettier|jest|cypress|storybook|graphql|rest|websocket|oop|fp|dry|kiss|solid|mvc|mvvm|mvp|mobx|zustand|rxjs|saga|thunk|middleware|nextjs|nuxtjs|angular|vue|svelte|node|express|django|flask|fastapi|spring|kotlin|java|c#|cpp|rust|go|php|ruby|swift|dart|flutter|android|ios|web|mobile|desktop|game|data science|ml|ai|blockchain|cloud|aws|azure|gcp|devops|ci|cd|agile|scrum|kanban|trello|jira|figma|photoshop|illustrator|sketch|vscode|intellij|sublime|atom|vim|emacs|bash|zsh|powershell|cmd|terminal|ssh|ftp|http|https|tcp|udp|ip|dns|vpn|ssl|tls|jwt|oauth|oidc|restful|microservices|monolith|serverless|kubernetes|docker compose|nginx|apache|redis|kafka|rabbitmq|postgresql|mysql|mongodb|elasticsearch|firebase|heroku|netlify|vercel|storybook|jest|redux-saga|redux-thunk|rtk query|axios|fetch|lodash|moment|dayjs|uuid|classnames|tailwind|material-ui|ant-design|bootstrap|semantic-ui|bulma|chakra-ui|radix-ui|headless-ui|react-query|swr|formik|react-hook-form|yup|zod|date-fns|immer|reselect|storybook|react-router|next-auth|graphql-request|apollo-client|urql|axios-mock-adapter|msw|enzyme|react-testing-library|jest-dom|eslint-plugin-react|typescript-eslint|prettier-plugin-tailwind|husky|lint-staged|commitlint|semantic-release|lerna|nx|rush|turborepo|pnpm|npm|yarn|vite-plugin-pwa|rollup|esbuild|parcel|browserify|rollup-plugin-node-resolve|rollup-plugin-commonjs|rollup-plugin-typescript2|rollup-plugin-terser|rollup-plugin-postcss|rollup-plugin-svg|rollup-plugin-json|rollup-plugin-url|rollup-plugin-peer-deps-external|rollup-plugin-clean|rollup-plugin-visualizer|rollup-plugin-analyzer|rollup-plugin-bundle-size|rollup-plugin-license|rollup-plugin-copy|rollup-plugin-gzip|rollup-plugin-brotli|rollup-plugin-filesize|rollup-plugin-progress|rollup-plugin-typescript)$"""

def clean_company_name(company: str) -> str:
    """Очищает название компании от мусора, стараясь сохранить потенциальные части названия."""
    company = company.lower().strip()
    
    # Убираем только скобки, если они в самом конце строки и содержат пояснения.
    company = re.sub(r'\s*\([^)]*\)$|\[[^\]]*\]$', '', company).strip()
    
    # Удаляем очень общие фразы, которые точно не являются частью названий компаний
    cleanups_to_remove = [
        'нельзя копировать массив, то есть inplace',
        'без set, сказать сложность, будет ли set работать с объектами',
        'для экспертов',
        'свистунова екатерина александровна',
        'часто в целом', 'на личном собесе', 'не мутируем'
    ]
    
    for cleanup in cleanups_to_remove:
        company = re.sub(cleanup, '', company, flags=re.IGNORECASE).strip()
    
    # Убираем лишние символы и нормализуем пробелы
    company = re.sub(r'[-–—_./]+', ' ', company).strip() # Добавлены точки и слеши
    company = re.sub(r'\s+', ' ', company).strip()
    
    return company

def is_valid_company(company: str) -> bool:
    """Проверяет, является ли строка потенциальным названием компании (более мягкая проверка)."""
    original_company = company
    company = clean_company_name(company)
    
    if not company or len(company) < 2:
        return False
    
    # Исключаем явный мусор, который точно не компания
    # Этот список должен быть ОЧЕНЬ тщательно составлен, чтобы не отфильтровать реальные компании.
    # Сосредоточимся на предлогах, вопросительных словах, общих понятиях программирования.
    if re.match(EXCLUSION_PATTERN, company, re.IGNORECASE): # Расширенный список мусора
        return False
    
    # Если строка содержит цифры, но также содержит хотя бы 2 буквы и не является просто числом
    if re.search(r'\d', company) and len(re.findall(r'[а-яa-z]', company)) >= 2 and not company.isdigit():
        return True

    # Положительные индикаторы (если строка содержит эти слова, она, вероятно, является компанией)
    if re.search(r'\b(банк|тех|софт|лаб|групп?|технологии|решения|платформа|системы|сервис|разработка|компани|корпорация|холдинг|ао|ооо|пкк|нии|кб|завод|фабрика|центр|институт)\b', company, re.IGNORECASE):
        return True
    
    # Если это несколько слов и хотя бы одно слово начинается с заглавной буквы (в оригинальной строке)
    if ' ' in original_company and any(word and word[0].isupper() for word in original_company.split()):
        # Дополнительно проверяем, чтобы это не был просто заголовок из одного или двух общих слов
        if len(original_company.split()) > 1 or original_company.lower() not in ['задача', 'пример', 'решение']:
            return True

    # Fallback: Если строка не является мусором и содержит достаточно букв
    if re.match(r'^[а-яa-z0-9\s-]+$', company) and len(re.findall(r'[а-яa-z]', company)) >= 2:
        return True

    return False

def extract_companies_from_block(block_text: str) -> list[str]:
    """Извлекает компании из блока "встречалось в"""
    companies = []
    lines = block_text.split('\n')
    
    for line in lines[1:]:  # Пропускаем первую строку
        # Убираем маркеры списков
        cleaned = re.sub(r'^[\t\s]*[-*+•]\s*', '', line).strip()
        cleaned = re.sub(r'^[\t\s]*\d+\.\s*', '', cleaned).strip()
        
        if not cleaned:
            continue
        
        # Разбиваем по запятым, если есть несколько компаний в строке
        potential_companies = [c.strip() for c in re.split(r'[,;]', cleaned)]
        
        for company in potential_companies:
            if is_valid_company(company):
                clean_name = clean_company_name(company)
                if clean_name:
                    companies.append(clean_name)
    
    return companies

def extract_companies_from_headers(headers: list, context: str) -> list[str]:
    """Извлекает компании из заголовков (особенно для файлов типа Ререндер.md)"""
    companies = []
    
    for header in headers:
        header_text = header['text'].strip()
        header_lower = header_text.lower()
        
        # Специальная логика для файлов с компаниями в заголовках
        if any(keyword in context.lower() for keyword in ['ререндер', 'рефактор']):
            # В этих файлах заголовки часто являются названиями компаний
            if (header['level'] <= 3 and 
                len(header_text) < 50 and
                not re.match(r'^(задач|example|пример|counter|todo|списки|рефактор|тренировочные|other|use|test|решени|мини|мощн)', header_lower)):
                
                if is_valid_company(header_text):
                    clean_name = clean_company_name(header_text)
                    if clean_name:
                        companies.append(clean_name)
    
    return companies

def extract_all_from_md_file(file_path: str) -> dict:
    """Точно извлекает компании и задачи из .md файла"""
    if not os.path.exists(file_path):
        return {}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    result = {
        'file_path': file_path,
        'tasks': [],
        'companies': [],
        'all_headers': [],
        'statistics': {}
    }
    
    # 1. Извлекаем все заголовки
    all_headers = re.findall(r'^(#{1,6})\s*(.+)$', content, re.MULTILINE)
    for level, header_text in all_headers:
        result['all_headers'].append({
            'level': len(level),
            'text': header_text.strip(),
            'normalized': header_text.strip().lower()
        })
    
    # 2. Извлекаем компании из блоков "встречалось в"
    company_block_patterns = [
        r'встречалось в.*?(?=\n\S|\n#+|\n```|\Z)',
        r'встречается в.*?(?=\n\S|\n#+|\n```|\Z)', 
        r'встречался в.*?(?=\n\S|\n#+|\n```|\Z)',
        r'попадалось в.*?(?=\n\S|\n#+|\n```|\Z)'
    ]
    
    all_companies = set()
    
    for pattern in company_block_patterns:
        blocks = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
        for block in blocks:
            companies_in_block = extract_companies_from_block(block)
            all_companies.update(companies_in_block)
    
    # 3. Извлекаем компании из заголовков
    header_companies = extract_companies_from_headers(result['all_headers'], file_path)
    all_companies.update(header_companies)
    
    result['companies'] = sorted(list(all_companies))
    
    # 4. Разбиваем на задачи
    sections = re.split(r'(^#{1,6}\s+.+)$', content, flags=re.MULTILINE)
    
    current_task = None
    current_content = ""
    
    for section in sections:
        if re.match(r'^#{1,6}\s+', section):
            # Сохраняем предыдущую задачу
            if current_task and current_content:
                task_companies = set()
                
                # Ищем компании в контенте задачи
                for pattern in company_block_patterns:
                    task_blocks = re.findall(pattern, current_content, re.IGNORECASE | re.DOTALL)
                    for block in task_blocks:
                        companies_in_task = extract_companies_from_block(block)
                        task_companies.update(companies_in_task)
                
                result['tasks'].append({
                    'title': current_task,
                    'normalized_title': re.sub(r'^#+\s*', '', current_task).strip().lower(),
                    'companies': sorted(list(task_companies)),
                    'content_length': len(current_content),
                    'has_code': '```' in current_content
                })
            
            # Начинаем новую задачу
            current_task = section.strip()
            current_content = ""
        else:
            current_content += section
    
    # Обрабатываем последнюю задачу
    if current_task and current_content:
        task_companies = set()
        for pattern in company_block_patterns:
            task_blocks = re.findall(pattern, current_content, re.IGNORECASE | re.DOTALL)
            for block in task_blocks:
                companies_in_task = extract_companies_from_block(block)
                task_companies.update(companies_in_task)
        
        result['tasks'].append({
            'title': current_task,
            'normalized_title': re.sub(r'^#+\s*', '', current_task).strip().lower(),
            'companies': sorted(list(task_companies)),
            'content_length': len(current_content),
            'has_code': '```' in current_content
        })
    
    # 5. Статистика
    result['statistics'] = {
        'total_headers': len(result['all_headers']),
        'total_tasks': len(result['tasks']),
        'tasks_with_companies': len([t for t in result['tasks'] if t['companies']]),
        'total_companies': len(result['companies'])
    }
    
    return result

def analyze_all_md_files():
    """Анализирует все .md файлы только в папках js, react, ts в корне проекта"""
    
    # Папки для анализа
    target_dirs = [
        os.path.join('..', 'js'),
        os.path.join('..', 'react'),
        os.path.join('..', 'ts'),
    ]
    
    md_files = []
    for target_dir in target_dirs:
        for root, dirs, files in os.walk(target_dir):
            for file in files:
                if file.endswith('.md'):
                    md_files.append(os.path.join(root, file))
    
    print(f"🔍 Найдено .md файлов: {len(md_files)} (только в js, react, ts)")
    print("=" * 80)
    
    all_results = []
    all_companies = set()
    all_tasks = []
    
    for file_path in md_files:
        print(f"\n📄 Анализируем: {file_path}")
        result = extract_all_from_md_file(file_path)
        
        if result['tasks'] or result['companies']:
            all_results.append(result)
            
            # Собираем все уникальные компании
            all_companies.update(result['companies'])
            
            # Собираем все задачи
            all_tasks.extend(result['tasks'])
            
            # Выводим статистику по файлу
            stats = result['statistics']
            print(f"   📊 Заголовков: {stats['total_headers']}")
            print(f"   📋 Задач: {stats['total_tasks']}")
            print(f"   🏢 Задач с компаниями: {stats['tasks_with_companies']}")
            print(f"   🏪 Всего компаний в файле: {stats['total_companies']}")
            
            if result['companies']:
                print(f"   📝 Компании: {', '.join(result['companies'][:5])}")
                if len(result['companies']) > 5:
                    print(f"       ... и еще {len(result['companies']) - 5}")
    
    print("\n" + "=" * 80)
    print("📈 ОБЩАЯ СТАТИСТИКА:")
    print(f"   📄 Обработано файлов: {len(all_results)}")
    print(f"   📋 Всего задач: {len(all_tasks)}")
    print(f"   🏢 Задач с компаниями: {len([t for t in all_tasks if t['companies']])}")
    print(f"   🏪 Уникальных компаний: {len(all_companies)}")
    
    print(f"\n🏢 ВСЕ НАЙДЕННЫЕ КОМПАНИИ ({len(all_companies)}):")
    sorted_companies = sorted(list(all_companies))
    for i, company in enumerate(sorted_companies, 1):
        print(f"   {i:3d}. {company}")
    
    print(f"\n📋 ПРИМЕРЫ ЗАДАЧ С КОМПАНИЯМИ:")
    tasks_with_companies = [t for t in all_tasks if t['companies']][:15]  # Первые 15
    for i, task in enumerate(tasks_with_companies, 1):
        companies_str = ', '.join(task['companies'][:3])  # Первые 3 компании
        if len(task['companies']) > 3:
            companies_str += f" (и еще {len(task['companies']) - 3})"
        print(f"   {i:2d}. '{task['normalized_title']}' -> [{companies_str}]")
    
    # Сохраняем результаты в JSON
    output_data = {
        'summary': {
            'total_files': len(all_results),
            'total_tasks': len(all_tasks),
            'tasks_with_companies': len([t for t in all_tasks if t['companies']]),
            'unique_companies': len(all_companies)
        },
        'all_companies': sorted(list(all_companies)),
        'all_tasks': all_tasks,
        'file_results': all_results
    }
    
    with open('extraction_results_improved.json', 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Результаты сохранены в 'extraction_results_improved.json'")
    
    return output_data

if __name__ == "__main__":
    analyze_all_md_files() 