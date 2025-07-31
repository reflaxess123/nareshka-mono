"""
Скрипт импорта данных из sobes-data в базу данных
Обрабатывает MASSIV_GROUPED.json и связывает с markdown отчетами
"""

import json
import hashlib
import re
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import uuid

# Добавляем путь к app в PYTHONPATH
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.shared.database import get_session
from app.shared.entities.interview import InterviewRecord, InterviewAnalytics


class InterviewImporter:
    def __init__(self, session: Session):
        self.session = session
        self.imported_count = 0
        self.skipped_count = 0
        self.errors: List[str] = []
    
    def import_from_json(self, json_path: str) -> None:
        """Импорт данных из MASSIV_GROUPED.json"""
        print(f"Начинаю импорт из {json_path}")
        
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"Загружено {len(data)} групп компаний")
        
        for company_group in data:
            company_name = company_group["company"]
            records = company_group["records"]
            
            print(f"Обрабатываю компанию: {company_name} ({len(records)} записей)")
            
            for record in records:
                try:
                    interview_record = self._process_record(record, company_name)
                    if interview_record:
                        self.session.add(interview_record)
                        self.imported_count += 1
                        
                        if self.imported_count % 100 == 0:
                            print(f"Импортировано {self.imported_count} записей...")
                            
                except Exception as e:
                    self.errors.append(f"Ошибка импорта записи {record.get('timestamp', 'unknown')}: {str(e)}")
                    self.skipped_count += 1
        
        print("Сохраняю данные в БД...")
        self.session.commit()
        print(f"Импортировано: {self.imported_count}, Пропущено: {self.skipped_count}")
        
        if self.errors:
            print(f"Ошибки: {len(self.errors)}")
            for error in self.errors[:5]:  # Показываем первые 5 ошибок
                print(f"  - {error}")
    
    def _process_record(self, record: Dict, company_name: str) -> Optional[InterviewRecord]:
        """Обработка одной записи интервью"""
        timestamp_str = record["timestamp"]
        content = record["content"]
        full_content = record["full_content"]
        
        # Создание content_hash для дедупликации
        content_hash = hashlib.md5(full_content.encode()).hexdigest()
        
        # Проверка дубликатов
        existing = self.session.query(InterviewRecord).filter_by(content_hash=content_hash).first()
        if existing:
            return None
        
        # Парсинг timestamp
        interview_date = self._parse_timestamp(timestamp_str)
        if not interview_date:
            return None
        
        # Извлечение данных из контента
        extracted_data = self._extract_metadata(full_content)
        
        # Создание записи
        interview_record = InterviewRecord(
            id=str(uuid.uuid4()),
            company_name=company_name,
            interview_date=interview_date,
            content=content,
            full_content=full_content,
            content_hash=content_hash,
            stage_number=extracted_data.get("stage"),
            position=extracted_data.get("position"),
            technologies=extracted_data.get("technologies", []),
            tags=extracted_data.get("tags", []),
            companies=[company_name],
            telegram_author=extracted_data.get("author"),
            difficulty_level=extracted_data.get("difficulty"),
            createdAt=datetime.now(),
            updatedAt=datetime.now()
        )
        
        return interview_record
    
    def _parse_timestamp(self, timestamp_str: str) -> Optional[datetime]:
        """Парсинг временной метки"""
        try:
            return datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            try:
                # Попробуем другие форматы
                return datetime.strptime(timestamp_str.split()[0], "%Y-%m-%d")
            except ValueError:
                return None
    
    def _extract_metadata(self, content: str) -> Dict:
        """Извлечение метаданных из текста интервью"""
        result = {}
        
        # Извлечение автора Telegram
        author_match = re.search(r'(\w+\s*\w*)\s*->', content)
        if author_match:
            result["author"] = author_match.group(1).strip()
        
        # Извлечение этапа
        stage_match = re.search(r'(\d+)\s*этап', content, re.IGNORECASE)
        if stage_match:
            result["stage"] = int(stage_match.group(1))
        
        # Извлечение должности
        position_patterns = [
            r'должность[:\s]*([^\n]+)',
            r'позиция[:\s]*([^\n]+)',
            r'вакансия[:\s]*([^\n]+)'
        ]
        for pattern in position_patterns:
            position_match = re.search(pattern, content, re.IGNORECASE)
            if position_match:
                result["position"] = position_match.group(1).strip()
                break
        
        # Извлечение технологий (React, TypeScript, etc.)
        technologies = []
        tech_patterns = [
            r'\bReact\b', r'\bTypeScript\b', r'\bJavaScript\b', r'\bVue\b',
            r'\bAngular\b', r'\bNode\.js\b', r'\bGo\b', r'\bPython\b',
            r'\bNext\.js\b', r'\bNuxt\b', r'\bSvelte\b', r'\bRedux\b'
        ]
        for pattern in tech_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                tech_name = pattern.replace(r'\b', '').replace(r'\.', '.')
                technologies.append(tech_name)
        
        result["technologies"] = list(set(technologies))  # Уникальные технологии
        
        # Извлечение тегов
        tags = []
        if 'frontend' in content.lower() or 'фронтенд' in content.lower():
            tags.append('Frontend')
        if 'backend' in content.lower() or 'бэкенд' in content.lower():
            tags.append('Backend')
        if 'fullstack' in content.lower() or 'фулстек' in content.lower():
            tags.append('Fullstack')
        if 'алгоритм' in content.lower() or 'algorithm' in content.lower():
            tags.append('Algorithms')
        if 'система' in content.lower() or 'system design' in content.lower():
            tags.append('System Design')
        
        result["tags"] = tags
        
        # Простая оценка сложности по ключевым словам
        difficulty_keywords = {
            1: ['простой', 'легкий', 'базовый', 'начальный'],
            2: ['средний', 'обычный', 'стандартный'],
            3: ['сложный', 'продвинутый', 'средний+'],
            4: ['очень сложный', 'экспертный', 'senior'],
            5: ['невозможный', 'крайне сложный', 'ведущий разработчик']
        }
        
        for level, keywords in difficulty_keywords.items():
            if any(keyword in content.lower() for keyword in keywords):
                result["difficulty"] = level
                break
        
        # Если нет явных индикаторов сложности, попробуем оценить по контексту
        if "difficulty" not in result:
            if len(technologies) >= 3:
                result["difficulty"] = 3  # Много технологий = средняя сложность
            elif any(word in content.lower() for word in ['junior', 'стажер', 'начинающий']):
                result["difficulty"] = 1
            elif any(word in content.lower() for word in ['senior', 'ведущий', 'архитектор']):
                result["difficulty"] = 4
        
        return result


