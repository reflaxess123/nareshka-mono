#!/usr/bin/env python3
"""
Улучшенная финальная очистка списка компаний
Более агрессивная очистка от мусора и дублей
"""

import re
from typing import List, Dict, Set
from collections import defaultdict

def aggressive_normalize(name: str) -> str:
    """Агрессивная нормализация названия компании"""
    if not name:
        return ""
    
    # Убираем нумерацию в начале
    name = re.sub(r'^\s*\d+\.\s*', '', name)
    
    # Убираем все префиксы и обрывки
    prefixes = [
        r'^[:\-\*\"\'\s]*',  # Начальные символы
        r'^Компания[:\s]*',
        r'^Название[:\s]*', 
        r'^компания[:\s]*',
        r'^название[:\s]*',
        r'^Компани[:\s]*',
        r'^[a-zA-Zа-яёA-ЯЁ]*\s*:\s*',  # Любые слова с двоеточием
    ]
    for prefix in prefixes:
        name = re.sub(prefix, '', name, flags=re.IGNORECASE)
    
    # Убираем все что в скобках/кавычках в конце
    name = re.sub(r'\s*\([^)]*\)\s*$', '', name)
    name = re.sub(r'\s*\[[^\]]*\]\s*$', '', name)
    name = re.sub(r'\s*"[^"]*"\s*$', '', name)
    name = re.sub(r'\s*\*\*[^*]*\*\*\s*$', '', name)
    
    # Убираем описания после тире/запятой
    name = re.sub(r'\s*[-–—,]\s*.*$', '', name)
    
    # Убираем HTML/Markdown символы
    name = re.sub(r'\*\*', '', name)
    name = name.replace('"', '').replace("'", '').replace('`', '')
    name = re.sub(r'[#\*]', '', name)
    
    # Убираем лишние пробелы и символы в начале/конце
    name = re.sub(r'^[:\-\s\*\"\']+', '', name)
    name = re.sub(r'[:\-\s\*\"\']+$', '', name)
    
    # Убираем лишние пробелы
    name = ' '.join(name.split())
    
    return name.strip()

def is_valid_company(name: str) -> bool:
    """Проверяет, является ли строка валидным названием компании"""
    if not name or len(name.strip()) < 2:
        return False
    
    name_clean = name.lower().strip()
    
    # Мусорные слова/фразы
    garbage_words = [
        'function', 'import', 'export', 'const', 'console', 'return',
        'typeof', 'async', 'await', 'promise', 'react', 'component',
        'тех собес', 'техсобес', 'лайвкодинг', 'скрининг', 'этап',
        'финал', 'интервью', 'задача', 'вопрос', 'решение', 'алгоритм',
        'что выведет', 'написать', 'реализовать', 'найти', 'создать'
    ]
    
    # Проверяем на мусорные слова
    for word in garbage_words:
        if word in name_clean:
            return False
    
    # Слишком короткие или состоящие только из символов
    if len(name) < 2 or not re.search(r'[а-яёa-zA-Z]', name):
        return False
    
    # Даты и числа
    if re.match(r'^\d+[\.\-/]\d+', name) or re.match(r'^\d+$', name):
        return False
    
    # Только символы без букв
    if re.match(r'^[^а-яёa-zA-Z]*$', name):
        return False
    
    # Слишком длинные описания
    if len(name) > 60:
        return False
    
    # Обрывки строк (начинаются с символов)
    if re.match(r'^[:\-\*\"\'\s]+', name):
        return False
    
    return True

def get_company_key(name: str) -> str:
    """Создает ключ для группировки похожих компаний"""
    # Упрощенное название для группировки
    key = re.sub(r'[^а-яёa-z0-9]', '', name.lower())
    
    # Особые правила для известных компаний
    if 'сбер' in key:
        if 'банк' in key or key == 'сбер' or key == 'сбербанк':
            return 'сбер'
        elif 'тех' in key:
            return 'сбертех'
        elif 'маркет' in key:
            return 'сбермаркет'
        # Иначе оставляем как есть для СберМобайл, СберАналитика и т.д.
    elif 'альфа' in key and ('банк' in key or key == 'альфа'):
        return 'альфабанк'
    elif key in ['тинькофф', 'тбанк', 'тбанк', 'т-банк']:
        return 'тинькофф'
    elif key == 'мтс':
        return 'мтс'
    elif key == 'втб':
        return 'втб'
    elif 'яндекс' in key:
        return 'яндекс'
    elif 'газпром' in key and 'банк' in key:
        return 'газпромбанк'
    
    return key

