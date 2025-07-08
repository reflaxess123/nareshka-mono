#!/usr/bin/env python3
"""
Тестовый скрипт для проверки новых инструментов MCP Telegram сервера

Проверяет работу:
1. ListForumTopics - список тем в супергруппе
2. FindTopicByName - поиск темы "Записи собеседований"
3. ListTopicMessages - получение сообщений из найденной темы
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Добавляем путь к mcp-telegram модулю
sys.path.insert(0, str(Path("mcp-telegram-main/src").resolve()))

from mcp_telegram.tools import (
    ListForumTopics,
    FindTopicByName, 
    ListTopicMessages,
    tool_runner
)

async def test_forum_topics():
    """Тест получения списка тем"""
    print("=== Тест 1: Получение списка тем ===")
    
    DIALOG_ID = -1002071074234  # "Frontend – TO THE JOB"
    
    try:
        args = ListForumTopics(dialog_id=DIALOG_ID, limit=50)
        result = await tool_runner(args)
        
        print(f"Результат получения тем из диалога {DIALOG_ID}:")
        for content in result:
            if content.type == "text":
                print(f"  {content.text}")
        
        return True
    except Exception as e:
        print(f"Ошибка при получении тем: {e}")
        return False

async def test_find_topic():
    """Тест поиска темы по названию"""
    print("\n=== Тест 2: Поиск темы 'Записи собеседований' ===")
    
    DIALOG_ID = -1002071074234
    TOPIC_NAME = "Записи собеседований"
    
    try:
        args = FindTopicByName(
            dialog_id=DIALOG_ID,
            topic_name=TOPIC_NAME
        )
        result = await tool_runner(args)
        
        print(f"Поиск темы '{TOPIC_NAME}':")
        topic_id = None
        
        for content in result:
            if content.type == "text":
                print(f"  {content.text}")
                
                # Извлекаем topic_id если найден
                if "FOUND:" in content.text and "topic_id=" in content.text:
                    parts = content.text.split()
                    for part in parts:
                        if part.startswith("topic_id="):
                            topic_id = int(part.split("=")[1])
        
        return topic_id
    except Exception as e:
        print(f"Ошибка при поиске темы: {e}")
        return None

async def test_topic_messages(topic_id: int):
    """Тест получения сообщений из темы"""
    print(f"\n=== Тест 3: Получение сообщений из темы {topic_id} ===")
    
    DIALOG_ID = -1002071074234
    
    try:
        args = ListTopicMessages(
            dialog_id=DIALOG_ID,
            topic_id=topic_id,
            limit=10  # Получаем только 10 сообщений для теста
        )
        result = await tool_runner(args)
        
        print(f"Последние 10 сообщений из темы {topic_id}:")
        message_count = 0
        
        for content in result:
            if content.type == "text":
                if "id=" in content.text and "text=" in content.text:
                    message_count += 1
                    print(f"  Сообщение {message_count}: {content.text[:100]}...")
                else:
                    print(f"  {content.text}")
        
        print(f"Получено сообщений: {message_count}")
        return message_count > 0
    except Exception as e:
        print(f"Ошибка при получении сообщений: {e}")
        return False

async def main():
    """Основная функция тестирования"""
    print("🔍 Тестирование новых инструментов MCP Telegram сервера")
    print("=" * 60)
    
    # Проверяем переменные окружения
    if not os.getenv('TELEGRAM_API_ID') or not os.getenv('TELEGRAM_API_HASH'):
        print("❌ Ошибка: Необходимо установить TELEGRAM_API_ID и TELEGRAM_API_HASH")
        print("\nПример:")
        print("export TELEGRAM_API_ID='your_api_id'")
        print("export TELEGRAM_API_HASH='your_api_hash'")
        sys.exit(1)
    
    print(f"✅ API ID: {os.getenv('TELEGRAM_API_ID')}")
    print(f"✅ API Hash: {'*' * 10}")
    
    try:
        # Тест 1: Получение списка тем
        topics_success = await test_forum_topics()
        
        # Тест 2: Поиск конкретной темы
        topic_id = await test_find_topic()
        
        # Тест 3: Получение сообщений (если тема найдена)
        messages_success = False
        if topic_id:
            messages_success = await test_topic_messages(topic_id)
        
        # Результаты
        print("\n" + "=" * 60)
        print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
        print(f"✅ Получение тем: {'OK' if topics_success else 'FAILED'}")
        print(f"✅ Поиск темы: {'OK' if topic_id else 'FAILED'}")
        print(f"✅ Получение сообщений: {'OK' if messages_success else 'FAILED'}")
        
        if topic_id and messages_success:
            print(f"\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
            print(f"🚀 Тема найдена с ID: {topic_id}")
            print(f"🚀 Можно запускать массовый парсинг!")
            print(f"\nДля запуска полного парсинга выполните:")
            print(f"python telegram_topic_mass_parser.py")
        else:
            print(f"\n❌ Некоторые тесты не прошли")
            
    except Exception as e:
        print(f"\n💥 Критическая ошибка при тестировании: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 