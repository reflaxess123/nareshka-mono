import json
import sys
from collections import Counter
import re
from datetime import datetime

# Загружаем данные
with open('MASSIV_GROUPED.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print('=== БАЗОВАЯ СТАТИСТИКА ===')
print(f'Количество компаний: {len(data)}')
total_records = sum(company['count'] for company in data)
print(f'Общее количество записей: {total_records}')

# Проверяем консистентность count
inconsistent = []
for company in data:
    actual_count = len(company['records'])
    if company['count'] != actual_count:
        inconsistent.append((company['company'], company['count'], actual_count))

if inconsistent:
    print(f'НАЙДЕНЫ НЕСООТВЕТСТВИЯ COUNT: {len(inconsistent)}')
    for comp, declared, actual in inconsistent[:5]:
        print(f'  {comp}: заявлено {declared}, фактически {actual}')
else:
    print('Поле count соответствует фактическому количеству записей')

# Анализ заполненности полей
empty_content = 0
empty_full_content = 0  
identical_content = 0
content_lengths = []
full_content_lengths = []

for company in data:
    for record in company['records']:
        # Проверяем пустые поля
        if not record.get('content', '').strip():
            empty_content += 1
        if not record.get('full_content', '').strip():
            empty_full_content += 1
            
        # Проверяем идентичность
        if record.get('content', '') == record.get('full_content', ''):
            identical_content += 1
            
        # Собираем длины
        content_lengths.append(len(record.get('content', '')))
        full_content_lengths.append(len(record.get('full_content', '')))

print(f'\nПустые content: {empty_content}')
print(f'Пустые full_content: {empty_full_content}')
print(f'Идентичные content и full_content: {identical_content} ({identical_content/total_records*100:.1f}%)')
print(f'Средняя длина content: {sum(content_lengths)/len(content_lengths):.0f} символов')
print(f'Средняя длина full_content: {sum(full_content_lengths)/len(full_content_lengths):.0f} символов')