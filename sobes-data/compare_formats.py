import json
import os
import re
from collections import Counter

# Загружаем JSON данные
with open('MASSIV_GROUPED.json', 'r', encoding='utf-8') as f:
    json_data = json.load(f)

print('=== СРАВНЕНИЕ JSON И MARKDOWN ДАННЫХ ===')

# Подсчитываем файлы в reports
reports_dir = 'reports'
if os.path.exists(reports_dir):
    md_files = [f for f in os.listdir(reports_dir) if f.endswith('.md')]
    print(f'Файлов markdown отчетов: {len(md_files)}')
else:
    print('Папка reports не найдена')
    md_files = []

# Статистика JSON
total_json_records = sum(company['count'] for company in json_data)
total_json_companies = len(json_data)

print(f'Записей в JSON: {total_json_records}')
print(f'Компаний в JSON: {total_json_companies}')

# Анализ покрытия
coverage_ratio = len(md_files) / total_json_records if total_json_records > 0 else 0
print(f'Покрытие отчетами: {coverage_ratio:.1%} ({len(md_files)} отчетов на {total_json_records} записей)')

# Анализ временных паттернов в названиях файлов
date_patterns = []
timestamp_patterns = []

for filename in md_files:
    # Ищем даты в формате YYYY-MM-DD
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
    if date_match:
        date_patterns.append(date_match.group(1))
    
    # Ищем таймстампы в формате числа
    timestamp_match = re.search(r'(\d{10,})', filename)
    if timestamp_match:
        timestamp_patterns.append(timestamp_match.group(1))

print(f'\nФайлов с датами в названии: {len(date_patterns)}')
print(f'Файлов с таймстампами в названии: {len(timestamp_patterns)}')

if date_patterns:
    date_counter = Counter(date_patterns)
    print('Топ-5 дат в названиях файлов:')
    for date, count in date_counter.most_common(5):
        print(f'  {date}: {count} файлов')

# Проверяем типы отчетов
report_types = {
    'transcript_llm_FULL_report': 0,
    'other_formats': 0
}

for filename in md_files:
    if 'transcript_llm_FULL_report' in filename:
        report_types['transcript_llm_FULL_report'] += 1
    else:
        report_types['other_formats'] += 1

print(f'\nТипы отчетов:')
for report_type, count in report_types.items():
    print(f'  {report_type}: {count} файлов')

# Анализ ID в названиях файлов  
id_patterns = []
for filename in md_files:
    # Ищем паттерн 2208833410_XXXX_
    id_match = re.search(r'2208833410_(\d+)_', filename)
    if id_match:
        id_patterns.append(id_match.group(1))

print(f'\nФайлов с ID паттерном: {len(id_patterns)}')

# Читаем несколько отчетов для анализа структуры
print(f'\n=== АНАЛИЗ СТРУКТУРЫ ОТЧЕТОВ ===')
sample_reports = md_files[:3]  # Берем первые 3 файла

for filename in sample_reports:
    filepath = os.path.join(reports_dir, filename)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Подсчитываем блоки
        blocks = {
            'Блок 1': 'Блок 1:' in content,
            'Блок 2': 'Блок 2:' in content,
            'Блок 3': 'Блок 3:' in content,
            'Блок 4': 'Блок 4:' in content,
        }
        
        # Подсчитываем вопросы в таблице
        table_rows = len(re.findall(r'^\|.*\|.*\|.*\|$', content, re.MULTILINE))
        questions_count = max(0, table_rows - 1)  # Минус заголовок
        
        print(f'\n{filename}:')
        print(f'  Размер: {len(content)} символов')
        print(f'  Блоки: {sum(blocks.values())}/4')
        print(f'  Вопросов в таблице: {questions_count}')
        
    except Exception as e:
        print(f'Ошибка чтения {filename}: {e}')

print(f'\n=== ВЫВОДЫ ===')
print(f'1. JSON содержит {total_json_records} записей, markdown отчетов {len(md_files)}')
print(f'2. Селективность обработки: ~{coverage_ratio:.1%}')
print(f'3. Основной формат отчетов: transcript_llm_FULL_report')
print(f'4. Отчеты имеют структурированный 4-блочный формат')