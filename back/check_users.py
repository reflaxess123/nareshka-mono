#!/usr/bin/env python3

import psycopg2

from app.config.new_settings import legacy_settings as settings


def check_users():
    """Проверка пользователей в базе данных"""

    # Парсим URL базы данных
    db_url = settings.database_url
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    try:
        # Подключение к базе данных
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()

        print("✅ Подключение к базе данных успешно!")

        # Получаем всех пользователей
        cursor.execute('SELECT id, email, password, role FROM "User"')
        users = cursor.fetchall()

        print(f"\n👥 Найдено пользователей: {len(users)}")
        for user in users:
            print(
                f"  ID: {user[0]}, Email: {user[1]}, Hash: {user[2][:20]}..., Role: {user[3]}"
            )

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ Ошибка: {e}")


if __name__ == "__main__":
    check_users()
