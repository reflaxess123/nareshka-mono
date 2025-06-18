import re
import os
import json
from collections import defaultdict

def extract_all_from_md_file(file_path: str) -> dict:
    """Извлекает ВСЕ возможные упоминания компаний и задач из .md файла"""
    if not os.path.exists(file_path):
        return {}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    result = {
        'file_path': file_path,
        'tasks': [],
        'companies_in_blocks': [],
        'companies_in_headers': [],
        'all_headers': [],
        'company_blocks_raw': [],
        'statistics': {}
    }
    
    # 1. Извлекаем ВСЕ заголовки (любого уровня)
    all_headers = re.findall(r'^(#{1,6})\s*(.+)$', content, re.MULTILINE)
    for level, header_text in all_headers:
        result['all_headers'].append({
            'level': len(level),
            'text': header_text.strip(),
            'normalized': header_text.strip().lower()
        })
    
    # 2. Извлекаем блоки "встречалось в" с полным контекстом
    company_block_patterns = [
        r'встречалось в.*?(?=\n\S|\n#+|\n```|\Z)',
        r'встречается в.*?(?=\n\S|\n#+|\n```|\Z)', 
        r'встречался в.*?(?=\n\S|\n#+|\n```|\Z)',
        r'попадалось в.*?(?=\n\S|\n#+|\n```|\Z)'
    ]
    
    for pattern in company_block_patterns:
        blocks = re.findall(pattern, content, re.IGNORECASE | re.DOTALL)
        for block in blocks:
            result['company_blocks_raw'].append(block)
            
            # Парсим компании из блока
            lines = block.split('\n')
            companies_in_block = []
            
            for line in lines[1:]:  # Пропускаем первую строку
                # Убираем разные варианты маркеров списков
                cleaned_line = re.sub(r'^[\t\s]*[-*+]\s*', '', line).strip()
                cleaned_line = re.sub(r'^[\t\s]*\d+\.\s*', '', cleaned_line).strip()
                
                if cleaned_line and len(cleaned_line) > 1:
                    companies_in_block.append(cleaned_line)
            
            result['companies_in_blocks'].extend(companies_in_block)
    
    # 3. Разбиваем на секции по заголовкам для извлечения задач
    sections = re.split(r'(^#{1,6}\s+.+)$', content, flags=re.MULTILINE)
    
    current_task = None
    current_content = ""
    
    for section in sections:
        if re.match(r'^#{1,6}\s+', section):
            # Сохраняем предыдущую задачу
            if current_task and current_content:
                task_companies = []
                
                # Ищем компании в контенте задачи
                for pattern in company_block_patterns:
                    task_blocks = re.findall(pattern, current_content, re.IGNORECASE | re.DOTALL)
                    for block in task_blocks:
                        lines = block.split('\n')
                        for line in lines[1:]:
                            cleaned = re.sub(r'^[\t\s]*[-*+]\s*', '', line).strip()
                            if cleaned and len(cleaned) > 1:
                                task_companies.append(cleaned)
                
                result['tasks'].append({
                    'title': current_task,
                    'normalized_title': re.sub(r'^#+\s*', '', current_task).strip().lower(),
                    'companies': task_companies,
                    'content_length': len(current_content),
                    'has_code': '```' in current_content
                })
            
            # Начинаем новую задачу
            current_task = section.strip()
            current_content = ""
        else:
            current_content += section
    
    # Обрабатываем последнюю задачу
    if current_task and current_content:
        task_companies = []
        for pattern in company_block_patterns:
            task_blocks = re.findall(pattern, current_content, re.IGNORECASE | re.DOTALL)
            for block in task_blocks:
                lines = block.split('\n')
                for line in lines[1:]:
                    cleaned = re.sub(r'^[\t\s]*[-*+]\s*', '', line).strip()
                    if cleaned and len(cleaned) > 1:
                        task_companies.append(cleaned)
        
        result['tasks'].append({
            'title': current_task,
            'normalized_title': re.sub(r'^#+\s*', '', current_task).strip().lower(),
            'companies': task_companies,
            'content_length': len(current_content),
            'has_code': '```' in current_content
        })
    
    # 4. Анализируем заголовки на предмет компаний
    potential_company_headers = []
    for header in result['all_headers']:
        header_text = header['normalized']
        
        # Заголовки уровня 1-3, которые могут быть компаниями
        if header['level'] <= 3 and len(header_text) < 50:
            # Исключаем явно техничные заголовки
            if not re.match(r'^(задач|example|пример|counter|todo|списки|рефактор|тренировочные|other|use|test|решени)', header_text):
                potential_company_headers.append(header_text)
    
    result['companies_in_headers'] = potential_company_headers
    
    # 5. Статистика
    result['statistics'] = {
        'total_headers': len(result['all_headers']),
        'total_tasks': len(result['tasks']),
        'tasks_with_companies': len([t for t in result['tasks'] if t['companies']]),
        'total_company_mentions': len(result['companies_in_blocks']),
        'potential_company_headers': len(potential_company_headers),
        'company_blocks_found': len(result['company_blocks_raw'])
    }
    
    return result

