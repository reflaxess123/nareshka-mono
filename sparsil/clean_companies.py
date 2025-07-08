#!/usr/bin/env python3
"""
Очистка списка компаний от мусора
Удаляет фрагменты кода, описания задач, этапы собеседований и прочий мусор
"""

import re
from typing import List, Set

def is_garbage(company_name: str) -> bool:
    """Проверяет, является ли строка мусором (не компанией)"""
    
    if not company_name or len(company_name.strip()) == 0:
        return True
    
    name = company_name.strip().lower()
    
    # Слишком короткие или слишком длинные
    if len(name) < 2 or len(name) > 60:
        return True
    
    # Фрагменты кода
    code_patterns = [
        r'```', r'function\s*\(', r'import\s+', r'export\s+', r'const\s+', 
        r'console\.log', r'\.prototype', r'\.then', r'\.map', r'\.filter',
        r'^\s*//\s*', r'^\s*/\*', r'<script>', r'useeffect', r'usestate',
        r'array\.', r'object\.', r'\.length', r'\.push', r'\.splice'
    ]
    
    for pattern in code_patterns:
        if re.search(pattern, name, re.IGNORECASE):
            return True
    
    # Описания задач и действий
    task_keywords = [
        'задача', 'план действий', 'план решения', 'решение', 'найти все',
        'реализовать', 'написать', 'создать', 'сделать', 'выполнить',
        'продолжение записи', 'формат ввода', 'формулировка задачи',
        'условие', 'клонирование объекта', 'работа браузера', 'что является',
        'почему выбрали', 'расскажи о себе', 'чем горжусь', 'важность собеседования',
        'успех собеса', 'фидбек', 'весь экран', 'кликнули по диву',
        'лайвкодинг', 'отрефакторить код', 'кик из сообщества'
    ]
    
    for keyword in task_keywords:
        if keyword in name:
            return True
    
    # Этапы собеседований
    stage_patterns = [
        r'\d+\s*этап', r'первый этап', r'второй этап', r'третий этап', r'финал',
        r'скрининг', r'техсобес', r'тех\s*собес', r'техничка', r'знакомство с командой',
        r'общение с командой', r'встреча с лидом', r'hr.скрининг', r'созвон',
        r'livecoding', r'live\s*coding', r'алгоритм', r'система дизайн', r'system design'
    ]
    
    for pattern in stage_patterns:
        if re.search(pattern, name, re.IGNORECASE):
            return True
    
    # Даты и числа
    date_patterns = [
        r'^\d{1,2}\.\d{1,2}', r'^\d{1,2}/\d{1,2}', r'^\d{4}-\d{2}-\d{2}',
        r'^\d+$', r'^\d+-\d+$', r'запросил \d+', r'зп.*\d+', r'до \d+к',
        r'озвученная.*зп', r'просил \d+', r'вилка \d+'
    ]
    
    for pattern in date_patterns:
        if re.search(pattern, name, re.IGNORECASE):
            return True
    
    # URL и ссылки
    if re.search(r'https?://', name) or re.search(r't\.me/', name):
        return True
    
    # Описательные фразы
    descriptive_phrases = [
        'вакансия', 'hr написала', 'название компании', 'компания:', 'название:',
        'отозвали оффер', 'трудовую увидели', 'потярено', 'утеряно', 'по факту не',
        'до сих пор', 'будут делать', 'плохо, я туда', 'хоть это не',
        'так мы же', 'так что еще', 'ну ещё тогда', 'неприятно, надеюсь',
        'целый месяц', 'хорош, попробуй', 'с нуля вкатываешься', 'других слов нет'
    ]
    
    for phrase in descriptive_phrases:
        if phrase in name:
            return True
    
    # Проектные описания
    project_keywords = [
        'проект сбера', 'аутстафф', 'аутсорс', 'на проект', 'дочка', 'через',
        'в команду', 'команда', 'стрим', 'платформа', 'отдел'
    ]
    
    # Разрешаем если это часть названия компании
    project_count = sum(1 for keyword in project_keywords if keyword in name)
    if project_count > 1:  # Если много проектных слов - скорее всего описание
        return True
    
    # Специальные символы в начале (маркеры списков)
    if re.match(r'^[•\-\*\d+\.\)\]\}\#\@\$\%\^\&\[\(\{]', name):
        return True
    
    # Односимвольные или двухсимвольные "названия"
    if len(name.strip()) <= 2:
        return True
    
    # Эмодзи и специальные символы
    if re.search(r'[📌🔥🤡✅⚠️❌]', name):
        return True
    
    return False

def clean_companies_list():
    """Очищает список компаний от мусора"""
    
    print("🧹 ОЧИСТКА СПИСКА КОМПАНИЙ ОТ МУСОРА")
    print("=" * 60)
    
    # Загружаем исходный файл
    try:
        with open('companies_list.txt', 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ Файл companies_list.txt не найден")
        return
    
    # Извлекаем список компаний
    lines = content.split('\n')
    companies = []
    
    # Находим секцию с алфавитным списком
    in_alphabetic = False
    for line in lines:
        if "АЛФАВИТНЫЙ СПИСОК:" in line:
            in_alphabetic = True
            continue
        if in_alphabetic and "ТОП-20 ПОПУЛЯРНЫХ:" in line:
            break
        if in_alphabetic and line.strip():
            # Извлекаем название компании (убираем номер и количество)
            match = re.match(r'\s*\d+\.\s*(.+?)\s*\(\d+\)\s*$', line)
            if match:
                company_name = match.group(1).strip()
                companies.append(company_name)
    
    print(f"📊 Исходное количество записей: {len(companies)}")
    
    # Фильтруем мусор
    clean_companies = []
    garbage_list = []
    
    for company in companies:
        if is_garbage(company):
            garbage_list.append(company)
        else:
            clean_companies.append(company)
    
    # Сортируем очищенный список
    clean_companies.sort(key=str.lower)
    
    print(f"✅ Чистых компаний: {len(clean_companies)}")
    print(f"🗑️ Удалено мусора: {len(garbage_list)}")
    print(f"📈 Процент очистки: {len(garbage_list)/len(companies)*100:.1f}%")
    
    # Сохраняем очищенный список
    with open('clean_companies_list.txt', 'w', encoding='utf-8') as f:
        f.write("ОЧИЩЕННЫЙ СПИСОК КОМПАНИЙ\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Всего компаний: {len(clean_companies)}\n")
        f.write(f"Удалено мусора: {len(garbage_list)}\n\n")
        
        f.write("ЧИСТЫЙ СПИСОК КОМПАНИЙ:\n")
        f.write("-" * 30 + "\n")
        for i, company in enumerate(clean_companies, 1):
            f.write(f"{i:3d}. {company}\n")
        
        f.write("\n\nУДАЛЕННЫЙ МУСОР:\n")
        f.write("-" * 30 + "\n")
        for i, garbage in enumerate(sorted(garbage_list, key=str.lower), 1):
            f.write(f"{i:3d}. {garbage}\n")
    
    print(f"\n✅ РЕЗУЛЬТАТ СОХРАНЕН: clean_companies_list.txt")
    
    # Показываем топ-10 чистых компаний
    print(f"\n🏆 ТОП-10 ЧИСТЫХ КОМПАНИЙ:")
    for i, company in enumerate(clean_companies[:10], 1):
        print(f"{i:2d}. {company}")

if __name__ == "__main__":
    clean_companies_list() 