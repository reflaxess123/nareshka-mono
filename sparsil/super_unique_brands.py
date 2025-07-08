#!/usr/bin/env python3
"""
Супер-агрессивное создание уникальных брендов компаний
Максимально очищает и объединяет все варианты одной компании
"""

import re
from typing import List, Dict, Set
from collections import defaultdict

def super_clean_brand(company: str) -> str:
    """Супер-агрессивная очистка названия до базового бренда"""
    if not company:
        return ""
    
    # Убираем нумерацию
    name = re.sub(r'^\s*\d+\.\s*', '', company)
    
    # АГРЕССИВНО убираем ВСЁ что в скобках и после них
    name = re.sub(r'\s*\([^)]*\).*$', '', name)
    name = re.sub(r'\s*\[[^\]]*\].*$', '', name)
    
    # Убираем всё после тире, запятой, двоеточия
    name = re.sub(r'\s*[-–—,:;].*$', '', name)
    
    # Убираем всё после ключевых слов
    stop_words = [
        'проект', 'аутстафф', 'команда', 'отдел', 'стрим', 'платформа',
        'на проект', 'в команду', 'через', 'от', 'для', 'в',
        'тех', 'техничка', 'собес', 'скрининг', 'интервью', 'финал',
        'этап', 'секция', 'часть', 'встреча', 'знакомство', 'разговор',
        'hr', 'эйчарка', 'написала', 'сама', 'лид', 'лидом',
        'внутренний', 'внутри', 'внешний', 'внутр', 'аутсорс',
        'дочка', 'ранее', 'было', 'указано', 'нужен', 'кто', 'что',
        'где', 'когда', 'почему', 'как', 'которая', 'который',
        'школа', 'онлайн', 'образования', 'университет'
    ]
    
    for stop_word in stop_words:
        # Ищем стоп-слово как отдельное слово
        pattern = r'\s+' + re.escape(stop_word) + r'.*$'
        name = re.sub(pattern, '', name, flags=re.IGNORECASE)
    
    # Убираем даты и номера
    name = re.sub(r'\s+\d{2}\.\d{2}.*$', '', name)
    name = re.sub(r'\s+\d{4}.*$', '', name)
    name = re.sub(r'\s+от\s+\d+.*$', '', name)
    name = re.sub(r'\s+\d+\s*$', '', name)
    
    # Убираем markdown и специальные символы
    name = re.sub(r'\*\*', '', name)
    name = name.replace('"', '').replace("'", '').replace('`', '')
    name = name.replace('#', '').replace('*', '')
    
    # Убираем лишние символы в начале и конце
    name = re.sub(r'^[:\-\*\s\"\']+', '', name)
    name = re.sub(r'[:\-\*\s\"\']+$', '', name)
    
    # Убираем точки в конце (кроме доменов)
    if not re.search(r'\.(ru|com|org|net)$', name.lower()):
        name = re.sub(r'\.+$', '', name)
    
    # Убираем лишние пробелы
    name = ' '.join(name.split())
    
    return name.strip()

def normalize_brand_key(name: str) -> str:
    """Создает ключ для группировки брендов"""
    if not name:
        return ""
    
    # Приводим к нижнему регистру
    key = name.lower()
    
    # Убираем все символы кроме букв и цифр
    key = re.sub(r'[^а-яёa-z0-9]', '', key)
    
    # Специальные правила для мегабрендов
    mega_brands = {
        'сбер': ['сбер', 'сбербанк', 'сберт', 'сберкорус', 'сберцити'],
        'альфабанк': ['альфа', 'альфабанк', 'альфабанк'],
        'тинькофф': ['тинькофф', 'тбанк', 'тинь'],
        'яндекс': ['яндекс', 'yandex'],
        'мтс': ['мтс'],
        'втб': ['втб'],
        'газпромбанк': ['газпромбанк', 'газпром', 'гпб'],
        'росбанк': ['росбанк'],
        'райффайзен': ['райффайзен', 'райфайзен'],
        'ozon': ['ozon', 'озон'],
        'wildberries': ['wildberries', 'wb'],
        'avito': ['avito', 'авито'],
        'epam': ['epam'],
        'ibs': ['ibs'],
        'x5': ['x5', 'x5tech', 'x5group', 'x5retail'],
        'северсталь': ['северсталь'],
        'совкомбанк': ['совкомбанк'],
        'rshb': ['рсхб', 'рсхбинтех'],
        'psb': ['псб', 'промсвязьбанк']
    }
    
    # Проверяем принадлежность к мегабренду
    for main_brand, variants in mega_brands.items():
        if key in variants:
            return main_brand
    
    return key

def is_valid_final_brand(name: str) -> bool:
    """Финальная проверка валидности бренда"""
    if not name or len(name) < 2:
        return False
    
    name_lower = name.lower().strip()
    
    # Исключаем мусор
    garbage_exact = [
        'hr', 'эйчарка', 'тех', 'собес', 'этап', 'финал', 'проект',
        'аутстафф', 'аутсорс', 'команда', 'отдел', 'стрим', 'платформа',
        'встреча', 'знакомство', 'разговор', 'интервью', 'скрининг',
        'внутренний', 'внешний', 'дочка', 'часть', 'секция'
    ]
    
    if name_lower in garbage_exact:
        return False
    
    # Исключаем технический мусор
    if re.search(r'^(then|function|import|export|const|console)', name_lower):
        return False
    
    # Исключаем описательные фразы
    if re.search(r'(что выведет|написать|реализовать|найти все)', name_lower):
        return False
    
    # Должны быть буквы
    if not re.search(r'[а-яёa-zA-Z]', name):
        return False
    
    # Не слишком длинные
    if len(name) > 40:
        return False
    
    return True

