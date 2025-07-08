#!/usr/bin/env python3
"""
Анализ чистых записей собеседований
"""

import json
from datetime import datetime
from collections import Counter

def analyze_clean_records():
    """Анализ структуры и хронологии записей"""
    
    print("📊 АНАЛИЗ ЧИСТЫХ ЗАПИСЕЙ СОБЕСЕДОВАНИЙ")
    print("=" * 60)
    
    # Загружаем данные
    with open('telegram_topic_messages.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    messages = data['messages']
    print(f"✔️ Загружено сообщений: {len(messages)}")
    
    # Хронология
    print(f"\n📅 ХРОНОЛОГИЯ:")
    print(f"Самое старое: {messages[-1]['date']} (ID={messages[-1]['id']})")
    print(f"Самое новое: {messages[0]['date']} (ID={messages[0]['id']})")
    
    # Парсим даты
    dates = []
    for msg in messages:
        if msg['date']:
            dates.append(datetime.fromisoformat(msg['date'].replace('Z', '+00:00')))
    
    dates.sort()
    print(f"Период: {dates[0].strftime('%Y-%m-%d')} — {dates[-1].strftime('%Y-%m-%d')}")
    print(f"Длительность: {(dates[-1] - dates[0]).days} дней")
    
    # Анализ по месяцам
    print(f"\n📈 РАСПРЕДЕЛЕНИЕ ПО МЕСЯЦАМ:")
    monthly = Counter()
    for date in dates:
        month_key = date.strftime('%Y-%m')
        monthly[month_key] += 1
    
    for month, count in sorted(monthly.items()):
        print(f"  {month}: {count} записей")
    
    # Проверяем структуру сообщений
    print(f"\n🔍 СТРУКТУРА СООБЩЕНИЙ:")
    
    # Длина текстов
    text_lengths = [len(msg['text']) for msg in messages if msg['text']]
    avg_length = sum(text_lengths) / len(text_lengths)
    
    print(f"Средняя длина текста: {avg_length:.0f} символов")
    print(f"Самый короткий: {min(text_lengths)} символов")
    print(f"Самый длинный: {max(text_lengths)} символов")
    
    # Примеры коротких и длинных сообщений
    print(f"\n📝 ПРИМЕРЫ ЗАПИСЕЙ:")
    
    # Короткое сообщение
    short_msg = min(messages, key=lambda x: len(x['text']) if x['text'] else 999999)
    print(f"\n🔸 Короткое сообщение ({len(short_msg['text'])} символов):")
    print(f"  Дата: {short_msg['date']}")
    print(f"  Текст: {short_msg['text'][:200]}...")
    
    # Длинное сообщение
    long_msg = max(messages, key=lambda x: len(x['text']) if x['text'] else 0)
    print(f"\n🔸 Длинное сообщение ({len(long_msg['text'])} символов):")
    print(f"  Дата: {long_msg['date']}")
    print(f"  Текст: {long_msg['text'][:200]}...")
    
    # Поиск ключевых слов
    print(f"\n🔍 АНАЛИЗ СОДЕРЖАНИЯ:")
    
    all_text = ' '.join([msg['text'].lower() for msg in messages if msg['text']])
    
    keywords = [
        'компания', 'вакансия', 'зарплата', 'собеседование', 
        'задача', 'вопрос', 'react', 'vue', 'javascript', 'typescript',
        'опыт', 'проект', 'команда'
    ]
    
    for keyword in keywords:
        count = all_text.count(keyword)
        if count > 10:
            print(f"  '{keyword}': {count} упоминаний")
    
    print(f"\n✔️ ИТОГО: {len(messages)} чистых записей собеседований")
    print(f"   с {dates[0].strftime('%Y-%m-%d')} по {dates[-1].strftime('%Y-%m-%d')}")

if __name__ == "__main__":
    analyze_clean_records() 