"""
Скрипт импорта LLM-отчетов интервью из sobes-data/reports в базу данных
Использует сопоставления компаний из companies_extracted.md
"""

import hashlib
import os
import re
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

# Добавляем путь к app в PYTHONPATH
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.shared.database import get_session
from app.shared.models.interview_models import InterviewAnalytics, InterviewRecord


class LLMReportImporter:
    def __init__(self, session: Session):
        self.session = session
        self.imported_count = 0
        self.skipped_count = 0
        self.errors: List[str] = []
        self.companies_mapping = {}

        # Стандартизация технологий
        self.tech_standardization = {
            "javascript": "JavaScript",
            "js": "JavaScript",
            "react": "React",
            "typescript": "TypeScript",
            "ts": "TypeScript",
            "css": "CSS",
            "html": "HTML",
            "redux": "Redux",
            "node": "Node.js",
            "nodejs": "Node.js",
            "vue": "Vue.js",
            "angular": "Angular",
            "python": "Python",
            "архитектура": "Architecture",
            "команда": "TeamWork",
            "алгоритмы": "Algorithms",
            "git": "Git",
        }

        # Стандартизация компаний
        self.company_standardization = {
            "сбербанк": "Сбер",
            "сбер": "Сбер",
            "альфа-банк": "Альфа-Банк",
            "альфабанк": "Альфа-Банк",
            "яндекс": "Яндекс",
            "вк видео": "ВК",
            "вк": "ВК",
            "втб": "ВТБ",
            "авито": "Авито",
            "тинькофф": "Т-Банк",
            "т-банк": "Т-Банк",
        }

    def load_companies_mapping(self, companies_file: str) -> None:
        """Загрузка сопоставления файлов и компаний"""
        if not os.path.exists(companies_file):
            print(f"ERROR: Файл {companies_file} не найден!")
            return

        mapping = {}

        with open(companies_file, encoding="utf-8") as f:
            content = f.read()

        # Парсим записи вида: ### 1. filename.md
        pattern = r"### (\d+)\. (.+?)\.md\n- \*\*Компания\*\*: (.+?)\n"
        matches = re.findall(pattern, content)

        for match in matches:
            number, filename, company = match
            # Убираем лишние пробелы и стандартизируем
            company = company.strip()
            if company.lower() in self.company_standardization:
                company = self.company_standardization[company.lower()]
            elif company == "Нет названия компании" or company == "Нет данных":
                company = "Unknown"

            mapping[filename + ".md"] = company

        print(f"INFO: Загружено {len(mapping)} сопоставлений компаний")
        self.companies_mapping = mapping

    def parse_date_from_filename(self, filename: str) -> Optional[datetime]:
        """Извлечение даты из названия файла"""
        # Паттерн: 2024-07-11 15-00-11_transcript_llm_FULL_report.md
        date_pattern = r"(\d{4}-\d{2}-\d{2})\s+(\d{2})-(\d{2})-(\d{2})"
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
        table_pattern = r"\|\s*№.*?\|\s*Вопрос.*?\|\s*Темы.*?\|(.+?)(?=\n##|\n\n|\Z)"
        table_match = re.search(table_pattern, content, re.DOTALL)

        if table_match:
            table_content = table_match.group(1)
            # Парсим строки таблицы
            row_pattern = r"\|\s*(\d+)\s*\|.*?\|\s*([^|]+)\s*\|"
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
        duration_pattern = r"Длительность:\s*([\d.]+)\s*мин"
        match = re.search(duration_pattern, content)

        if match:
            try:
                return int(float(match.group(1)))
            except ValueError:
                pass

        return None

    def calculate_difficulty(
        self, questions_count: int, duration_minutes: Optional[int]
    ) -> int:
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

    def parse_report_file(self, file_path: str) -> Optional[InterviewRecord]:
        """Парсинг одного файла отчета"""
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        filename = os.path.basename(file_path)

        # Создание content_hash для дедупликации
        content_hash = hashlib.md5(content.encode("utf-8")).hexdigest()

        # Проверка дубликатов
        existing = (
            self.session.query(InterviewRecord)
            .filter_by(content_hash=content_hash)
            .first()
        )
        if existing:
            return None

        # Извлекаем данные
        interview_date = self.parse_date_from_filename(filename)
        if not interview_date:
            print(f"WARNING: Не удалось извлечь дату из {filename}")
            interview_date = datetime.now()

        questions_count, technologies = self.parse_questions_from_content(content)
        duration_minutes = self.parse_duration_from_content(content)
        company_name = self.companies_mapping.get(filename, "Unknown")
        difficulty_level = self.calculate_difficulty(questions_count, duration_minutes)

        # Определяем теги
        tags = ["frontend", "llm_report"]
        if "React" in technologies:
            tags.append("react")
        if "JavaScript" in technologies:
            tags.append("javascript")

        # Создание записи
        interview_record = InterviewRecord(
            id=str(uuid.uuid4()),
            company_name=company_name,
            interview_date=interview_date,
            position="Frontend разработчик",
            full_content=content,
            duration_minutes=duration_minutes,
            questions_count=questions_count if questions_count > 0 else None,
            source_type="llm_report",
            content_hash=content_hash,
            extracted_urls=[],
            companies=[company_name] if company_name != "Unknown" else [],
            tags=tags,
            has_audio_recording=True,  # LLM-отчеты имеют аудио/видеозапись
            updatedAt=datetime.now(),
        )

        return interview_record

    def import_from_reports_directory(self, reports_dir: str) -> None:
        """Импорт всех отчетов из директории"""
        reports_path = Path(reports_dir)

        if not reports_path.exists():
            print(f"ERROR: Директория {reports_dir} не найдена")
            return

        md_files = list(reports_path.glob("*.md"))
        print(f"INFO: Найдено {len(md_files)} .md файлов")

        for file_path in md_files:
            try:
                print(f"PROCESSING: {file_path.name}")
                record = self.parse_report_file(str(file_path))

                if record:
                    self.session.add(record)
                    self.imported_count += 1

                    if self.imported_count % 10 == 0:
                        print(
                            f"SUCCESS: Обработано {self.imported_count}/{len(md_files)}"
                        )
                        self.session.commit()  # Периодические коммиты
                else:
                    self.skipped_count += 1

            except Exception as e:
                error_msg = f"Ошибка обработки {file_path.name}: {e}"
                print(f"ERROR: {error_msg}")
                self.errors.append(error_msg)

        print("INFO: Сохраняю данные в БД...")
        self.session.commit()

        print("\nITOGO:")
        print(f"SUCCESS: Успешно обработано: {self.imported_count}")
        print(f"SKIPPED: Пропущено (дубликаты): {self.skipped_count}")
        print(f"ERRORS: Ошибок: {len(self.errors)}")

        if self.errors:
            print("\nПервые 5 ошибок:")
            for error in self.errors[:5]:
                print(f"  - {error}")


