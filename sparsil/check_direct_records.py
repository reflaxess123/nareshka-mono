#!/usr/bin/env python3
"""
Проверка прямых записей собеседований
Записи = либо без ответа, либо ответ на тему 489
"""

import json

def check_direct_records():
    """Анализ прямых записей собеседований"""
    
    print("🔍 АНАЛИЗ ПРЯМЫХ ЗАПИСЕЙ СОБЕСЕДОВАНИЙ")
    print("=" * 60)
    
    # Загружаем данные
    with open('telegram_topic_messages.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    messages = data['messages']
    
    # Классификация сообщений
    no_reply = []           # reply_to_msg_id = null
    reply_to_topic = []     # reply_to_msg_id = 489
    reply_to_others = []    # reply_to_msg_id = другое
    
    for msg in messages:
        reply_id = msg.get('reply_to_msg_id')
        
        if reply_id is None:
            no_reply.append(msg)
        elif reply_id == 489:
            reply_to_topic.append(msg)
        else:
            reply_to_others.append(msg)
    
    print(f"📊 КЛАССИФИКАЦИЯ СООБЩЕНИЙ:")
    print(f"  Без ответа (прямые): {len(no_reply)}")
    print(f"  Ответ на тему 489: {len(reply_to_topic)}")  
    print(f"  Ответы на другие: {len(reply_to_others)}")
    print(f"  Всего: {len(messages)}")
    
    # Прямые записи = без ответа + ответы на тему
    direct_records = no_reply + reply_to_topic
    
    print(f"\n✔️ ПРЯМЫЕ ЗАПИСИ СОБЕСЕДОВАНИЙ: {len(direct_records)}")
    print(f"   = {len(no_reply)} без ответа + {len(reply_to_topic)} ответов на тему")
    
    # Показываем примеры каждой категории
    if no_reply:
        print(f"\n📝 ПРИМЕРЫ СООБЩЕНИЙ БЕЗ ОТВЕТА:")
        for i, msg in enumerate(no_reply[:3], 1):
            print(f"  {i}. ID {msg['id']}, дата: {msg['date']}")
            print(f"     Текст: {msg['text'][:150]}...")
            print()
    else:
        print(f"\n❌ Сообщений без ответа НЕТ")
        print(f"   Возможно парсер получил только ответы, но не прямые сообщения темы")
    
    if reply_to_topic:
        print(f"\n📝 ПРИМЕРЫ ОТВЕТОВ НА ТЕМУ 489:")
        for i, msg in enumerate(reply_to_topic[:3], 1):
            print(f"  {i}. ID {msg['id']}, дата: {msg['date']}")
            print(f"     Текст: {msg['text'][:150]}...")
            print()
    
    # Анализ временного распределения
    from datetime import datetime
    
    if direct_records:
        dates = []
        for msg in direct_records:
            if msg['date']:
                dates.append(datetime.fromisoformat(msg['date'].replace('Z', '+00:00')))
        
        dates.sort()
        print(f"\n📅 ВРЕМЕННОЕ РАСПРЕДЕЛЕНИЕ ПРЯМЫХ ЗАПИСЕЙ:")
        print(f"   Период: {dates[0].strftime('%Y-%m-%d')} — {dates[-1].strftime('%Y-%m-%d')}")
        print(f"   Длительность: {(dates[-1] - dates[0]).days} дней")
    
    # Проверяем что мы используем правильный метод
    print(f"\n🤔 АНАЛИЗ МЕТОДА ПАРСИНГА:")
    print(f"   Использовали: client.iter_messages(reply_to=489)")
    print(f"   Получили: только сообщения с reply_to_msg_id = 489")
    print(f"   НЕ получили: сообщения без reply_to_msg_id (прямые сообщения темы)")
    
    if len(no_reply) == 0:
        print(f"\n❌ ПРОБЛЕМА: Нет сообщений без reply_to")
        print(f"   Это означает что мы НЕ получили прямые сообщения темы")
        print(f"   Нужен другой метод парсинга для получения ВСЕХ сообщений темы")
    else:
        print(f"\n✔️ Данные полные: есть и прямые сообщения и ответы")
    
    # Итоговая рекомендация
    print(f"\n📋 ИТОГОВЫЙ АНАЛИЗ:")
    print(f"   📊 Прямые записи собеседований: {len(direct_records)}")
    print(f"   📊 Ответы/обсуждения: {len(reply_to_others)}")
    
    if len(no_reply) == 0:
        print(f"   ❌ Данные НЕПОЛНЫЕ - отсутствуют прямые сообщения темы")
        print(f"   💡 Нужно использовать другой API метод")
    else:
        print(f"   ✔️ Данные корректные - есть прямые записи")
    
    return len(direct_records), len(reply_to_others)

if __name__ == "__main__":
    check_direct_records() 