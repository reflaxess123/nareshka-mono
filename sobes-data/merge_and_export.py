#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Улучшенный скрипт объединения и экспорта v2
Исправляет критические проблемы с CSV и добавляет лучшую дедупликацию
"""

import json
import csv
import hashlib
from pathlib import Path
from typing import List, Dict
from collections import Counter, defaultdict
import logging
import sys

# Для Parquet
try:
    import pandas as pd
    import pyarrow.parquet as pq
    PARQUET_AVAILABLE = True
except ImportError:
    PARQUET_AVAILABLE = False
    print("⚠️  Для Parquet установите: pip install pandas pyarrow")

sys.stdout.reconfigure(encoding='utf-8')
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


class DataMergerV2:
    """Улучшенный класс для объединения данных"""

    def __init__(self):
        self.all_items = []
        self.clean_items = []
        self.stats = defaultdict(int)
        self.seen_hashes = set()
        self.company_fixes = {
            'Full': None,  # Будет удалено
            'Unknown': None  # Будет пытаться восстановить
        }

    def run_parsers(self):
        """Запуск улучшенных парсеров"""
        logger.info("=" * 60)
        logger.info("ЗАПУСК УЛУЧШЕННЫХ ПАРСЕРОВ")
        logger.info("=" * 60)

        # JSON парсер (используем старый, он работает нормально)
        from parser_json import JSONParser
        json_parser = JSONParser()
        json_path = Path(r'/sobes-data/MASSIV_GROUPED.json')

        if json_path.exists():
            json_items = json_parser.parse_file(json_path)

            json_output = Path('parsed_json.json')
            with open(json_output, 'w', encoding='utf-8') as f:
                from dataclasses import asdict
                json.dump([asdict(item) for item in json_items], f, ensure_ascii=False, indent=2)

        # Markdown парсер V2 (улучшенный)
        from parser_markdown import MarkdownParserV2
        md_parser = MarkdownParserV2()
        reports_dir = Path(r'/sobes-data/reports')

        if reports_dir.exists():
            md_items = md_parser.parse_directory(reports_dir)

            md_output = Path('parsed_markdown_v2.json')
            with open(md_output, 'w', encoding='utf-8') as f:
                from dataclasses import asdict
                json.dump([asdict(item) for item in md_items], f, ensure_ascii=False, indent=2)

    def fix_company_name(self, company: str, item: Dict) -> str:
        """Исправление проблемных названий компаний"""
        if not company or company == 'Full':
            # Пытаемся извлечь из original_filename если есть
            if 'original_filename' in item:
                filename = item['original_filename']
                # Простые паттерны для восстановления
                if 'gazprom' in filename.lower():
                    return 'Газпромбанк'
                elif 'sber' in filename.lower() or 'сбер' in filename.lower():
                    return 'Сбер'
                elif 'alfa' in filename.lower() or 'альфа' in filename.lower():
                    return 'Альфа-Банк'
                elif 'yandex' in filename.lower() or 'яндекс' in filename.lower():
                    return 'Яндекс'
            return 'Unknown'

        return company

    def clean_text(self, text: str) -> str:
        """Очистка текста"""
        # Убираем лишние пробелы и переносы
        text = ' '.join(text.split())

        # Ограничиваем длину
        if len(text) > 3000:
            text = text[:2997] + '...'

        return text.strip()

    def is_valid_item(self, item: Dict) -> bool:
        """Валидация записи"""
        text = item.get('text', '').strip()

        # Минимальная длина
        if len(text) < 15:
            self.stats['rejected_short'] += 1
            return False

        # Исключаем технический мусор
        garbage = ['use strict', '// ---', '/*', '*/', '...', '.', '', 'undefined', 'null']
        if text in garbage:
            self.stats['rejected_garbage'] += 1
            return False

        # Компания не должна быть Full
        if item.get('company') == 'Full':
            item['company'] = self.fix_company_name('Full', item)

        return True

    def classify_type(self, item: Dict) -> str:
        """Улучшенная классификация типа"""
        text = item.get('text', '').lower()

        # Код - если есть синтаксис языков программирования
        code_indicators = [
            'function ', 'const ', 'let ', 'var ', 'class ',
            'return ', 'if (', 'for (', 'while (',
            '=>', '===', '!==', '```'
        ]
        if any(indicator in text for indicator in code_indicators):
            return 'code'

        # Задачи - императивные формулировки
        task_keywords = [
            'напиши', 'напишите', 'реализуй', 'реализуйте',
            'создай', 'создайте', 'implement', 'write',
            'реши', 'решите', 'оптимизируй', 'исправь',
            'доработай', 'добавь', 'измени'
        ]
        if any(keyword in text for keyword in task_keywords):
            return 'task'

        # По умолчанию - вопрос
        return 'question'

    def merge_data(self):
        """Объединение данных"""
        logger.info("\n" + "=" * 60)
        logger.info("ОБЪЕДИНЕНИЕ ДАННЫХ")
        logger.info("=" * 60)

        # Загружаем данные
        json_data = []
        json_path = Path('parsed_json.json')
        if json_path.exists():
            with open(json_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)

        md_data = []
        md_path = Path('parsed_markdown_v2.json')
        if md_path.exists():
            with open(md_path, 'r', encoding='utf-8') as f:
                md_data = json.load(f)

        self.all_items = json_data + md_data
        logger.info(f"Всего загружено: {len(self.all_items)} записей")

        # Обработка
        for item in self.all_items:
            # Очистка текста
            item['text'] = self.clean_text(item['text'])

            # Исправление компаний
            item['company'] = self.fix_company_name(item.get('company', ''), item)

            # Переклассификация типа если нужно
            if item.get('type') == 'question' and len(item['text']) > 50:
                item['type'] = self.classify_type(item)

        # Фильтрация
        valid_items = [item for item in self.all_items if self.is_valid_item(item)]
        logger.info(f"После фильтрации: {len(valid_items)} записей")

        # Дедупликация
        seen = set()
        unique_items = []
        for item in valid_items:
            # Создаем хеш
            text_normalized = item['text'].lower().strip()
            text_hash = hashlib.md5(text_normalized.encode('utf-8')).hexdigest()

            if text_hash not in seen:
                seen.add(text_hash)
                unique_items.append(item)
                self.stats[f"type_{item['type']}"] += 1
                self.stats[f"source_{item['source']}"] += 1
            else:
                self.stats['duplicates_removed'] += 1

        self.clean_items = unique_items
        logger.info(f"После дедупликации: {len(self.clean_items)} записей")

    def export_csv(self, output_path: Path):
        """КРИТИЧЕСКИ УЛУЧШЕННЫЙ экспорт в CSV"""
        logger.info(f"\nЭкспорт в CSV: {output_path}")

        fieldnames = [
            'interview_id', 'company', 'source', 'type', 'text',
            'date', 'time', 'salary_range', 'level', 'duration',
            'topics', 'complexity', 'question_number', 'sender'
        ]

        # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: правильное экранирование
        with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(
                f,
                fieldnames=fieldnames,
                quoting=csv.QUOTE_ALL,  # Экранируем все поля
                quotechar='"',
                escapechar='\\',
                doublequote=True  # Удваиваем кавычки внутри полей
            )
            writer.writeheader()

            # Убираем лишние поля перед записью
            rows_to_write = []
            for item in self.clean_items:
                row = {field: item.get(field, '') for field in fieldnames}
                rows_to_write.append(row)

            writer.writerows(rows_to_write)

        logger.info(f"✅ CSV сохранен: {len(self.clean_items)} записей")

    def export_parquet(self, output_path: Path):
        """Экспорт в Parquet"""
        if not PARQUET_AVAILABLE:
            logger.warning("⚠️  Parquet недоступен")
            return

        logger.info(f"\nЭкспорт в Parquet: {output_path}")

        # Создаем DataFrame
        df = pd.DataFrame(self.clean_items)

        # Убираем лишние колонки
        columns_to_keep = [
            'interview_id', 'company', 'source', 'type', 'text',
            'date', 'time', 'salary_range', 'level', 'duration',
            'topics', 'complexity', 'question_number', 'sender'
        ]

        for col in columns_to_keep:
            if col not in df.columns:
                df[col] = ''

        df = df[columns_to_keep]

        # Сохраняем
        df.to_parquet(output_path, engine='pyarrow', compression='snappy', index=False)

        size_mb = output_path.stat().st_size / 1024 / 1024
        logger.info(f"✅ Parquet сохранен: {len(df)} записей ({size_mb:.2f} MB)")

    def print_statistics(self):
        """Статистика"""
        logger.info("\n" + "=" * 60)
        logger.info("ФИНАЛЬНАЯ СТАТИСТИКА")
        logger.info("=" * 60)

        logger.info(f"\n📊 Итоги:")
        logger.info(f"  Всего записей: {len(self.clean_items)}")
        logger.info(f"  Дубликатов удалено: {self.stats['duplicates_removed']}")
        logger.info(f"  Отклонено коротких: {self.stats['rejected_short']}")

        logger.info(f"\n📝 По типам:")
        logger.info(f"  Вопросов: {self.stats['type_question']}")
        logger.info(f"  Задач: {self.stats['type_task']}")
        logger.info(f"  Кода: {self.stats['type_code']}")

        logger.info(f"\n📁 По источникам:")
        logger.info(f"  Из JSON: {self.stats['source_json']}")
        logger.info(f"  Из Markdown: {self.stats['source_markdown']}")

        # Топ компаний
        companies = Counter(item['company'] for item in self.clean_items)
        logger.info(f"\n🏢 Топ-10 компаний:")
        for company, count in companies.most_common(10):
            pct = count * 100 / len(self.clean_items)
            logger.info(f"  {company}: {count} ({pct:.1f}%)")

        # Проверка проблем
        full_count = companies.get('Full', 0)
        unknown_count = companies.get('Unknown', 0)

        if full_count > 0:
            logger.warning(f"\n⚠️  Осталось {full_count} записей с 'Full'")
        if unknown_count > 100:
            logger.warning(f"⚠️  {unknown_count} записей с 'Unknown'")
        else:
            logger.info(f"\n✅ Проблема с 'Full' исправлена!")
            logger.info(f"✅ Unknown сокращено до {unknown_count} записей")


def main():
    """Основная функция"""
    logger.info("=" * 60)
    logger.info("УЛУЧШЕННАЯ ОБРАБОТКА ДАННЫХ v2")
    logger.info("=" * 60)

    merger = DataMergerV2()

    # Запускаем парсеры
    merger.run_parsers()

    # Объединяем
    merger.merge_data()

    # Экспортируем
    csv_path = Path('interview_questions_v2.csv')
    merger.export_csv(csv_path)

    parquet_path = Path('interview_questions_v2.parquet')
    merger.export_parquet(parquet_path)

    # Статистика
    merger.print_statistics()

    logger.info("\n✅ Обработка завершена!")


if __name__ == "__main__":
    main()
