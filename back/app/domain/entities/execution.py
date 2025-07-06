"""Сущности выполнения кода"""

from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ...infrastructure.database.connection import Base
from .enums import CodeLanguage, ExecutionStatus


class SupportedLanguage(Base):
    __tablename__ = "SupportedLanguage"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    language: SQLEnum = Column(SQLEnum(CodeLanguage), nullable=False, unique=True)
    version = Column(String, nullable=False)
    dockerImage = Column(String, nullable=False)
    fileExtension = Column(String, nullable=False)
    compileCommand = Column(String)
    runCommand = Column(String, nullable=False)
    timeoutSeconds = Column(Integer, nullable=False)
    memoryLimitMB = Column(Integer, nullable=False)
    isEnabled = Column(Boolean, default=True, nullable=False)

    createdAt = Column(DateTime, default=func.now(), nullable=False)
    updatedAt = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    executions = relationship("CodeExecution", back_populates="language")
    solutions = relationship("UserCodeSolution", back_populates="language")


class CodeExecution(Base):
    __tablename__ = "CodeExecution"

    id = Column(String, primary_key=True)
    userId = Column(Integer, ForeignKey("User.id", ondelete="CASCADE"), nullable=True)
    blockId = Column(String, ForeignKey("ContentBlock.id", ondelete="CASCADE"), nullable=True)
    languageId = Column(String, ForeignKey("SupportedLanguage.id", ondelete="CASCADE"), nullable=False)
    sourceCode = Column(Text, nullable=False)
    stdin = Column(Text)

    status: SQLEnum = Column(SQLEnum(ExecutionStatus), default=ExecutionStatus.PENDING, nullable=False)
    stdout = Column(Text)
    stderr = Column(Text)
    exitCode = Column(Integer)
    executionTimeMs = Column(Integer)
    memoryUsedMB = Column(Integer)
    containerLogs = Column(Text)
    errorMessage = Column(String)

    createdAt = Column(DateTime, default=func.now(), nullable=False)
    completedAt = Column(DateTime)

    user = relationship("User")
    block = relationship("ContentBlock")
    language = relationship("SupportedLanguage", back_populates="executions")

    __table_args__ = (
        Index("idx_codeexecution_userid", "userId"),
        Index("idx_codeexecution_blockid", "blockId"),
        Index("idx_codeexecution_status", "status"),
        Index("idx_codeexecution_createdat", "createdAt"),
    )


class UserCodeSolution(Base):
    __tablename__ = "UserCodeSolution"

    id = Column(String, primary_key=True)
    userId = Column(Integer, ForeignKey("User.id", ondelete="CASCADE"), nullable=False)
    blockId = Column(String, ForeignKey("ContentBlock.id", ondelete="CASCADE"), nullable=False)
    languageId = Column(String, ForeignKey("SupportedLanguage.id", ondelete="CASCADE"), nullable=False)
    sourceCode = Column(Text, nullable=False)
    isCompleted = Column(Boolean, default=False, nullable=False)

    executionCount = Column(Integer, default=0, nullable=False)
    successfulExecutions = Column(Integer, default=0, nullable=False)
    lastExecutionId = Column(String)

    createdAt = Column(DateTime, default=func.now(), nullable=False)
    updatedAt = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User")
    block = relationship("ContentBlock")
    language = relationship("SupportedLanguage", back_populates="solutions")

    __table_args__ = (
        Index("idx_usercodesolution_userid", "userId"),
        Index("idx_usercodesolution_blockid", "blockId"),
        Index("idx_usercodesolution_userid_blockid", "userId", "blockId"),
    ) 