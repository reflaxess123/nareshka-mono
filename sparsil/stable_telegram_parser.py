#!/usr/bin/env python3
"""
Стабильный Telegram парсер
Создает ОДНУ сессию и переиспользует ее
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from telethon import TelegramClient
from telethon.errors import *

async def create_stable_session():
    """Создание стабильной сессии один раз"""
    
    api_id = os.getenv('TELEGRAM_API_ID') or os.getenv('TG_APP_ID')
    api_hash = os.getenv('TELEGRAM_API_HASH') or os.getenv('TG_API_HASH')
    
    print(f"🔐 Создание стабильной сессии...")
    
    # Используем стабильное имя сессии
    client = TelegramClient('stable_parser_session', api_id, api_hash)
    
    await client.connect()
    
    if not await client.is_user_authorized():
        print("Требуется авторизация...")
        phone = '+79296450669'
        await client.send_code_request(phone)
        
        code = input("Введите код: ")
        await client.sign_in(phone, code)
        
        print("✔️ Авторизация успешна!")
    else:
        print("✔️ Уже авторизован!")
    
    # Проверяем что все работает
    me = await client.get_me()
    print(f"✔️ Пользователь: {me.first_name} (@{me.username})")
    
    return client

async def parse_topic_with_stable_client(client):
    """Парсинг темы с использованием стабильного клиента"""
    
    DIALOG_ID = -1002071074234
    TOPIC_ID = 489
    
    print(f"\n🔍 Парсинг темы {TOPIC_ID}...")
    
    # Получаем информацию о чате
    entity = await client.get_entity(DIALOG_ID)
    print(f"✔️ Чат: {entity.title}")
    
    messages = []
    count = 0
    
    try:
        # Используем стабильный клиент для итерации
        async for message in client.iter_messages(
            entity=DIALOG_ID,
            limit=None,
            reply_to=TOPIC_ID
        ):
            if message.text:
                count += 1
                msg_data = {
                    'id': message.id,
                    'date': message.date.isoformat() if message.date else None,
                    'text': message.message,
                    'from_id': str(getattr(message, 'from_id', None)),  # Конвертируем в строку
                    'reply_to_msg_id': getattr(message.reply_to, 'reply_to_msg_id', None) if hasattr(message, 'reply_to') and message.reply_to else None,
                    'topic_id': TOPIC_ID
                }
                messages.append(msg_data)
                
                if count % 100 == 0:
                    print(f"Получено {count} сообщений...")
                
                # Промежуточное сохранение каждые 1000 сообщений
                if count % 1000 == 0:
                    temp_file = f"stable_temp_{count}.json"
                    with open(temp_file, 'w', encoding='utf-8') as f:
                        json.dump({'messages': messages}, f, ensure_ascii=False, indent=2)
                    print(f"💾 Промежуточное сохранение: {temp_file}")
    
    except Exception as e:
        print(f"⚠️  Ошибка парсинга: {e}")
        print(f"✔️ Получено {len(messages)} сообщений до ошибки")
    
    print(f"\n✔️ Итого: {len(messages)} сообщений")
    
    # Финальное сохранение
    if messages:
        filename = f"stable_topic_messages_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'metadata': {
                    'topic_id': TOPIC_ID,
                    'dialog_id': DIALOG_ID,
                    'total_messages': len(messages),
                    'extraction_date': datetime.now().isoformat(),
                    'method': 'stable_client_approach'
                },
                'messages': messages
            }, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Результаты сохранены в {filename}")
        
        # Статистика
        print(f"\n📊 Статистика:")
        print(f"ID диапазон: {min(msg['id'] for msg in messages)} - {max(msg['id'] for msg in messages)}")
        print(f"Первое: {messages[0]['date']}")
        print(f"Последнее: {messages[-1]['date']}")
    
    return messages

async def main():
    """Основная функция"""
    
    try:
        # Создаем стабильную сессию ОДИН раз
        client = await create_stable_session()
        
        # Используем ее для парсинга
        messages = await parse_topic_with_stable_client(client)
        
        print(f"\n🎉 Завершено! Получено {len(messages)} сообщений")
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # НЕ отключаемся - оставляем сессию активной
        print("ℹ️  Сессия остается активной для будущих запусков")

if __name__ == "__main__":
    asyncio.run(main()) 