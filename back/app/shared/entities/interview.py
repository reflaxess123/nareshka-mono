"""
Interview entities - SQLAlchemy модели для работы с собеседованиями
Следует паттернам существующих entities (ContentBlock, TheoryCard)
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import ARRAY, Boolean, Column, DateTime, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from app.shared.database import Base

# Очищаем кэш метаданных для InterviewRecord
if hasattr(Base, "metadata") and "InterviewRecord" in Base.metadata.tables:
    Base.metadata.remove(Base.metadata.tables["InterviewRecord"])


class InterviewRecord(Base):
    """
    Модель записи собеседования
    Повторяет паттерн ContentBlock с timestamp полями и ARRAY полями
    """

    __tablename__ = "InterviewRecord"

    id: str = Column(String, primary_key=True)
    company_name: str = Column(String, nullable=False)
    interview_date: datetime = Column(DateTime, nullable=False)
    position: Optional[str] = Column(String, nullable=True)
    full_content: str = Column(Text, nullable=False)  # Полная версия
    duration_minutes: Optional[int] = Column(Integer, nullable=True)
    questions_count: Optional[int] = Column(Integer, nullable=True)

    # ARRAY поля как в ContentBlock
    companies: List[str] = Column(ARRAY(String), nullable=False, default=list)
    tags: List[str] = Column(ARRAY(String), nullable=False, default=list)
    extracted_urls: List[str] = Column(ARRAY(String), nullable=False, default=list)

    # Метаданные
    source_type: str = Column(String, nullable=True, default="telegram")
    content_hash: Optional[str] = Column(String, nullable=True)
    has_audio_recording: bool = Column(Boolean, nullable=False, default=False)

    # Timestamp поля (как в BaseModel)
    updatedAt: datetime = Column(
        "updatedAt", DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )


class InterviewAnalytics(Base):
    """
    Модель предрасчитанной аналитики
    Для быстрой отдачи статистики без тяжелых запросов
    """

    __tablename__ = "InterviewAnalytics"

    id: str = Column(String, primary_key=True)
    metric_type: str = Column(
        String, nullable=False
    )  # 'company', 'technology', 'monthly'
    metric_value: str = Column(String, nullable=False)  # 'Яндекс', 'React', '2024-11'
    period: Optional[str] = Column(String, nullable=True)  # 'monthly', 'yearly', 'all'

    # Статистические данные
    total_interviews: int = Column(Integer, nullable=False, default=0)
    avg_difficulty: Optional[float] = Column(
        Numeric(precision=3, scale=2), nullable=True
    )
    avg_duration: Optional[int] = Column(Integer, nullable=True)
    common_questions: Optional[List[str]] = Column(ARRAY(Text), nullable=True)
    additional_data: Optional[dict] = Column(JSONB, nullable=True)

    # Время расчета и обновления
    calculated_at: datetime = Column(DateTime, nullable=False)
    createdAt: datetime = Column(
        "createdAt", DateTime, nullable=False, default=func.now()
    )
    updatedAt: datetime = Column(
        "updatedAt", DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )
