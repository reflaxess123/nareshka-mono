#!/usr/bin/env python3
"""
ФИНАЛЬНАЯ версия создания уникальных брендов
Максимально простая и агрессивная логика
"""

import re
from typing import List, Dict
from collections import defaultdict

def extract_base_brand(company_name: str) -> str:
    """Извлекает базовое название бренда максимально агрессивно"""
    if not company_name:
        return ""
    
    # Убираем нумерацию в начале
    name = re.sub(r'^\s*\d+\.\s*', '', company_name)
    
    # МАКСИМАЛЬНО АГРЕССИВНО убираем всё что может быть описанием
    # Убираем всё начиная с первой скобки
    name = re.sub(r'\s*[\(\[].*$', '', name)
    
    # Убираем всё после тире, запятой, двоеточия
    name = re.sub(r'\s*[-–—,:;].*$', '', name)
    
    # Убираем всё после стоп-слов (в любом регистре)
    stop_words = [
        'на', 'в', 'для', 'от', 'через', 'к', 'с', 'по', 'из', 'о', 'про',
        'аутстафф', 'аутсорс', 'проект', 'команда', 'отдел', 'стрим', 
        'платформа', 'собес', 'тех', 'техничка', 'скрининг', 'интервью',
        'этап', 'финал', 'встреча', 'знакомство', 'разговор', 'созвон',
        'hr', 'эйчарка', 'написала', 'сама', 'лид', 'лидом', 'команды',
        'внутренний', 'внутри', 'внешний', 'дочка', 'ранее', 'было'
    ]
    
    # Создаем паттерн для поиска стоп-слов как отдельных слов
    stop_pattern = r'\s+(?:' + '|'.join(re.escape(word) for word in stop_words) + r')\b.*$'
    name = re.sub(stop_pattern, '', name, flags=re.IGNORECASE)
    
    # Убираем специальные символы в начале и конце
    name = re.sub(r'^[*"\'\s\-:]+', '', name)
    name = re.sub(r'[*"\'\s\-:\.]+$', '', name)
    
    # Убираем лишние пробелы
    name = ' '.join(name.split())
    
    return name.strip()

def normalize_brand_for_grouping(brand: str) -> str:
    """Нормализует бренд для группировки"""
    if not brand:
        return ""
    
    # Убираем все кроме букв и цифр, приводим к нижнему регистру
    normalized = re.sub(r'[^а-яёa-z0-9]', '', brand.lower())
    
    # Особые случаи для крупных брендов
    brand_mapping = {
        'сбер': 'сбер',
        'сбербанк': 'сбер',
        'сберт': 'сбер',
        'сберкорус': 'сбер',
        'альфа': 'альфабанк',
        'альфабанк': 'альфабанк',
        'тинькофф': 'тинькофф',
        'тбанк': 'тинькофф',
        'яндекс': 'яндекс',
        'yandex': 'яндекс',
        'мтс': 'мтс',
        'втб': 'втб',
        'газпромбанк': 'газпромбанк',
        'газпром': 'газпромбанк',
        'гпб': 'газпромбанк',
        'ozon': 'ozon',
        'озон': 'ozon',
        'wildberries': 'wildberries',
        'wb': 'wildberries',
        'авито': 'авито',
        'avito': 'авито'
    }
    
    return brand_mapping.get(normalized, normalized)

def is_valid_brand_name(name: str) -> bool:
    """Проверяет что название валидно как бренд компании"""
    if not name or len(name) < 2:
        return False
    
    # Должны быть буквы
    if not re.search(r'[а-яёa-zA-Z]', name):
        return False
    
    # Исключаем очевидный мусор
    garbage_words = [
        'тех', 'собес', 'этап', 'финал', 'hr', 'эйчарка', 'скрининг',
        'интервью', 'встреча', 'знакомство', 'разговор', 'созвон',
        'аутстафф', 'аутсорс', 'проект', 'команда', 'отдел', 'стрим',
        'function', 'import', 'export', 'const', 'console', 'return'
    ]
    
    name_lower = name.lower()
    if name_lower in garbage_words:
        return False
    
    # Не слишком длинные
    if len(name) > 30:
        return False
    
    return True

def select_best_brand_name(brand_variants: List[str]) -> str:
    """Выбирает лучший вариант названия бренда"""
    if not brand_variants:
        return ""
    
    # Фильтруем валидные
    valid_variants = [v for v in brand_variants if is_valid_brand_name(v)]
    if not valid_variants:
        return ""
    
    # Убираем точные дубликаты
    unique_variants = list(set(valid_variants))
    
    # Качественные критерии (чем меньше, тем лучше)
    def quality_score(name: str) -> tuple:
        # Приоритет: известные бренды
        known_brands = ['Сбер', 'Яндекс', 'МТС', 'ВТБ', 'Тинькофф', 'Газпромбанк', 'Авито', 'Ozon', 'IBS']
        is_known = name in known_brands
        
        # Качество названия
        length = len(name)
        has_symbols = bool(re.search(r'[^а-яёА-ЯЁa-zA-Z0-9\s\.]', name))
        has_numbers = bool(re.search(r'\d', name))
        is_all_caps = name.isupper()
        has_dots = '.' in name and not name.endswith('.ru')
        
        return (not is_known, has_symbols, has_dots, has_numbers, is_all_caps, length)
    
    # Сортируем по качеству
    sorted_variants = sorted(unique_variants, key=quality_score)
    return sorted_variants[0]

