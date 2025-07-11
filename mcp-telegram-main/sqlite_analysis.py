import os
import sqlite3
from datetime import datetime


def analyze_session_db():
    """Детальный анализ SQLite базы данных сессии"""

    session_path = r"C:\Users\refla\.local\state\mcp-telegram\mcp_telegram_session.session"

    if not os.path.exists(session_path):
        print("❌ Файл сессии не найден")
        return

    print("=== ДЕТАЛЬНЫЙ АНАЛИЗ SQLite СЕССИИ ===\n")

    try:
        conn = sqlite3.connect(session_path)
        cursor = conn.cursor()

        # 1. Структура базы данных
        print("📊 СТРУКТУРА ТАБЛИЦ:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()

        for table in tables:
            table_name = table[0]
            print(f"\n🔹 Таблица: {table_name}")

            # Получаем структуру таблицы
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()

            for col in columns:
                print(f"   {col[1]} ({col[2]})")

            # Получаем данные
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            print(f"   Записей: {len(rows)}")

            # Показываем данные для некоторых таблиц
            if table_name == "version":
                print(f"   Версия: {rows[0] if rows else 'Нет данных'}")

            elif table_name == "sessions":
                if rows:
                    print(f"   Данные сессии: {len(rows)} записей")
                    for i, row in enumerate(rows):
                        print(f"     Запись {i+1}: {len(str(row))} символов")
                        # Не показываем сырые данные по безопасности

            elif table_name == "entities":
                print(f"   Сущности: {len(rows)} записей")
                for row in rows[:5]:  # Показываем первые 5
                    print(f"     ID: {row[0]}, Hash: {row[1]}")

            elif table_name == "sent_files":
                print(f"   Отправленные файлы: {len(rows)} записей")

            elif table_name == "update_state":
                if rows:
                    print(f"   Состояние обновлений: {rows[0] if rows else 'Нет данных'}")

        # 2. Проверка целостности данных
        print("\n🔍 ПРОВЕРКА ЦЕЛОСТНОСТИ:")

        # Проверяем, есть ли данные сессии
        cursor.execute("SELECT COUNT(*) FROM sessions")
        session_count = cursor.fetchone()[0]
        print(f"   Количество сессий: {session_count}")

        if session_count > 0:
            cursor.execute("SELECT * FROM sessions")
            session_data = cursor.fetchone()
            print(f"   Размер данных сессии: {len(str(session_data))} символов")

            # Проверяем основные поля
            if session_data:
                print(f"   DC ID: {session_data[0] if len(session_data) > 0 else 'Нет'}")
                print(f"   IP: {session_data[1] if len(session_data) > 1 else 'Нет'}")
                print(f"   Порт: {session_data[2] if len(session_data) > 2 else 'Нет'}")
                print(f"   Ключ аутентификации: {'Есть' if len(session_data) > 3 and session_data[3] else 'Нет'}")

        # 3. Анализ временных меток
        print("\n⏰ АНАЛИЗ ВРЕМЕНИ:")

        # Проверяем файл
        stat = os.stat(session_path)
        print(f"   Файл создан: {datetime.fromtimestamp(stat.st_ctime)}")
        print(f"   Последнее изменение: {datetime.fromtimestamp(stat.st_mtime)}")
        print(f"   Последний доступ: {datetime.fromtimestamp(stat.st_atime)}")

        # Время сейчас
        now = datetime.now()
        modified_ago = now - datetime.fromtimestamp(stat.st_mtime)
        print(f"   Изменен {modified_ago} назад")

        conn.close()

        # 4. Диагностика проблем
        print("\n🔍 ДИАГНОСТИКА ПРОБЛЕМ:")

        if session_count == 0:
            print("   ❌ ПРОБЛЕМА: Нет данных сессии")
            print("   🔧 РЕШЕНИЕ: Переавторизация необходима")

        elif modified_ago.days > 30:
            print("   ⚠️  ПРОБЛЕМА: Сессия устарела (>30 дней)")
            print("   🔧 РЕШЕНИЕ: Рекомендуется переавторизация")

        else:
            print("   ✅ Структура сессии выглядит корректно")
            print("   🔧 ПРОБЛЕМА: Возможно, сессия была отозвана сервером")
            print("   🔧 ПРИЧИНА: Подозрительная активность или нарушение лимитов")

    except Exception as e:
        print(f"❌ Ошибка анализа: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_session_db()
