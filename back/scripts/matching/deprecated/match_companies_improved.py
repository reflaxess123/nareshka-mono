import re
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..' )))

from app.database import get_db
from app.models import ContentBlock

def normalize_title_smart(title: str) -> str:
    """Умная нормализация заголовков"""
    # Удаляем markdown ссылки [text](url) -> text
    title = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', title)
    
    # Удаляем номера в начале: "1. title" -> "title"
    title = re.sub(r'^\d+\.\s*', '', title)
    
    # Удаляем лишние пробелы и приводим к нижнему регистру
    title = re.sub(r'\s+', ' ', title.lower().strip())
    
    # Удаляем специальные символы, но оставляем важные
    title = re.sub(r'[#\-\*\+\[\]]', '', title)
    
    return title.strip()

def extract_companies_from_md_text(text: str) -> list[str]:
    """Улучшенное извлечение компаний из текста"""
    companies = []
    
    # Паттерн для захвата всего блока после "встречалось в"
    # Ищем "встречалось в" и все строки после него до следующего раздела
    patterns = [
        r'встречалось в\s*[-\s]*\n((?:\s*[-\t]+\s*[^\n]+\n?)*)',
        r'встречается в\s*[-\s]*\n((?:\s*[-\t]+\s*[^\n]+\n?)*)',
        r'встречался в\s*[-\s]*\n((?:\s*[-\t]+\s*[^\n]+\n?)*)',
        # Также ловим случаи когда все на одной строке
        r'встречалось в\s*[-\s]*([^\n]+)',
        r'встречается в\s*[-\s]*([^\n]+)', 
        r'встречался в\s*[-\s]*([^\n]+)'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            # Обрабатываем многострочный блок
            lines = match.split('\n')
            for line in lines:
                # Удаляем табуляции, тире, пробелы в начале
                line = re.sub(r'^[\s\t\-]+', '', line.strip())
                if line:
                    # Разбиваем по запятым если есть
                    sub_companies = re.split(r'[,;]', line)
                    for company in sub_companies:
                        company = company.strip().lower()
                        # Фильтруем мусор
                        if (company and len(company) > 2 and 
                            not company.startswith('(') and 
                            company not in ['то есть', 'нельзя копировать массив', 'inplace)', 'нельзя мутировать']):
                            companies.append(company)
    
    # Дополнительно ищем компании в более простых форматах
    # "компания:" в начале строки
    company_lines = re.findall(r'^[\s\t]*[-•]\s*(.+)$', text, re.MULTILINE)
    for line in company_lines:
        line = line.strip().lower()
        if any(keyword in text.lower() for keyword in ['встречалось', 'встречается', 'встречался']):
            # Только если в тексте есть упоминание о встречах
            if (line and len(line) > 2 and 
                not line.startswith('решено') and 
                not re.match(r'\d+\s*раз', line)):
                companies.append(line)
    
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
                        
                        # Парсинг заголовков
                        lines = content.split('\n')
                        current_title = None
                        current_content = ""
                        
                        for line in lines:
                            header_match = re.match(r'^(#{1,6})\s+(.+)$', line.strip())
                            if header_match:
                                # Сохраняем предыдущую задачу
                                if current_title and current_content.strip():
                                    companies = extract_companies_from_md_text(current_content)
                                    if companies:
                                        tasks.append({
                                            'title': current_title,
                                            'content': current_content.strip(),
                                            'companies': companies,
                                            'file': file_name,
                                            'normalized': normalize_title_smart(current_title)
                                        })
                                
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
                                    'normalized': normalize_title_smart(current_title)
                                })
                                
                    except Exception as e:
                        print(f"Error reading file {file_path}: {e}")
    
    return tasks

