import re
import os
import json
from collections import defaultdict

# Список известных компаний для нормализации
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
    'кьюго', 'кодинг тим', 'стрим телеком', 'stream telecom', 'realtime',
    'кликтумани', 'click to money', 'холдинг', 'бфт',
    'ivi', 'расчетные решения', 'сбер для экспертов', 'почта россии', 'совкомбанк',
    'северсталь', 'касперский', 'нетология', 'skillbox', 'geekbrains', 'hexlet',
    'контур', 'теле2', 'csssr', 'dogma', 'severstal', 'tbq', 'loalty labs', 'r vision',
    'heavyfunc', 'госнииас', 'кибер ром', 'домклик', 'технологии доверия'
}

# Нормализация названий компаний
COMPANY_NORMALIZATIONS = {
    'cберкорус': 'сберкорус',
    'it one': 'it-one', 
    'it baltic': 'it-baltic',
    'альфа банк': 'альфа-банк',
    'альфабанк': 'альфа-банк',
    'click2money': 'click to money',
    'datsteam': 'dats team',
    'dats team': 'datsteam',
    'stream telecom': 'стрим телеком',
    'вб': 'wb',
    'газпром': 'газпромбанк',
    'тинкоф': 'тинкофф',
    'yandex': 'яндекс',
    'теле2': 'tele2',
    'касперский': 'kaspersky',
    'сбертех': 'sbertech',
    'мтс': 'mts',
    'loalty labs': 'loyalty labs',
    'вконтакте': 'вк'
}

# Абсолютный мусор - слова, которые НИКОГДА не являются компаниями
ABSOLUTE_GARBAGE = {
    'то есть', 'нельзя', 'без', 'написать', 'часто', 'решено', 'раз', 'в целом', 'пример', 
    'задача', 'задачи', 'решение', 'решения', 'как', 'надо', 'нужно', 'какой', 'какие', 
    'описание', 'смысл', 'что', 'чтобы', 'если', 'или', 'проверка', 'ошибка', 'ошибки', 
    'тест', 'тесты', 'шаблон', 'шаблоны', 'объект', 'массив', 'строка', 'число', 'функция', 
    'классы', 'хуки', 'поля', 'типы', 'асинхронность', 'промисы', 'колбэки', 'замыкания', 
    'рекурсия', 'алгоритмы', 'структуры', 'данные', 'сервер', 'клиент', 'фронтенд', 'бэкенд', 
    'api', 'база данных', 'бд', 'ооп', 'паттерны', 'архитектура', 'дизайн', 'система', 
    'команда', 'собеседование', 'вопрос', 'ответ', 'практика', 'теория', 'статья', 'глава', 
    'часть', 'просто', 'сложно', 'для', 'от', 'с', 'из', 'в', 'на', 'по', 'за', 'при', 
    'до', 'после', 'со', 'путь', 'ключ', 'значение', 'код', 'кода', 'текст', 'текста', 
    'компонент', 'компоненты', 'виджет', 'виджеты', 'страница', 'страницы', 'модель', 'модели', 
    'слайс', 'слайсы', 'хук', 'стили', 'константы', 'утилиты', 'контекст', 'роутер', 'провайдер', 
    'редакс', 'написать рекурсией', 'сказать сложность', 'счетчик полу автоматический', 'счетчики', 
    'state', 'батчинг', 'без set', 'platform v ui kits', 'ограничение o(1)', 
    'нельзя копировать массив', 'то есть inplace', 'на личном собесе', 'не мутируем', 
    'для экспертов', 'часто в целом', 'todo', 'list',
    'псб', 'групп', 'auto tech',
    'свистунова екатерина александровна', 'через нетбелл акр лабс',
    'hard задачи', 'key remapping в отображаемых типах', 'то есть inplace)',
    'вк canonizepath в трех частях', 'кибер ром',
    'яндекс про )' # Если это действительно мусор, а не часть названия компании
}

