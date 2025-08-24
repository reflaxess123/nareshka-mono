#!/usr/bin/env python3
"""
Скрипт для добавления поддерживаемых языков программирования в базу данных
"""

import asyncio
import os
import sys

# Добавляем корневую папку в PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.core.settings import settings


async def populate_languages():
    """Добавляет поддерживаемые языки в базу данных"""

    # Создаем синхронный engine для простоты
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(bind=engine)

    languages_data = [
        {
            "id": "python3",
            "name": "Python 3",
            "language": "PYTHON",
            "version": "3.8.1",
            "dockerImage": "python:3.8-slim",
            "fileExtension": ".py",
            "compileCommand": None,
            "runCommand": "python {file}",
            "timeoutSeconds": 30,
            "memoryLimitMB": 128,
        },
        {
            "id": "javascript",
            "name": "JavaScript (Node.js)",
            "language": "JAVASCRIPT",
            "version": "12.14.0",
            "dockerImage": "node:12-slim",
            "fileExtension": ".js",
            "compileCommand": None,
            "runCommand": "node {file}",
            "timeoutSeconds": 30,
            "memoryLimitMB": 128,
        },
        {
            "id": "typescript",
            "name": "TypeScript",
            "language": "TYPESCRIPT",
            "version": "3.7.4",
            "dockerImage": "node:12-slim",
            "fileExtension": ".ts",
            "compileCommand": "tsc {file} --outDir /tmp",
            "runCommand": "node /tmp/{file}.js",
            "timeoutSeconds": 30,
            "memoryLimitMB": 128,
        },
        {
            "id": "java",
            "name": "Java",
            "language": "JAVA",
            "version": "13.0.1",
            "dockerImage": "openjdk:13-slim",
            "fileExtension": ".java",
            "compileCommand": "javac {file}",
            "runCommand": "java Main",
            "timeoutSeconds": 30,
            "memoryLimitMB": 256,
        },
        {
            "id": "cpp",
            "name": "C++",
            "language": "CPP",
            "version": "9.2.0",
            "dockerImage": "gcc:9",
            "fileExtension": ".cpp",
            "compileCommand": "g++ -o main {file}",
            "runCommand": "./main",
            "timeoutSeconds": 30,
            "memoryLimitMB": 128,
        },
        {
            "id": "c",
            "name": "C",
            "language": "C",
            "version": "9.2.0",
            "dockerImage": "gcc:9",
            "fileExtension": ".c",
            "compileCommand": "gcc -o main {file}",
            "runCommand": "./main",
            "timeoutSeconds": 30,
            "memoryLimitMB": 128,
        },
        {
            "id": "go",
            "name": "Go",
            "language": "GO",
            "version": "1.13.5",
            "dockerImage": "golang:1.13-alpine",
            "fileExtension": ".go",
            "compileCommand": None,
            "runCommand": "go run {file}",
            "timeoutSeconds": 30,
            "memoryLimitMB": 128,
        },
        {
            "id": "rust",
            "name": "Rust",
            "language": "RUST",
            "version": "1.40.0",
            "dockerImage": "rust:1.40",
            "fileExtension": ".rs",
            "compileCommand": "rustc {file} -o main",
            "runCommand": "./main",
            "timeoutSeconds": 30,
            "memoryLimitMB": 128,
        },
        {
            "id": "php",
            "name": "PHP",
            "language": "PHP",
            "version": "7.4.1",
            "dockerImage": "php:7.4-cli",
            "fileExtension": ".php",
            "compileCommand": None,
            "runCommand": "php {file}",
            "timeoutSeconds": 30,
            "memoryLimitMB": 128,
        },
        {
            "id": "ruby",
            "name": "Ruby",
            "language": "RUBY",
            "version": "2.7.0",
            "dockerImage": "ruby:2.7",
            "fileExtension": ".rb",
            "compileCommand": None,
            "runCommand": "ruby {file}",
            "timeoutSeconds": 30,
            "memoryLimitMB": 128,
        },
    ]

    session = SessionLocal()

    try:
        print("Adding supported programming languages to database...")

        for lang_data in languages_data:
            # Проверяем, существует ли уже язык
            result = session.execute(
                text('SELECT COUNT(*) FROM "SupportedLanguage" WHERE id = :id'),
                {"id": lang_data["id"]},
            )

            if result.scalar() > 0:
                print(f"Language {lang_data['name']} already exists, skipping...")
                continue

            # Добавляем язык
            session.execute(
                text("""
                    INSERT INTO "SupportedLanguage" (
                        id, name, language, version, "dockerImage", "fileExtension",
                        "compileCommand", "runCommand", "timeoutSeconds", "memoryLimitMB",
                        "isEnabled", "createdAt", "updatedAt"
                    ) VALUES (
                        :id, :name, :language, :version, :dockerImage, :fileExtension,
                        :compileCommand, :runCommand, :timeoutSeconds, :memoryLimitMB,
                        true, NOW(), NOW()
                    )
                """),
                lang_data,
            )

            print(f"Added language: {lang_data['name']}")

        session.commit()
        print(
            f"\nSUCCESS: Added {len(languages_data)} programming languages to database!"
        )

        # Проверяем результат
        result = session.execute(text('SELECT COUNT(*) FROM "SupportedLanguage"'))
        total_count = result.scalar()
        print(f"Total languages in database: {total_count}")

    except Exception as e:
        session.rollback()
        print(f"ERROR: Failed to add languages: {str(e)}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    print("Populating supported programming languages...")
    asyncio.run(populate_languages())
