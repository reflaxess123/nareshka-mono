#!/usr/bin/env python3
"""
Скрипт для инициализации поддерживаемых языков программирования
"""

import os
import sys
from pathlib import Path

# Добавляем корневую директорию в PYTHONPATH
back_dir = Path(__file__).parent.parent
sys.path.append(str(back_dir))

# Переходим в back директорию для импортов
os.chdir(str(back_dir))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.settings import settings
from app.shared.database.models import BaseModel
from app.shared.models.code_execution_models import SupportedLanguage

# Создаем подключение к БД
database_url = settings.database_url
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

engine = create_engine(database_url, pool_pre_ping=True, pool_recycle=300)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_supported_languages():
    """Инициализация поддерживаемых языков программирования"""

    # Создаем таблицы если их нет
    BaseModel.metadata.create_all(bind=engine)

    session = SessionLocal()

    try:
        # Проверяем, есть ли уже языки в БД
        existing_count = session.query(SupportedLanguage).count()
        if existing_count > 0:
            print(f"В базе уже есть {existing_count} языков. Пропускаем инициализацию.")
            return

        # Список поддерживаемых языков
        languages_data = [
            {
                "id": "python",
                "name": "Python",
                "language": "python",
                "version": "3.11",
                "fileExtension": ".py",
                "timeoutSeconds": 30,
                "memoryLimitMB": 128,
                "isEnabled": True,
            },
            {
                "id": "javascript",
                "name": "JavaScript (Node.js)",
                "language": "javascript",
                "version": "18",
                "fileExtension": ".js",
                "timeoutSeconds": 30,
                "memoryLimitMB": 128,
                "isEnabled": True,
            },
            {
                "id": "java",
                "name": "Java",
                "language": "java",
                "version": "17",
                "fileExtension": ".java",
                "timeoutSeconds": 45,
                "memoryLimitMB": 256,
                "isEnabled": True,
            },
            {
                "id": "cpp",
                "name": "C++",
                "language": "cpp",
                "version": "17",
                "fileExtension": ".cpp",
                "timeoutSeconds": 30,
                "memoryLimitMB": 128,
                "isEnabled": True,
            },
            {
                "id": "c",
                "name": "C",
                "language": "c",
                "version": "11",
                "fileExtension": ".c",
                "timeoutSeconds": 30,
                "memoryLimitMB": 128,
                "isEnabled": True,
            },
            {
                "id": "go",
                "name": "Go",
                "language": "go",
                "version": "1.21",
                "fileExtension": ".go",
                "timeoutSeconds": 30,
                "memoryLimitMB": 128,
                "isEnabled": True,
            },
            {
                "id": "rust",
                "name": "Rust",
                "language": "rust",
                "version": "1.70",
                "fileExtension": ".rs",
                "timeoutSeconds": 45,
                "memoryLimitMB": 256,
                "isEnabled": True,
            },
        ]

        # Добавляем языки в БД
        for lang_data in languages_data:
            language = SupportedLanguage(**lang_data)
            session.add(language)

        session.commit()
        print(f"✅ Успешно добавлено {len(languages_data)} поддерживаемых языков")

        # Выводим список добавленных языков
        for lang_data in languages_data:
            print(f"  - {lang_data['name']} ({lang_data['version']})")

    except Exception as e:
        session.rollback()
        print(f"❌ Ошибка при инициализации языков: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    print("🚀 Инициализация поддерживаемых языков программирования...")
    init_supported_languages()
    print("✅ Инициализация завершена!")
