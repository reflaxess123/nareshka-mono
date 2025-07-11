from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.infrastructure.database.connection import Base


class TestCase(Base):
    __tablename__ = "TestCase"

    id = Column(String, primary_key=True)
    blockId = Column(
        String, ForeignKey("ContentBlock.id", ondelete="CASCADE"), nullable=False
    )

    # Основные данные тест-кейса
    name = Column(String, nullable=False)
    description = Column(Text)
    input = Column(Text, default="", nullable=False)
    expectedOutput = Column(Text, nullable=False)

    # Метаданные
    isPublic = Column(
        Boolean, default=True, nullable=False
    )  # Показывать пользователю или скрытый
    difficulty = Column(String, default="BASIC")  # BASIC, INTERMEDIATE, ADVANCED
    weight = Column(Float, default=1.0, nullable=False)  # Вес теста при подсчете баллов
    timeoutSeconds = Column(Integer, default=5, nullable=False)

    # AI-генерация
    isAIGenerated = Column(Boolean, default=False, nullable=False)
    generationPrompt = Column(Text)  # Промпт, использованный для генерации
    generatedAt = Column(DateTime)
    generationModel = Column(String)  # Модель AI, использованная для генерации

    # Статистика использования
    executionCount = Column(Integer, default=0, nullable=False)
    passRate = Column(Float, default=0.0, nullable=False)  # Процент прохождения

    # Системные поля
    isActive = Column(Boolean, default=True, nullable=False)
    orderIndex = Column(Integer, default=0, nullable=False)

    createdAt = Column(DateTime, default=func.now(), nullable=False)
    updatedAt = Column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )

    # Связи
    block = relationship("ContentBlock", back_populates="testCases")
    validationResults = relationship("TestValidationResult", back_populates="testCase")

    __table_args__ = (
        Index("idx_testcase_blockid", "blockId"),
        Index("idx_testcase_ispublic", "isPublic"),
        Index("idx_testcase_difficulty", "difficulty"),
        Index("idx_testcase_orderindex", "orderIndex"),
    )


class TestValidationResult(Base):
    __tablename__ = "TestValidationResult"

    id = Column(String, primary_key=True)
    testCaseId = Column(
        String, ForeignKey("TestCase.id", ondelete="CASCADE"), nullable=False
    )
    attemptId = Column(
        String, ForeignKey("TaskAttempt.id", ondelete="CASCADE"), nullable=False
    )

    # Результаты выполнения
    passed = Column(Boolean, nullable=False)
    actualOutput = Column(Text)
    executionTimeMs = Column(Integer)
    errorMessage = Column(Text)

    # Детали сравнения
    outputMatch = Column(Boolean, default=False)
    outputSimilarity = Column(Float, default=0.0)  # Процент схожести выводов

    createdAt = Column(DateTime, default=func.now(), nullable=False)

    # Связи
    testCase = relationship("TestCase", back_populates="validationResults")
    attempt = relationship("TaskAttempt", back_populates="validationResults")

    __table_args__ = (
        Index("idx_testvalidationresult_testcaseid", "testCaseId"),
        Index("idx_testvalidationresult_attemptid", "attemptId"),
        Index("idx_testvalidationresult_passed", "passed"),
        Index(
            "idx_testvalidationresult_testcaseid_attemptid",
            "testCaseId",
            "attemptId",
            unique=True,
        ),
    )
