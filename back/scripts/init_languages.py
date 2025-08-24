#!/usr/bin/env python3
"""
Скрипт для инициализации поддерживаемых языков программирования в базе данных
"""

import sys
import uuid

from sqlalchemy.orm import Session

from app.features.code_editor.models.code_execution_models import SupportedLanguage
from app.shared.database.connection import engine
from app.shared.models.enums import CodeLanguage

# Конфигурация поддерживаемых языков
SUPPORTED_LANGUAGES = [
    {
        "id": str(uuid.uuid4()),
        "name": "Python 3.9",
        "language": CodeLanguage.PYTHON,
        "version": "3.9",
        "dockerImage": "python:3.9-alpine",
        "fileExtension": ".py",
        "compileCommand": None,
        "runCommand": "python main.py",
        "timeoutSeconds": 10,
        "memoryLimitMB": 128,
        "isEnabled": True,
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Node.js 18",
        "language": CodeLanguage.JAVASCRIPT,
        "version": "18",
        "dockerImage": "node:18-alpine",
        "fileExtension": ".js",
        "compileCommand": None,
        "runCommand": "node main.js",
        "timeoutSeconds": 10,
        "memoryLimitMB": 128,
        "isEnabled": True,
    },
    {
        "id": str(uuid.uuid4()),
        "name": "TypeScript 5.0",
        "language": CodeLanguage.TYPESCRIPT,
        "version": "5.0",
        "dockerImage": "node:18-alpine",
        "fileExtension": ".ts",
        "compileCommand": "npx tsc main.ts --target es2020 --module commonjs",
        "runCommand": "node main.js",
        "timeoutSeconds": 15,
        "memoryLimitMB": 256,
        "isEnabled": True,
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Java 17",
        "language": CodeLanguage.JAVA,
        "version": "17",
        "dockerImage": "openjdk:17-alpine",
        "fileExtension": ".java",
        "compileCommand": "javac Main.java",
        "runCommand": "java Main",
        "timeoutSeconds": 15,
        "memoryLimitMB": 256,
        "isEnabled": True,
    },
    {
        "id": str(uuid.uuid4()),
        "name": "C++ (GCC 11)",
        "language": CodeLanguage.CPP,
        "version": "11",
        "dockerImage": "gcc:11-alpine",
        "fileExtension": ".cpp",
        "compileCommand": "g++ -o main main.cpp -std=c++17",
        "runCommand": "./main",
        "timeoutSeconds": 10,
        "memoryLimitMB": 128,
        "isEnabled": True,
    },
    {
        "id": str(uuid.uuid4()),
        "name": "C (GCC 11)",
        "language": CodeLanguage.C,
        "version": "11",
        "dockerImage": "gcc:11-alpine",
        "fileExtension": ".c",
        "compileCommand": "gcc -o main main.c -std=c99",
        "runCommand": "./main",
        "timeoutSeconds": 10,
        "memoryLimitMB": 128,
        "isEnabled": True,
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Go 1.21",
        "language": CodeLanguage.GO,
        "version": "1.21",
        "dockerImage": "golang:1.21-alpine",
        "fileExtension": ".go",
        "compileCommand": None,
        "runCommand": "go run main.go",
        "timeoutSeconds": 10,
        "memoryLimitMB": 128,
        "isEnabled": True,
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Rust 1.70",
        "language": CodeLanguage.RUST,
        "version": "1.70",
        "dockerImage": "rust:1.70-alpine",
        "fileExtension": ".rs",
        "compileCommand": "rustc main.rs -o main",
        "runCommand": "./main",
        "timeoutSeconds": 15,
        "memoryLimitMB": 256,
        "isEnabled": True,
    },
    {
        "id": str(uuid.uuid4()),
        "name": "PHP 8.2",
        "language": CodeLanguage.PHP,
        "version": "8.2",
        "dockerImage": "php:8.2-alpine",
        "fileExtension": ".php",
        "compileCommand": None,
        "runCommand": "php main.php",
        "timeoutSeconds": 10,
        "memoryLimitMB": 128,
        "isEnabled": True,
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Ruby 3.2",
        "language": CodeLanguage.RUBY,
        "version": "3.2",
        "dockerImage": "ruby:3.2-alpine",
        "fileExtension": ".rb",
        "compileCommand": None,
        "runCommand": "ruby main.rb",
        "timeoutSeconds": 10,
        "memoryLimitMB": 128,
        "isEnabled": True,
    },
]


