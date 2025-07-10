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


class TaskAttempt(Base):
    __tablename__ = "TaskAttempt"

    id = Column(String, primary_key=True)
    userId = Column(Integer, ForeignKey("User.id", ondelete="CASCADE"), nullable=False)
    blockId = Column(
        String, ForeignKey("ContentBlock.id", ondelete="CASCADE"), nullable=False
    )

    sourceCode = Column(Text, nullable=False)
    language = Column(String, nullable=False)
    isSuccessful = Column(Boolean, default=False, nullable=False)
    attemptNumber = Column(Integer, nullable=False)

    executionTimeMs = Column(Integer)
    memoryUsedMB = Column(Float)
    errorMessage = Column(Text)
    stderr = Column(Text)

    durationMinutes = Column(Integer)
    createdAt = Column(DateTime, default=func.now(), nullable=False)

    user = relationship("User", back_populates="taskAttempts")
    block = relationship("ContentBlock", back_populates="taskAttempts")
    validationResults = relationship("TestValidationResult", back_populates="attempt")

    __table_args__ = (
        Index("idx_taskattempt_userid", "userId"),
        Index("idx_taskattempt_blockid", "blockId"),
        Index("idx_taskattempt_userid_blockid", "userId", "blockId"),
        Index("idx_taskattempt_createdat", "createdAt"),
    )


class TaskSolution(Base):
    __tablename__ = "TaskSolution"

    id = Column(String, primary_key=True)
    userId = Column(Integer, ForeignKey("User.id", ondelete="CASCADE"), nullable=False)
    blockId = Column(
        String, ForeignKey("ContentBlock.id", ondelete="CASCADE"), nullable=False
    )

    finalCode = Column(Text, nullable=False)
    language = Column(String, nullable=False)

    totalAttempts = Column(Integer, nullable=False)
    timeToSolveMinutes = Column(Integer, nullable=False)

    firstAttempt = Column(DateTime, nullable=False)
    solvedAt = Column(DateTime, default=func.now(), nullable=False)

    createdAt = Column(DateTime, default=func.now(), nullable=False)
    updatedAt = Column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )

    user = relationship("User", back_populates="taskSolutions")
    block = relationship("ContentBlock", back_populates="taskSolutions")

    __table_args__ = (
        Index("idx_tasksolution_userid", "userId"),
        Index("idx_tasksolution_blockid", "blockId"),
        Index("idx_tasksolution_userid_blockid", "userId", "blockId", unique=True),
        Index("idx_tasksolution_solvedat", "solvedAt"),
    )