def generate_basic_analytics(session: Session):
    """Генерация базовой аналитики после импорта"""
    print("Генерирую базовую аналитику...")
    
    # Удаляем старую аналитику
    session.query(InterviewAnalytics).delete()
    
    # Аналитика по компаниям
    companies_stats = session.query(
        InterviewRecord.company_name,
        func.count(InterviewRecord.id).label('total'),
        func.avg(InterviewRecord.difficulty_level).label('avg_difficulty')
    ).group_by(InterviewRecord.company_name).all()
    
    for company, total, avg_diff in companies_stats:
        analytics = InterviewAnalytics(
            id=str(uuid.uuid4()),
            metric_type="COMPANY",
            metric_value=company,
            period="all",
            total_interviews=int(total),
            avg_difficulty=float(avg_diff) if avg_diff else None,
            calculated_at=datetime.now(),
            createdAt=datetime.now(),
            updatedAt=datetime.now()
        )
        session.add(analytics)
    
    # Аналитика по технологиям
    tech_subquery = session.query(func.unnest(InterviewRecord.technologies).label('tech')).subquery()
    tech_stats = session.query(
        tech_subquery.c.tech,
        func.count(tech_subquery.c.tech).label('count')
    ).group_by(tech_subquery.c.tech).all()
    
    for tech, count in tech_stats:
        if tech:  # Пропускаем пустые технологии
            analytics = InterviewAnalytics(
                id=str(uuid.uuid4()),
                metric_type="TECHNOLOGY",
                metric_value=tech,
                period="all",
                total_interviews=int(count),
                calculated_at=datetime.now(),
                createdAt=datetime.now(),
                updatedAt=datetime.now()
            )
            session.add(analytics)
    
    session.commit()
    print("✅ Базовая аналитика сгенерирована")


def main():
    """Основная функция импорта"""
    json_path = "C:/Users/refla/nareshka-mono/sobes-data/MASSIV_GROUPED.json"
    
    if not os.path.exists(json_path):
        print(f"Файл {json_path} не найден!")
        return
    
    print("Начинаю импорт интервью...")
    
    session = next(get_session())
    try:
        importer = InterviewImporter(session)
        importer.import_from_json(json_path)
        
        # Генерация базовой аналитики
        generate_basic_analytics(session)
    finally:
        session.close()
    
    print("Импорт завершен!")


if __name__ == "__main__":
    main()