def choose_best_name(names: List[str]) -> str:
    """Выбирает лучшее название из группы дубликатов"""
    if not names:
        return ""
    
    # Фильтруем валидные названия
    valid_names = [n for n in names if is_valid_company(n)]
    if not valid_names:
        return ""
    
    # Приоритет: короткие, без символов, без описаний
    def name_score(name: str) -> tuple:
        length = len(name)
        has_symbols = bool(re.search(r'[^\w\sа-яёА-ЯЁ]', name))
        has_brackets = '(' in name or '[' in name
        has_quotes = '"' in name or "'" in name
        is_upper = name.isupper()
        has_description = any(word in name.lower() for word in ['проект', 'аутстафф', 'этап'])
        
        return (has_description, has_brackets, has_quotes, has_symbols, is_upper, length)
    
    # Сортируем и выбираем лучший
    sorted_names = sorted(valid_names, key=name_score)
    return sorted_names[0]

def ultra_clean_companies():
    """Ультра-очистка списка компаний"""
    
    print("🚀 УЛЬТРА-ОЧИСТКА СПИСКА КОМПАНИЙ")
    print("=" * 60)
    
    # Читаем исходный список
    try:
        with open('clean_companies_list.txt', 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ Файл clean_companies_list.txt не найден")
        return
    
    # Извлекаем компании из секции
    lines = content.split('\n')
    companies = []
    in_section = False
    
    for line in lines:
        line = line.strip()
        if 'ЧИСТЫЙ СПИСОК КОМПАНИЙ:' in line:
            in_section = True
            continue
        elif 'УДАЛЕННЫЙ МУСОР:' in line:
            break
        elif in_section and line and not line.startswith('-'):
            # Убираем нумерацию
            clean_line = re.sub(r'^\s*\d+\.\s*', '', line)
            if clean_line:
                companies.append(clean_line)
    
    print(f"📋 Исходных записей: {len(companies)}")
    
    # Нормализуем и группируем
    groups = defaultdict(list)
    garbage_count = 0
    
    for company in companies:
        normalized = aggressive_normalize(company)
        
        if not is_valid_company(normalized):
            garbage_count += 1
            continue
        
        key = get_company_key(normalized)
        groups[key].append(normalized)
    
    # Создаем финальный список
    final_companies = []
    duplicates_removed = 0
    
    print(f"\n🔍 НАЙДЕННЫЕ ДУБЛИКАТЫ:")
    for key, group in groups.items():
        if len(group) > 1:
            print(f"  {key}: {group}")
            duplicates_removed += len(group) - 1
        
        best_name = choose_best_name(group)
        if best_name:
            final_companies.append(best_name)
    
    # Сортируем по алфавиту
    final_companies.sort(key=lambda x: x.lower())
    
    print(f"\n✅ РЕЗУЛЬТАТ:")
    print(f"   Финальных компаний: {len(final_companies)}")
    print(f"   Удалено дубликатов: {duplicates_removed}")
    print(f"   Удалено мусора: {garbage_count}")
    
    # Сохраняем результат
    output_file = 'ultra_clean_companies.txt'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("УЛЬТРА-ЧИСТЫЙ СПИСОК КОМПАНИЙ\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Всего компаний: {len(final_companies)}\n")
        f.write(f"Удалено дубликатов: {duplicates_removed}\n") 
        f.write(f"Удалено мусора: {garbage_count}\n\n")
        
        f.write("ТОП-30 САМЫХ ПОПУЛЯРНЫХ:\n")
        f.write("-" * 30 + "\n")
        
        # Подсчитываем упоминания
        mentions = defaultdict(int)
        for group in groups.values():
            mentions[choose_best_name(group)] = len(group)
        
        # Сортируем по популярности
        popular = sorted(final_companies, key=lambda x: mentions.get(x, 1), reverse=True)
        
        for i, company in enumerate(popular[:30], 1):
            count = mentions.get(company, 1)
            f.write(f"{i:2d}. {company} ({count} упоминаний)\n")
        
        f.write(f"\n\nПОЛНЫЙ СПИСОК ({len(final_companies)} компаний):\n")
        f.write("-" * 30 + "\n")
        
        for i, company in enumerate(final_companies, 1):
            f.write(f"{i:3d}. {company}\n")
    
    print(f"💾 Сохранено в: {output_file}")
    
    # Показываем ТОП-20
    print(f"\n🏆 ТОП-20 САМЫХ ЧИСТЫХ КОМПАНИЙ:")
    for i, company in enumerate(final_companies[:20], 1):
        print(f"{i:2d}. {company}")

if __name__ == "__main__":
    ultra_clean_companies() 