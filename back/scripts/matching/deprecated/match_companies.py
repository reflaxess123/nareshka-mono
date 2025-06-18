import re
import os
import sys
import json

# Добавляем путь к корневой папке проекта в sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..' )))

from app.database import get_db
from app.models import ContentBlock, ContentFile

def extract_companies_from_md_text(text: str) -> list[str]:
    """Простое извлечение компаний из текста"""
    companies = []
    
    # Ищем паттерны
    patterns = [
        r'встречалось в\s*[-\s]*([^\n]+)',
        r'встречается в\s*[-\s]*([^\n]+)', 
        r'встречался в\s*[-\s]*([^\n]+)'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            # Разбиваем по разделителям и чистим
            clean_companies = re.split(r'[,\n\-]', match.strip())
            for company in clean_companies:
                company = company.strip().lower()
                if company and len(company) > 2:
                    companies.append(company)
    
    return list(set(companies))

def parse_all_md_files():
    """Парсим все .md файлы из js/, react/, ts/"""
    tasks = []
    
    # Корневая папка проекта
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    folders = [
        os.path.join(base_dir, 'js', 'Основные задачи'), 
        os.path.join(base_dir, 'js', 'решения'), 
        os.path.join(base_dir, 'react'), 
        os.path.join(base_dir, 'ts', 'Задачи')
    ]
    
    for folder_path in folders:
        if not os.path.exists(folder_path):
            print(f"Warning: Folder not found: {folder_path}")
            continue
            
        for root, _, files in os.walk(folder_path):
            for file_name in files:
                if file_name.endswith('.md'):
                    file_path = os.path.join(root, file_name)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        # Разбиваем на задачи по заголовкам
                        # Улучшенный паттерн для заголовков: #+ Пробел Заголовок
                        task_blocks = re.split(r'^(#+)\s+(.+)$', content, flags=re.MULTILINE)
                        
                        # task_blocks будет выглядеть примерно так:
                        # ['', '##', 'Заголовок 1', 'Контент 1', '###', 'Заголовок 2', 'Контент 2']
                        # Начинаем с 2, так как 0-й элемент - пустая строка, 1-й и 2-й - первый заголовок и контент
                        
                        current_title = None
                        current_content = ""
                        
                        for i in range(len(task_blocks)):
                            if i % 3 == 1: # Это уровень заголовка, пропускаем
                                pass
                            elif i % 3 == 2: # Это заголовок
                                if current_title is not None: # Если уже есть незаконченная задача
                                    tasks.append({
                                        'title': current_title,
                                        'content': current_content.strip(),
                                        'file': file_name
                                    })
                                current_title = task_blocks[i].strip()
                                current_content = ""
                            else: # Это контент
                                current_content += task_blocks[i]
                        
                        # Добавляем последнюю задачу, если она есть
                        if current_title is not None:
                            tasks.append({
                                'title': current_title,
                                'content': current_content.strip(),
                                'file': file_name
                            })
                            
                    except Exception as e:
                        print(f"Error reading file {file_path}: {e}")
    
    return tasks

def normalize_title(title: str) -> str:
    """Нормализация заголовка для сравнения"""
    # Удаляем ссылки в скобках []()
    title = re.sub(r'\[.*?\]\(.*?\)', '', title)
    # Удаляем знаки препинания и приводим к нижнему регистру
    return re.sub(r'[^\w\s]', '', title.lower().strip())

def match_and_update():
    """Главная функция - запустить один раз"""
    db = next(get_db())
    
    print("Parsing all .md files...")
    md_tasks = parse_all_md_files()
    print(f"Found {len(md_tasks)} tasks in .md files.")
    
    print("Fetching all ContentBlocks from DB...")
    db_blocks = db.query(ContentBlock).all()
    print(f"Found {len(db_blocks)} content blocks in DB.")
    
    matched_count = 0
    updated_blocks = []
    
    db_blocks_map = {normalize_title(block.blockTitle): block for block in db_blocks}
    
    for md_task in md_tasks:
        companies = extract_companies_from_md_text(md_task['content'])
        
        if not companies:
            continue
            
        normalized_md_title = normalize_title(md_task['title'])
        
        if normalized_md_title in db_blocks_map:
            block = db_blocks_map[normalized_md_title]
            
            # Проверяем, изменились ли компании
            if sorted(block.companies) != sorted(companies):
                block.companies = companies
                updated_blocks.append(block)
                print(f"✅ Matched and updated: {block.blockTitle} -> {companies}")
                matched_count += 1
            else:
                print(f"➡️ Already matched: {block.blockTitle} -> {companies}")
        else:
            print(f"❌ No match found for: {md_task['title']}")
            
    if updated_blocks:
        try:
            db.bulk_save_objects(updated_blocks)
            db.commit()
            print(f"🎉 Successfully updated {matched_count} content blocks.")
        except Exception as e:
            db.rollback()
            print(f"Error during bulk update: {e}")
    else:
        print("No content blocks needed updating.")
        
    db.close()

if __name__ == "__main__":
    match_and_update() 