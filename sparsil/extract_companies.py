#!/usr/bin/env python3
"""
Извлечение полного списка компаний из записей собеседований
Создает отсортированный список уникальных компаний
"""

import json
import re
from collections import Counter
from typing import List, Set, Tuple

def clean_company_name(name: str) -> str:
    """Очистка и нормализация названия компании"""
    if not name:
        return ""
    
    # Убираем лишние пробелы и переводы строк
    name = ' '.join(name.split())
    
    # Убираем кавычки и скобки в конце
    name = re.sub(r'["\'\(\)]*$', '', name)
    name = re.sub(r'^["\'\(\)]*', '', name)
    
    # Убираем лишние символы
    name = re.sub(r'[:\-\—\–]+$', '', name)
    name = re.sub(r'^[:\-\—\–]+', '', name)
    
    # Убираем "ООО", "ИП", "АО" и т.д.
    name = re.sub(r'\b(ООО|ИП|АО|ЗАО|ПАО|Ltd|LLC|Inc|Corp)\b\.?', '', name, flags=re.IGNORECASE)
    
    # Финальная очистка
    name = name.strip(' .,;:()[]{}"\'-')
    
    return name

def extract_company_patterns(text: str) -> List[str]:
    """Извлечение названий компаний по различным паттернам"""
    if not text:
        return []
    
    companies = []
    text = text.strip()
    
    # Паттерн 1: "Компания: Название"
    pattern1 = re.search(r'[Кк]омпания:\s*([^\n\r]+)', text)
    if pattern1:
        companies.append(pattern1.group(1).strip())
    
    # Паттерн 2: "Название компании - Название"  
    pattern2 = re.search(r'[Нн]азвание компании\s*[-:]\s*([^\n\r]+)', text)
    if pattern2:
        companies.append(pattern2.group(1).strip())
    
    # Паттерн 3: Первая строка (если содержит латиницу или известные слова)
    first_line = text.split('\n')[0].strip()
    if first_line and (
        re.search(r'[A-Za-z]', first_line) or 
        any(word in first_line.lower() for word in ['группа', 'банк', 'системы', 'технологии', 'студия'])
    ):
        companies.append(first_line)
    
    # Паттерн 4: Строки в начале, содержащие заглавные буквы
    lines = text.split('\n')[:5]  # Первые 5 строк
    for line in lines:
        line = line.strip()
        if (line and 
            len(line) < 80 and 
            len(line.split()) <= 6 and
            not line.startswith(('Вакансия', 'ЗП', 'Зарплата', 'Задач', 'Вопрос', 'http', 'https', 'tg:'))):
            companies.append(line)
    
    return companies