def init_languages():
    """Инициализация поддерживаемых языков в базе данных"""

    # Создаем сессию базы данных
    with Session(engine) as db:
        try:
            print("🚀 Инициализация поддерживаемых языков программирования...")

            # Проверяем, есть ли уже языки в БД
            existing_languages = db.query(SupportedLanguage).all()
            if existing_languages:
                print(
                    f"ℹ️  Найдено {len(existing_languages)} существующих языков в базе данных"
                )

                # Спрашиваем пользователя, нужно ли перезаписать
                response = input(
                    "Хотите перезаписать существующие данные? (y/N): "
                ).lower()
                if response != "y":
                    print("❌ Операция отменена")
                    return

                # Удаляем существующие языки
                db.query(SupportedLanguage).delete()
                print("🗑️  Удалены существующие языки")

            # Добавляем новые языки
            languages_added = 0
            for lang_config in SUPPORTED_LANGUAGES:
                language = SupportedLanguage(**lang_config)
                db.add(language)
                languages_added += 1
                print(f"➕ Добавлен: {lang_config['name']} ({lang_config['language']})")

            # Сохраняем изменения
            db.commit()

            print(
                f"\n✅ Успешно инициализировано {languages_added} языков программирования!"
            )
            print("\n📋 Добавленные языки:")

            # Выводим список добавленных языков
            for lang in SUPPORTED_LANGUAGES:
                status = "🟢" if lang["isEnabled"] else "🔴"
                print(f"  {status} {lang['name']} v{lang['version']}")
                print(f"     Docker: {lang['dockerImage']}")
                print(
                    f"     Timeout: {lang['timeoutSeconds']}s, Memory: {lang['memoryLimitMB']}MB"
                )
                print()

            print(
                "🎉 Инициализация завершена! Теперь можно использовать редактор кода."
            )

        except Exception as e:
            print(f"❌ Ошибка при инициализации языков: {e}")
            db.rollback()
            sys.exit(1)


def update_language_config(language_name: str, **updates):
    """Обновление конфигурации конкретного языка"""

    with Session(engine) as db:
        try:
            language = (
                db.query(SupportedLanguage)
                .filter(SupportedLanguage.name == language_name)
                .first()
            )

            if not language:
                print(f"❌ Язык '{language_name}' не найден")
                return

            # Применяем обновления
            for key, value in updates.items():
                if hasattr(language, key):
                    setattr(language, key, value)
                    print(f"✅ Обновлено {key}: {value}")
                else:
                    print(f"⚠️  Неизвестное поле: {key}")

            db.commit()
            print(f"✅ Конфигурация языка '{language_name}' обновлена")

        except Exception as e:
            print(f"❌ Ошибка при обновлении языка: {e}")
            db.rollback()


def list_languages():
    """Вывод списка всех языков в базе данных"""

    with Session(engine) as db:
        languages = db.query(SupportedLanguage).all()

        if not languages:
            print("📭 В базе данных нет поддерживаемых языков")
            return

        print(f"\n📋 Найдено {len(languages)} языков в базе данных:\n")

        for lang in languages:
            status = "🟢" if lang.isEnabled else "🔴"
            print(f"{status} {lang.name} v{lang.version}")
            print(f"   ID: {lang.id}")
            print(f"   Язык: {lang.language}")
            print(f"   Docker: {lang.dockerImage}")
            print(f"   Расширение: {lang.fileExtension}")
            if lang.compileCommand:
                print(f"   Компиляция: {lang.compileCommand}")
            print(f"   Запуск: {lang.runCommand}")
            print(f"   Лимиты: {lang.timeoutSeconds}s, {lang.memoryLimitMB}MB")
            print(f"   Создан: {lang.createdAt}")
            print()


def toggle_language(language_name: str):
    """Включение/выключение языка"""

    with Session(engine) as db:
        language = (
            db.query(SupportedLanguage)
            .filter(SupportedLanguage.name == language_name)
            .first()
        )

        if not language:
            print(f"❌ Язык '{language_name}' не найден")
            return

        language.isEnabled = not language.isEnabled
        status = "включен" if language.isEnabled else "выключен"
        emoji = "🟢" if language.isEnabled else "🔴"

        db.commit()
        print(f"{emoji} Язык '{language_name}' {status}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("📖 Использование:")
        print(
            "  python init_languages.py init                    # Инициализация языков"
        )
        print("  python init_languages.py list                    # Список языков")
        print(
            "  python init_languages.py toggle <name>           # Включить/выключить язык"
        )
        print(
            "  python init_languages.py update <name> key=value # Обновить конфигурацию"
        )
        sys.exit(1)

    command = sys.argv[1]

    if command == "init":
        init_languages()
    elif command == "list":
        list_languages()
    elif command == "toggle" and len(sys.argv) >= 3:
        toggle_language(sys.argv[2])
    elif command == "update" and len(sys.argv) >= 4:
        language_name = sys.argv[2]
        updates = {}
        for arg in sys.argv[3:]:
            if "=" in arg:
                key, value = arg.split("=", 1)
                # Попытка преобразовать типы
                if value.lower() == "true":
                    value = True
                elif value.lower() == "false":
                    value = False
                elif value.isdigit():
                    value = int(value)
                updates[key] = value

        if updates:
            update_language_config(language_name, **updates)
        else:
            print("❌ Не указаны параметры для обновления")
    else:
        print("❌ Неизвестная команда")
        sys.exit(1)
