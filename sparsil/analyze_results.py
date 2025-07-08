#!/usr/bin/env python3
"""Анализ результатов парсинга сообщений из темы 'Записи собеседований'"""

import json
from datetime import datetime
from collections import Counter
import re

def analyze_telegram_data():
    """Анализирует данные из telegram_topic_messages.json"""
    
    # Загружаем данные
    with open('telegram_topic_messages.json', encoding='utf-8') as f:
        data = json.load(f)
    
    messages = data['messages']
    metadata = data['metadata']
    
    print("=" * 60)
    print("📊 АНАЛИЗ РЕЗУЛЬТАТОВ ПАРСИНГА")
    print("=" * 60)
    
    # Основная статистика
    print(f"📁 Тема: {metadata['topic_name']}")
    print(f"🆔 Topic ID: {metadata['topic_id']}")
    print(f"📊 Всего сообщений: {metadata['total_messages']}")
    print(f"📅 Дата парсинга: {metadata['extraction_date']}")
    
    # Временной период
    if messages:
        first_date = messages[-1]['date']  # Самое старое
        last_date = messages[0]['date']    # Самое новое
        print(f"📅 Период: с {first_date} по {last_date}")
    
    print("\n" + "=" * 60)
    print("🏢 АНАЛИЗ КОМПАНИЙ")
    print("=" * 60)
    
    # Поиск сообщений с компаниями
    companies = []
    company_pattern = r'Компания[:\s]+([^\n]+)'
    
    for msg in messages:
        text = msg['text']
        match = re.search(company_pattern, text, re.IGNORECASE)
        if match:
            company = match.group(1).strip()
            companies.append(company)
    
    print(f"💼 Сообщений с компаниями: {len(companies)}")
    print(f"📈 Уникальных компаний: {len(set(companies))}")
    
    # Топ компаний
    if companies:
        company_counts = Counter(companies)
        print(f"\n🏆 ТОП-10 КОМПАНИЙ:")
        for i, (company, count) in enumerate(company_counts.most_common(10), 1):
            print(f"  {i:2d}. {company} ({count} раз)")
    
    print("\n" + "=" * 60)
    print("💰 АНАЛИЗ ЗАРПЛАТ")
    print("=" * 60)
    
    # Поиск зарплатных вилок
    salary_patterns = [
        r'[Вв]илка[:\s]+([^\n]+)',
        r'[Зз]арплата[:\s]+([^\n]+)',
        r'(\d{2,3})[к\s]*[-–]\s*(\d{2,3})[к\s]*[тыс]*',
        r'(\d{2,3})\s*[к]*\s*[тыс]*'
    ]
    
    salaries = []
    for msg in messages:
        text = msg['text']
        for pattern in salary_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            salaries.extend(matches)
    
    print(f"💰 Упоминаний зарплат: {len(salaries)}")
    
    # Анализ зарплатных диапазонов
    salary_numbers = []
    for salary in salaries:
        if isinstance(salary, tuple):
            # Диапазон зарплат
            try:
                min_sal = int(re.search(r'\d+', str(salary[0])).group())
                max_sal = int(re.search(r'\d+', str(salary[1])).group())
                salary_numbers.extend([min_sal, max_sal])
            except:
                pass
        else:
            # Одиночное значение
            nums = re.findall(r'\d{2,3}', str(salary))
            salary_numbers.extend([int(n) for n in nums])
    
    if salary_numbers:
        print(f"💵 Минимальная зарплата: {min(salary_numbers)}k")
        print(f"💵 Максимальная зарплата: {max(salary_numbers)}k")
        print(f"💵 Средняя зарплата: {sum(salary_numbers)/len(salary_numbers):.1f}k")
    
    print("\n" + "=" * 60)
    print("👥 АНАЛИЗ АВТОРОВ")
    print("=" * 60)
    
    # Авторы сообщений
    authors = [msg['from_username'] for msg in messages if msg.get('from_username')]
    author_counts = Counter(authors)
    
    print(f"👤 Всего авторов: {len(set(authors))}")
    print(f"📝 Среднее сообщений на автора: {len(messages)/len(set(authors)):.1f}")
    
    print(f"\n🏆 ТОП-10 АКТИВНЫХ АВТОРОВ:")
    for i, (author, count) in enumerate(author_counts.most_common(10), 1):
        print(f"  {i:2d}. @{author} ({count} сообщений)")
    
    print("\n" + "=" * 60)
    print("🔍 ПРИМЕРЫ СООБЩЕНИЙ")
    print("=" * 60)
    
    # Показываем несколько примеров
    for i, msg in enumerate(messages[:3]):
        print(f"\n📝 Сообщение #{i+1} (ID: {msg['id']}):")
        print(f"📅 Дата: {msg['date']}")
        print(f"👤 Автор: @{msg.get('from_username', 'unknown')}")
        print(f"💬 Текст: {msg['text'][:200]}{'...' if len(msg['text']) > 200 else ''}")
        print("-" * 40)
    
    print("\n🎉 АНАЛИЗ ЗАВЕРШЕН!")
    print(f"📄 Полные данные доступны в: telegram_topic_messages.json")
    print(f"📊 CSV для анализа: telegram_topic_messages.csv")

if __name__ == "__main__":
    analyze_telegram_data() 