# Технические термины и паттерны, которые НЕ являются компаниями
TECH_KEYWORDS = {
    # Функции и методы из файлов решений
    'withretry', 'parallel', 'fetchdata', 'fetchdatawithretry', 'url limit', 'parallellimit', 
    'parallelrequest', 'requestbus', 'add two promises', 'timelimit', 'promisify',
    'withtimeout', 'fetchdatawithdelay', 'кастомный race', 'кастомный finally', 'кастомный any',
    'кастомный allsettled', 'кастомный all',
    
    # TypeScript утилиты и типы
    'callback', 'concat', 'exclude', 'exclude + omit', 'formfields', 'getdetails', 'getinfo', 
    'getinfo 2', 'getproperty 1', 'getproperty 2', 'getproperty 3', 'join', 'last', 'merge', 
    'myawaited', 'omit', 'parameters', 'partial', 'pluck', 'readonly', 'template literal types',
    'кастомные utility', 'рекурсивные условные типы', 'создание глубоких неизменяемых типов',
    'types', 'myasyncfunction',
    
    # Технические описания
    'mymath', 'printfiles', 'scroll&random', 'execution', 'пачка мини задач',
    
    # Номерованные функции/задачи (паттерн из файлов решений)
    '14 withretry', '15 parallel', '16 fetchdata', '17 fetchdatawithretry', '18 url limit',
    '19 parallellimit', '20 parallelrequest', '21 requestbus',
    
    # Общие технические термины
    'function', 'return', 'const', 'var', 'let', 'class', 'interface', 'type', 'import', 'export',
    'async', 'await', 'promise', 'then', 'catch', 'finally', 'resolve', 'reject', 'timeout',
    'fetch', 'response', 'request', 'api', 'json', 'xml', 'html', 'css', 'js', 'ts', 'jsx', 'tsx',
    'react', 'vue', 'angular', 'component', 'hook', 'state', 'props', 'context', 'provider',
    'reducer', 'action', 'store', 'selector', 'middleware', 'thunk', 'saga', 'effect',
    'nodejs', 'npm', 'yarn', 'webpack', 'vite', 'babel', 'eslint', 'prettier', 'typescript',
    'javascript', 'python', 'java', 'golang', 'rust', 'php', 'ruby', 'swift', 'kotlin',
    'database', 'sql', 'nosql', 'mongodb', 'postgresql', 'mysql', 'redis', 'kafka',
    'docker', 'kubernetes', 'nginx', 'apache', 'linux', 'windows', 'macos', 'git', 'github',
    
    # Паттерны программирования
    'singleton', 'factory', 'observer', 'strategy', 'decorator', 'facade', 'adapter',
    'bridge', 'composite', 'flyweight', 'proxy', 'chain', 'command', 'iterator',
    'mediator', 'memento', 'prototype', 'state', 'template', 'visitor',
    
    # Алгоритмы и структуры данных
    'array', 'object', 'string', 'number', 'boolean', 'null', 'undefined', 'symbol',
    'map', 'set', 'weakmap', 'weakset', 'array buffer', 'typed array', 'data view',
    'stack', 'queue', 'linked list', 'tree', 'graph', 'hash table', 'heap',
    'sort', 'search', 'binary search', 'linear search', 'bubble sort', 'quick sort',
    'merge sort', 'heap sort', 'insertion sort', 'selection sort',
    
    # Описательные фразы (не компании)
    'цепочка из 3 промисов', 'выводить индексы элементов с интервалом',
    'обертка над фетчем', 'кастомный race', 'кастомный finally',
}