def choose_best_brand_variant(variants: List[str]) -> str:
    """Выбирает лучший вариант названия бренда"""
    if not variants:
        return ""
    
    # Фильтруем валидные
    valid = [v for v in variants if is_valid_final_brand(v)]
    if not valid:
        return ""
    
    # Убираем дубликаты
    unique_valid = list(set(valid))
    
    # Критерии качества (чем меньше, тем лучше)
    def quality_score(name: str) -> tuple:
        length = len(name)
        has_dots = '.' in name and not name.endswith('.ru')
        has_numbers = bool(re.search(r'\d', name))
        has_symbols = bool(re.search(r'[^а-яёА-ЯЁa-zA-Z0-9\s\.]', name))
        is_all_caps = name.isupper()
        has_extra_spaces = '  ' in name
        
        # Предпочитаем знакомые написания
        is_known_good = name in [
            'Сбер', 'Яндекс', 'МТС', 'ВТБ', 'Альфа-Банк', 'Тинькофф',
            'Газпромбанк', 'Авито', 'Ozon', 'Wildberries', 'EPAM', 'IBS'
        ]
        
        return (not is_known_good, has_symbols, has_dots, has_numbers, is_all_caps, has_extra_spaces, length)
    
    # Сортируем и берем лучший
    sorted_variants = sorted(unique_valid, key=quality_score)
    return sorted_variants[0]

def create_super_unique_brands():
    """Создает супер-уникальный список брендов"""
    
    print("🚀 СОЗДАНИЕ СУПЕР-УНИКАЛЬНЫХ БРЕНДОВ КОМПАНИЙ")
    print("=" * 60)
    
    # Читаем ультра-чистый список
    try:
        with open('ultra_clean_companies.txt', 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ Файл ultra_clean_companies.txt не найден")
        return
    
    # Извлекаем компании
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
    
    # Супер-агрессивная группировка
    brand_groups = defaultdict(list)
    processed = 0
    
    for company in companies:
        clean_brand = super_clean_brand(company)
        if not clean_brand:
            continue
        
        brand_key = normalize_brand_key(clean_brand)
        if brand_key and is_valid_final_brand(clean_brand):
            brand_groups[brand_key].append(clean_brand)
            processed += 1
    
    print(f"📋 Обработано: {processed}")
    print(f"📋 Групп брендов: {len(brand_groups)}")
    
    # Показываем крупные объединения
    print(f"\n🔥 КРУПНЫЕ ОБЪЕДИНЕНИЯ:")
    large_groups = [(k, v) for k, v in brand_groups.items() if len(v) > 2]
    large_groups.sort(key=lambda x: len(x[1]), reverse=True)
    
    for brand_key, variants in large_groups[:10]:
        unique_variants = list(set(variants))
        print(f"  {brand_key}: {unique_variants} ({len(variants)} упоминаний)")
    
    # Создаем финальный список
    final_brands = []
    total_merged = 0
    
    for brand_key, variants in brand_groups.items():
        if len(variants) > 1:
            total_merged += len(variants) - 1
        
        best_brand = choose_best_brand_variant(variants)
        if best_brand:
            final_brands.append(best_brand)
    
    # Сортируем
    final_brands.sort(key=lambda x: x.lower())
    
    print(f"\n✅ РЕЗУЛЬТАТ:")
    print(f"   Супер-уникальных брендов: {len(final_brands)}")
    print(f"   Объединено записей: {total_merged}")
    
    # Подсчитываем упоминания
    brand_popularity = defaultdict(int)
    for brand_key, variants in brand_groups.items():
        best_brand = choose_best_brand_variant(variants)
        if best_brand:
            brand_popularity[best_brand] = len(variants)
    
    # Сохраняем
    output_file = 'super_unique_brands.txt'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("СУПЕР-УНИКАЛЬНЫЕ БРЕНДЫ КОМПАНИЙ\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Всего супер-уникальных брендов: {len(final_brands)}\n")
        f.write(f"Объединено дубликатов: {total_merged}\n\n")
        
        # ТОП по популярности
        popular = sorted(final_brands, key=lambda x: brand_popularity.get(x, 1), reverse=True)
        
        f.write("ТОП-30 САМЫХ ПОПУЛЯРНЫХ:\n")
        f.write("-" * 40 + "\n")
        for i, brand in enumerate(popular[:30], 1):
            count = brand_popularity.get(brand, 1)
            f.write(f"{i:2d}. {brand} ({count} упоминаний)\n")
        
        f.write(f"\n\nВСЕ СУПЕР-УНИКАЛЬНЫЕ БРЕНДЫ ({len(final_brands)}):\n")
        f.write("-" * 40 + "\n")
        
        for i, brand in enumerate(final_brands, 1):
            f.write(f"{i:3d}. {brand}\n")
    
    print(f"💾 Сохранено в: {output_file}")
    
    # ТОП-20
    print(f"\n🏆 ТОП-20 САМЫХ ПОПУЛЯРНЫХ:")
    top20 = sorted(final_brands, key=lambda x: brand_popularity.get(x, 1), reverse=True)[:20]
    for i, brand in enumerate(top20, 1):
        count = brand_popularity.get(brand, 1)
        print(f"{i:2d}. {brand} ({count} упоминаний)")

if __name__ == "__main__":
    create_super_unique_brands() 