def analyze_all_md_files():
    """Анализирует все .md файлы в проекте"""
    
    # Находим все .md файлы
    md_files = []
    for root, dirs, files in os.walk('..'):
        for file in files:
            if file.endswith('.md'):
                md_files.append(os.path.join(root, file))
    
    print(f"🔍 Найдено .md файлов: {len(md_files)}")
    print("=" * 80)
    
    all_results = []
    all_companies = set()
    all_tasks = []
    
    for file_path in md_files:
        print(f"\n📄 Анализируем: {file_path}")
        result = extract_all_from_md_file(file_path)
        
        if result['tasks']:
            all_results.append(result)
            
            # Собираем все уникальные компании
            for company in result['companies_in_blocks']:
                all_companies.add(company.lower().strip())
            
            for company in result['companies_in_headers']:
                all_companies.add(company.lower().strip())
            
            # Собираем все задачи
            all_tasks.extend(result['tasks'])
            
            # Выводим статистику по файлу
            stats = result['statistics']
            print(f"   📊 Заголовков: {stats['total_headers']}")
            print(f"   📋 Задач: {stats['total_tasks']}")
            print(f"   🏢 Задач с компаниями: {stats['tasks_with_companies']}")
            print(f"   🔗 Упоминаний компаний: {stats['total_company_mentions']}")
            print(f"   🏪 Потенциальных компаний в заголовках: {stats['potential_company_headers']}")
    
    print("\n" + "=" * 80)
    print("📈 ОБЩАЯ СТАТИСТИКА:")
    print(f"   📄 Обработано файлов: {len(all_results)}")
    print(f"   📋 Всего задач: {len(all_tasks)}")
    print(f"   🏢 Задач с компаниями: {len([t for t in all_tasks if t['companies']])}")
    print(f"   🏪 Уникальных компаний: {len(all_companies)}")
    
    print(f"\n🏢 ВСЕ НАЙДЕННЫЕ КОМПАНИИ ({len(all_companies)}):")
    sorted_companies = sorted(list(all_companies))
    for i, company in enumerate(sorted_companies, 1):
        print(f"   {i:3d}. {company}")
    
    print(f"\n📋 ПРИМЕРЫ ЗАДАЧ С КОМПАНИЯМИ:")
    tasks_with_companies = [t for t in all_tasks if t['companies']][:20]  # Первые 20
    for i, task in enumerate(tasks_with_companies, 1):
        companies_str = ', '.join(task['companies'][:3])  # Первые 3 компании
        if len(task['companies']) > 3:
            companies_str += f" (и еще {len(task['companies']) - 3})"
        print(f"   {i:2d}. '{task['normalized_title']}' -> [{companies_str}]")
    
    # Сохраняем результаты в JSON для дальнейшего анализа
    output_data = {
        'summary': {
            'total_files': len(all_results),
            'total_tasks': len(all_tasks),
            'tasks_with_companies': len([t for t in all_tasks if t['companies']]),
            'unique_companies': len(all_companies)
        },
        'all_companies': sorted(list(all_companies)),
        'all_tasks': all_tasks,
        'file_results': all_results
    }
    
    with open('extraction_results.json', 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Результаты сохранены в 'extraction_results.json'")
    
    return output_data

if __name__ == "__main__":
    analyze_all_md_files() 