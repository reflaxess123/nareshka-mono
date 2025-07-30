#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

with open('MASSIV_GROUPED.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print('=== ПРОВЕРКА КОНСИСТЕНТНОСТИ ===')
inconsistent_counts = 0
for group in data:
    actual_count = len(group['records'])
    declared_count = group['count']
    if actual_count != declared_count:
        inconsistent_counts += 1
        print(f'Компания "{group["company"]}": заявлено {declared_count}, фактически {actual_count}')

print(f'Проверено {len(data)} групп компаний')
if inconsistent_counts == 0:
    print('Все поля count соответствуют фактическому количеству записей')
else:
    print(f'Найдено {inconsistent_counts} несоответствий в поле count')

print('\n=== ИТОГОВАЯ СХЕМА ДАННЫХ ===')
print('Корневой уровень: массив объектов компаний')
print('Каждый объект компании содержит:')
print('- company (string): название компании')
print('- count (integer): количество записей интервью')
print('- records (array): массив записей интервью')
print('\nКаждая запись интервью содержит:')
print('- timestamp (string): временная метка в формате YYYY-MM-DD HH:MM:SS')
print('- content (string): краткое содержимое интервью')
print('- full_content (string): полное содержимое интервью')