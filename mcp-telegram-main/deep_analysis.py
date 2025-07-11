import asyncio
import logging
import os
import sqlite3
from datetime import datetime

from telethon.errors import AuthKeyUnregisteredError
from telethon.errors.rpcerrorlist import *

from src.mcp_telegram.telegram import create_client

# Настройка детального логирования
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("telegram_debug.log"),
        logging.StreamHandler(),
    ],
)

async def deep_session_analysis():
    """Глубокий анализ сессии Telegram"""

    print("=== АНАЛИЗ СЕССИИ TELEGRAM ===\n")

    # 1. Анализ файла сессии
    session_path = r"C:\Users\refla\.local\state\mcp-telegram\mcp_telegram_session.session"

    if os.path.exists(session_path):
        stat = os.stat(session_path)
        print("📁 Файл сессии:")
        print(f"   Размер: {stat.st_size} bytes")
        print(f"   Создан: {datetime.fromtimestamp(stat.st_ctime)}")
        print(f"   Изменен: {datetime.fromtimestamp(stat.st_mtime)}")
        print(f"   Доступен: {datetime.fromtimestamp(stat.st_atime)}")

        # Анализ содержимого SQLite
        try:
            conn = sqlite3.connect(session_path)
            cursor = conn.cursor()

            # Проверяем таблицы
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            print(f"\n📊 Таблицы в сессии: {[t[0] for t in tables]}")

            # Анализ версии и данных
            cursor.execute("SELECT * FROM version")
            version = cursor.fetchone()
            print(f"   Версия: {version}")

            # Проверяем сессию
            cursor.execute("SELECT * FROM sessions")
            sessions = cursor.fetchall()
            print(f"   Сессии: {len(sessions)} записей")

            conn.close()

        except Exception as e:
            print(f"❌ Ошибка анализа SQLite: {e}")

    # 2. Тест подключения с детальной диагностикой
    print("\n🔌 ТЕСТ ПОДКЛЮЧЕНИЯ:")

    client = create_client()

    try:
        print("   Подключение к Telegram...")
        await client.connect()

        print(f"   Статус подключения: {client.is_connected()}")

        # Проверка авторизации
        print("   Проверка авторизации...")

        try:
            is_authorized = await client.is_user_authorized()
            print(f"   Авторизован: {is_authorized}")

            if not is_authorized:
                print("   ⚠️  Сессия недействительна")

                # Попытка получить информацию о пользователе
                try:
                    user = await client.get_me()
                    print(f"   Пользователь: {user}")
                except Exception as e:
                    print(f"   ❌ Ошибка получения пользователя: {type(e).__name__}: {e}")

                    # Специфическая диагностика ошибок
                    if "AUTH_KEY_UNREGISTERED" in str(e):
                        print("   🔍 ДИАГНОЗ: Ключ авторизации отозван сервером")
                    elif "SESSION_REVOKED" in str(e):
                        print("   🔍 ДИАГНОЗ: Сессия была отозвана пользователем")
                    elif "AUTH_KEY_DUPLICATED" in str(e):
                        print("   🔍 ДИАГНОЗ: Дублирование ключа авторизации")
                    elif "SESSION_PASSWORD_NEEDED" in str(e):
                        print("   🔍 ДИАГНОЗ: Требуется пароль 2FA")

            else:
                user = await client.get_me()
                print(f"   ✅ Пользователь: {user.first_name} (@{user.username})")

        except AuthKeyUnregisteredError:
            print("   ❌ AUTH_KEY_UNREGISTERED: Ключ авторизации не зарегистрирован")
            print("   🔍 ПРИЧИНА: Telegram удалил ключ авторизации")

        except Exception as e:
            print(f"   ❌ Ошибка авторизации: {type(e).__name__}: {e}")

    except Exception as e:
        print(f"   ❌ Ошибка подключения: {type(e).__name__}: {e}")

    finally:
        await client.disconnect()

    # 3. Анализ других файлов сессий
    print("\n📋 СРАВНЕНИЕ СЕССИЙ:")

    session_dir = r"C:\Users\refla\.local\state\mcp-telegram"
    if os.path.exists(session_dir):
        for file in os.listdir(session_dir):
            if file.endswith(".session"):
                filepath = os.path.join(session_dir, file)
                stat = os.stat(filepath)
                print(f"   {file}: {stat.st_size} bytes, {datetime.fromtimestamp(stat.st_mtime)}")

    print("\n📋 РЕКОМЕНДАЦИИ:")
    print("   1. Проверить активные сессии в настройках Telegram")
    print("   2. Удалить файл сессии и переавторизоваться")
    print("   3. Уменьшить частоту API запросов")
    print("   4. Проверить лимиты API в документации Telegram")

if __name__ == "__main__":
    asyncio.run(deep_session_analysis())
