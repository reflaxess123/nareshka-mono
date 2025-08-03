#!/usr/bin/env python3
"""
Скрипт для импорта LLM-отчетов интервью в базу данных PostgreSQL
"""

import os
import re
import hashlib
import json
from datetime import datetime
from pathlib import Path
import psycopg2
from psycopg2.extras import RealDictCursor
import uuid
from typing import Dict, List, Optional, Tuple


class InterviewReportImporter:
    def __init__(self, db_config: Dict[str, str]):
        """
        Инициализация импортера
        
        Args:
            db_config: Конфигурация подключения к БД
        """
        self.db_config = db_config
        self.connection = None
        self.companies_mapping = {}
        self.tech_standardization = {
            'javascript': 'JavaScript',
            'js': 'JavaScript', 
            'react': 'React',
            'typescript': 'TypeScript',
            'ts': 'TypeScript',
            'css': 'CSS',
            'html': 'HTML',
            'redux': 'Redux',
            'node': 'Node.js',
            'nodejs': 'Node.js',
            'vue': 'Vue.js',
            'angular': 'Angular',
            'python': 'Python',
            'архитектура': 'Architecture',
            'команда': 'TeamWork',
            'алгоритмы': 'Algorithms',
            'git': 'Git'
        }
        self.company_standardization = {
            'сбербанк': 'Сбер',
            'сбер': 'Сбер',
            'альфа-банк': 'Альфа-Банк',
            'альфабанк': 'Альфа-Банк',
            'яндекс': 'Яндекс',
            'вк видео': 'ВК',
            'вк': 'ВК',
            'втб': 'ВТБ',
            'авито': 'Авито',
            'тинькофф': 'Т-Банк',
            'т-банк': 'Т-Банк'
        }

    def connect_db(self):
        """Подключение к базе данных"""
        try:
            self.connection = psycopg2.connect(**self.db_config)
            self.connection.autocommit = True
            print("✅ Подключение к БД установлено")
        except Exception as e:
            print(f"❌ Ошибка подключения к БД: {e}")
            raise

    def load_companies_mapping(self, companies_file: str):
        """Загрузка сопоставления файлов и компаний"""
        mapping = {}
        
        with open(companies_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Парсим записи вида: ### 1. filename.md
        pattern = r'### (\d+)\. (.+?)\.md\n- \*\*Компания\*\*: (.+?)\n'
        matches = re.findall(pattern, content)
        
        for match in matches:
            number, filename, company = match
            # Убираем лишние пробелы и стандартизируем
            company = company.strip()
            if company.lower() in self.company_standardization:
                company = self.company_standardization[company.lower()]
            elif company == "Нет названия компании" or company == "Нет данных":
                company = "Unknown"
            
            mapping[filename + '.md'] = company
            
        print(f"📋 Загружено {len(mapping)} сопоставлений компаний")
        self.companies_mapping = mapping

    def parse_date_from_filename(self, filename: str) -> Optional[datetime]:
        """Извлечение даты из названия файла"""
        # Паттерн: 2024-07-11 15-00-11_transcript_llm_FULL_report.md
        date_pattern = r'(\d{4}-\d{2}-\d{2})\s+(\d{2})-(\d{2})-(\d{2})'
        match = re.search(date_pattern, filename)
        
        if match:
            date_part = match.group(1)
            hour = match.group(2)
            minute = match.group(3) 
            second = match.group(4)
            
            datetime_str = f"{date_part} {hour}:{minute}:{second}"
            return datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
        
        return None

    def parse_questions_from_content(self, content: str) -> Tuple[int, List[str]]:
        """Извлечение вопросов и технологий из контента"""
        questions_count = 0
        technologies = set()
        
        # Ищем таблицу вопросов
        table_pattern = r'\|\s*№.*?\|\s*Вопрос.*?\|\s*Темы.*?\|(.+?)(?=\n##|\n\n|\Z)'
        table_match = re.search(table_pattern, content, re.DOTALL)
        
        if table_match:
            table_content = table_match.group(1)
            # Парсим строки таблицы
            row_pattern = r'\|\s*(\d+)\s*\|.*?\|\s*([^|]+)\s*\|'
            rows = re.findall(row_pattern, table_content)
            
            questions_count = len(rows)
            
            for row in rows:
                tech = row[1].strip().lower()
                if tech in self.tech_standardization:
                    technologies.add(self.tech_standardization[tech])
                else:
                    technologies.add(tech.title())
        
        return questions_count, list(technologies)

    def parse_duration_from_content(self, content: str) -> Optional[int]:
        """Извлечение длительности из блока показателей"""
        duration_pattern = r'Длительность:\s*([\d.]+)\s*мин'
        match = re.search(duration_pattern, content)
        
        if match:
            try:
                return int(float(match.group(1)))
            except ValueError:
                pass
                
        return None

    def calculate_difficulty(self, questions_count: int, duration_minutes: Optional[int]) -> int:
        """Расчет уровня сложности интервью"""
        # Базовая сложность по количеству вопросов
        if questions_count <= 5:
            difficulty = 1
        elif questions_count <= 10:
            difficulty = 2
        elif questions_count <= 15:
            difficulty = 3
        elif questions_count <= 20:
            difficulty = 4
        else:
            difficulty = 5
            
        # Корректировка по длительности
        if duration_minutes:
            if duration_minutes >= 90:
                difficulty = min(5, difficulty + 1)
            elif duration_minutes <= 30:
                difficulty = max(1, difficulty - 1)
                
        return difficulty

    def parse_report_file(self, file_path: str) -> Dict:
        """Парсинг одного файла отчета"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        filename = os.path.basename(file_path)
        
        # Извлекаем данные
        interview_date = self.parse_date_from_filename(filename)
        questions_count, technologies = self.parse_questions_from_content(content)
        duration_minutes = self.parse_duration_from_content(content)
        company_name = self.companies_mapping.get(filename, "Unknown")
        difficulty_level = self.calculate_difficulty(questions_count, duration_minutes)
        
        # Создаем хеш контента
        content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        
        # Определяем теги
        tags = ["frontend", "llm_report"]
        if "React" in technologies:
            tags.append("react")
        if "JavaScript" in technologies:
            tags.append("javascript")
            
        return {
            'id': str(uuid.uuid4()),
            'company_name': company_name,
            'interview_date': interview_date or datetime.now(),
            'position': "Frontend разработчик",
            'full_content': content,
            'duration_minutes': duration_minutes,
            'questions_count': questions_count if questions_count > 0 else None,
            'source_type': 'llm_report',
            'content_hash': content_hash,
            'extracted_urls': [],
            'companies': [company_name] if company_name != "Unknown" else [],
            'difficulty_level': difficulty_level,
            'telegram_author': None,
            'tags': tags,
            'stage_number': 1,
            'technologies': technologies
        }

    def insert_interview_record(self, record: Dict):
        """Вставка записи в базу данных"""
        sql = """
        INSERT INTO "InterviewRecord" (
            id, company_name, interview_date, position, full_content,
            duration_minutes, questions_count, source_type, content_hash,
            extracted_urls, companies, difficulty_level, "createdAt", "updatedAt",
            telegram_author, tags, stage_number, technologies
        ) VALUES (
            %(id)s, %(company_name)s, %(interview_date)s, %(position)s, %(full_content)s,
            %(duration_minutes)s, %(questions_count)s, %(source_type)s, %(content_hash)s,
            %(extracted_urls)s, %(companies)s, %(difficulty_level)s, NOW(), NOW(),
            %(telegram_author)s, %(tags)s, %(stage_number)s, %(technologies)s
        ) ON CONFLICT (content_hash) DO NOTHING;
        """
        
        with self.connection.cursor() as cursor:
            cursor.execute(sql, record)

    def process_reports_directory(self, reports_dir: str):
        """Обработка всех отчетов в директории"""
        reports_path = Path(reports_dir)
        
        if not reports_path.exists():
            print(f"❌ Директория {reports_dir} не найдена")
            return
            
        md_files = list(reports_path.glob("*.md"))
        print(f"📁 Найдено {len(md_files)} .md файлов")
        
        processed = 0
        errors = 0
        
        for file_path in md_files:
            try:
                print(f"📄 Обрабатываем: {file_path.name}")
                record = self.parse_report_file(str(file_path))
                self.insert_interview_record(record)
                processed += 1
                
                if processed % 10 == 0:
                    print(f"✅ Обработано {processed}/{len(md_files)}")
                    
            except Exception as e:
                print(f"❌ Ошибка обработки {file_path.name}: {e}")
                errors += 1
                
        print(f"\n🎯 Итого:")
        print(f"✅ Успешно обработано: {processed}")
        print(f"❌ Ошибок: {errors}")

    def close_connection(self):
        """Закрытие соединения с БД"""
        if self.connection:
            self.connection.close()
            print("🔌 Соединение с БД закрыто")


def main():
    """Основная функция"""
    # Конфигурация БД (настройте под свою базу)
    DB_CONFIG = {
        'host': 'localhost',
        'port': 5432,
        'database': 'nareshka',  # Замените на ваше название БД
        'user': 'postgres',      # Замените на ваш пользователь
        'password': 'password'   # Замените на ваш пароль
    }
    
    # Пути к файлам
    REPORTS_DIR = r"C:\Users\refla\nareshka-mono\sobes-data\reports"
    COMPANIES_FILE = r"C:\Users\refla\nareshka-mono\sobes-data\companies_extracted.md"
    
    # Создаем импортер
    importer = InterviewReportImporter(DB_CONFIG)
    
    try:
        # Подключаемся к БД
        importer.connect_db()
        
        # Загружаем сопоставления компаний
        importer.load_companies_mapping(COMPANIES_FILE)
        
        # Обрабатываем отчеты
        importer.process_reports_directory(REPORTS_DIR)
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
    finally:
        importer.close_connection()


if __name__ == "__main__":
    main()