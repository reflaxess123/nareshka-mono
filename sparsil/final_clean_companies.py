#!/usr/bin/env python3
"""
Финальная очистка списка компаний
Удаляет дубликаты, остатки мусора и нормализует названия
"""

import re
from typing import List, Dict, Set
from collections import defaultdict

def normalize_company_name(name: str) -> str:
    """Нормализация названия компании для поиска дубликатов"""
    if not name:
        return ""
    
    # Убираем нумерацию в начале
    name = re.sub(r'^\s*\d+\.\s*', '', name)
    
    # Убираем префиксы
    prefixes = [
        r'^Компания:?\s*',
        r'^Название:?\s*', 
        r'^компания:?\s*',
        r'^название:?\s*',
        r'^Компани:?\s*'
    ]
    for prefix in prefixes:
        name = re.sub(prefix, '', name, flags=re.IGNORECASE)
    
    # Убираем описания в скобках и после тире
    name = re.sub(r'\s*\([^)]*\)\s*$', '', name)
    name = re.sub(r'\s*\[[^\]]*\]\s*$', '', name)
    name = re.sub(r'\s*[-–—]\s*.*$', '', name)
    name = re.sub(r'\s*,\s*.*$', '', name)
    
    # Убираем лишние пробелы
    name = ' '.join(name.split())
    
    return name.strip()

def get_canonical_name(names: List[str]) -> str:
    """Выбирает лучший вариант названия из группы дубликатов"""
    if not names:
        return ""
    
    # Удаляем пустые
    names = [n for n in names if n.strip()]
    if not names:
        return ""
    
    # Приоритет: короткие названия без лишних символов
    def score_name(name: str) -> tuple:
        # Чем меньше скор, тем лучше
        length = len(name)
        has_quotes = '"' in name or "'" in name
        has_brackets = '(' in name or '[' in name
        has_dash = '–' in name or '—' in name or ' - ' in name
        has_comma = ',' in name
        has_hash = '#' in name
        is_caps = name.isupper()
        
        return (has_quotes, has_brackets, has_dash, has_comma, has_hash, is_caps, length)
    
    # Сортируем по качеству
    sorted_names = sorted(names, key=score_name)
    return sorted_names[0]

def is_still_garbage(name: str) -> bool:
    """Проверяет, является ли название мусором после нормализации"""
    if not name or len(name.strip()) < 2:
        return True
    
    name_lower = name.lower().strip()
    
    # Остатки кода
    code_fragments = [
        'function', 'import', 'export', 'const', 'console.log',
        'then(', '=>', '```', 'useeffect', 'usestate', 'return',
        'typeof', 'async', 'await', 'promise', '.map', '.filter',
        'react', 'component', 'props', 'state'
    ]
    
    # Технические фразы
    tech_phrases = [
        'тех собес', 'техсобес', 'лайвкодинг', 'скрининг',
        'этап', 'финал', 'интервью', 'собеседование',
        'задача', 'вопрос', 'решение', 'алгоритм'
    ]
    
    # Описательные фразы
    descriptive = [
        'аутстафф', 'аутсорс', 'проект', 'команда', 'стрим',
        'платформа', 'отдел', 'департамент', 'группа'
    ]
    
    # Даты и числа
    if re.match(r'^\d+[\.\-/]\d+', name) or re.match(r'^\d+$', name):
        return True
    
    # Проверяем на мусор
    for fragment in code_fragments + tech_phrases:
        if fragment in name_lower:
            return True
    
    # Если состоит только из описательных слов
    words = name_lower.split()
    if len(words) <= 2 and all(word in descriptive for word in words):
        return True
    
    # Слишком длинные фразы (скорее всего описания)
    if len(name) > 80:
        return True
    
    # Содержит только символы без букв
    if not re.search(r'[а-яёa-z]', name_lower):
        return True
    
    return False