def generate_analytics_for_llm_reports(session: Session):
    """Генерация аналитики для LLM отчетов"""
    print("INFO: Генерирую аналитику для LLM отчетов...")

    # Удаляем старую аналитику по LLM отчетам
    session.query(InterviewAnalytics).filter_by(metric_type="LLM_COMPANY").delete()

    # Аналитика по компаниям из LLM отчетов
    llm_companies_stats = (
        session.query(
            InterviewRecord.company_name, func.count(InterviewRecord.id).label("total")
        )
        .filter(InterviewRecord.source_type == "llm_report")
        .group_by(InterviewRecord.company_name)
        .all()
    )

    for company, total in llm_companies_stats:
        analytics = InterviewAnalytics(
            id=str(uuid.uuid4()),
            metric_type="LLM_COMPANY",
            metric_value=company,
            period="all",
            total_interviews=int(total),
            calculated_at=datetime.now(),
            createdAt=datetime.now(),
            updatedAt=datetime.now(),
        )
        session.add(analytics)

    session.commit()
    print("SUCCESS: Аналитика для LLM отчетов сгенерирована")


def main():
    """Основная функция импорта"""
    # Пути к файлам
    REPORTS_DIR = r"C:\Users\refla\nareshka-mono\sobes-data\reports"
    COMPANIES_FILE = r"C:\Users\refla\nareshka-mono\sobes-data\companies_extracted.md"

    print(">> Начинаю импорт LLM-отчетов интервью...")

    session = next(get_session())
    try:
        importer = LLMReportImporter(session)

        # Загружаем сопоставления компаний
        importer.load_companies_mapping(COMPANIES_FILE)

        # Импортируем отчеты
        importer.import_from_reports_directory(REPORTS_DIR)

        # Генерация аналитики
        generate_analytics_for_llm_reports(session)

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        session.rollback()
    finally:
        session.close()

    print("DONE: Импорт LLM-отчетов завершен!")


if __name__ == "__main__":
    main()
