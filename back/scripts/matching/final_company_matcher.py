#!/usr/bin/env python3
"""
ФИНАЛЬНЫЙ СКРИПТ ДЛЯ СОПОСТАВЛЕНИЯ КОМПАНИЙ
Максимально быстро и эффективно заполняет поле companies в БД
"""

import re
import os
import sys
from difflib import SequenceMatcher
from typing import Dict, List, Set

# Добавляем путь к корневой папке проекта
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import get_db
from app.models import ContentBlock

def normalize_title(title: str) -> str:
    """Агрессивная нормализация заголовков для лучшего сопоставления"""
    # Удаляем markdown ссылки [text](url) -> text
    title = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', title)
    
    # Удаляем номера в начале
    title = re.sub(r'^\d+\.\s*', '', title)
    
    # Удаляем markdown символы
    title = re.sub(r'[#\-\*\+\[\]`_]', ' ', title)
    
    # Убираем множественные пробелы
    title = re.sub(r'\s+', ' ', title.lower().strip())
    
    return title

def similarity(a: str, b: str) -> float:
    """Вычисляет схожесть строк"""
    return SequenceMatcher(None, a, b).ratio()

def extract_companies_from_text(text: str) -> List[str]:
    """Извлекает компании из текста с максимальной точностью"""
    companies = set()
    
    # Паттерны для поиска блоков с компаниями
    company_patterns = [
        r'встречал[аось]+\s+в[:\s]*\n(.*?)(?=\n\n|\n#|\n```|\Z)',
        r'встречалось в[:\s]*\n(.*?)(?=\n\n|\n#|\n```|\Z)',
        r'попадалось в[:\s]*\n(.*?)(?=\n\n|\n#|\n```|\Z)',
    ]
    
    for pattern in company_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
        for match in matches:
            # Разбиваем на строки и чистим
            lines = match.strip().split('\n')
            for line in lines:
                # Убираем маркеры списков и лишние символы
                clean_line = re.sub(r'^\s*[-•*]\s*', '', line.strip())
                clean_line = re.sub(r'^\s*\d+\.\s*', '', clean_line)
                
                if clean_line and len(clean_line) > 2:
                    # Дополнительная очистка
                    clean_line = clean_line.lower()
                    
                    # Убираем комментарии в скобках
                    clean_line = re.sub(r'\([^)]*\)', '', clean_line).strip()
                    
                    # Фильтруем мусор
                    if (clean_line and 
                        not clean_line.startswith('решено') and
                        not re.match(r'\d+\s*раз', clean_line) and
                        len(clean_line) > 2):
                        companies.add(clean_line)
    
    return sorted(list(companies))

def parse_md_file(file_path: str) -> Dict[str, Dict]:
    """Парсит .md файл и возвращает задачи с компаниями"""
    if not os.path.exists(file_path):
        return {}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"⚠️ Ошибка чтения файла {file_path}: {e}")
        return {}
    
    tasks = {}
    
    # Разбиваем на секции по заголовкам
    sections = re.split(r'(^#{1,6}\s+.+)$', content, flags=re.MULTILINE)
    
    current_title = None
    current_content = ""
    
    for section in sections:
        if re.match(r'^#{1,6}\s+', section):
            # Сохраняем предыдущую секцию
            if current_title and current_content:
                normalized_title = normalize_title(current_title)
                companies = extract_companies_from_text(current_content)
                
                if normalized_title and companies:
                    tasks[normalized_title] = {
                        'original_title': current_title,
                        'companies': companies,
                        'content_preview': current_content[:200]
                    }
            
            # Начинаем новую секцию
            current_title = re.sub(r'^#+\s*', '', section).strip()
            current_content = ""
        else:
            current_content += section
    
    # Обрабатываем последнюю секцию
    if current_title and current_content:
        normalized_title = normalize_title(current_title)
        companies = extract_companies_from_text(current_content)
        
        if normalized_title and companies:
            tasks[normalized_title] = {
                'original_title': current_title,
                'companies': companies,
                'content_preview': current_content[:200]
            }
    
    return tasks

