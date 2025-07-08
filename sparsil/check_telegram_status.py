#!/usr/bin/env python3
"""
Проверка статуса Telegram API
"""

import asyncio
import os
import sys
from pathlib import Path

# Добавляем путь к mcp-telegram модулю
sys.path.insert(0, str(Path("mcp-telegram-main/src").resolve()))

from telethon import TelegramClient
from telethon.errors import *

async def check_api_status():
    """Проверка статуса API"""
    
    api_id = os.getenv('TELEGRAM_API_ID') or os.getenv('TG_APP_ID')
    api_hash = os.getenv('TELEGRAM_API_HASH') or os.getenv('TG_API_HASH')
    
    print(f"🔍 Проверка API {api_id}")
    
    # Создаем чистый клиент без существующих сессий
    client = TelegramClient('test_clean_session', api_id, api_hash)
    
    try:
        print("Попытка подключения...")
        await client.connect()
        
        if await client.is_user_authorized():
            print("✔️ Пользователь авторизован")
            me = await client.get_me()
            print(f"✔️ Пользователь: {me.first_name}")
        else:
            print("❌ Пользователь НЕ авторизован")
            
            # Попытка отправить код
            try:
                phone = '+79296450669'
                print(f"Отправляем код на {phone}...")
                result = await client.send_code_request(phone)
                print("✔️ Код отправлен успешно")
                print("ℹ️  API работает, но требуется новая авторизация")
            except FloodWaitError as e:
                print(f"❌ FLOOD WAIT: ждите {e.seconds} секунд")
            except PhoneNumberInvalidError:
                print("❌ Неверный номер телефона")
            except ApiIdInvalidError:
                print("❌ Неверный API_ID или API_HASH")
            except Exception as e:
                print(f"❌ Ошибка отправки кода: {e}")
                
    except AuthKeyUnregisteredError:
        print("❌ AUTH_KEY_UNREGISTERED - ключ не зарегистрирован")
        print("🔧 Возможные причины:")
        print("   1. Слишком много попыток подключения")
        print("   2. Telegram заблокировал API_ID")
        print("   3. Нужен новый API_ID")
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(check_api_status()) 