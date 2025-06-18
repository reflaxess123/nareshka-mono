import re
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..' )))

from app.database import get_db
from app.models import ContentBlock

def normalize_title_v1(title: str) -> str:
    """Текущая нормализация (слишком грубая)"""
    title = re.sub(r'\[.*?\]\(.*?\)', '', title)
    return re.sub(r'[^\w\s]', '', title.lower().strip())

def normalize_title_v2(title: str) -> str:
    """Улучшенная нормализация"""
    # Удаляем ссылки markdown [text](url)
    title = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', title)
    # Удаляем лишние пробелы и приводим к нижнему регистру
    title = re.sub(r'\s+', ' ', title.lower().strip())
    # Удаляем только ненужные символы, оставляем важные
    title = re.sub(r'[#\-\*\+]', '', title)
    return title.strip()

def extract_companies_from_md_text(text: str) -> list[str]:
    """Извлечение компаний из текста"""
    companies = []
    patterns = [
        r'встречалось в\s*[-\s]*([^\n]+)',
        r'встречается в\s*[-\s]*([^\n]+)', 
        r'встречался в\s*[-\s]*([^\n]+)'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            clean_companies = re.split(r'[,\n\-]', match.strip())
            for company in clean_companies:
                company = company.strip().lower()
                if company and len(company) > 2:
                    companies.append(company)
    
    return list(set(companies))

def parse_md_files_improved():
    """Улучшенный парсинг .md файлов"""
    tasks = []
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    folders = [
        os.path.join(base_dir, 'js', 'Основные задачи'), 
        os.path.join(base_dir, 'js', 'решения'), 
        os.path.join(base_dir, 'react'), 
        os.path.join(base_dir, 'ts', 'Задачи')
    ]
    
    for folder_path in folders:
        if not os.path.exists(folder_path):
            continue
            
        for root, _, files in os.walk(folder_path):
            for file_name in files:
                if file_name.endswith('.md'):
                    file_path = os.path.join(root, file_name)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Улучшенный парсинг заголовков
                        # Ищем заголовки: #### Title или ## Title и т.д.
                        lines = content.split('\n')
                        current_title = None
                        current_content = ""
                        
                        for line in lines:
                            # Проверяем если это заголовок
                            header_match = re.match(r'^(#{1,6})\s+(.+)$', line.strip())
                            if header_match:
                                # Сохраняем предыдущую задачу если есть
                                if current_title and current_content.strip():
                                    companies = extract_companies_from_md_text(current_content)
                                    if companies:  # Только задачи с компаниями
                                        tasks.append({
                                            'title': current_title,
                                            'content': current_content.strip(),
                                            'companies': companies,
                                            'file': file_name,
                                            'normalized_v1': normalize_title_v1(current_title),
                                            'normalized_v2': normalize_title_v2(current_title)
                                        })
                                
                                # Начинаем новую задачу
                                current_title = header_match.group(2).strip()
                                current_content = ""
                            else:
                                current_content += line + "\n"
                        
                        # Добавляем последнюю задачу
                        if current_title and current_content.strip():
                            companies = extract_companies_from_md_text(current_content)
                            if companies:
                                tasks.append({
                                    'title': current_title,
                                    'content': current_content.strip(),
                                    'companies': companies,
                                    'file': file_name,
                                    'normalized_v1': normalize_title_v1(current_title),
                                    'normalized_v2': normalize_title_v2(current_title)
                                })
                                
                    except Exception as e:
                        print(f"Error reading file {file_path}: {e}")
    
    return tasks

def analyze_matching():
    """Анализируем качество сопоставления"""
    print("=== АНАЛИЗ СОПОСТАВЛЕНИЯ ===\n")
    
    # Получаем данные из БД
    db = next(get_db())
    db_blocks = db.query(ContentBlock).all()
    
    # Получаем данные из .md файлов
    md_tasks = parse_md_files_improved()
    
    print(f"📊 Статистика:")
    print(f"   • ContentBlocks в БД: {len(db_blocks)}")
    print(f"   • Задачи с компаниями в .md: {len(md_tasks)}")
    
    # Создаем словари для разных стратегий сопоставления
    db_blocks_v1 = {normalize_title_v1(block.blockTitle): block for block in db_blocks}
    db_blocks_v2 = {normalize_title_v2(block.blockTitle): block for block in db_blocks}
    
    print(f"\n🔍 Примеры заголовков из БД:")
    for i, block in enumerate(db_blocks[:10]):
        print(f"   {i+1}. '{block.blockTitle}' -> v1: '{normalize_title_v1(block.blockTitle)}' -> v2: '{normalize_title_v2(block.blockTitle)}'")
    
    print(f"\n🔍 Примеры заголовков из .md (с компаниями):")
    for i, task in enumerate(md_tasks[:10]):
        print(f"   {i+1}. '{task['title']}' -> v1: '{task['normalized_v1']}' -> v2: '{task['normalized_v2']}' -> компании: {task['companies']}")
    
    # Тестируем разные стратегии
    matches_v1 = 0
    matches_v2 = 0
    partial_matches = []
    
    print(f"\n📈 Анализ совпадений:")
    
    for md_task in md_tasks:
        # Стратегия 1: точное совпадение v1
        if md_task['normalized_v1'] in db_blocks_v1:
            matches_v1 += 1
            
        # Стратегия 2: точное совпадение v2  
        if md_task['normalized_v2'] in db_blocks_v2:
            matches_v2 += 1
            
        # Стратегия 3: частичное совпадение
        for db_title_norm, db_block in db_blocks_v2.items():
            # Проверяем содержится ли одно в другом
            if (md_task['normalized_v2'] in db_title_norm or 
                db_title_norm in md_task['normalized_v2']) and len(db_title_norm) > 3:
                partial_matches.append({
                    'md_title': md_task['title'],
                    'db_title': db_block.blockTitle,
                    'companies': md_task['companies']
                })
                break
    
    print(f"   • Совпадений v1 (старая стратегия): {matches_v1}")
    print(f"   • Совпадений v2 (новая стратегия): {matches_v2}")
    print(f"   • Частичных совпадений: {len(partial_matches)}")
    
    if partial_matches:
        print(f"\n🎯 Примеры частичных совпадений:")
        for i, match in enumerate(partial_matches[:10]):
            print(f"   {i+1}. MD: '{match['md_title']}' <-> DB: '{match['db_title']}' -> {match['companies']}")
    
    # Поиск несопоставленных
    unmatched_md = []
    for md_task in md_tasks:
        found = False
        for db_title_norm in db_blocks_v2.keys():
            if (md_task['normalized_v2'] == db_title_norm or
                md_task['normalized_v2'] in db_title_norm or 
                db_title_norm in md_task['normalized_v2']) and len(db_title_norm) > 3:
                found = True
                break
        if not found:
            unmatched_md.append(md_task)
    
    print(f"\n❌ Несопоставленные задачи из .md ({len(unmatched_md)}):")
    for i, task in enumerate(unmatched_md[:15]):
        print(f"   {i+1}. '{task['title']}' -> {task['companies']}")
    
    db.close()

if __name__ == "__main__":
    analyze_matching() 