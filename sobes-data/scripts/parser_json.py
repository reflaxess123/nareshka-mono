#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Парсер для JSON файла MASSIV_GROUPED.json
Извлекает вопросы, задачи и код из неструктурированного текста
"""

import json
import re
import hashlib
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
import logging
from difflib import get_close_matches

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


@dataclass
class InterviewItem:
    """Единица данных интервью"""
    interview_id: str
    company: str
    source: str = 'json'
    type: str = ''  # question/task/code
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


class JSONParser:
    """Парсер JSON данных собеседований"""

    def __init__(self):
        self.items: List[InterviewItem] = []
        self.stats = {
            'companies': 0,
            'records': 0,
            'questions': 0,
            'tasks': 0,
            'codes': 0,
            'skipped_short': 0,
            'skipped_duplicate': 0,
            'companies_from_list': 0,
            'companies_fuzzy_matched': 0
        }
        self.seen_texts = set()  # Для дедупликации
        self._load_companies_list()
        self._compile_patterns()

    def _load_companies_list(self):
        """Загрузка списка всех возможных компаний"""
        companies_file = Path(r'/sobes-data/companies_final_clean.json')
        if companies_file.exists():
            with open(companies_file, 'r', encoding='utf-8') as f:
                self.all_companies = json.load(f)

                # Чистим проблемные записи
                cleaned_companies = []
                for company in self.all_companies:
                    # Исправляем опечатки и проблемы
                    if company.startswith('Копания:'):
                        company = company.replace('Копания:', '').strip()
                    elif company.startswith('Компани:'):
                        company = company.replace('Компани:', '').strip()
                    elif company.startswith('Компания:'):
                        company = company.replace('Компания:', '').strip()

                    # Убираем технические префиксы
                    company = re.sub(r'^(Ооо|ООО|OOO)\s+', '', company)
                    company = company.strip()

                    if company and len(company) > 1:
                        cleaned_companies.append(company)

                self.all_companies = cleaned_companies
                # Создаем множество для быстрого поиска
                self.companies_set = set(self.all_companies)
                # Создаем словарь для нормализации
                self.companies_lower = {c.lower(): c for c in self.all_companies}
                logger.info(f"Загружено {len(self.all_companies)} компаний из справочника")
        else:
            self.all_companies = []
            self.companies_set = set()
            self.companies_lower = {}
            logger.warning("Файл companies_final_clean.json не найден")

    def _find_company_in_list(self, text: str) -> Optional[str]:
        """Поиск компании в справочнике с fuzzy matching"""
        if not text:
            return None

        text_clean = text.strip()
        text_lower = text_clean.lower()

        # Точное совпадение (case-insensitive)
        if text_lower in self.companies_lower:
            self.stats['companies_from_list'] += 1
            return self.companies_lower[text_lower]

        # Частичное совпадение
        for company_lower, company in self.companies_lower.items():
            if len(company_lower) > 3:  # Избегаем слишком коротких совпадений
                if company_lower in text_lower or text_lower in company_lower:
                    self.stats['companies_from_list'] += 1
                    return company

        # Fuzzy matching для похожих названий
        close_matches = get_close_matches(text_clean, self.all_companies, n=1, cutoff=0.8)
        if close_matches:
            self.stats['companies_fuzzy_matched'] += 1
            return close_matches[0]

        return None

    def _compile_patterns(self):
        """Компиляция регулярных выражений"""
        # Метаданные
        self.re_date_time = re.compile(r'^(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2}:\d{2})', re.MULTILINE)
        self.re_sender = re.compile(r'\n\s*([^->\n]+?)\s*->\s*\d+:')

        # Ком��ания - несколько паттернов
        self.re_company_patterns = [
            re.compile(r'Компания:\s*([^\n]+)'),
            re.compile(r'iFellow\s+в\s+([^\n]+)'),
            re.compile(r'Собеседование\s+в\s+([^\n]+)'),
            re.compile(r'^([А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ][а-яё]+)*)\s+(?:\d+\s+этап|Финтех)', re.MULTILINE),
        ]

        # Зарплата - разные форматы
        self.re_salary_patterns = [
            re.compile(r'ЗП:?\s*(?:от\s*)?(\d+)(?:\s*-\s*(\d+))?(?:\s*(?:к|К|тыс|т\.р|000))?'),
            re.compile(r'(?:Зарплата|Оклад|Вилка):?\s*(\d+)(?:\s*-\s*(\d+))?'),
            re.compile(r'(\d{3})\s*(?:тыс|т\.р|000|к|К)(?:\s*-\s*(\d{3})\s*(?:тыс|т\.р|000|к|К))?'),
        ]

        # Уровень
        self.re_level = re.compile(
            r'\b(?:junior|middle|senior|jun|mid|sen|джун|мидл|синьор)\b',
            re.IGNORECASE
        )

        # ВОПРОСЫ - улучшенные паттерны
        # 1. Нумерованные вопросы со знаком ?
        self.re_question_numbered = re.compile(
            r'^(?:\s*)?(\d{1,3})[\.\)]\s*([^\n?]+\?)',
            re.MULTILINE
        )

        # 2. Вопросы в блоке "Вопросы:"
        self.re_questions_block = re.compile(
            r'Вопросы:\s*\n((?:[^\n]+\n){1,50}?)(?:\n\n|Задач|Ответ|---)',
            re.MULTILINE | re.DOTALL
        )

        # 3. Вопросы с ключевыми словами
        self.re_question_keywords = re.compile(
            r'^(?:\s*)?(?:\d{1,3}[\.\)])?\s*((?:Что такое|Что значит|Как работает|Как|Зачем|Почему|'
            r'Расскажи|Объясни|Опиши|Чем отличается|В чем разница|Какие|Какой|Когда|Где|Для чего)'
            r'[^?\n.]{10,300})[\.\n]',
            re.MULTILINE | re.IGNORECASE
        )

        # ЗАДАЧИ - улучшенные паттерны
        # 1. Явные задачи с номером
        self.re_task_numbered = re.compile(
            r'Задача\s+(\d+):?\s*\n?((?:(?!Задача\s+\d+|---|\n\n)[^\n].*\n?){1,30})',
            re.MULTILINE | re.DOTALL
        )

        # 2. Императивные задачи
        self.re_task_imperative = re.compile(
            r'^(?:\s*)?(?:\d{1,3}[\.\)])?\s*((?:Напиши|Напишите|Реализуй|Реализуйте|Создай|Создайте|'
            r'Разработай|Implement|Write|Create|Сделай|Построй|Найди|Реши|Доработай)'
            r'[^.\n]{15,400})',
            re.MULTILINE | re.IGNORECASE
        )

        # 3. Алгоритмические задачи
        self.re_task_algorithmic = re.compile(
            r'^(?:\s*)?(?:\d{1,3}[\.\)])?\s*((?:Дан|Дана|Даны|Дано|Есть|Имеется|Имеются|Задан)'
            r'[^.\n]*(?:массив|строка|список|объект|функция|дерево|граф|число)[^.\n]{15,400})',
            re.MULTILINE | re.IGNORECASE
        )

        # КОД - только значимые фрагменты
        self.re_code_functions = re.compile(
            r'(?:^|\n)((?:async\s+)?(?:function|const|let|var|class)\s+\w+[^\n]*\{[^}]*\})',
            re.MULTILINE | re.DOTALL
        )

        self.re_code_multiline = re.compile(
            r'(?:^|\n)((?:function|class|const|let|var)\s+\w+[^\n]*\n(?:(?:[ \t]+[^\n]*\n?)*\}?))',
            re.MULTILINE
        )

    def _normalize_company_name(self, name: str) -> str:
        """Улучшенная нормализация названия компании с использованием справочника"""
        if not name:
            return ""

        # Очистка от лишнего
        name = re.sub(r'\s+\d+\s+этап.*$', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\s+(?:Финтех|финтех).*$', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\s*\([^)]*\).*$', '', name)
        name = re.sub(r'\s+в\s+.*$', '', name)
        name = re.sub(r'^\d+\s+', '', name)
        name = re.sub(r'^-\s*', '', name)

        # ПРИОРИТЕТ 1: Проверяем в справочнике компаний
        found_company = self._find_company_in_list(name)
        if found_company:
            return found_company

        # ПРИОРИТЕТ 2: Стандартизация известных компаний (только для не найденных)
        name_map = {
            'сбер': 'Сбер',
            'sber': 'Сбер',
            'сбербанк': 'Сбер',
            'яндекс': 'Яндекс',
            'yandex': 'Яндекс',
            'втб': 'ВТБ',
            'vtb': 'ВТБ',
            'альфа': 'Альфа-Банк',
            'alfa': 'Альфа-Банк',
            'т-банк': 'Т-Банк',
            'tbank': 'Т-Банк',
            'тинькофф': 'Т-Банк',
            'avito': 'Авито',
            'авито': 'Авито',
            'озон': 'Ozon',
            'ozon': 'Ozon',
        }

        name_lower = name.lower().strip()
        for key, value in name_map.items():
            if key in name_lower:
                return value

        # ПРИОРИТЕТ 3: Капитализация для неизвестных
        name = ' '.join(word.capitalize() for word in name.strip().split())

        return name[:100]  # Ограничение длины

    def _extract_metadata(self, content: str, company_from_parent: str) -> Dict:
        """Извлечение метаданных из текста"""
        metadata = {'company': company_from_parent}

        # Дата и время
        match = self.re_date_time.search(content)
        if match:
            metadata['date'] = match.group(1)
            metadata['time'] = match.group(2)

        # Отправитель
        match = self.re_sender.search(content)
        if match:
            metadata['sender'] = match.group(1).strip()

        # Компания из текста (приоритетнее)
        for pattern in self.re_company_patterns:
            match = pattern.search(content)
            if match:
                extracted_company = self._normalize_company_name(match.group(1))
                if extracted_company and extracted_company != "Unknown":
                    metadata['company'] = extracted_company
                    break

        # Зарплата
        for pattern in self.re_salary_patterns:
            match = pattern.search(content)
            if match:
                salary = match.group(1)
                if match.lastindex >= 2 and match.group(2):
                    salary = f"{match.group(1)}-{match.group(2)}"
                metadata['salary_range'] = salary
                break

        # Уровень
        match = self.re_level.search(content)
        if match:
            level = match.group(0).lower()
            if 'jun' in level or 'джун' in level:
                metadata['level'] = 'junior'
            elif 'mid' in level or 'мидл' in level:
                metadata['level'] = 'middle'
            elif 'sen' in level or 'синьор' in level:
                metadata['level'] = 'senior'

        return metadata

    def _is_valid_text(self, text: str, min_length: int = 15) -> bool:
        """Проверка валидности текста"""
        if len(text) < min_length:
            return False

        # Исключаем чисто технические строки
        if text.strip() in ['use strict', '// ---', '/*', '*/', '...', '.', '']:
            return False

        # Исключаем одиночные объявления без содержания
        if re.match(r'^(const|let|var|function)\s+\w+\s*;?$', text.strip()):
            return False

        return True

    def _extract_questions(self, content: str) -> List[Dict]:
        """Извлечение вопросов"""
        questions = []

        # 1. Нумерованные вопросы
        for match in self.re_question_numbered.finditer(content):
            text = match.group(2).strip()
            if self._is_valid_text(text):
                questions.append({
                    'type': 'question',
                    'text': text,
                    'number': match.group(1)
                })

        # 2. Блок вопросов
        match = self.re_questions_block.search(content)
        if match:
            block = match.group(1)
            lines = block.split('\n')
            for line in lines:
                line = line.strip()
                # Убираем номер если есть
                line = re.sub(r'^\d{1,3}[\.\)]\s*', '', line)
                if self._is_valid_text(line, 10) and '?' in line:
                    # Проверяем на дубликат
                    if not any(line in q['text'] or q['text'] in line for q in questions):
                        questions.append({
                            'type': 'question',
                            'text': line,
                            'number': ''
                        })

        # 3. Вопросы с ключевыми словами
        for match in self.re_question_keywords.finditer(content):
            text = match.group(1).strip()
            if self._is_valid_text(text, 20):
                # Проверяем на дубликат
                if not any(text in q['text'] or q['text'] in text for q in questions):
                    questions.append({
                        'type': 'question',
                        'text': text,
                        'number': ''
                    })

        return questions

    def _extract_tasks(self, content: str) -> List[Dict]:
        """Извлечение задач"""
        tasks = []

        # 1. Нумерованные задачи
        for match in self.re_task_numbered.finditer(content):
            text = match.group(2).strip()
            if self._is_valid_text(text, 30):
                tasks.append({
                    'type': 'task',
                    'text': text[:1000],  # Ограничиваем длину
                    'number': match.group(1)
                })

        # 2. Императивные задачи
        for match in self.re_task_imperative.finditer(content):
            text = match.group(1).strip()
            if self._is_valid_text(text, 30):
                # Проверяем на дубликат
                if not any(text in t['text'] or t['text'] in text for t in tasks):
                    tasks.append({
                        'type': 'task',
                        'text': text[:1000],
                        'number': ''
                    })

        # 3. Алгоритмические задачи
        for match in self.re_task_algorithmic.finditer(content):
            text = match.group(1).strip()
            if self._is_valid_text(text, 30):
                # Проверяем на дубликат
                if not any(text in t['text'] or t['text'] in text for t in tasks):
                    tasks.append({
                        'type': 'task',
                        'text': text[:1000],
                        'number': ''
                    })

        return tasks

    def _extract_code(self, content: str) -> List[Dict]:
        """Извлечение фрагментов кода"""
        code_items = []

        # Функции с телом
        for match in self.re_code_functions.finditer(content):
            text = match.group(1).strip()
            if self._is_valid_text(text, 50):
                code_items.append({
                    'type': 'code',
                    'text': text[:1000],
                    'number': ''
                })

        # Многострочный код
        for match in self.re_code_multiline.finditer(content):
            text = match.group(1).strip()
            if self._is_valid_text(text, 50) and not any(text in c['text'] for c in code_items):
                code_items.append({
                    'type': 'code',
                    'text': text[:1000],
                    'number': ''
                })

        # Ограничиваем количество
        return code_items[:10]

    def parse_file(self, filepath: Path) -> List[InterviewItem]:
        """Основной метод парсинга JSON файла"""
        logger.info(f"Парсинг JSON: {filepath}")

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.stats['companies'] = len(data)
        logger.info(f"Найдено {len(data)} компаний")

        for idx, company_data in enumerate(data, 1):
            if idx % 50 == 0:
                logger.info(f"  Обработано {idx}/{len(data)} компаний...")

            if not isinstance(company_data, dict):
                continue

            company_name = self._normalize_company_name(company_data.get('company', ''))

            if 'records' not in company_data:
                continue

            for record_idx, record in enumerate(company_data['records']):
                if 'full_content' not in record:
                    continue

                self.stats['records'] += 1
                content = record['full_content']

                # Извлекаем метаданные
                metadata = self._extract_metadata(content, company_name)

                # Финальное название компании
                final_company = metadata.get('company', company_name)
                if not final_company or final_company == "Unknown":
                    final_company = company_name or "Unknown"

                # Извлекаем элементы
                questions = self._extract_questions(content)
                tasks = self._extract_tasks(content)
                code_items = self._extract_code(content)

                # Создаем записи
                base_id = f"{final_company}_{metadata.get('date', 'nodate')}_{idx}_{record_idx}"

                for item_idx, item in enumerate(questions + tasks + code_items):
                    # Проверка на дубликат
                    text_hash = hashlib.md5(item['text'].encode('utf-8')).hexdigest()
                    if text_hash in self.seen_texts:
                        self.stats['skipped_duplicate'] += 1
                        continue

                    self.seen_texts.add(text_hash)

                    # Создаем запись
                    interview_item = InterviewItem(
                        interview_id=f"{base_id}_{item_idx}_{text_hash[:8]}",
                        company=final_company,
                        source='json',
                        type=item['type'],
                        text=item['text'],
                        date=metadata.get('date', ''),
                        time=metadata.get('time', ''),
                        salary_range=metadata.get('salary_range', ''),
                        level=metadata.get('level', ''),
                        question_number=item.get('number', ''),
                        sender=metadata.get('sender', '')
                    )

                    self.items.append(interview_item)

                    # Обновляем статистику
                    if item['type'] == 'question':
                        self.stats['questions'] += 1
                    elif item['type'] == 'task':
                        self.stats['tasks'] += 1
                    elif item['type'] == 'code':
                        self.stats['codes'] += 1

        logger.info(f"Извлечено из JSON: {len(self.items)} записей")
        logger.info(f"  Вопросов: {self.stats['questions']}")
        logger.info(f"  Задач: {self.stats['tasks']}")
        logger.info(f"  Кода: {self.stats['codes']}")
        logger.info(f"  Пропущ��но дубликатов: {self.stats['skipped_duplicate']}")

        return self.items


def main():
    """Тестовый запуск"""
    parser = JSONParser()
    json_path = Path(r'/sobes-data/MASSIV_GROUPED.json')

    if json_path.exists():
        items = parser.parse_file(json_path)

        # Сохраняем в промежуточный файл
        import json
        output_path = Path(r'C:\Users\refla\nareshka-mono\parsed_json.json')

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump([asdict(item) for item in items], f, ensure_ascii=False, indent=2)

        print(f"\n✅ Сохранено в {output_path}")
    else:
        print(f"❌ Файл не найден: {json_path}")


if __name__ == "__main__":
    main()
