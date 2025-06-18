import re
import os

def analyze_md_files():
    """Анализ структуры .md файлов для понимания форматов компаний"""
    
    # Пути к файлам
    md_files = [
        '../react/Реакт Мини Апп.md',
        '../react/Реакт Ререндер.md', 
        '../react/Реакт Рефактор.md',
        '../react/Реакт Хуки.md',
        '../js/Основные задачи/массивы.md',
        '../js/Основные задачи/промисы.md',
        '../js/Основные задачи/строки.md',
        '../js/Основные задачи/числа.md'
    ]
    
    print("=== АНАЛИЗ СТРУКТУРЫ .MD ФАЙЛОВ ===\n")
    
    for file_path in md_files:
        if not os.path.exists(file_path):
            continue
            
        print(f"📁 Файл: {file_path}")
        print("-" * 50)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 1. Ищем заголовки задач
        task_headers = re.findall(r'^#+\s*(.+)$', content, re.MULTILINE)
        print(f"🔍 Найденные заголовки задач ({len(task_headers)}):")
        for i, header in enumerate(task_headers[:10]):  # Показываем первые 10
            print(f"   {i+1}. {header.strip()}")
        if len(task_headers) > 10:
            print(f"   ... и еще {len(task_headers) - 10} заголовков")
        
        # 2. Ищем блоки "встречалось в"
        company_blocks = re.findall(
            r'встречалось в.*?(?=\n\S|\n#+|\n```|\Z)', 
            content, 
            re.IGNORECASE | re.DOTALL
        )
        print(f"\n📋 Блоки 'встречалось в' ({len(company_blocks)}):")
        for i, block in enumerate(company_blocks):
            # Извлекаем компании из блока
            companies = []
            lines = block.split('\n')
            for line in lines[1:]:  # Пропускаем первую строку "встречалось в"
                line = line.strip()
                if line.startswith('-') or line.startswith('\t-'):
                    company = re.sub(r'^[\t\s]*-\s*', '', line).strip()
                    if company:
                        companies.append(company)
            
            print(f"   Блок {i+1}: {companies}")
        
        # 3. Ищем компании в заголовках (как в Реакт Ререндер.md)
        section_companies = []
        lines = content.split('\n')
        for line in lines:
            # Заголовки уровня 1-3, которые могут быть названиями компаний
            match = re.match(r'^#{1,3}\s*(.+)$', line)
            if match:
                header_text = match.group(1).strip()
                # Проверяем, похоже ли на название компании
                if (len(header_text) < 30 and 
                    not header_text.lower().startswith(('задач', 'example', 'пример', 'counter', 'todo'))):
                    section_companies.append(header_text)
        
        print(f"\n🏢 Потенциальные компании в заголовках ({len(section_companies)}):")
        for company in section_companies[:15]:  # Показываем первые 15
            print(f"   - {company}")
        
        # 4. Ищем вложенные заголовки с компаниями (### росбанк)
        subsection_companies = re.findall(r'^###\s*(.+)$', content, re.MULTILINE)
        print(f"\n🏪 Подзаголовки уровня 3 ({len(subsection_companies)}):")
        for company in subsection_companies[:10]:
            print(f"   - {company}")
        
        print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    analyze_md_files() 