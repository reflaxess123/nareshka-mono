#!/usr/bin/env python3

import psycopg2

from app.core.settings import settings


def check_users_and_progress():
    """Проверка пользователей и их прогресса в базе данных"""

    # Парсим URL базы данных
    db_url = settings.database_url
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    try:
        # Подключение к базе данных
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()

        print("✅ Подключение к базе данных успешно!")

        # 1. Получаем всех пользователей
        cursor.execute('SELECT id, email, password, role FROM "User"')
        users = cursor.fetchall()

        print(f"\n👥 Найдено пользователей: {len(users)}")
        for user in users:
            print(f"  ID: {user[0]}, Email: {user[1]}, Role: {user[3]}")

        # 2. Проверяем прогресс пользователей
        cursor.execute("""
            SELECT "userId", "blockId", "solvedCount", "createdAt", "updatedAt" 
            FROM "UserContentProgress" 
            ORDER BY "createdAt" DESC 
            LIMIT 10
        """)
        progress_records = cursor.fetchall()

        print(f"\n📊 Найдено записей прогресса: {len(progress_records)}")
        for progress in progress_records:
            user_id, block_id, solved_count, created_at, updated_at = progress
            print(
                f"  UserID: {user_id}, BlockID: {block_id}, SolvedCount: {solved_count}, Updated: {updated_at}"
            )

        # 3. Проверяем общую статистику по пользователям
        cursor.execute("""
            SELECT 
                u.id,
                u.email,
                COUNT(p."blockId") as blocks_with_progress,
                SUM(p."solvedCount") as total_solved
            FROM "User" u
            LEFT JOIN "UserContentProgress" p ON u.id = p."userId"
            GROUP BY u.id, u.email
            ORDER BY total_solved DESC NULLS LAST
        """)
        stats = cursor.fetchall()

        print("\n📈 Статистика пользователей:")
        for stat in stats:
            user_id, email, blocks_count, total_solved = stat
            print(f"  {email}: {blocks_count or 0} блоков, {total_solved or 0} решений")

        # 4. Найдем первого пользователя с прогрессом для тестирования
        cursor.execute("""
            SELECT DISTINCT "userId", u.email
            FROM "UserContentProgress" p
            JOIN "User" u ON u.id = p."userId"
            LIMIT 1
        """)
        test_user = cursor.fetchone()

        if test_user:
            print(
                f"\n🧪 Тестовый пользователь: ID={test_user[0]}, Email={test_user[1]}"
            )
        else:
            print("\n⚠️ Нет пользователей с прогрессом для тестирования")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ Ошибка: {e}")


if __name__ == "__main__":
    check_users_and_progress()