def similarity_score(str1: str, str2: str) -> float:
    """Вычисляет коэффициент сходства между строками"""
    if not str1 or not str2:
        return 0.0
    
    # Точное совпадение
    if str1 == str2:
        return 1.0
    
    # Одна строка содержится в другой
    if str1 in str2 or str2 in str1:
        shorter = min(len(str1), len(str2))
        longer = max(len(str1), len(str2))
        return shorter / longer
    
    # Similarity по словам
    words1 = set(str1.split())
    words2 = set(str2.split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    
    return intersection / union if union > 0 else 0.0

def find_best_match(md_task: dict, db_blocks: list, threshold: float = 0.5):
    """Находит лучшее совпадение для задачи из .md"""
    best_match = None
    best_score = 0.0
    
    md_normalized = md_task['normalized']
    
    for block in db_blocks:
        db_normalized = normalize_title_smart(block.blockTitle)
        score = similarity_score(md_normalized, db_normalized)
        
        if score > best_score and score >= threshold:
            best_score = score
            best_match = block
    
    return best_match, best_score

def match_and_update_improved():
    """Улучшенная функция сопоставления и обновления"""
    db = next(get_db())
    
    print("🔍 Парсинг .md файлов...")
    md_tasks = parse_md_files_improved()
    print(f"📝 Найдено {len(md_tasks)} задач с компаниями в .md файлах")
    
    print("🗄️ Получение ContentBlocks из БД...")
    db_blocks = db.query(ContentBlock).all()
    print(f"📊 Найдено {len(db_blocks)} блоков в БД")
    
    matches = []
    no_matches = []
    
    print("\n🎯 Поиск совпадений...")
    
    for md_task in md_tasks:
        best_match, score = find_best_match(md_task, db_blocks, threshold=0.3)
        
        if best_match:
            matches.append({
                'md_task': md_task,
                'db_block': best_match,
                'score': score
            })
            print(f"✅ [{score:.2f}] '{md_task['title'][:50]}...' -> '{best_match.blockTitle}' -> {md_task['companies']}")
        else:
            no_matches.append(md_task)
            print(f"❌ Не найдено: '{md_task['title'][:50]}...' -> {md_task['companies']}")
    
    print(f"\n📈 Результаты:")
    print(f"   • Найдено совпадений: {len(matches)}")
    print(f"   • Не найдено: {len(no_matches)}")
    
    if matches:
        print(f"\n💾 Обновление базы данных...")
        updated_count = 0
        
        for match in matches:
            db_block = match['db_block']
            companies = match['md_task']['companies']
            
            # Проверяем, нужно ли обновление
            if sorted(db_block.companies) != sorted(companies):
                db_block.companies = companies
                updated_count += 1
        
        try:
            db.commit()
            print(f"🎉 Успешно обновлено {updated_count} блоков в БД!")
        except Exception as e:
            db.rollback()
            print(f"❌ Ошибка при обновлении БД: {e}")
    
    # Показываем лучшие совпадения
    if matches:
        print(f"\n🏆 ТОП-10 лучших совпадений:")
        sorted_matches = sorted(matches, key=lambda x: x['score'], reverse=True)
        for i, match in enumerate(sorted_matches[:10]):
            print(f"   {i+1}. [{match['score']:.2f}] {match['md_task']['title']} -> {match['db_block'].blockTitle}")
    
    db.close()
    
    return {
        'total_md_tasks': len(md_tasks),
        'total_db_blocks': len(db_blocks),
        'matches_found': len(matches),
        'no_matches': len(no_matches),
        'updated_count': updated_count if matches else 0
    }

if __name__ == "__main__":
    result = match_and_update_improved()
    print(f"\n🎯 Итоговая статистика:")
    print(f"   📁 Задач в .md: {result['total_md_tasks']}")
    print(f"   🗄️ Блоков в БД: {result['total_db_blocks']}")
    print(f"   ✅ Найдено совпадений: {result['matches_found']}")
    print(f"   💾 Обновлено в БД: {result['updated_count']}")
    print(f"   📊 Процент покрытия: {result['matches_found']/result['total_md_tasks']*100:.1f}%") 