def group_similar_companies(companies: List[str]) -> Dict[str, List[str]]:
    """Группирует похожие названия компаний"""
    groups = defaultdict(list)
    
    for company in companies:
        normalized = normalize_company_name(company)
        if not normalized or is_still_garbage(normalized):
            continue
            
        # Ключ для группировки - упрощенное название
        key = re.sub(r'[^а-яёa-z0-9]', '', normalized.lower())
        
        # Особые случаи для популярных банков/компаний
        if 'сбер' in key:
            if 'банк' in key or key == 'сбер':
                key = 'сбер'
            else:
                pass  # Оставляем как есть для СберТех, СберМаркет и т.д.
        elif 'альфа' in key and 'банк' in key:
            key = 'альфабанк'
        elif key in ['тинькофф', 'тбанк']:
            key = 'тинькофф'
        elif key in ['мтс']:
            key = 'мтс'
        elif key in ['втб']:
            key = 'втб'
        elif 'яндекс' in key:
            key = 'яндекс'
        
        groups[key].append(company)
    
    return groups

def final_clean_companies():
    """Финальная очистка списка компаний"""
    
    print("🧹 ФИНАЛЬНАЯ ОЧИСТКА СПИСКА КОМПАНИЙ")
    print("=" * 60)
    
    # Читаем текущий список
    try:
        with open('clean_companies_list.txt', 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ Файл clean_companies_list.txt не найден")
        return
    
    # Извлекаем список компаний из секции "ЧИСТЫЙ СПИСОК КОМПАНИЙ"
    lines = content.split('\n')
    companies = []
    in_companies_section = False
    
    for line in lines:
        line = line.strip()
        if 'ЧИСТЫЙ СПИСОК КОМПАНИЙ:' in line:
            in_companies_section = True
            continue
        elif 'УДАЛЕННЫЙ МУСОР:' in line:
            break
        elif in_companies_section and line:
            # Убираем нумерацию
            clean_line = re.sub(r'^\s*\d+\.\s*', '', line)
            if clean_line:
                companies.append(clean_line)
    
    print(f"📋 Исходно компаний: {len(companies)}")
    
    # Группируем похожие компании
    groups = group_similar_companies(companies)
    
    # Создаем финальный список
    final_companies = []
    duplicates_removed = 0
    garbage_removed = 0
    
    for key, group in groups.items():
        if len(group) > 1:
            duplicates_removed += len(group) - 1
            print(f"🔄 Дубликаты '{key}': {group}")
        
        canonical = get_canonical_name(group)
        
        # Финальная проверка на мусор
        normalized = normalize_company_name(canonical)
        if not is_still_garbage(normalized) and normalized:
            final_companies.append(normalized)
        else:
            garbage_removed += 1
    
    # Сортируем по алфавиту
    final_companies.sort(key=lambda x: x.lower())
    
    print(f"✅ Финальных компаний: {len(final_companies)}")
    print(f"🗑️ Удалено дубликатов: {duplicates_removed}")
    print(f"🗑️ Удалено мусора: {garbage_removed}")
    
    # Сохраняем результат
    output_file = 'final_companies_list.txt'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("ФИНАЛЬНЫЙ СПИСОК КОМПАНИЙ\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Всего компаний: {len(final_companies)}\n")
        f.write(f"Удалено дубликатов: {duplicates_removed}\n") 
        f.write(f"Удалено мусора: {garbage_removed}\n\n")
        f.write("СПИСОК КОМПАНИЙ:\n")
        f.write("-" * 30 + "\n")
        
        for i, company in enumerate(final_companies, 1):
            f.write(f"{i:3d}. {company}\n")
    
    print(f"💾 Сохранено в: {output_file}")
    
    # Показываем ТОП-20
    print(f"\n📊 ПЕРВЫЕ 20 КОМПАНИЙ:")
    for i, company in enumerate(final_companies[:20], 1):
        print(f"{i:3d}. {company}")

if __name__ == "__main__":
    final_clean_companies() 