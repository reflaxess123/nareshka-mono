#!/usr/bin/env python3
"""
Скрипт для генерации OpenAPI спецификации
Использование: python generate_openapi.py [--output=openapi.json]
"""

import argparse
import json
import sys
from pathlib import Path

# Добавляем текущую директорию в PATH для импорта
sys.path.insert(0, str(Path(__file__).parent))

from main import app


def generate_openapi(output_file: str = "openapi.json") -> None:
    """Генерирует OpenAPI спецификацию и сохраняет в файл"""
    try:
        # Генерируем OpenAPI schema
        openapi_schema = app.openapi()
        
        # Сохраняем в файл
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(openapi_schema, f, ensure_ascii=False, indent=2)
        
        print(f"✅ OpenAPI спецификация успешно сгенерирована: {output_file}")
        print(f"📊 Найдено {len(openapi_schema.get('paths', {}))} endpoints")
        
    except Exception as e:
        print(f"❌ Ошибка генерации OpenAPI: {e}")
        sys.exit(1)


def main():
    """Основная функция CLI"""
    parser = argparse.ArgumentParser(description="Генератор OpenAPI спецификации")
    parser.add_argument(
        "--output", 
        default="openapi.json",
        help="Выходной файл для OpenAPI спецификации (по умолчанию: openapi.json)"
    )
    
    args = parser.parse_args()
    generate_openapi(args.output)


if __name__ == "__main__":
    main() 