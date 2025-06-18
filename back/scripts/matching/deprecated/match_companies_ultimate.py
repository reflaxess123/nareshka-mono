import re
import os
import sys
from difflib import SequenceMatcher

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..' )))

from app.database import get_db
from app.models import ContentBlock

def normalize_title_ultimate(title: str) -> str:
    """Максимально точная нормализация заголовков"""
    # Удаляем markdown ссылки [text](url) -> text  
    title = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', title)
    
    # Удаляем номера в начале: "1. title", "22. title" -> "title"
    title = re.sub(r'^\d+\.\s*', '', title)
    
    # Удаляем специальные символы markdown
    title = re.sub(r'[#\-\*\+\[\]`]', '', title)
    
    # Приводим к lowercase и убираем лишние пробелы
    title = re.sub(r'\s+', ' ', title.lower().strip())
    
    return title

def similarity(a: str, b: str) -> float:
    """Вычисляет схожесть строк от 0 до 1"""
    return SequenceMatcher(None, a, b).ratio()

def extract_companies_comprehensive(text: str, context: str = "") -> list[str]:
    """Всесторонний парсинг компаний из текста"""
    companies = []
    
    # Предварительный список известных компаний для более точного извлечения
    KNOWN_COMPANIES = {
        'яндекс', 'сбер', 'тинкофф', 'лемма', 'wb', 'иннотех', 'отп', 'газпром', 
        'profsoft', 'altenar', 'it-one', 'сбертех', 'альфа', 'вк', 'автомакон', 
        'мойсклад', 'цезио', 'qugo', 'ibs', 'росбанк', 'ооо мобайлдевелопмент', 
        'сибур', 'гк т1', 'билайн', 'kotelov', 'unisender', 'озон', 'поле.рф', 
        'artw', 'авито', 'realweb', 'itfb', 'киберлаб', 'portalbilet', 'marpla',
        'росгосстрах', 'right line', 'quantum art', 'аласкар технологии', 'селекти',
        'алфабанк', 'промсвязьбанк', 'сбердевайсы', 'funbox', 'цум', 'it baltic',
        'cберкорус', 'рутуб', 'евротехклимат', 'luxsoft', 'tilda', 'промсвязьбанк (псб)',
        'антара', 'втб через нетбелл акр лабс', 'sber autotech', 'финам',
        'баланс платформа', 'лаб касп', 'яндекс такси', 'click2money', 'kts',
        'premium it solution', 'moex', 'eesee', 'дом.рф', 'лига цифровой экономики',
        'вб', 'яндекс про', 'coding team', 'ютэир', 'goinvest', 'сбер', 'yandex.pay',
        'yandex.multitrack', 'баум', 'кокос.group', 'ип свистунова екатерина александровна (сбер)',
        'сквад (squad)', 'точка банк', 'strahovaya kompaniya puls', 'vision', 'itq group (proekt mkb)',
        'sbertech', 'онлайн школа тетрика', 'сфера', 'yandex', 'mail.ru group', 'kaspersky', 'райфайзен'
    }
    
    # 1. Извлечение из блоков "встречалось в" с улучшенным парсингом
    company_blocks = re.findall(
        r'встречал[аось]+ в.*?(?=\n\S|\n#+|\n```|\Z)', 
        text, 
        re.IGNORECASE | re.DOTALL
    )
    
    for block in company_blocks:
        lines = block.split('\n')
        for line in lines[1:]:  # Пропускаем первую строку "встречалось в"
            # Убираем табуляцию и пробелы в начале
            cleaned_line = re.sub(r'^[\t\s]*-\s*', '', line).strip()
            if cleaned_line and len(cleaned_line) > 1:
                # Фильтруем мусор и добавляем только известные компании
                normalized_company = cleaned_line.lower()
                # Добавляем дополнительные нормализации
                normalized_company = normalized_company.replace('(нельзя копировать массив, то есть inplace)', '').strip()
                normalized_company = normalized_company.replace('(без set, сказать сложность, будет ли set работать с объектами)', '').strip()
                normalized_company = normalized_company.replace('(проект мтс)', '').strip()
                normalized_company = normalized_company.replace('(platform v ui kits)', '').strip()
                normalized_company = normalized_company.replace('(псб)', '').strip()
                normalized_company = normalized_company.replace('(ограничение o(1))', '').strip()
                normalized_company = normalized_company.replace('(проект мкб)', '').strip()
                normalized_company = normalized_company.replace('через нетбелл акр лабс', '').strip()
                normalized_company = normalized_company.replace('для экспертов', '').strip()
                normalized_company = normalized_company.replace('свистунова екатерина александровна', '').strip()
                normalized_company = normalized_company.replace('групп', '').strip()
                normalized_company = normalized_company.replace('auto tech', 'autotech').strip()
                
                if normalized_company in KNOWN_COMPANIES or \
                   any(comp in normalized_company for comp in KNOWN_COMPANIES): # Проверяем вхождение
                    companies.append(normalized_company)
    
    # 2. Извлечение компаний из заголовков (# компания)
    header_companies = re.findall(r'^#{1,3}\s*([^#\n]+)$', text, re.MULTILINE)
    
    for company in header_companies:
        company_text = company.strip().lower()
        # Проверяем, содержится ли название компании из KNOWN_COMPANIES в заголовке
        for known_company in KNOWN_COMPANIES:
            if known_company in company_text and len(known_company) > 1 and \
               not re.match(r'(задач|example|пример|counter|todo|списки|рефактор|тренировочные|other|use|module)', company_text, re.IGNORECASE):
                companies.append(known_company)
    
    # 3. Чистка и дедупликация
    cleaned_companies = []
    for company in companies:
        company = company.strip().replace(' ', '') # Убираем пробелы для лучшей дедупликации
        if company and company not in cleaned_companies:
            cleaned_companies.append(company)
    
    return cleaned_companies