def load_all_md_tasks() -> Dict[str, Dict]:
    """Загружает все задачи из .md файлов"""
    print("🔍 Парсинг .md файлов...")
    
    # Все .md файлы с задачами
    md_files = [
        '../js/Основные задачи/замыки.md',
        '../js/Основные задачи/кастомные методы и функции.md',
        '../js/Основные задачи/классы.md',
        '../js/Основные задачи/массивы.md',
        '../js/Основные задачи/матрицы.md',
        '../js/Основные задачи/объекты.md',
        '../js/Основные задачи/промисы.md',
        '../js/Основные задачи/строки.md',
        '../js/Основные задачи/числа.md',
        '../react/Реакт Мини Апп.md',
        '../react/Реакт Ререндер.md',
        '../react/Реакт Рефактор.md',
        '../react/Реакт Хуки.md',
        '../ts/Задачи/ts задачи.md',
    ]
    
    all_tasks = {}
    
    for file_path in md_files:
        if os.path.exists(file_path):
            print(f"  📄 {os.path.basename(file_path)}")
            tasks = parse_md_file(file_path)
            all_tasks.update(tasks)
            print(f"     Найдено задач с компаниями: {len(tasks)}")
        else:
            print(f"  ❌ Файл не найден: {file_path}")
    
    print(f"\n📊 Всего задач с компаниями: {len(all_tasks)}")
    return all_tasks

def find_best_match(db_title: str, md_tasks: Dict[str, Dict]) -> tuple:
    """Находит лучшее совпадение для задачи из БД"""
    normalized_db_title = normalize_title(db_title)
    
    best_match = None
    best_score = 0
    best_md_title = None
    
    for md_title, md_data in md_tasks.items():
        # Точное совпадение
        if normalized_db_title == md_title:
            return md_data, 1.0, md_title
        
        # Similarity matching
        score = similarity(normalized_db_title, md_title)
        if score > best_score and score >= 0.75:
            best_match = md_data
            best_score = score
            best_md_title = md_title
        
        # Частичное вхождение
        if (md_title in normalized_db_title or normalized_db_title in md_title) and score >= 0.6:
            if score > best_score:
                best_match = md_data
                best_score = score
                best_md_title = md_title
    
    return best_match, best_score, best_md_title

def main():
    """Главная функция - быстрое сопоставление и обновление"""
    print("🚀 БЫСТРОЕ СОПОСТАВЛЕНИЕ КОМПАНИЙ")
    print("=" * 50)
    
    # 1. Загружаем задачи из .md файлов
    md_tasks = load_all_md_tasks()
    
    if not md_tasks:
        print("❌ Не найдено задач с компаниями в .md файлах!")
        return
    
    # 2. Подключаемся к БД
    db = next(get_db())
    
    try:
        # 3. Получаем все задачи из БД
        print("\n🗄️ Загрузка задач из БД...")
        db_blocks = db.query(ContentBlock).all()
        print(f"📊 Найдено {len(db_blocks)} блоков в БД")
        
        # 4. Сопоставление
        print("\n🎯 Сопоставление задач...")
        updated_count = 0
        total_companies = 0
        
        for db_block in db_blocks:
            if not db_block.blockTitle:
                continue
            
            # Ищем лучшее совпадение
            best_match, score, md_title = find_best_match(db_block.blockTitle, md_tasks)
            
            if best_match and score >= 0.75:
                companies = best_match['companies']
                
                # Обновляем только если компании изменились
                if sorted(db_block.companies or []) != sorted(companies):
                    db_block.companies = companies
                    updated_count += 1
                    total_companies += len(companies)
                    
                    print(f"  ✅ [{score:.2f}] '{db_block.blockTitle[:40]}...' -> {companies}")
        
        # 5. Сохраняем изменения
        if updated_count > 0:
            print(f"\n💾 Сохранение изменений в БД...")
            db.commit()
            print(f"🎉 УСПЕШНО ОБНОВЛЕНО: {updated_count} задач")
            print(f"🏢 Всего добавлено компаний: {total_companies}")
        else:
            print("\n💡 Нет новых данных для обновления")
        
        # 6. Статистика
        print(f"\n📈 ИТОГОВАЯ СТАТИСТИКА:")
        blocks_with_companies = [b for b in db_blocks if b.companies]
        print(f"   📋 Задач в БД: {len(db_blocks)}")
        print(f"   🏢 Задач с компаниями: {len(blocks_with_companies)}")
        print(f"   📊 Покрытие: {len(blocks_with_companies)/len(db_blocks)*100:.1f}%")
        
        # Показываем топ компании
        company_count = {}
        for block in blocks_with_companies:
            for company in block.companies:
                company_count[company] = company_count.get(company, 0) + 1
        
        if company_count:
            print(f"\n🏆 ТОП-10 КОМПАНИЙ:")
            top_companies = sorted(company_count.items(), key=lambda x: x[1], reverse=True)[:10]
            for i, (company, count) in enumerate(top_companies, 1):
                print(f"   {i:2d}. {company} ({count} задач)")
    
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main() 