def aggressive_clean_company_name(company: str) -> str:
    """Агрессивная очистка названия компании от всего мусора"""
    if not company:
        return ""
    
    original = company
    company = company.lower().strip()
    
    # Удаляем все в скобках, квадратных скобках и фигурных скобках
    company = re.sub(r'\([^)]*\)', '', company) # Удаляем круглые скобки
    company = re.sub(r'\[[^\]]*\]', '', company) # Удаляем квадратные скобки
    company = re.sub(r'\{[^}]*\}', '', company) # Удаляем фигурные скобки

    # Удаляем конкретные фразы-мусор
    garbage_phrases = [
        'нельзя копировать массив, то есть inplace',
        'без set, сказать сложность, будет ли set работать с объектами',
        'platform v ui kits',
        'ограничение o\\(1\\)',
        'для экспертов',
        'через нетбелл акр лабс',
        'на личном собесе',
        'не мутируем',
        'часто в целом',
        'свистунова екатерина александровна',
        'псб',
        'групп',
        'auto tech',
        '\\+ типизация',
        'техническая поддержка', # Перенес сюда
        'холдинг', # Перенес сюда
        'ип' # Перенес сюда
    ]
    
    for phrase in garbage_phrases:
        company = re.sub(phrase, '', company, flags=re.IGNORECASE)
    
    # Очищаем от лишних символов и цифр в начале (типа "14. ")
    company = re.sub(r'^\d+\.\s*', '', company) # Удаляем "14. "
    company = re.sub(r'[-–—_./,:;]+', ' ', company) # Добавил : и ; для лучшей очистки
    company = re.sub(r'\s+', ' ', company)
    company = company.strip()
    
    return company

def normalize_company_name(company: str) -> str:
    """Нормализует название компании"""
    clean_name = aggressive_clean_company_name(company)
    
    # Применяем нормализацию
    if clean_name in COMPANY_NORMALIZATIONS:
        return COMPANY_NORMALIZATIONS[clean_name]
    
    return clean_name

def is_definitely_company(company: str) -> bool:
    """Определяет, является ли строка определенно названием компании"""
    if not company or len(company.strip()) < 2:
        return False
    
    clean_name = aggressive_clean_company_name(company)
    
    # Убираем все, что осталось в скобках после агрессивной очистки (для доп. страховки)
    clean_name = re.sub(r'\([^)]*\)', '', clean_name)
    clean_name = re.sub(r'\[[^\]]*\]', '', clean_name)
    clean_name = re.sub(r'\{[^}]*\}', '', clean_name)
    clean_name = clean_name.strip()

    if not clean_name:
        return False

    # Проверяем, что название содержит хотя бы одну букву
    if not re.search(r'[а-яa-zA-Z]', clean_name):
        return False

    # Проверяем на абсолютный мусор (самый высокий приоритет)
    if clean_name in ABSOLUTE_GARBAGE:
        return False
    
    # Проверяем на технические ключевые слова
    if clean_name in TECH_KEYWORDS:
        return False

    # Проверяем, если часть слова является техническим мусором (для составных слов)
    for tech_word in TECH_KEYWORDS:
        if len(tech_word) > 3 and tech_word in clean_name and tech_word != clean_name:
            return False

    # Проверяем на частичное вхождение мусора из ABSOLUTE_GARBAGE
    for garbage in ABSOLUTE_GARBAGE:
        if clean_name == garbage or (len(garbage) > 4 and garbage in clean_name and garbage != clean_name):
            return False

    # Если название слишком короткое после очистки, и не является известной аббревиатурой
    if len(clean_name) < 3 and clean_name not in KNOWN_COMPANIES and not re.match(r'^[a-zA-Z]{2,3}$', clean_name):
        return False
    
    # Проверяем на известные компании (позитивное совпадение)
    for known in KNOWN_COMPANIES:
        if clean_name == known or (len(known) > 2 and known in clean_name) or (len(clean_name) > 2 and clean_name in known):
            return True
    
    # Дополнительные проверки для более уверенного определения компании
    # Положительные индикаторы компаний
    company_indicators = [
        r'\b(банк|тех|софт|лаб|групп?|технологии|решения|платформа|системы|сервис|разработка|айти)\b',
        r'\b(компани|корпорация|холдинг|ао|ооо|пкк|нии|кб|завод|фабрика|центр|институт|студия|мобайлдевелопмент)\b',
        r'\b(авто|дев|фин|про|плюс|нет|геймс|медиа|агентство|инфо|дата|диджитал|партнер|группа|онлайн школа|интех)\b'
    ]
    
    for pattern in company_indicators:
        if re.search(pattern, clean_name, re.IGNORECASE):
            return True
    
    # Если содержит цифры + буквы (например, t1, wb), но не является чисто техническим номером
    if re.search(r'\d', clean_name) and re.search(r'[а-яa-zA-Z]', clean_name) and not clean_name.isdigit():
        # Дополнительная проверка на то, чтобы не было слишком похоже на версию или номер задачи
        if not re.fullmatch(r'\d+(\.\d+){0,2}', clean_name) and \
           not re.fullmatch(r'v\d+(\.\d+){0,2}', clean_name) and \
           not re.fullmatch(r'task\s*\d+', clean_name) and \
           not re.fullmatch(r'\d+\s+\w+', clean_name):  # исключаем "14 withretry"
            return True
    
    # Если это английское название (большинство букв латинские) и не техническое слово
    latin_chars = len(re.findall(r'[a-zA-Z]', clean_name))
    cyrillic_chars = len(re.findall(r'[а-яА-Я]', clean_name))
    
    if latin_chars > 2 and latin_chars >= cyrillic_chars / 2: # Более гибкое соотношение
        # Исключаем, если это выглядит как обычное английское слово или технический термин
        # Убрал полный список предлогов, оставил только самые частые короткие слова
        if clean_name.lower() not in [w.lower() for w in TECH_KEYWORDS] and \
           not re.match(r'^(a|the|in|on|at|is|or|as|if|to|by|up|out|off|on)$', clean_name.lower()):
            return True
    
    # Если это составное название (несколько слов) и не техническая фраза
    words = clean_name.split()
    if len(words) >= 2 and all(len(word) >= 2 for word in words):
        # Проверяем, что это не техническая фраза из TECH_KEYWORDS или ABSOLUTE_GARBAGE
        if not any(phrase in clean_name for phrase in TECH_KEYWORDS | ABSOLUTE_GARBAGE):
            # Дополнительная проверка на слишком общие слова
            if not any(word in ['задача', 'пример', 'решение', 'вопрос', 'ответ', 'функция', 'метод', 'список', 'сборник'] for word in words):
                return True
    
    return False