def create_final_unique_brands():
    """Создает финальный список уникальных брендов"""
    
    print("🎯 ФИНАЛЬНОЕ СОЗДАНИЕ УНИКАЛЬНЫХ БРЕНДОВ")
    print("=" * 60)
    
    # Читаем исходный список
    try:
        with open('ultra_clean_companies.txt', 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ Файл ultra_clean_companies.txt не найден")
        return
    
    # Извлекаем все компании
    lines = content.split('\n')
    companies = []
    in_full_list = False
    
    for line in lines:
        line = line.strip()
        if 'ПОЛНЫЙ СПИСОК' in line:
            in_full_list = True
            continue
        elif in_full_list and line and not line.startswith('-'):
            clean_line = re.sub(r'^\s*\d+\.\s*', '', line)
            if clean_line:
                companies.append(clean_line)
    
    print(f"📋 Исходных записей: {len(companies)}")
    
    # Извлекаем базовые бренды и группируем
    brand_groups = defaultdict(list)
    
    for company in companies:
        base_brand = extract_base_brand(company)
        if not base_brand or not is_valid_brand_name(base_brand):
            continue
        
        group_key = normalize_brand_for_grouping(base_brand)
        if group_key:
            brand_groups[group_key].append(base_brand)
    
    print(f"📋 Уникальных групп: {len(brand_groups)}")
    
    # Показываем крупные объединения
    print(f"\n🔥 КРУПНЫЕ ОБЪЕДИНЕНИЯ (3+ дубликата):")
    large_merges = [(k, v) for k, v in brand_groups.items() if len(v) >= 3]
    large_merges.sort(key=lambda x: len(x[1]), reverse=True)
    
    for group_key, variants in large_merges[:15]:
        unique_variants = list(set(variants))
        if len(unique_variants) > 1:
            print(f"  {group_key}: {unique_variants} ({len(variants)} упоминаний)")
    
    # Создаем финальный список
    final_brands = []
    total_merged = 0
    
    for group_key, variants in brand_groups.items():
        if len(variants) > 1:
            total_merged += len(variants) - 1
        
        best_brand = select_best_brand_name(variants)
        if best_brand:
            final_brands.append(best_brand)
    
    # Сортируем
    final_brands.sort(key=lambda x: x.lower())
    
    print(f"\n✅ ИТОГОВЫЙ РЕЗУЛЬТАТ:")
    print(f"   Финальных уникальных брендов: {len(final_brands)}")
    print(f"   Объединено дубликатов: {total_merged}")
    print(f"   Эффективность: {(1 - len(final_brands)/len(companies))*100:.1f}%")
    
    # Подсчитываем популярность
    brand_popularity = {}
    for group_key, variants in brand_groups.items():
        best_brand = select_best_brand_name(variants)
        if best_brand:
            brand_popularity[best_brand] = len(variants)
    
    # Сохраняем результат
    output_file = 'final_unique_brands.txt'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("ФИНАЛЬНЫЕ УНИКАЛЬНЫЕ БРЕНДЫ КОМПАНИЙ\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Всего уникальных брендов: {len(final_brands)}\n")
        f.write(f"Объединено дубликатов: {total_merged}\n")
        f.write(f"Эффективность сжатия: {(1 - len(final_brands)/len(companies))*100:.1f}%\n\n")
        
        # ТОП популярных
        popular_brands = sorted(final_brands, key=lambda x: brand_popularity.get(x, 1), reverse=True)
        
        f.write("ТОП-30 САМЫХ ПОПУЛЯРНЫХ БРЕНДОВ:\n")
        f.write("-" * 40 + "\n")
        for i, brand in enumerate(popular_brands[:30], 1):
            count = brand_popularity.get(brand, 1)
            f.write(f"{i:2d}. {brand} ({count} упоминаний)\n")
        
        f.write(f"\n\nВСЕ УНИКАЛЬНЫЕ БРЕНДЫ ({len(final_brands)}):\n")
        f.write("-" * 40 + "\n")
        
        for i, brand in enumerate(final_brands, 1):
            f.write(f"{i:3d}. {brand}\n")
    
    print(f"💾 Сохранено в: {output_file}")
    
    # ТОП-20 для вывода
    print(f"\n🏆 ТОП-20 САМЫХ ПОПУЛЯРНЫХ БРЕНДОВ:")
    top20 = sorted(final_brands, key=lambda x: brand_popularity.get(x, 1), reverse=True)[:20]
    for i, brand in enumerate(top20, 1):
        count = brand_popularity.get(brand, 1)
        print(f"{i:2d}. {brand} ({count} упоминаний)")

if __name__ == "__main__":
    create_final_unique_brands() 