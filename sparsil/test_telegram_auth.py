#!/usr/bin/env python3
"""
Простой тест аутентификации в Telegram API

Проверяет:
1. Правильность API параметров
2. Возможность подключения
3. Получение информации о пользователе
"""

import asyncio
import os
import sys
from pathlib import Path

# Добавляем путь к mcp-telegram модулю
sys.path.insert(0, str(Path("mcp-telegram-main/src").resolve()))

from mcp_telegram.telegram import create_client

async def test_auth():
    """Тестирование аутентификации"""
    
    # Получаем API параметры
    api_id = os.getenv('TELEGRAM_API_ID') or os.getenv('TG_APP_ID')
    api_hash = os.getenv('TELEGRAM_API_HASH') or os.getenv('TG_API_HASH')
    
    print(f"API ID: {api_id}")
    print(f"API Hash: {api_hash[:10] if api_hash else 'НЕ НАЙДЕН'}...")
    
    if not api_id or not api_hash:
        print("❌ ОШИБКА: Не найдены API параметры!")
        print("Установите переменные окружения:")
        print("$env:TELEGRAM_API_ID=\"23628237\"")
        print("$env:TELEGRAM_API_HASH=\"b4fed8cf04844f325c5fc228397852b5\"")
        return
    
    try:
        # Создаем клиент с новой сессией
        client = create_client(
            api_id=api_id,
            api_hash=api_hash,
            session_name="test_auth_session"
        )
        
        print("Подключаемся к Telegram...")
        async with client:
            print("✔️ Подключение успешно!")
            
            # Получаем информацию о себе
            try:
                me = await client.get_me()
                print(f"✔️ Пользователь: {me.first_name} (@{me.username})")
                print(f"✔️ ID: {me.id}")
                print(f"✔️ Телефон: {me.phone}")
                
                # Тестируем доступ к целевому чату
                print("\nПроверяем доступ к целевому чату...")
                entity = await client.get_entity(-1002071074234)
                print(f"✔️ Чат найден: {entity.title}")
                
            except Exception as e:
                print(f"⚠️ Ошибка получения данных: {e}")
    
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        if "PHONE_NUMBER_INVALID" in str(e):
            print("Возможно неправильный номер телефона")
        elif "API_ID_INVALID" in str(e):
            print("Неправильные API_ID или API_HASH")
        elif "FLOOD_WAIT" in str(e):
            print("Слишком много попыток, нужно подождать")

if __name__ == "__main__":
    asyncio.run(test_auth()) 