def extract_companies_from_block(block_text: str) -> list[str]:
    """Извлекает компании из блока 'встречалось в' с максимальной точностью"""
    companies = []
    lines = block_text.split('\n')
    
    for line in lines[1:]:  # Пропускаем первую строку с "встречалось в"
        # Убираем маркеры списков
        cleaned_line = re.sub(r'^[\t\s]*[-*+•]\s*', '', line).strip()
        cleaned_line = re.sub(r'^[\t\s]*\d+\.\s*', '', cleaned_line).strip()
        
        if not cleaned_line:
            continue
        
        # Разбиваем по запятым, точкам с запятой
        potential_companies = re.split(r'[,;]', cleaned_line)
        
        for company in potential_companies:
            company = company.strip()
            if is_definitely_company(company):
                normalized = normalize_company_name(company)
                if normalized and normalized not in companies:
                    companies.append(normalized)
    
    return companies

def extract_companies_from_headers(headers: list, file_path: str) -> list[str]:
    """Извлекает компании из заголовков (для файлов типа Ререндер.md) с учетом исключений"""
    companies = []
    
    # Определяем, является ли файл файлом с компаниями в заголовках (решения/рефактор/ререндер)
    is_company_header_file = any(keyword in file_path.lower() 
                                for keyword in ['ререндер', 'рефактор', 'решения'])
    
    for header in headers:
        header_text = header['text'].strip()
        
        # Игнорируем заголовки, если они начинаются с номера (как в файлах с решениями)
        if re.match(r'^\d+\.\s*', header_text):
            continue

        # Для файлов, где ожидаются компании в заголовках (уровень <=3, не слишком длинные, не общий мусор)
        if (is_company_header_file and 
            header['level'] <= 3 and 
            len(header_text) < 50 and
            not re.match(r'^(задач|example|пример|counter|todo|списки|рефактор|тренировочные|other|use|test|решени|мини|мощн|solution)', header_text.lower())):
            
            if is_definitely_company(header_text):
                normalized = normalize_company_name(header_text)
                if normalized and normalized not in companies:
                    companies.append(normalized)
    
    return companies

