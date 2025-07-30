#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import re

def analyze_truncated_content(file_path):
    """
    Анализирует файл MASSIV_GROUPED.json на предмет обрезанного контента
    """
    print("Загружаем и анализируем файл...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Счетчики
    total_records = 0
    content_ending_dots = 0
    full_content_ending_dots = 0
    content_dots_examples = []
    full_content_dots_examples = []
    
    # Для анализа длин
    content_lengths = []
    full_content_lengths = []
    length_differences = []
    
    # Другие признаки обрезки
    other_truncation_signs = {
        'content': 0,      # контент обрезан по другим признакам
        'full_content': 0  # full_content обрезан по другим признакам
    }
    
    # Примеры других признаков обрезки
    other_examples = []
    
    print("Анализируем записи...")
    
    for company_data in data:
        if 'records' in company_data:
            for record in company_data['records']:
                total_records += 1
                
                content = record.get('content', '')
                full_content = record.get('full_content', '')
                
                # Проверяем окончания на "..."
                if content.rstrip().endswith('...'):
                    content_ending_dots += 1
                    if len(content_dots_examples) < 5:  # Собираем первые 5 примеров
                        content_dots_examples.append({
                            'company': company_data.get('company', 'Unknown'),
                            'timestamp': record.get('timestamp', 'Unknown'),
                            'content_end': content[-100:] if len(content) > 100 else content,
                            'content_length': len(content),
                            'full_content_length': len(full_content)
                        })
                
                if full_content.rstrip().endswith('...'):
                    full_content_ending_dots += 1
                    if len(full_content_dots_examples) < 5:  # Собираем первые 5 примеров
                        full_content_dots_examples.append({
                            'company': company_data.get('company', 'Unknown'),
                            'timestamp': record.get('timestamp', 'Unknown'),
                            'full_content_end': full_content[-100:] if len(full_content) > 100 else full_content,
                            'content_length': len(content),
                            'full_content_length': len(full_content)
                        })
                
                # Проверяем другие признаки обрезки
                # Обрезка по словам в середине
                content_stripped = content.rstrip()
                full_content_stripped = full_content.rstrip()
                
                # Признаки обрезки: обрывается на половине слова, незакрытые скобки и т.д.
                def has_other_truncation_signs(text):
                    signs = []
                    
                    # Заканчивается не полным словом (если не заканчивается точкой, вопросом, восклицанием)
                    if text and not re.search(r'[.!?;:)\]}"\s]$', text):
                        if not text.endswith('...'):
                            signs.append('incomplete_word')
                    
                    # Незакрытые кавычки
                    quotes = text.count('"') + text.count("'")
                    if quotes % 2 != 0:
                        signs.append('unclosed_quotes')
                    
                    # Незакрытые скобки
                    open_parens = text.count('(') + text.count('[') + text.count('{')
                    close_parens = text.count(')') + text.count(']') + text.count('}')
                    if open_parens != close_parens:
                        signs.append('unmatched_brackets')
                    
                    # Обрывается на коде (если заканчивается на { или ; без закрытия)
                    if re.search(r'[{;,]$', text.rstrip()):
                        signs.append('incomplete_code')
                    
                    return signs
                
                content_signs = has_other_truncation_signs(content_stripped)
                full_content_signs = has_other_truncation_signs(full_content_stripped)
                
                if content_signs:
                    other_truncation_signs['content'] += 1
                    if len(other_examples) < 10:
                        other_examples.append({
                            'field': 'content',
                            'company': company_data.get('company', 'Unknown'),
                            'timestamp': record.get('timestamp', 'Unknown'),
                            'signs': content_signs,
                            'text_end': content[-100:] if len(content) > 100 else content,
                            'content_length': len(content),
                            'full_content_length': len(full_content)
                        })
                
                if full_content_signs:
                    other_truncation_signs['full_content'] += 1
                    if len(other_examples) < 10:
                        other_examples.append({
                            'field': 'full_content',
                            'company': company_data.get('company', 'Unknown'),
                            'timestamp': record.get('timestamp', 'Unknown'),
                            'signs': full_content_signs,
                            'text_end': full_content[-100:] if len(full_content) > 100 else full_content,
                            'content_length': len(content),
                            'full_content_length': len(full_content)
                        })
                
                # Собираем статистику по длинам
                content_lengths.append(len(content))
                full_content_lengths.append(len(full_content))
                length_differences.append(len(full_content) - len(content))
    
    # Выводим результаты
    print("\n" + "="*60)
    print("ТОЧНАЯ СТАТИСТИКА ПО ОБРЕЗАННОМУ КОНТЕНТУ")
    print("="*60)
    
    print(f"\nОбщее количество записей: {total_records}")
    
    print(f"\n1. ЗАПИСИ, ЗАКАНЧИВАЮЩИЕСЯ НА '...':")
    print(f"   content заканчивается на '...': {content_ending_dots} записей ({content_ending_dots/total_records*100:.2f}%)")
    print(f"   full_content заканчивается на '...': {full_content_ending_dots} записей ({full_content_ending_dots/total_records*100:.2f}%)")
    
    print(f"\n2. ПРИМЕРЫ ЗАПИСЕЙ С '...' В CONTENT:")
    for i, example in enumerate(content_dots_examples[:3], 1):
        print(f"   Пример {i}:")
        print(f"   Компания: {example['company']}")
        print(f"   Timestamp: {example['timestamp']}")
        print(f"   Длина content: {example['content_length']}")
        print(f"   Длина full_content: {example['full_content_length']}")
        print(f"   Окончание content: ...{example['content_end'][-50:]}")
        print()
    
    print(f"\n3. ПРИМЕРЫ ЗАПИСЕЙ С '...' В FULL_CONTENT:")
    for i, example in enumerate(full_content_dots_examples[:3], 1):
        print(f"   Пример {i}:")
        print(f"   Компания: {example['company']}")
        print(f"   Timestamp: {example['timestamp']}")
        print(f"   Длина content: {example['content_length']}")
        print(f"   Длина full_content: {example['full_content_length']}")
        print(f"   Окончание full_content: ...{example['full_content_end'][-50:]}")
        print()
    
    print(f"\n4. АНАЛИЗ ДЛИН КОНТЕНТА:")
    avg_content_length = sum(content_lengths) / len(content_lengths)
    avg_full_content_length = sum(full_content_lengths) / len(full_content_lengths)
    avg_difference = sum(length_differences) / len(length_differences)
    
    print(f"   Средняя длина content: {avg_content_length:.0f} символов")
    print(f"   Средняя длина full_content: {avg_full_content_length:.0f} символов")
    print(f"   Средняя разница (full - content): {avg_difference:.0f} символов")
    
    # Считаем сколько записей где full_content длиннее content
    longer_full_content = sum(1 for diff in length_differences if diff > 0)
    print(f"   Записей где full_content длиннее content: {longer_full_content} ({longer_full_content/total_records*100:.2f}%)")
    
    print(f"\n5. ДРУГИЕ ПРИЗНАКИ ОБРЕЗАННОГО КОНТЕНТА:")
    print(f"   content с признаками обрезки: {other_truncation_signs['content']} записей ({other_truncation_signs['content']/total_records*100:.2f}%)")
    print(f"   full_content с признаками обрезки: {other_truncation_signs['full_content']} записей ({other_truncation_signs['full_content']/total_records*100:.2f}%)")
    
    print(f"\n6. ПРИМЕРЫ ДРУГИХ ПРИЗНАКОВ ОБРЕЗКИ:")
    for i, example in enumerate(other_examples[:5], 1):
        print(f"   Пример {i} ({example['field']}):")
        print(f"   Компания: {example['company']}")
        print(f"   Признаки: {', '.join(example['signs'])}")
        print(f"   Длины: content={example['content_length']}, full_content={example['full_content_length']}")
        print(f"   Окончание: ...{example['text_end'][-50:]}")
        print()
    
    # Дополнительная статистика
    print(f"\n7. ДОПОЛНИТЕЛЬНАЯ СТАТИСТИКА:")
    
    # Максимальные длины
    max_content = max(content_lengths)
    max_full_content = max(full_content_lengths)
    max_diff = max(length_differences)
    
    print(f"   Максимальная длина content: {max_content} символов")
    print(f"   Максимальная длина full_content: {max_full_content} символов")
    print(f"   Максимальная разница: {max_diff} символов")
    
    # Квартили для разниц в длинах
    length_differences.sort()
    q1 = length_differences[len(length_differences)//4]
    median = length_differences[len(length_differences)//2]
    q3 = length_differences[3*len(length_differences)//4]
    
    print(f"   Разница в длинах (квартили): Q1={q1}, медиана={median}, Q3={q3}")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    file_path = r"C:\Users\refla\nareshka-mono\sobes-data\MASSIV_GROUPED.json"
    analyze_truncated_content(file_path)