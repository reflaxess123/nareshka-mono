#!/usr/bin/env python3
"""
Создание списка уникальных брендов компаний
Убирает все дубликаты одной компании с разными описаниями
"""

import re
from typing import List, Dict, Set
from collections import defaultdict

def extract_brand_name(company: str) -> str:
    """Извлекает базовое название бренда компании"""
    if not company:
        return ""
    
    # Убираем нумерацию
    name = re.sub(r'^\s*\d+\.\s*', '', company)
    
    # Убираем все в скобках и после них
    name = re.sub(r'\s*\([^)]*\).*$', '', name)
    name = re.sub(r'\s*\[[^\]]*\].*$', '', name)
    
    # Убираем описания после тире, запятой
    name = re.sub(r'\s*[-–—,].*$', '', name)
    
    # Убираем проекты и описания
    name = re.sub(r'\s+(проект|аутстафф|команда|отдел|стрим|платформа).*$', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s+(на проект|в команду|через|от).*$', '', name, flags=re.IGNORECASE)
    
    # Убираем номера этапов и техническую информацию
    name = re.sub(r'\s+\d+\s*(этап|й этап|ой этап|секция|часть).*$', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s+(тех|техничка|собес|скрининг|интервью|финал).*$', '', name, flags=re.IGNORECASE)
    
    # Убираем даты
    name = re.sub(r'\s+\d{2}\.\d{2}.*$', '', name)
    name = re.sub(r'\s+от \d{2}\.\d{2}.*$', '', name)
    
    # Убираем markdown и символы
    name = re.sub(r'\*\*', '', name)
    name = name.replace('"', '').replace("'", '').replace('`', '')
    name = re.sub(r'^[:\-\*\s]+', '', name)
    name = re.sub(r'[:\-\*\s]+$', '', name)
    
    # Убираем лишние пробелы
    name = ' '.join(name.split())
    
    return name.strip()

def normalize_for_comparison(name: str) -> str:
    """Нормализует название для сравнения и группировки"""
    if not name:
        return ""
    
    # Приводим к нижнему регистру
    normalized = name.lower()
    
    # Убираем все символы кроме букв и цифр
    normalized = re.sub(r'[^а-яёa-z0-9]', '', normalized)
    
    # Специальные правила для известных компаний
    if normalized in ['сбер', 'сбербанк']:
        return 'сбер'
    elif normalized in ['альфабанк', 'альфа']:
        return 'альфабанк'
    elif normalized in ['тинькофф', 'тбанк', 'т-банк']:
        return 'тинькофф'
    elif normalized in ['яндекс']:
        return 'яндекс'
    elif normalized in ['газпромбанк']:
        return 'газпромбанк'
    elif normalized in ['мтс']:
        return 'мтс'
    elif normalized in ['втб']:
        return 'втб'
    
    return normalized

def is_valid_brand(name: str) -> bool:
    """Проверяет, является ли название валидным брендом"""
    if not name or len(name) < 2:
        return False
    
    name_lower = name.lower()
    
    # Исключаем мусорные названия
    garbage_patterns = [
        r'^[:\-\*\s\d]+$',  # Только символы и цифры
        r'тех\s*собес', r'лайвкодинг', r'скрининг', r'этап', r'финал',
        r'задача', r'вопрос', r'решение', r'написать', r'реализовать',
        r'function', r'import', r'export', r'const', r'console',
        r'аутстафф$', r'аутсорс$', r'проект$', r'команда$',
        r'что выведет', r'найти все', r'создать', r'добавить'
    ]
    
    for pattern in garbage_patterns:
        if re.search(pattern, name_lower):
            return False
    
    # Проверяем на наличие букв
    if not re.search(r'[а-яёa-zA-Z]', name):
        return False
    
    # Слишком длинные описания
    if len(name) > 50:
        return False
    
    return True

def choose_best_brand_name(names: List[str]) -> str:
    """Выбирает лучшее название бренда из группы"""
    if not names:
        return ""
    
    # Фильтруем валидные
    valid_names = [n for n in names if is_valid_brand(n)]
    if not valid_names:
        return ""
    
    # Критерии качества названия (чем меньше, тем лучше)
    def name_quality_score(name: str) -> tuple:
        length = len(name)
        has_symbols = bool(re.search(r'[^\w\sа-яёА-ЯЁ]', name))
        has_numbers = bool(re.search(r'\d', name))
        is_all_caps = name.isupper()
        has_spaces_issues = '  ' in name or name.startswith(' ') or name.endswith(' ')
        has_description_words = any(word in name.lower() for word in [
            'проект', 'аутстафф', 'команда', 'отдел', 'этап', 'тех', 'собес'
        ])
        
        return (has_description_words, has_symbols, has_numbers, is_all_caps, has_spaces_issues, length)
    
    # Сортируем по качеству и берем лучший
    sorted_names = sorted(valid_names, key=name_quality_score)
    return sorted_names[0]

def create_unique_brands():
    """Создает список уникальных брендов компаний"""
    
    print("🏢 СОЗДАНИЕ СПИСКА УНИКАЛЬНЫХ БРЕНДОВ КОМПАНИЙ")
    print("=" * 60)
    
    # Читаем ультра-чистый список
    try:
        with open('ultra_clean_companies.txt', 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ Файл ultra_clean_companies.txt не найден")
        return
    
    # Извлекаем компании из полного списка
    lines = content.split('\n')
    companies = []
    in_full_list = False
    
    for line in lines:
        line = line.strip()
        if 'ПОЛНЫЙ СПИСОК' in line:
            in_full_list = True
            continue
        elif in_full_list and line and not line.startswith('-'):
            # Убираем нумерацию
            clean_line = re.sub(r'^\s*\d+\.\s*', '', line)
            if clean_line:
                companies.append(clean_line)
    
    print(f"📋 Исходных записей: {len(companies)}")
    
    # Группируем по базовому бренду
    brand_groups = defaultdict(list)
    processed = 0
    
    for company in companies:
        brand = extract_brand_name(company)
        if not brand or not is_valid_brand(brand):
            continue
        
        normalized_key = normalize_for_comparison(brand)
        if normalized_key:
            brand_groups[normalized_key].append(brand)
            processed += 1
    
    print(f"📋 Обработано: {processed}")
    print(f"📋 Уникальных брендов: {len(brand_groups)}")
    
    # Создаем финальный список уникальных брендов
    unique_brands = []
    duplicates_merged = 0
    
    print(f"\n🔄 ОБЪЕДИНЕННЫЕ ДУБЛИКАТЫ:")
    for normalized_key, brand_variants in brand_groups.items():
        if len(brand_variants) > 1:
            # Убираем дубликаты в вариантах
            unique_variants = list(set(brand_variants))
            if len(unique_variants) > 1:
                print(f"  {normalized_key}: {unique_variants}")
                duplicates_merged += len(unique_variants) - 1
        
        best_brand = choose_best_brand_name(brand_variants)
        if best_brand:
            unique_brands.append(best_brand)
    
    # Сортируем по алфавиту
    unique_brands.sort(key=lambda x: x.lower())
    
    print(f"\n✅ РЕЗУЛЬТАТ:")
    print(f"   Уникальных брендов: {len(unique_brands)}")
    print(f"   Объединено дубликатов: {duplicates_merged}")
    
    # Подсчитываем упоминания для рейтинга
    brand_mentions = defaultdict(int)
    for normalized_key, variants in brand_groups.items():
        best_brand = choose_best_brand_name(variants)
        if best_brand:
            brand_mentions[best_brand] = len(variants)
    
    # Сохраняем результат
    output_file = 'unique_brands_list.txt'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("УНИКАЛЬНЫЕ БРЕНДЫ КОМПАНИЙ\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Всего уникальных брендов: {len(unique_brands)}\n")
        f.write(f"Объединено дубликатов: {duplicates_merged}\n\n")
        
        # ТОП по популярности
        popular_brands = sorted(unique_brands, key=lambda x: brand_mentions.get(x, 1), reverse=True)
        
        f.write("ТОП-30 САМЫХ ПОПУЛЯРНЫХ БРЕНДОВ:\n")
        f.write("-" * 40 + "\n")
        for i, brand in enumerate(popular_brands[:30], 1):
            mentions = brand_mentions.get(brand, 1)
            f.write(f"{i:2d}. {brand} ({mentions} упоминаний)\n")
        
        f.write(f"\n\nПОЛНЫЙ СПИСОК УНИКАЛЬНЫХ БРЕНДОВ ({len(unique_brands)}):\n")
        f.write("-" * 40 + "\n")
        
        for i, brand in enumerate(unique_brands, 1):
            f.write(f"{i:3d}. {brand}\n")
    
    print(f"💾 Сохранено в: {output_file}")
    
    # Показываем ТОП-20
    print(f"\n🏆 ТОП-20 САМЫХ ПОПУЛЯРНЫХ БРЕНДОВ:")
    popular_top20 = sorted(unique_brands, key=lambda x: brand_mentions.get(x, 1), reverse=True)[:20]
    for i, brand in enumerate(popular_top20, 1):
        mentions = brand_mentions.get(brand, 1)
        print(f"{i:2d}. {brand} ({mentions} упоминаний)")

if __name__ == "__main__":
    create_unique_brands() 