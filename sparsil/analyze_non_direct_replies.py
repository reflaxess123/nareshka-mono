#!/usr/bin/env python3
"""
Детальный анализ сообщений которые не являются прямыми ответами на тему 489
"""

import json
from collections import Counter

def analyze_non_direct_replies():
    """Анализ непрямых ответов"""
    
    print("🔍 АНАЛИЗ НЕПРЯМЫХ ОТВЕТОВ")
    print("=" * 60)
    
    # Загружаем данные
    with open('telegram_topic_messages.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    messages = data['messages']
    
    # Фильтруем сообщения
    direct_replies = [m for m in messages if m.get('reply_to_msg_id') == 489]
    non_direct_replies = [m for m in messages if m.get('reply_to_msg_id') and m.get('reply_to_msg_id') != 489]
    
    print(f"✔️ Прямые ответы на тему 489: {len(direct_replies)}")
    print(f"⚠️ Ответы на другие сообщения: {len(non_direct_replies)}")
    
    # Анализируем на что отвечают
    reply_targets = Counter()
    for msg in non_direct_replies:
        reply_targets[msg['reply_to_msg_id']] += 1
    
    print(f"\n📊 СТАТИСТИКА ОТВЕТОВ:")
    for target_id, count in reply_targets.most_common():
        # Ищем исходное сообщение
        original = next((m for m in messages if m['id'] == target_id), None)
        if original:
            print(f"\n📌 Ответы на сообщение {target_id} ({count} раз):")
            print(f"   Исходное: {original['text'][:150]}...")
            
            # Показываем примеры ответов
            replies_to_this = [m for m in non_direct_replies if m['reply_to_msg_id'] == target_id]
            for i, reply in enumerate(replies_to_this[:2], 1):
                print(f"   Ответ {i}: {reply['text'][:100]}...")
        else:
            print(f"\n📌 Ответы на сообщение {target_id} ({count} раз) - исходное не найдено")
    
    # Проверяем временные паттерны
    print(f"\n📅 ВРЕМЕННОЙ АНАЛИЗ:")
    
    # Сравниваем даты
    from datetime import datetime
    
    direct_dates = []
    non_direct_dates = []
    
    for msg in direct_replies:
        if msg['date']:
            direct_dates.append(datetime.fromisoformat(msg['date'].replace('Z', '+00:00')))
    
    for msg in non_direct_replies:
        if msg['date']:
            non_direct_dates.append(datetime.fromisoformat(msg['date'].replace('Z', '+00:00')))
    
    if direct_dates and non_direct_dates:
        direct_dates.sort()
        non_direct_dates.sort()
        
        print(f"Прямые ответы: {direct_dates[0].strftime('%Y-%m-%d')} - {direct_dates[-1].strftime('%Y-%m-%d')}")
        print(f"Непрямые ответы: {non_direct_dates[0].strftime('%Y-%m-%d')} - {non_direct_dates[-1].strftime('%Y-%m-%d')}")
    
    # Анализируем содержание
    print(f"\n🔍 АНАЛИЗ СОДЕРЖАНИЯ НЕПРЯМЫХ ОТВЕТОВ:")
    
    # Проверяем ключевые слова
    non_direct_text = ' '.join([msg['text'].lower() for msg in non_direct_replies if msg['text']])
    
    # Слова характерные для обсуждений vs записей собеседований
    discussion_words = ['спасибо', 'согласен', 'да', 'нет', 'тоже', 'у меня', 'а я']
    interview_words = ['компания', 'собеседование', 'вакансия', 'зарплата', 'вопрос', 'задача']
    
    print(f"Слова обсуждений:")
    for word in discussion_words:
        count = non_direct_text.count(word)
        if count > 0:
            print(f"  '{word}': {count}")
    
    print(f"Слова записей собеседований:")
    for word in interview_words:
        count = non_direct_text.count(word)
        if count > 0:
            print(f"  '{word}': {count}")
    
    # Рекомендации
    print(f"\n📋 РЕКОМЕНДАЦИИ:")
    
    discussion_score = sum(non_direct_text.count(w) for w in discussion_words)
    interview_score = sum(non_direct_text.count(w) for w in interview_words)
    
    print(f"Счет 'обсуждения': {discussion_score}")
    print(f"Счет 'записи собеседований': {interview_score}")
    
    if interview_score > discussion_score:
        print(f"✔️ Непрямые ответы тоже содержат записи собеседований")
        print(f"✔️ Можно включить в финальный датасет")
    else:
        print(f"❌ Непрямые ответы содержат больше обсуждений")
        print(f"⚠️ Лучше использовать только прямые ответы")
    
    return direct_replies, non_direct_replies

if __name__ == "__main__":
    analyze_non_direct_replies() 