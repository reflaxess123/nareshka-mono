#!/usr/bin/env python3
"""
Простой скрипт для инициализации поддерживаемых языков программирования
"""

import os

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

# Загружаем переменные окружения
load_dotenv()


def init_supported_languages():
    """Инициализация поддерживаемых языков программирования"""

    # Подключение к базе данных
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL не найден в переменных окружения")
        return

    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Проверяем, есть ли уже языки в БД
        cursor.execute('SELECT COUNT(*) as count FROM "SupportedLanguage"')
        result = cursor.fetchone()
        existing_count = result["count"] if result else 0

        if existing_count > 0:
            print(f"В базе уже есть {existing_count} языков. Пропускаем инициализацию.")
            return

        # Список поддерживаемых языков
        languages_data = [
            (
                "python",
                "Python",
                "PYTHON",
                "3.11",
                "python:3.11-slim",
                ".py",
                None,
                "python /tmp/code.py",
                30,
                128,
                True,
            ),
            (
                "javascript",
                "JavaScript (Node.js)",
                "JAVASCRIPT",
                "18",
                "node:18-slim",
                ".js",
                None,
                "node /tmp/code.js",
                30,
                128,
                True,
            ),
            (
                "java",
                "Java",
                "JAVA",
                "17",
                "openjdk:17-slim",
                ".java",
                "javac /tmp/Main.java",
                "java -cp /tmp Main",
                45,
                256,
                True,
            ),
            (
                "cpp",
                "C++",
                "CPP",
                "17",
                "gcc:latest",
                ".cpp",
                "g++ -o /tmp/code /tmp/code.cpp",
                "/tmp/code",
                30,
                128,
                True,
            ),
            (
                "c",
                "C",
                "C",
                "11",
                "gcc:latest",
                ".c",
                "gcc -o /tmp/code /tmp/code.c",
                "/tmp/code",
                30,
                128,
                True,
            ),
            (
                "go",
                "Go",
                "GO",
                "1.21",
                "golang:1.21-alpine",
                ".go",
                None,
                "go run /tmp/code.go",
                30,
                128,
                True,
            ),
            (
                "rust",
                "Rust",
                "RUST",
                "1.70",
                "rust:1.70-slim",
                ".rs",
                "rustc /tmp/code.rs -o /tmp/code",
                "/tmp/code",
                45,
                256,
                True,
            ),
        ]

        # Вставляем языки в БД
        insert_query = """
        INSERT INTO "SupportedLanguage" 
        (id, name, language, version, "dockerImage", "fileExtension", "compileCommand", "runCommand", "timeoutSeconds", "memoryLimitMB", "isEnabled", "createdAt", "updatedAt")
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
        """

        cursor.executemany(insert_query, languages_data)
        conn.commit()

        print(f"✅ Успешно добавлено {len(languages_data)} поддерживаемых языков")

        # Выводим список добавленных языков
        for lang_data in languages_data:
            print(f"  - {lang_data[1]} ({lang_data[3]})")

    except Exception as e:
        print(f"❌ Ошибка при инициализации языков: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


if __name__ == "__main__":
    print("🚀 Инициализация поддерживаемых языков программирования...")
    init_supported_languages()
    print("✅ Инициализация завершена!")
