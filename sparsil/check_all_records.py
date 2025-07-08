#!/usr/bin/env python3
"""
Проверка полноты записей собеседований
Действительно ли мы получили ВСЕ записи?
"""

import json
import re
from collections import Counter

def check_all_records():
    """Проверка полноты записи собеседований"""
    
    print("🔍 ПРОВЕРКА ПОЛНОТЫ ЗАПИСЕЙ СОБЕСЕДОВАНИЙ")
    print("=" * 60)
    
    # Загружаем данные
    with open('telegram_topic_messages.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    messages = data['messages']
    
    # Разделяем сообщения
    direct_replies = [m for m in messages if m.get('reply_to_msg_id') == 489]
    non_direct_replies = [m for m in messages if m.get('reply_to_msg_id') and m.get('reply_to_msg_id') != 489]
    
    print(f"📊 ТЕКУЩИЕ ДАННЫЕ:")
    print(f"  Прямые ответы на 489: {len(direct_replies)}")
    print(f"  Ответы на другие: {len(non_direct_replies)}")
    print(f"  Всего: {len(messages)}")
    
    # Ищем само сообщение темы 489
    topic_message = next((m for m in messages if m['id'] == 489), None)
    if topic_message:
        print(f"\n📋 СООБЩЕНИЕ ТЕМЫ 489:")
        print(f"  Дата: {topic_message['date']}")
        print(f"  Текст: {topic_message['text'][:200]}...")
    else:
        print(f"\n❌ СООБЩЕНИЕ ТЕМЫ 489 НЕ НАЙДЕНО!")
        print(f"   Это означает что мы НЕ получили все сообщения темы")
    
    # Анализируем 173 "обсуждения" на предмет записей собеседований
    print(f"\n🔍 ПРОВЕРКА 173 'ОБСУЖДЕНИЙ' НА ЗАПИСИ СОБЕСЕДОВАНИЙ:")
    
    # Маркеры записей собеседований
    interview_markers = [
        r'компания[:\-\s]',
        r'название компании[:\-\s]',
        r'вакансия[:\-\s]',
        r'зп[:\-\s]',
        r'зарплата[:\-\s]',
        r'вопросы[:\-\s]',
        r'задач[аи][:\-\s]',
        r'собеседование',
        r'собес',
        r'этап[:\-\s]',
        r'успех[:\-\s]'
    ]
    
    potential_records = []
    
    for msg in non_direct_replies:
        text = msg['text'].lower()
        marker_count = 0
        
        for marker in interview_markers:
            if re.search(marker, text):
                marker_count += 1
        
        # Если найдено 2+ маркера - возможно это запись собеседования
        if marker_count >= 2:
            potential_records.append({
                'message': msg,
                'markers': marker_count,
                'reply_to': msg['reply_to_msg_id']
            })
    
    print(f"  Найдено потенциальных записей: {len(potential_records)}")
    
    if potential_records:
        print(f"\n📝 ПОТЕНЦИАЛЬНЫЕ ЗАПИСИ В 'ОБСУЖДЕНИЯХ':")
        for i, record in enumerate(potential_records[:5], 1):
            msg = record['message']
            print(f"  {i}. ID {msg['id']} (ответ на {record['reply_to']}, маркеров: {record['markers']})")
            print(f"     Дата: {msg['date']}")
            print(f"     Текст: {msg['text'][:150]}...")
            print()
    
    # Проверяем есть ли записи которые отвечают на записи
    print(f"\n🔗 ПРОВЕРКА ЦЕПОЧЕК ЗАПИСЕЙ:")
    
    # ID всех прямых записей
    direct_record_ids = set(m['id'] for m in direct_replies)
    
    # Ищем сообщения которые отвечают на прямые записи
    replies_to_records = []
    for msg in non_direct_replies:
        if msg['reply_to_msg_id'] in direct_record_ids:
            replies_to_records.append(msg)
    
    print(f"  Ответов на записи собеседований: {len(replies_to_records)}")
    
    if replies_to_records:
        print(f"\n📝 ОТВЕТЫ НА ЗАПИСИ СОБЕСЕДОВАНИЙ:")
        for i, msg in enumerate(replies_to_records[:3], 1):
            # Находим исходную запись
            original = next(m for m in direct_replies if m['id'] == msg['reply_to_msg_id'])
            print(f"  {i}. ID {msg['id']} отвечает на запись {msg['reply_to_msg_id']}")
            print(f"     Исходная запись: {original['text'][:100]}...")
            print(f"     Ответ: {msg['text'][:100]}...")
            print()
    
    # Оценка полноты
    print(f"\n📊 ОЦЕНКА ПОЛНОТЫ ДАННЫХ:")
    
    missed_records = len(potential_records)
    total_estimated = len(direct_replies) + missed_records
    
    print(f"  ✔️ Прямые записи: {len(direct_replies)}")
    print(f"  ❓ Возможно пропущено: {missed_records}")
    print(f"  📈 Оценочно всего: {total_estimated}")
    print(f"  📊 Полнота: {len(direct_replies)/total_estimated*100:.1f}%")
    
    # Рекомендации
    print(f"\n💡 РЕКОМЕНДАЦИИ:")
    
    if missed_records == 0 and topic_message:
        print(f"  ✔️ Скорее всего получены ВСЕ записи собеседований")
        print(f"  ✔️ Данные можно считать полными")
    elif missed_records > 0:
        print(f"  ⚠️ Возможно пропущено {missed_records} записей")
        print(f"  💡 Рекомендуется дополнительная проверка")
        print(f"  💡 Можно попробовать другие методы парсинга")
    
    if not topic_message:
        print(f"  ❌ Сообщение темы 489 отсутствует")
        print(f"  ❌ Данные НЕПОЛНЫЕ - нужно улучшить парсинг")
    
    return len(direct_replies), missed_records

if __name__ == "__main__":
    check_all_records() 