def extract_companies_from_records():
    """Основная функция извлечения компаний"""
    
    print("🏢 ИЗВЛЕЧЕНИЕ СПИСКА КОМПАНИЙ")
    print("=" * 40)
    
    # Загружаем данные
    try:
        with open('telegram_topic_messages.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ Файл telegram_topic_messages.json не найден!")
        return
    except json.JSONDecodeError as e:
        print(f"❌ Ошибка парсинга JSON: {e}")
        return
    
    messages = data.get('messages', [])
    print(f"📁 Загружено сообщений: {len(messages)}")
    
    # Фильтруем только записи собеседований
    interview_records = [
        msg for msg in messages 
        if msg.get('reply_to_msg_id') == 489 and 
           msg.get('text') and 
           len(msg['text'].strip()) > 10
    ]
    
    print(f"✔️ Записей собеседований: {len(interview_records)}")
    
    # Извлекаем компании
    all_companies = []
    processed_count = 0
    
    for record in interview_records:
        text = record.get('text', '')
        
        # Извлекаем возможные названия компаний
        candidates = extract_company_patterns(text)
        
        if candidates:
            # Берем лучший кандидат (обычно первый)
            best_candidate = candidates[0]
            cleaned = clean_company_name(best_candidate)
            
            if cleaned and len(cleaned) > 2 and len(cleaned) < 100:
                all_companies.append(cleaned)
                processed_count += 1
        else:
            # Если ничего не нашли - берем первые слова
            words = text.strip().split()[:3]
            if words:
                candidate = ' '.join(words)
                cleaned = clean_company_name(candidate)
                if cleaned and len(cleaned) > 2:
                    all_companies.append(cleaned)
                    processed_count += 1
    
    print(f"📊 Обработано записей: {processed_count}")
    print(f"📋 Извлечено названий: {len(all_companies)}")
    
    # Подсчет и очистка дубликатов
    company_counter = Counter(all_companies)
    unique_companies = sorted(company_counter.keys(), key=str.lower)
    
    print(f"🎯 Уникальных компаний: {len(unique_companies)}")
    
    # Группируем по типам
    english_companies = []
    russian_companies = []
    mixed_companies = []
    
    for company in unique_companies:
        if re.search(r'^[A-Za-z0-9\s\.\-\_]+$', company):
            english_companies.append(company)
        elif re.search(r'^[А-Яа-я0-9\s\.\-\_]+$', company):
            russian_companies.append(company)
        else:
            mixed_companies.append(company)
    
    # Выводим результаты
    print(f"\n📈 СТАТИСТИКА:")
    print(f"  🌍 Английские названия: {len(english_companies)}")
    print(f"  🇷🇺 Русские названия: {len(russian_companies)}")
    print(f"  🔀 Смешанные: {len(mixed_companies)}")
    
    # Полный список
    print(f"\n📋 ПОЛНЫЙ СПИСОК КОМПАНИЙ ({len(unique_companies)}):")
    print("-" * 50)
    
    for i, company in enumerate(unique_companies, 1):
        count = company_counter[company]
        print(f"{i:4d}. {company} ({count} упоминаний)")
    
    # Топ-20 самых упоминаемых
    print(f"\n🏆 ТОП-20 САМЫХ ПОПУЛЯРНЫХ:")
    print("-" * 40)
    
    top_companies = company_counter.most_common(20)
    for i, (company, count) in enumerate(top_companies, 1):
        print(f"{i:2d}. {company:<30} {count:3d} упоминаний")
    
    # Сохраняем в файл
    output_file = 'companies_list.txt'
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("ПОЛНЫЙ СПИСОК КОМПАНИЙ ИЗ ЗАПИСЕЙ СОБЕСЕДОВАНИЙ\n")
            f.write("=" * 60 + "\n\n")
            
            f.write(f"Всего уникальных компаний: {len(unique_companies)}\n")
            f.write(f"Английские названия: {len(english_companies)}\n")
            f.write(f"Русские названия: {len(russian_companies)}\n")
            f.write(f"Смешанные: {len(mixed_companies)}\n\n")
            
            f.write("АЛФАВИТНЫЙ СПИСОК:\n")
            f.write("-" * 30 + "\n")
            for i, company in enumerate(unique_companies, 1):
                count = company_counter[company]
                f.write(f"{i:4d}. {company} ({count})\n")
            
            f.write(f"\n\nТОП-20 ПОПУЛЯРНЫХ:\n")
            f.write("-" * 30 + "\n")
            for i, (company, count) in enumerate(top_companies, 1):
                f.write(f"{i:2d}. {company} - {count} упоминаний\n")
            
            # Группы по типам
            if english_companies:
                f.write(f"\n\nАНГЛИЙСКИЕ НАЗВАНИЯ ({len(english_companies)}):\n")
                f.write("-" * 30 + "\n")
                for company in english_companies:
                    f.write(f"• {company}\n")
            
            if russian_companies:
                f.write(f"\n\nРУССКИЕ НАЗВАНИЯ ({len(russian_companies)}):\n")
                f.write("-" * 30 + "\n")
                for company in russian_companies:
                    f.write(f"• {company}\n")
        
        print(f"\n✅ СПИСОК СОХРАНЕН: {output_file}")
        
    except Exception as e:
        print(f"\n❌ Ошибка сохранения: {e}")
    
    return unique_companies, company_counter

if __name__ == "__main__":
    companies, counter = extract_companies_from_records()
    print(f"\n🎉 ГОТОВО! Извлечено {len(companies)} уникальных компаний.") 