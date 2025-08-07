#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Улучшенный парсер для Markdown файлов v2
Исправляет критические проблемы с извлечением компаний
"""

import re
import json
import hashlib
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Set
import logging
from difflib import get_close_matches

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


@dataclass
class InterviewItem:
    """Единица данных интервью"""
    interview_id: str
    company: str
    source: str = 'markdown'
    type: str = ''
    text: str = ''
    date: str = ''
    time: str = ''
    salary_range: str = ''
    level: str = ''
    duration: str = ''
    topics: str = ''
    complexity: str = ''
    question_number: str = ''
    sender: str = ''
    original_filename: str = ''  # Добавлено для отладки


class MarkdownParserV2:
    """Улучшенный парсер Markdown файлов"""

    def __init__(self):
        self.items: List[InterviewItem] = []
        self.stats = {
            'files': 0,
            'questions': 0,
            'tasks': 0,
            'codes': 0,
            'skipped_duplicate': 0,
            'companies_extracted': 0,
            'companies_from_list': 0,
            'unknown_companies': 0
        }
        self.seen_texts = set()
        self._load_companies_list()
        self._load_companies_extracted()  # Новый метод
        self._compile_patterns()

    def _load_companies_extracted(self):
        """Загрузка точных привязок файл->компания из companies_extracted.md"""
        self.file_to_company = {}

        companies_extracted_file = Path(r'/sobes-data/companies_extracted.md')
        if companies_extracted_file.exists():
            with open(companies_extracted_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Парсим структуру: ### 36. filename.md -> **Компания**: название
            pattern = r'###\s+\d+\.\s+([^\n]+\.md)\s*\n.*?-\s*\*\*Компания\*\*:\s*([^\n]+)'
            matches = re.findall(pattern, content, re.DOTALL)

            for filename, company in matches:
                # Очищаем имя файла от лишних пробелов
                filename = filename.strip()
                company = company.strip()

                # Пропускаем файлы без названия компании
                if company.lower() not in ['нет названия компании', 'не указано', '']:
                    self.file_to_company[filename] = company

            logger.info(f"Загружено {len(self.file_to_company)} точных привязок файл->компания")
        else:
            logger.warning("Файл companies_extracted.md не найден")
            self.file_to_company = {}

    def _load_companies_list(self):
        """Загрузка списка всех возможных компаний"""
        companies_file = Path(r'/sobes-data/companies_final_clean.json')
        if companies_file.exists():
            with open(companies_file, 'r', encoding='utf-8') as f:
                self.all_companies = json.load(f)
                # Создаем множество для быстрого поиска
                self.companies_set = set(self.all_companies)
                # Создаем словарь для нормализации
                self.companies_lower = {c.lower(): c for c in self.all_companies}
                logger.info(f"Загружено {len(self.all_companies)} компаний из справочника")
        else:
            self.all_companies = []
            self.companies_set = set()
            self.companies_lower = {}

    def _compile_patterns(self):
        """Компиляция регулярных выражений"""

        # УЛУЧШЕННЫЕ паттерны для таблиц (более гибкие к пробелам)
        self.re_table_simple = re.compile(
            r'\|\s*№\s*\|\s*Вопрос\s*\|\s*Тем[ыа]?\s*\|[^\n]*\n'
            r'(?:\|[\s\-:|]+\|\n)?'
            r'((?:\|[^\n]+\|\n?)+)',
            re.MULTILINE | re.IGNORECASE
        )

        self.re_table_extended = re.compile(
            r'\|\s*№\s*\|\s*Вопрос\s*\|(?:\s*Тип\s*\|)?(?:\s*Сложность\s*\|)?\s*Тем[ыа]?\s*\|[^\n]*\n'
            r'(?:\|[\s\-:|]+\|\n)?'
            r'((?:\|[^\n]+\|\n?)+)',
            re.MULTILINE | re.IGNORECASE
        )

        # Метаданные
        self.re_duration = re.compile(r'Длительность:\s*([0-9.]+)\s*мин')
        self.re_question_count = re.compile(r'Количество вопросов:\s*(\d+)')
        self.re_date_in_filename = re.compile(r'(\d{4}-\d{2}-\d{2})')

        # Компания из содержимого
        self.re_company_patterns = [
            re.compile(r'Компания:\s*([^\n]+)'),
            re.compile(r'Собеседование\s+в\s+([^\n]+)'),
            re.compile(r'Интервью:\s*([^\n]+)'),
        ]

        # УЛУЧШЕННЫЕ паттерны для имени файла
        self.re_company_filename_patterns = [
            re.compile(r'interview[_\s]+([a-zA-Z]+)', re.IGNORECASE),
            re.compile(r'собес[_\s]+([А-Яа-яЁё]+)', re.IGNORECASE),
            re.compile(r'Frontend[-_]React[-_]([А-ЯЁ][а-яё]+)'),
            re.compile(r'sobes[_\s]+([a-zA-Z]+)', re.IGNORECASE),
            # Новые паттерны для сложных имен
            re.compile(r'_([А-ЯЁ][а-яё]+(?:[_\s][А-ЯЁ][а-яё]+)*)_'),
            re.compile(r'_([A-Z][a-z]+(?:[A-Z][a-z]+)*)_'),  # CamelCase
        ]

        # Зарплата и уровень
        self.re_salary_patterns = [
            re.compile(r'(?:ЗП|Зарплата|Вилка):\s*([^\n]+)'),
            re.compile(r'(\d{2,3})\s*(?:тыс|т\.р|к)(?:\s*-\s*\d{2,3})?'),
        ]

        self.re_level_patterns = [
            re.compile(r'Уровень:\s*([^\n]+)'),
            re.compile(r'(?:junior|middle|senior|джун|мидл|синьор)', re.IGNORECASE),
        ]

        # Технические части имени файла для исключения
        self.technical_parts = {
            'full', 'report', 'transcript', 'llm', 'water', 'bpm',
            'null', 'audio', 'video', 'mp3cut', 'online', 'converter',
            'com', 'net', 'blured', 'copy', 'копия', 'final', 'draft'
        }

    def _find_company_in_list(self, text: str) -> Optional[str]:
        """Поиск компании в справочнике с fuzzy matching"""
        text_lower = text.lower().strip()

        # Точное совпадение (case-insensitive)
        if text_lower in self.companies_lower:
            return self.companies_lower[text_lower]

        # Частичное совпадение
        for company_lower, company in self.companies_lower.items():
            if company_lower in text_lower or text_lower in company_lower:
                return company

        # Fuzzy matching для похожих названий
        close_matches = get_close_matches(text, self.all_companies, n=1, cutoff=0.8)
        if close_matches:
            return close_matches[0]

        return None

    def _normalize_company_name(self, name: str) -> str:
        """Улучшенная нормализация названия компании"""
        if not name:
            return ""

        # Убираем технические суффиксы
        name = re.sub(r'_transcript.*$', '', name, flags=re.IGNORECASE)
        name = re.sub(r'_report.*$', '', name, flags=re.IGNORECASE)
        name = re.sub(r'_water.*$', '', name, flags=re.IGNORECASE)
        name = re.sub(r'_FULL.*$', '', name, flags=re.IGNORECASE)
        name = re.sub(r'_llm.*$', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\s*\([^)]*\).*$', '', name)
        name = re.sub(r'^\d+_', '', name)
        name = name.replace('_', ' ').strip()

        # Проверяем в справочнике компаний
        found_company = self._find_company_in_list(name)
        if found_company:
            self.stats['companies_from_list'] += 1
            return found_company

        # Ручной маппинг для частых случаев
        name_map = {
            'gazprombank': 'Газпромбанк',
            'gazprom': 'Газпромбанк',
            'sber': 'Сбер',
            'сбер': 'Сбер',
            'сбербанк': 'Сбер',
            'домклик': 'Domclick',
            'domclick': 'Domclick',
            'yandex': 'Яндекс',
            'яндекс': 'Яндекс',
            'vtb': 'ВТБ',
            'втб': 'ВТБ',
            'alfa': 'Альфа-Банк',
            'alphabank': 'Альфа-Банк',
            'альфа': 'Альфа-Банк',
            'tbank': 'Т-Банк',
            'тинькофф': 'Т-Банк',
            'cian': 'Циан',
            'циан': 'Циан',
            'avito': 'Авито',
            'авито': 'Авито',
            'ozon': 'Ozon',
            'озон': 'Ozon',
            'wildberries': 'Wildberries',
            'вб': 'Wildberries',
            'usetech': 'Usetech',
            'exness': 'Exness',
            'innotech': 'Иннотех',
            'иннотех': 'Иннотех',
            'getmatch': 'GetMatch',
            'kodix': 'Kodix',
            'кодикс': 'Kodix',
            'вск': 'ВСК',
            'vsk': 'ВСК',
            'пурвеб': 'Purrweb',
            'purrweb': 'Purrweb',
        }

        name_lower = name.lower().strip()
        for key, value in name_map.items():
            if key in name_lower:
                return value

        # Капитализация
        if name and not name[0].isupper():
            name = ' '.join(word.capitalize() for word in name.split())

        return name[:100] if name else ""

    def _extract_company_from_filename(self, filename: str) -> str:
        """КРИТИЧЕСКИ УЛУЧШЕННОЕ извлечение компании из имени файла"""
        # Убираем расширение
        base_name = filename.replace('.md', '')

        # Убираем ID пользователя в начале
        base_name = re.sub(r'^\d{10}_\d{3,4}_', '', base_name)

        # Пробуем паттерны
        for pattern in self.re_company_filename_patterns:
            match = pattern.search(base_name)
            if match:
                potential_company = match.group(1)
                # Проверяем, что это не техническая часть
                if potential_company.lower() not in self.technical_parts:
                    normalized = self._normalize_company_name(potential_company)
                    if normalized and normalized != "Unknown":
                        return normalized

        # Разбиваем на части и ищем компанию
        parts = re.split(r'[_\-\s]+', base_name)
        for part in parts:
            # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: пропускаем технические части
            if part.lower() in self.technical_parts:
                continue

            # Проверяем в справочнике
            found = self._find_company_in_list(part)
            if found:
                return found

            # Если часть похожа на название компании
            if len(part) > 3 and part[0].isupper() and not part.isdigit():
                normalized = self._normalize_company_name(part)
                if normalized and normalized != "Unknown":
                    return normalized

        return ""

    def _extract_metadata(self, content: str, filename: str) -> Dict:
        """Извлечение метаданных"""
        metadata = {'original_filename': filename}

        # ПРИОРИТЕТ 1: Точная привязка из companies_extracted.md
        if filename in self.file_to_company:
            metadata['company'] = self.file_to_company[filename]
            self.stats['companies_extracted'] += 1
            logger.debug(f"Найдена точная привязка: {filename} -> {self.file_to_company[filename]}")
        else:
            # ПРИОРИТЕТ 2: Компания из содержимого файла
            for pattern in self.re_company_patterns:
                match = pattern.search(content)
                if match:
                    company = self._normalize_company_name(match.group(1))
                    if company and company != "Unknown":
                        metadata['company'] = company
                        self.stats['companies_extracted'] += 1
                        break

            # ПРИОРИТЕТ 3: Если не нашли в содержимом, ищем в имени файла
            if 'company' not in metadata:
                company = self._extract_company_from_filename(filename)
                if company:
                    metadata['company'] = company
                    self.stats['companies_extracted'] += 1
                else:
                    metadata['company'] = 'Unknown'
                    self.stats['unknown_companies'] += 1

        # Дата из имени файла
        match = self.re_date_in_filename.search(filename)
        if match:
            metadata['date'] = match.group(1)

        # Длительность и количество вопросов
        match = self.re_duration.search(content)
        if match:
            metadata['duration'] = match.group(1)

        match = self.re_question_count.search(content)
        if match:
            metadata['question_count'] = match.group(1)

        # Зарплата и уровень
        for pattern in self.re_salary_patterns:
            match = pattern.search(content)
            if match:
                metadata['salary_range'] = match.group(1).strip()
                break

        for pattern in self.re_level_patterns:
            match = pattern.search(content)
            if match:
                level_text = match.group(0) if match.lastindex == 0 else match.group(1)
                level_lower = level_text.lower()
                if 'junior' in level_lower or 'джун' in level_lower:
                    metadata['level'] = 'junior'
                elif 'middle' in level_lower or 'мидл' in level_lower:
                    metadata['level'] = 'middle'
                elif 'senior' in level_lower or 'синьор' in level_lower:
                    metadata['level'] = 'senior'
                break

        return metadata

    def _parse_table_row(self, row: str) -> Optional[Dict]:
        """Улучшенный парсинг строки таблицы"""
        # Разбиваем по |, убираем пустые
        cells = [cell.strip() for cell in row.split('|') if cell.strip()]

        if len(cells) < 2:
            return None

        # Проверяем, что первая ячейка - номер
        if not cells[0].replace('.', '').isdigit():
            return None

        result = {
            'number': cells[0].replace('.', ''),
            'text': cells[1],
            'type': 'question'
        }

        # Улучшенная классификация типа
        text_lower = cells[1].lower()
        if any(keyword in text_lower for keyword in
               ['напиши', 'реализуй', 'создай', 'implement', 'реши', 'оптимизируй']):
            result['type'] = 'task'
        elif 'function' in text_lower or 'const' in text_lower or 'class' in text_lower:
            result['type'] = 'code'

        # Дополнительные поля
        if len(cells) == 3:
            result['topics'] = cells[2]
        elif len(cells) >= 4:
            # ��ожет быть разный порядок колонок
            if len(cells) == 4:
                # № | Вопрос | Тип | Темы
                if cells[2] in ['direct', 'clarification', 'behavioral', 'task', 'code']:
                    result['question_type'] = cells[2]
                    result['topics'] = cells[3]
                else:
                    result['topics'] = cells[2]
            elif len(cells) >= 5:
                # № | Вопрос | Тип | Сложность | Темы
                result['question_type'] = cells[2]
                result['complexity'] = cells[3]
                result['topics'] = cells[4]

        return result

    def _extract_from_tables(self, content: str) -> List[Dict]:
        """Извлечение из таблиц с улучшенными паттернами"""
        items = []

        # Пробуем оба паттерна
        for pattern in [self.re_table_extended, self.re_table_simple]:
            match = pattern.search(content)
            if match:
                table_body = match.group(1)
                rows = table_body.strip().split('\n')

                for row in rows:
                    parsed = self._parse_table_row(row)
                    if parsed and len(parsed['text']) > 10:
                        items.append(parsed)

                if items:  # Если нашли данные, выходим
                    break

        return items

    def parse_file(self, filepath: Path) -> List[InterviewItem]:
        """Парсинг одного файла"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            filename = filepath.name

            # Извлекаем метаданные
            metadata = self._extract_metadata(content, filename)

            # Определяем компанию
            company = metadata.get('company', 'Unknown')

            # Извлекаем элементы
            items = self._extract_from_tables(content)

            # Создаем записи
            file_items = []
            base_id = f"{company}_{metadata.get('date', 'nodate')}_md_{self.stats['files']}"

            for idx, item in enumerate(items):
                # Дедупликация
                text_hash = hashlib.md5(item['text'].encode('utf-8')).hexdigest()
                if text_hash in self.seen_texts:
                    self.stats['skipped_duplicate'] += 1
                    continue

                self.seen_texts.add(text_hash)

                # Создаем запись
                interview_item = InterviewItem(
                    interview_id=f"{base_id}_{idx}_{text_hash[:8]}",
                    company=company,
                    source='markdown',
                    type=item.get('type', 'question'),
                    text=item['text'],
                    date=metadata.get('date', ''),
                    duration=metadata.get('duration', ''),
                    salary_range=metadata.get('salary_range', ''),
                    level=metadata.get('level', ''),
                    topics=item.get('topics', ''),
                    complexity=item.get('complexity', ''),
                    question_number=item.get('number', str(idx + 1)),
                    original_filename=filename
                )

                file_items.append(interview_item)

                # Статистика
                item_type = item.get('type', 'question')
                if item_type == 'question':
                    self.stats['questions'] += 1
                elif item_type == 'task':
                    self.stats['tasks'] += 1
                elif item_type == 'code':
                    self.stats['codes'] += 1

            return file_items

        except Exception as e:
            logger.error(f"Ошибка в {filepath.name}: {e}")
            return []

    def parse_directory(self, directory: Path) -> List[InterviewItem]:
        """Парсинг директории"""
        logger.info(f"Парсинг Markdown файлов из: {directory}")

        md_files = list(directory.glob('*.md'))
        logger.info(f"Найдено {len(md_files)} файлов")

        for idx, filepath in enumerate(md_files, 1):
            if idx % 20 == 0:
                logger.info(f"  Обработано {idx}/{len(md_files)} файлов...")

            self.stats['files'] += 1
            file_items = self.parse_file(filepath)
            self.items.extend(file_items)

        logger.info(f"\nИзвлечено из Markdown: {len(self.items)} записей")
        logger.info(f"  Вопросов: {self.stats['questions']}")
        logger.info(f"  Задач: {self.stats['tasks']}")
        logger.info(f"  Кода: {self.stats['codes']}")
        logger.info(f"  Компаний извлечено: {self.stats['companies_extracted']}")
        logger.info(f"  Компаний из справочника: {self.stats['companies_from_list']}")
        logger.info(f"  Unknown компаний: {self.stats['unknown_companies']}")

        return self.items


def main():
    """Тестовый запуск"""
    parser = MarkdownParserV2()
    reports_dir = Path(r'/sobes-data/reports')

    if reports_dir.exists():
        items = parser.parse_directory(reports_dir)

        # Сохраняем результат
        import json
        output_path = Path(r'C:\Users\refla\nareshka-mono\parsed_markdown_v2.json')

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump([asdict(item) for item in items], f, ensure_ascii=False, indent=2)

        print(f"\n✅ Сохранено в {output_path}")
    else:
        print(f"❌ Директория не найдена: {reports_dir}")


if __name__ == "__main__":
    main()
