import asyncio
import logging

from telethon.errors import *
from telethon.tl.functions.updates import GetStateRequest
from telethon.tl.functions.users import GetUsersRequest
from telethon.tl.types import InputUserSelf

from src.mcp_telegram.telegram import create_client

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_specific_api_calls():
    """Тестирование конкретных API вызовов для выявления точной ошибки"""

    print("=== ТЕСТИРОВАНИЕ API ВЫЗОВОВ ===\n")

    client = create_client()

    try:
        print("1. Подключение...")
        await client.connect()
        print(f"   ✅ Подключено: {client.is_connected()}")

        print("\n2. Проверка авторизации...")
        is_authorized = await client.is_user_authorized()
        print(f"   Авторизован: {is_authorized}")

        if not is_authorized:
            print("   ❌ Сессия не авторизована")

            print("\n3. Попытка получить состояние...")
            try:
                state = await client(GetStateRequest())
                print(f"   ✅ Состояние получено: {state}")
            except Exception as e:
                print(f"   ❌ Ошибка GetState: {type(e).__name__}: {e}")

            print("\n4. Попытка получить пользователя...")
            try:
                users = await client(GetUsersRequest([InputUserSelf()]))
                print(f"   ✅ Пользователь получен: {users}")
            except Exception as e:
                print(f"   ❌ Ошибка GetUsers: {type(e).__name__}: {e}")

                # Анализ конкретных ошибок
                if isinstance(e, AuthKeyUnregisteredError):
                    print("   🔍 ТОЧНАЯ ПРИЧИНА: AUTH_KEY_UNREGISTERED")
                    print("   📝 ОПИСАНИЕ: Ключ авторизации отозван сервером Telegram")
                    print("   💡 ПРИЧИНЫ:")
                    print("      - Подозрительная активность")
                    print("      - Превышение лимитов API")
                    print("      - Множественные одновременные сессии")
                    print("      - Нарушение условий использования API")

                elif isinstance(e, AuthKeyDuplicatedError):
                    print("   🔍 ТОЧНАЯ ПРИЧИНА: AUTH_KEY_DUPLICATED")
                    print("   📝 ОПИСАНИЕ: Ключ авторизации дублирован")

                elif isinstance(e, SessionRevokedError):
                    print("   🔍 ТОЧНАЯ ПРИЧИНА: SESSION_REVOKED")
                    print("   📝 ОПИСАНИЕ: Сессия была отозвана пользователем")

                elif isinstance(e, UserDeactivatedError):
                    print("   🔍 ТОЧНАЯ ПРИЧИНА: USER_DEACTIVATED")
                    print("   📝 ОПИСАНИЕ: Аккаунт деактивирован")

                elif isinstance(e, FloodWaitError):
                    print(f"   🔍 ТОЧНАЯ ПРИЧИНА: FLOOD_WAIT ({e.seconds} секунд)")
                    print("   📝 ОПИСАНИЕ: Превышен лимит запросов")

                else:
                    print(f"   🔍 НЕИЗВЕСТНАЯ ОШИБКА: {type(e).__name__}")
                    print(f"   📝 ОПИСАНИЕ: {e!s}")

        else:
            print("   ✅ Сессия авторизована")

            print("\n3. Получение информации о пользователе...")
            try:
                user = await client.get_me()
                print(f"   ✅ Пользователь: {user.first_name} (@{user.username})")
            except Exception as e:
                print(f"   ❌ Ошибка get_me: {type(e).__name__}: {e}")

        print("\n5. Тест простого API вызова...")
        try:
            # Попробуем простой вызов
            result = await client.get_dialogs(limit=1)
            print(f"   ✅ Диалоги получены: {len(result)} штук")
        except Exception as e:
            print(f"   ❌ Ошибка get_dialogs: {type(e).__name__}: {e}")

            # Детальный анализ ошибки
            error_code = getattr(e, "code", None)
            error_message = str(e)

            print(f"   🔍 Код ошибки: {error_code}")
            print(f"   🔍 Сообщение: {error_message}")

            if "401" in error_message:
                print("   🎯 ТОЧНАЯ ПРИЧИНА: Ошибка авторизации (401)")
                print("   📝 РЕШЕНИЕ: Необходима полная переавторизация")
            elif "420" in error_message:
                print("   🎯 ТОЧНАЯ ПРИЧИНА: Превышен лимит запросов (420)")
                print("   📝 РЕШЕНИЕ: Ожидание и снижение частоты запросов")
            elif "403" in error_message:
                print("   🎯 ТОЧНАЯ ПРИЧИНА: Доступ запрещен (403)")
                print("   📝 РЕШЕНИЕ: Проверка прав доступа")

    except Exception as e:
        print(f"❌ Критическая ошибка: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

    finally:
        await client.disconnect()
        print("\n✅ Соединение закрыто")

if __name__ == "__main__":
    asyncio.run(test_specific_api_calls())
