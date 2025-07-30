import json
import hashlib
from collections import Counter, defaultdict
import re
from datetime import datetime

# Загружаем данные
with open('MASSIV_GROUPED.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print('=== АНАЛИЗ КАЧЕСТВА ДАННЫХ ===')

# Анализ обрезанного контента
truncated_content = 0
truncated_full_content = 0
all_records = []

for company in data:
    for record in company['records']:
        all_records.append(record)
        
        # Проверяем на обрезанный контент (заканчивается на "...")
        if record.get('content', '').strip().endswith('...'):
            truncated_content += 1
        if record.get('full_content', '').strip().endswith('...'):
            truncated_full_content += 1

print(f'Записи с обрезанным content (...): {truncated_content}')
print(f'Записи с обрезанным full_content (...): {truncated_full_content}')

# Поиск дубликатов по хешу содержимого
content_hashes = defaultdict(list)
full_content_hashes = defaultdict(list)

for i, record in enumerate(all_records):
    # Хешируем content
    content_hash = hashlib.md5(record.get('content', '').encode()).hexdigest()
    content_hashes[content_hash].append(i)
    
    # Хешируем full_content
    full_content_hash = hashlib.md5(record.get('full_content', '').encode()).hexdigest()
    full_content_hashes[full_content_hash].append(i)

# Находим дубликаты
content_duplicates = {h: indices for h, indices in content_hashes.items() if len(indices) > 1}
full_content_duplicates = {h: indices for h, indices in full_content_hashes.items() if len(indices) > 1}

print(f'\nДубликаты по content: {len(content_duplicates)} групп')
if len(content_duplicates) > 0:
    total_duplicate_records = sum(len(indices) for indices in content_duplicates.values())
    print(f'Всего записей-дубликатов по content: {total_duplicate_records}')

print(f'Дубликаты по full_content: {len(full_content_duplicates)} групп')
if len(full_content_duplicates) > 0:
    total_duplicate_records = sum(len(indices) for indices in full_content_duplicates.values())
    print(f'Всего записей-дубликатов по full_content: {total_duplicate_records}')

# Анализ временных паттернов
timestamps = []
for record in all_records:
    timestamp_str = record.get('timestamp', '')
    if timestamp_str:
        try:
            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
            timestamps.append(timestamp)
        except:
            pass

if timestamps:
    timestamps.sort()
    print(f'\n=== ВРЕМЕННЫЕ ПАТТЕРНЫ ===')
    print(f'Период данных: {timestamps[0].strftime("%Y-%m-%d")} - {timestamps[-1].strftime("%Y-%m-%d")}')
    
    # Группировка по годам
    years = Counter(ts.year for ts in timestamps)
    print('Распределение по годам:')
    for year, count in sorted(years.items()):
        print(f'  {year}: {count} интервью')
    
    # Группировка по месяцам
    months = Counter(f'{ts.year}-{ts.month:02d}' for ts in timestamps)
    print(f'\nТоп-5 месяцев по активности:')
    for month, count in months.most_common(5):
        print(f'  {month}: {count} интервью')

print(f'\n=== ТОП КОМПАНИЙ ===')
# Сортируем компании по количеству записей
companies_by_count = sorted(data, key=lambda x: x['count'], reverse=True)
print('Топ-10 компаний по количеству интервью:')
for i, company in enumerate(companies_by_count[:10], 1):
    print(f'{i:2d}. {company["company"]}: {company["count"]} интервью')