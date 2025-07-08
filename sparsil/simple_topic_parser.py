#!/usr/bin/env python3
"""
Простой парсер сообщений из Telegram темы
Использует точно тот же подход что и в рабочем тесте
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# Добавляем путь к mcp-telegram модулю
sys.path.insert(0, str(Path("mcp-telegram-main/src").resolve()))

from mcp_telegram.telegram import create_client

async def get_topic_messages():
    """Получение сообщений из темы форума"""
    
    DIALOG_ID = -1002071074234
    TOPIC_ID = 489
    
    # Получаем API параметры
    api_id = os.getenv('TELEGRAM_API_ID') or os.getenv('TG_APP_ID')
    api_hash = os.getenv('TELEGRAM_API_HASH') or os.getenv('TG_API_HASH')
    
    print(f"API ID: {api_id}")
    print(f"API Hash: {api_hash[:10] if api_hash else 'НЕ НАЙДЕН'}...")
    
    if not api_id or not api_hash:
        print("❌ ОШИБКА: Не найдены API параметры!")
        return
    
    try:
        # Создаем клиент точно так же как в тесте
        client = create_client(
            api_id=api_id,
            api_hash=api_hash,
            session_name="test_auth_session"
        )
        
        print("Подключаемся к Telegram...")
        async with client:
            print("✔️ Подключение успешно!")
            
            # Получаем информацию о себе для проверки
            me = await client.get_me()
            print(f"✔️ Пользователь: {me.first_name} (@{me.username})")
            
            # Получаем информацию о чате
            entity = await client.get_entity(DIALOG_ID)
            print(f"✔️ Чат: {entity.title}")
            
            print(f"\n🔍 Ищем сообщения в теме {TOPIC_ID}...")
            
            # Используем простой метод - iter_messages с reply_to
            messages = []
            count = 0
            
            try:
                async for message in client.iter_messages(
                    entity=DIALOG_ID,
                    limit=None,  # Получаем все
                    reply_to=TOPIC_ID
                ):
                    if message.text:
                        count += 1
                        msg_data = {
                            'id': message.id,
                            'date': message.date.isoformat() if message.date else None,
                            'text': message.message,
                            'from_id': getattr(message, 'from_id', None),
                            'reply_to_msg_id': getattr(message.reply_to, 'reply_to_msg_id', None) if hasattr(message, 'reply_to') and message.reply_to else None,
                            'topic_id': TOPIC_ID
                        }
                        messages.append(msg_data)
                        
                        if count % 100 == 0:
                            print(f"Найдено {count} сообщений...")
                        
                        # Промежуточное сохранение каждые 500 сообщений
                        if count % 500 == 0:
                            temp_filename = f"temp_messages_{count}.json"
                            with open(temp_filename, 'w', encoding='utf-8') as f:
                                json.dump({'messages': messages}, f, ensure_ascii=False, indent=2)
                            print(f"💾 Промежуточное сохранение: {temp_filename}")
            
            except Exception as e:
                print(f"⚠️ Ошибка при получении сообщений: {e}")
                print(f"✔️ Но получено {len(messages)} сообщений до ошибки")
            
            print(f"\n✔️ Итого найдено {len(messages)} сообщений")
            
            # Сохраняем результаты в любом случае
            try:
                filename = f"simple_topic_messages_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump({
                        'metadata': {
                            'topic_id': TOPIC_ID,
                            'dialog_id': DIALOG_ID,
                            'total_messages': len(messages),
                            'extraction_date': datetime.now().isoformat(),
                            'method': 'simple_iter_messages_reply_to',
                            'status': 'completed_with_errors' if len(messages) > 0 else 'failed'
                        },
                        'messages': messages
                    }, f, ensure_ascii=False, indent=2)
                
                print(f"💾 Результаты сохранены в {filename}")
                
            except Exception as save_error:
                print(f"❌ Ошибка сохранения: {save_error}")
                # Попытка аварийного сохранения
                emergency_file = f"emergency_messages_{len(messages)}.json"
                with open(emergency_file, 'w', encoding='utf-8') as f:
                    json.dump(messages, f, ensure_ascii=False)
                print(f"💾 Аварийное сохранение: {emergency_file}")
            
            # Показываем статистику
            if messages:
                print(f"\n📊 Статистика:")
                print(f"Первое сообщение: {messages[0]['date']}")
                print(f"Последнее сообщение: {messages[-1]['date']}")
                print(f"ID диапазон: {min(msg['id'] for msg in messages)} - {max(msg['id'] for msg in messages)}")
    
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(get_topic_messages()) 