def parse_md_file_advanced(file_path: str) -> dict:
    """Продвинутый парсинг .md файла с извлечением задач и компаний"""
    if not os.path.exists(file_path):
        return {}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    tasks = {}
    
    # Разбиваем на секции по заголовкам
    sections = re.split(r'(^#{1,4}\s+.+)$', content, flags=re.MULTILINE)
    
    current_title = None
    current_content = ""
    
    for section in sections:
        if re.match(r'^#{1,4}\s+', section):
            # Сохраняем предыдущую секцию
            if current_title and current_content:
                normalized_title = normalize_title_ultimate(current_title)
                companies = extract_companies_comprehensive(current_content, file_path)
                
                if normalized_title and (companies or len(current_content) > 50):
                    tasks[normalized_title] = {
                        'original_title': current_title,
                        'companies': companies,
                        'content': current_content[:500]  # Первые 500 символов для отладки
                    }
            
            # Начинаем новую секцию
            current_title = re.sub(r'^#+\s*', '', section).strip()
            current_content = ""
        else:
            current_content += section
    
    # Обрабатываем последнюю секцию
    if current_title and current_content:
        normalized_title = normalize_title_ultimate(current_title)
        companies = extract_companies_comprehensive(current_content, file_path)
        
        if normalized_title and (companies or len(current_content) > 50):
            tasks[normalized_title] = {
                'original_title': current_title,
                'companies': companies,
                'content': current_content[:500]
            }
    
    return tasks

def match_and_update_ultimate():
    """Максимально точное сопоставление и обновление"""
    
    # Путь к .md файлам
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
    
    # Собираем все задачи из .md файлов
    all_md_tasks = {}
    
    print("🔍 Парсинг .md файлов...")
    for file_path in md_files:
        if os.path.exists(file_path):
            print(f"  📄 {file_path}")
            tasks = parse_md_file_advanced(file_path)
            all_md_tasks.update(tasks)
            print(f"     Найдено задач: {len(tasks)}")
    
    print(f"\n📊 Всего задач в .md файлах: {len(all_md_tasks)}")
    
    # Подключаемся к БД
    db = next(get_db())
    
    try:
        # Получаем все задачи из БД
        db_tasks = db.query(ContentBlock).all()
        print(f"📊 Всего задач в БД: {len(db_tasks)}")
        
        matched_count = 0
        company_updates = 0
        
        print("\n🔗 Сопоставление задач...")
        
        for db_task in db_tasks:
            if not db_task.blockTitle:
                continue
                
            normalized_db_title = normalize_title_ultimate(db_task.blockTitle)
            best_match = None
            best_score = 0
            
            # Ищем лучшее совпадение
            for md_title, md_data in all_md_tasks.items():
                score = similarity(normalized_db_title, md_title)
                
                # Точное совпадение
                if score >= 0.9:
                    best_match = md_data
                    best_score = score
                    break
                # Частичное совпадение
                elif score > best_score and score >= 0.7:
                    best_match = md_data
                    best_score = score
                # Проверка на содержание одного в другом
                elif (md_title in normalized_db_title or 
                      normalized_db_title in md_title) and score >= 0.5:
                    best_match = md_data
                    best_score = score
            
            # Обновляем компании если нашли совпадение
            if best_match and best_match['companies']:
                # Убираем дубликаты и очищаем компании
                unique_companies = []
                for company in best_match['companies']:
                    if company not in unique_companies:
                        unique_companies.append(company)
                
                db_task.companies = unique_companies
                company_updates += 1
                matched_count += 1
                
                print(f"  ✅ '{db_task.blockTitle}' -> {unique_companies} (score: {best_score:.2f})")
            
            elif best_match:
                matched_count += 1
                print(f"  📝 '{db_task.blockTitle}' -> сопоставлена, но без компаний (score: {best_score:.2f})")
        
        # Сохраняем изменения
        if company_updates > 0:
            db.commit()
            print(f"\n💾 Обновлено записей в БД: {company_updates}")
        else:
            print("\n⚠️ Нет записей для обновления")
        
        print(f"\n📈 ИТОГИ:")
        print(f"   🎯 Сопоставлено задач: {matched_count}/{len(db_tasks)}")
        print(f"   🏢 Задач с компаниями: {company_updates}")
        print(f"   📊 Процент покрытия: {(company_updates/len(db_tasks)*100):.1f}%")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    match_and_update_ultimate() 