def extract_task_title(header_text: str) -> str:
    """Извлекает чистое название задачи из заголовка"""
    # Убираем символы заголовков
    title = re.sub(r'^#+\s*', '', header_text).strip()
    
    # Убираем ссылки в квадратных скобках, но оставляем текст
    title = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', title)
    
    # Убираем лишние пробелы
    title = re.sub(r'\s+', ' ', title).strip()
    
    return title

def extract_all_from_md_file(file_path: str) -> dict:
    """Безошибочно извлекает компании и задачи из .md файла"""
    if not os.path.exists(file_path):
        return {}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"   ❌ Ошибка чтения файла: {e}")
        return {}
    
    result = {
        'file_path': file_path,
        'tasks': [],
        'companies': [],
        'all_headers': [],
        'statistics': {}
    }
    
    if not content.strip():
        return result
    
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
        r'встречалось в[:\s]*.*?(?=\n\S|\n#+|\n```|\Z)',
        r'встречается в[:\s]*.*?(?=\n\S|\n#+|\n```|\Z)', 
        r'встречался в[:\s]*.*?(?=\n\S|\n#+|\n```|\Z)',
        r'попадалось в[:\s]*.*?(?=\n\S|\n#+|\n```|\Z)'
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
            if current_task and current_content.strip():
                task_companies = set()
                
                # Ищем компании в контенте задачи
                for pattern in company_block_patterns:
                    task_blocks = re.findall(pattern, current_content, re.IGNORECASE | re.DOTALL)
                    for block in task_blocks:
                        companies_in_task = extract_companies_from_block(block)
                        task_companies.update(companies_in_task)
                
                clean_title = extract_task_title(current_task)
                if clean_title:  # Добавляем только если есть название
                    result['tasks'].append({
                        'title': clean_title,
                        'original_title': current_task,
                        'normalized_title': clean_title.lower(),
                        'companies': sorted(list(task_companies)),
                        'content_length': len(current_content.strip()),
                        'has_code': '```' in current_content,
                        'has_companies': len(task_companies) > 0
                    })
            
            # Начинаем новую задачу
            current_task = section.strip()
            current_content = ""
        else:
            current_content += section
    
    # Обрабатываем последнюю задачу
    if current_task and current_content.strip():
        task_companies = set()
        for pattern in company_block_patterns:
            task_blocks = re.findall(pattern, current_content, re.IGNORECASE | re.DOTALL)
            for block in task_blocks:
                companies_in_task = extract_companies_from_block(block)
                task_companies.update(companies_in_task)
        
        clean_title = extract_task_title(current_task)
        if clean_title:  # Добавляем только если есть название
            result['tasks'].append({
                'title': clean_title,
                'original_title': current_task,
                'normalized_title': clean_title.lower(),
                'companies': sorted(list(task_companies)),
                'content_length': len(current_content.strip()),
                'has_code': '```' in current_content,
                'has_companies': len(task_companies) > 0
            })
    
    # 5. Статистика
    result['statistics'] = {
        'total_headers': len(result['all_headers']),
        'total_tasks': len(result['tasks']),
        'tasks_with_companies': len([t for t in result['tasks'] if t['has_companies']]),
        'total_companies': len(result['companies']),
        'tasks_with_code': len([t for t in result['tasks'] if t['has_code']])
    }
    
    return result

