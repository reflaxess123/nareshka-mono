#!/usr/bin/env python3
"""
Анализ структуры ответов в Telegram API
Проверяем что означает reply_to и reply_to_msg_id
"""

import json
from collections import Counter

def analyze_reply_structure():
    """Анализ структуры ответов"""
    
    print("🔍 АНАЛИЗ СТРУКТУРЫ ОТВЕТОВ TELEGRAM API")
    print("=" * 60)
    
    # Загружаем данные
    with open('telegram_topic_messages.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    messages = data['messages']
    print(f"✔️ Всего сообщений: {len(messages)}")
    
    # Анализируем поле reply_to_msg_id
    print(f"\n📋 АНАЛИЗ ПОЛЯ reply_to_msg_id:")
    
    reply_to_counts = Counter()
    no_reply = 0
    reply_to_489 = 0
    reply_to_other = 0
    
    for msg in messages:
        reply_id = msg.get('reply_to_msg_id')
        if reply_id is None:
            no_reply += 1
        elif reply_id == 489:  # Прямой ответ на тему
            reply_to_489 += 1
        else:
            reply_to_other += 1
            reply_to_counts[reply_id] += 1
    
    print(f"  Без ответа (reply_to_msg_id = null): {no_reply}")
    print(f"  Ответ на тему 489: {reply_to_489}")
    print(f"  Ответ на другие сообщения: {reply_to_other}")
    
    # Показываем топ сообщений на которые отвечают
    if reply_to_other > 0:
        print(f"\n🔍 ТОП сообщений на которые отвечают:")
        for reply_id, count in reply_to_counts.most_common(10):
            # Ищем исходное сообщение
            original = next((m for m in messages if m['id'] == reply_id), None)
            if original:
                preview = original['text'][:100] if original['text'] else "без текста"
                print(f"  ID {reply_id}: {count} ответов")
                print(f"    Исходное: {preview}...")
            else:
                print(f"  ID {reply_id}: {count} ответов (исходное сообщение не найдено)")
    
    # Проверяем логику получения данных
    print(f"\n🤔 ЛОГИКА ПОЛУЧЕНИЯ ДАННЫХ:")
    print(f"Мы использовали: client.iter_messages(reply_to=489)")
    print(f"Это означает: получить сообщения где reply_to_msg_id = 489")
    print(f"")
    print(f"✔️ Сообщения с reply_to_msg_id = 489: {reply_to_489}")
    print(f"⚠️  Сообщения с reply_to_msg_id = другое: {reply_to_other}")
    print(f"❓ Сообщения без reply_to_msg_id: {no_reply}")
    
    if no_reply > 0:
        print(f"\n🔍 АНАЛИЗ СООБЩЕНИЙ БЕЗ REPLY_TO:")
        no_reply_examples = [m for m in messages if m.get('reply_to_msg_id') is None][:5]
        for i, msg in enumerate(no_reply_examples, 1):
            print(f"  {i}. ID {msg['id']}: {msg['text'][:100]}...")
    
    if reply_to_other > 0:
        print(f"\n🔍 АНАЛИЗ ОТВЕТОВ НА ДРУГИЕ СООБЩЕНИЯ:")
        other_reply_examples = [m for m in messages if m.get('reply_to_msg_id') and m.get('reply_to_msg_id') != 489][:5]
        for i, msg in enumerate(other_reply_examples, 1):
            print(f"  {i}. ID {msg['id']} отвечает на {msg['reply_to_msg_id']}")
            print(f"     Текст: {msg['text'][:100]}...")
    
    # Выводы
    print(f"\n📊 ВЫВОДЫ:")
    if reply_to_489 == len(messages):
        print(f"✔️ ВСЕ сообщения - прямые ответы на тему 489")
        print(f"✔️ Данные ЧИСТЫЕ - это записи собеседований")
    elif no_reply > 0 and reply_to_other == 0:
        print(f"⚠️ Есть сообщения без reply_to - возможно само сообщение темы")
        print(f"✔️ Нет ответов на ответы - данные относительно чистые")
    else:
        print(f"❌ Есть ответы на ответы - данные могут содержать обсуждения")
        print(f"❓ Требуется дополнительная фильтрация")

if __name__ == "__main__":
    analyze_reply_structure() 