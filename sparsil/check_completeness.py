#!/usr/bin/env python3
"""Проверка полноты извлеченных данных из темы"""

import json
import sys
from pathlib import Path

# Добавляем путь к mcp-telegram модулю
sys.path.insert(0, str(Path("mcp-telegram-main/src").resolve()))

from mcp_telegram.tools import ListTopicMessages, tool_runner
from mcp_telegram.telegram import create_client
import asyncio

async def check_data_completeness():
    """Проверяет полноту извлеченных данных"""
    
    # Загружаем наши данные
    with open('telegram_topic_messages.json', encoding='utf-8') as f:
        data = json.load(f)
    
    messages = data['messages']
    
    print("🔍 ПРОВЕРКА ПОЛНОТЫ ДАННЫХ")
    print("=" * 60)
    
    print(f"📊 Извлечено сообщений: {len(messages)}")
    print(f"🔢 Первое (новейшее) сообщение: ID={messages[0]['id']}, дата={messages[0]['date']}")
    print(f"🔢 Последнее (старейшее) сообщение: ID={messages[-1]['id']}, дата={messages[-1]['date']}")
    
    # Анализ ID сообщений
    message_ids = [msg['id'] for msg in messages]
    print(f"📈 Диапазон ID: {min(message_ids)} - {max(message_ids)}")
    print(f"🔍 Пропуски в ID: {max(message_ids) - min(message_ids) + 1 - len(message_ids)}")
    
    # Проверяем, есть ли еще более старые сообщения
    print(f"\n🔍 ПРОВЕРКА БОЛЕЕ СТАРЫХ СООБЩЕНИЙ:")
    print("Попробуем получить сообщения старше последнего...")
    
    DIALOG_ID = -1002071074234
    TOPIC_ID = 489
    oldest_id = min(message_ids)
    
    try:
        # Используем прямой доступ к Telethon для более точной проверки
        async with create_client() as client:
            # Пробуем получить сообщения старше нашего oldest_id
            older_messages = []
            async for message in client.iter_messages(
                entity=DIALOG_ID,
                limit=50,
                offset_id=oldest_id - 1,  # Начинаем с ID меньше самого старого
                reply_to=TOPIC_ID
            ):
                if message.text:
                    older_messages.append({
                        'id': message.id,
                        'date': message.date.isoformat() if message.date else None,
                        'text': message.text[:100] + '...' if len(message.text) > 100 else message.text
                    })
            
            print(f"📜 Найдено более старых сообщений: {len(older_messages)}")
            
            if older_messages:
                print(f"⚠️  ВНИМАНИЕ: Есть более старые сообщения!")
                print(f"🔢 Самое старое найденное: ID={older_messages[-1]['id']}, дата={older_messages[-1]['date']}")
                
                # Показываем примеры
                print(f"\n📋 ПРИМЕРЫ ПРОПУЩЕННЫХ СООБЩЕНИЙ:")
                for i, msg in enumerate(older_messages[:5]):
                    print(f"  {i+1}. ID={msg['id']}: {msg['text']}")
                
                return False  # Данные неполные
            else:
                print(f"✅ Более старых сообщений не найдено")
                
    except Exception as e:
        print(f"❌ Ошибка при проверке: {e}")
        
    # Проверяем более новые сообщения
    print(f"\n🔍 ПРОВЕРКА БОЛЕЕ НОВЫХ СООБЩЕНИЙ:")
    newest_id = max(message_ids)
    
    try:
        async with create_client() as client:
            newer_messages = []
            async for message in client.iter_messages(
                entity=DIALOG_ID,
                limit=50,
                max_id=newest_id + 100,  # Ищем сообщения новее
                reply_to=TOPIC_ID
            ):
                if message.text and message.id > newest_id:
                    newer_messages.append({
                        'id': message.id,
                        'date': message.date.isoformat() if message.date else None,
                        'text': message.text[:100] + '...' if len(message.text) > 100 else message.text
                    })
            
            print(f"📜 Найдено более новых сообщений: {len(newer_messages)}")
            
            if newer_messages:
                print(f"⚠️  ВНИМАНИЕ: Есть более новые сообщения!")
                for i, msg in enumerate(newer_messages[:3]):
                    print(f"  {i+1}. ID={msg['id']}: {msg['text']}")
                return False  # Данные неполные
            else:
                print(f"✅ Более новых сообщений не найдено")
                
    except Exception as e:
        print(f"❌ Ошибка при проверке новых: {e}")
    
    # Итоговый анализ
    print(f"\n" + "=" * 60)
    print(f"📊 ИТОГОВЫЙ АНАЛИЗ:")
    print(f"📈 Всего ID в диапазоне: {max(message_ids) - min(message_ids) + 1}")
    print(f"📋 Фактически извлечено: {len(messages)}")
    print(f"❓ Потенциально пропущено: {max(message_ids) - min(message_ids) + 1 - len(messages)}")
    
    # Анализ непрерывности
    gaps = []
    for i in range(len(message_ids) - 1):
        current_id = message_ids[i]
        next_id = message_ids[i + 1]
        if current_id - next_id > 1:
            gaps.append((next_id + 1, current_id - 1))
    
    print(f"🔍 Обнаружено пропусков в ID: {len(gaps)}")
    if gaps:
        print(f"🔍 Примеры пропусков:")
        for i, (start, end) in enumerate(gaps[:5]):
            print(f"  {i+1}. ID {start} - {end} (пропуск {end-start+1} сообщений)")
    
    return len(gaps) == 0

if __name__ == "__main__":
    result = asyncio.run(check_data_completeness())
    if result:
        print(f"\n✅ ДАННЫЕ ПОЛНЫЕ!")
    else:
        print(f"\n⚠️  ДАННЫЕ НЕПОЛНЫЕ - требуется дополнительный парсинг!") 