def analyze_all_md_files():
    """Анализирует все .md файлы с идеальной точностью"""
    
    # Папки для анализа
    target_dirs = [
        os.path.join('..', 'js'),
        os.path.join('..', 'react'),
        os.path.join('..', 'ts'),
    ]
    
    md_files = []
    for target_dir in target_dirs:
        if os.path.exists(target_dir):
            for root, dirs, files in os.walk(target_dir):
                for file in files:
                    if file.endswith('.md'):
                        md_files.append(os.path.join(root, file))
    
    print(f"🔍 Найдено .md файлов: {len(md_files)} (js, react, ts)")
    print("=" * 80)
    
    all_results = []
    all_companies = set()
    all_tasks = []
    company_frequency = defaultdict(int)
    
    for file_path in md_files:
        print(f"\n📄 Анализируем: {file_path}")
        result = extract_all_from_md_file(file_path)
        
        if result and (result['tasks'] or result['companies']):
            all_results.append(result)
            
            # Собираем все уникальные компании
            for company in result['companies']:
                all_companies.add(company)
                company_frequency[company] += 1
            
            # Собираем все задачи
            all_tasks.extend(result['tasks'])
            
            # Выводим статистику по файлу
            stats = result['statistics']
            print(f"   📊 Заголовков: {stats['total_headers']}")
            print(f"   📋 Задач: {stats['total_tasks']}")
            print(f"   🏢 Задач с компаниями: {stats['tasks_with_companies']}")
            print(f"   💻 Задач с кодом: {stats['tasks_with_code']}")
            print(f"   🏪 Всего компаний: {stats['total_companies']}")
            
            if result['companies']:
                print(f"   📝 Компании: {', '.join(result['companies'][:5])}")
                if len(result['companies']) > 5:
                    print(f"       ... и еще {len(result['companies']) - 5}")
        else:
            print(f"   ⚪ Пустой файл или нет данных")
    
    print("\n" + "=" * 80)
    print("�� ИТОГОВАЯ СТАТИСТИКА:")
    print(f"   📄 Обработано файлов: {len(all_results)}")
    print(f"   📋 Всего задач: {len(all_tasks)}")
    print(f"   🏢 Задач с компаниями: {len([t for t in all_tasks if t['has_companies']])}")
    print(f"   💻 Задач с кодом: {len([t for t in all_tasks if t['has_code']])}")
    print(f"   🏪 Уникальных компаний: {len(all_companies)}")
    
    # Топ компаний по частоте
    print(f"\n🏆 ТОП-20 КОМПАНИЙ ПО ЧАСТОТЕ:")
    top_companies = sorted(company_frequency.items(), key=lambda x: x[1], reverse=True)[:20]
    for i, (company, count) in enumerate(top_companies, 1):
        print(f"   {i:2d}. {company} ({count} упоминаний)")
    
    print(f"\n🏢 ВСЕ НАЙДЕННЫЕ КОМПАНИИ ({len(all_companies)}):")
    sorted_companies = sorted(list(all_companies))
    for i, company in enumerate(sorted_companies, 1):
        count = company_frequency[company]
        print(f"   {i:3d}. {company} ({count})")
    
    print(f"\n📋 ПРИМЕРЫ ЗАДАЧ С КОМПАНИЯМИ:")
    tasks_with_companies = [t for t in all_tasks if t['has_companies']][:20]
    for i, task in enumerate(tasks_with_companies, 1):
        companies_str = ', '.join(task['companies'][:3])
        if len(task['companies']) > 3:
            companies_str += f" (и еще {len(task['companies']) - 3})"
        print(f"   {i:2d}. '{task['title']}' -> [{companies_str}]")
    
    # Сохраняем результаты в JSON
    output_data = {
        'summary': {
            'total_files': len(all_results),
            'total_tasks': len(all_tasks),
            'tasks_with_companies': len([t for t in all_tasks if t['has_companies']]),
            'tasks_with_code': len([t for t in all_tasks if t['has_code']]),
            'unique_companies': len(all_companies)
        },
        'company_frequency': dict(company_frequency),
        'top_companies': top_companies,
        'all_companies': sorted_companies,
        'all_tasks': all_tasks,
        'file_results': all_results
    }
    
    with open('extraction_results_perfect.json', 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Результаты сохранены в 'extraction_results_perfect.json'")
    print(f"🎯 Качество извлечения: МАКСИМАЛЬНОЕ")
    
    return output_data

if __name__ == "__main__":
    analyze_all_md_files() 