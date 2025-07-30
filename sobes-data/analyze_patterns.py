import json
import re
from collections import Counter

# Загружаем данные
with open('MASSIV_GROUPED.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Собираем все тексты для анализа
all_texts = []
all_records = []

for company in data:
    for record in company['records']:
        all_records.append(record)
        # Объединяем content и full_content для анализа
        text = (record.get('content', '') + ' ' + record.get('full_content', '')).lower()
        all_texts.append(text)

combined_text = ' '.join(all_texts)

print('=== ТЕХНОЛОГИЧЕСКИЕ ПАТТЕРНЫ ===')

# Поиск технологий
technologies = {
    'react': r'\breact\b',
    'javascript': r'\bjavascript\b|js\b',
    'typescript': r'\btypescript\b|ts\b',
    'vue': r'\bvue\b',
    'angular': r'\bangular\b',
    'node': r'\bnode\.?js\b',
    'python': r'\bpython\b',
    'java': r'\bjava\b',
    'go': r'\bgo\b|\bgolang\b',
    'php': r'\bphp\b',
    'css': r'\bcss\b',
    'html': r'\bhtml\b',
    'sql': r'\bsql\b',
    'redux': r'\bredux\b',
    'next': r'\bnext\.?js\b',
    'express': r'\bexpress\b',
    'mongodb': r'\bmongodb\b|mongo\b',
    'postgresql': r'\bpostgresql\b|postgres\b',
    'docker': r'\bdocker\b',
    'git': r'\bgit\b',
    'webpack': r'\bwebpack\b',
    'babel': r'\bbabel\b'
}

tech_counts = {}
for tech, pattern in technologies.items():
    matches = len(re.findall(pattern, combined_text, re.IGNORECASE))
    if matches > 0:
        tech_counts[tech] = matches

print('Топ-15 технологий по упоминаниям:')
for tech, count in sorted(tech_counts.items(), key=lambda x: x[1], reverse=True)[:15]:
    print(f'{tech.upper()}: {count} упоминаний')

print('\n=== ЭТАПЫ ИНТЕРВЬЮ ===')
# Поиск этапов интервью
stages = Counter()
for i in range(1, 6):
    pattern = f'{i}\\s*этап'
    matches = len(re.findall(pattern, combined_text, re.IGNORECASE))
    if matches > 0:
        stages[f'{i} этап'] = matches

for stage, count in stages.most_common():
    print(f'{stage}: {count} упоминаний')

print('\n=== АНАЛИЗ АВТОРОВ TELEGRAM ===')
# Извлекаем авторов из паттерна "Автор -> ID:"
authors = Counter()
for record in all_records:
    content = record.get('content', '')
    # Паттерн: имя -> число:
    match = re.search(r'([А-Яа-яA-Za-z\s]+)\s*->\s*\d+:', content)
    if match:
        author = match.group(1).strip()
        if len(author) > 2 and len(author) < 50:  # Фильтруем разумные имена
            authors[author] += 1

print('Топ-10 авторов по количеству записей:')
for author, count in authors.most_common(10):
    print(f'{author}: {count} записей')

print('\n=== АНАЛИЗ CONTENT_HASH (ЕСЛИ ЕСТЬ) ===')
# Проверяем наличие поля content_hash
has_content_hash = False
for record in all_records:
    if 'content_hash' in record:
        has_content_hash = True
        break

if has_content_hash:
    print('Поле content_hash найдено в данных')
    # Анализ дубликатов по content_hash
    content_hashes = Counter()
    for record in all_records:
        if 'content_hash' in record:
            content_hashes[record['content_hash']] += 1
    
    duplicates_by_hash = {h: count for h, count in content_hashes.items() if count > 1}
    print(f'Дубликатов по content_hash: {len(duplicates_by_hash)} групп')
else:
    print('Поле content_hash отсутствует в данных')

print(f'\n=== ИТОГОВАЯ СТАТИСТИКА ===')
print(f'Всего записей: {len(all_records)}')
print(f'Всего компаний: {len(data)}')
print(f'Средняя длина текста записи: {sum(len(text) for text in all_texts) / len(all_texts):.0f} символов')