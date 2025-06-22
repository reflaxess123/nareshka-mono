from enum import Enum
from typing import List, Any
from decimal import Decimal

from sqlalchemy import (
    ARRAY,
    DECIMAL,
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum as SQLEnum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


class UserRole(str, Enum):
    GUEST = "GUEST"
    USER = "USER"
    ADMIN = "ADMIN"


class CardState(str, Enum):
    NEW = "NEW"
    LEARNING = "LEARNING"
    REVIEW = "REVIEW"
    RELEARNING = "RELEARNING"


class ProgressStatus(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    STRUGGLING = "STRUGGLING"


class User(Base):
    __tablename__ = "User"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role: SQLEnum = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    createdAt = Column(DateTime, default=func.now(), nullable=False)
    updatedAt = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    totalTasksSolved = Column(Integer, default=0, server_default="0", nullable=False)
    lastActivityDate = Column(DateTime, nullable=True)

    progress = relationship("UserContentProgress", back_populates="user")
    theoryProgress = relationship("UserTheoryProgress", back_populates="user")
    categoryProgress = relationship("UserCategoryProgress", back_populates="user")
    taskAttempts = relationship("TaskAttempt", back_populates="user")
    taskSolutions = relationship("TaskSolution", back_populates="user")
    pathProgress = relationship("UserPathProgress", back_populates="user")


class ContentFile(Base):
    __tablename__ = "ContentFile"

    id = Column(String, primary_key=True)
    webdavPath = Column(String, unique=True, nullable=False)
    mainCategory = Column(String, nullable=False)
    subCategory = Column(String, nullable=False)
    lastFileHash = Column(String)
    createdAt = Column(DateTime, default=func.now(), nullable=False)
    updatedAt = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    blocks = relationship("ContentBlock", back_populates="file")


class ContentBlock(Base):
    __tablename__ = "ContentBlock"

    id = Column(String, primary_key=True)
    fileId = Column(String, ForeignKey("ContentFile.id", ondelete="CASCADE"), nullable=False)
    pathTitles = Column(JSON, nullable=False)
    blockTitle = Column(String, nullable=False)
    blockLevel = Column(Integer, nullable=False)
    orderInFile = Column(Integer, nullable=False)

    textContent = Column(Text)
    codeContent = Column(Text)
    codeLanguage = Column(String)
    isCodeFoldable = Column(Boolean, default=False, nullable=False)
    codeFoldTitle = Column(String)

    extractedUrls: List[str] = Column(ARRAY(String), default=[], nullable=False)
    companies: List[str] = Column(ARRAY(String), default=[], nullable=False)
    rawBlockContentHash = Column(String)

    createdAt = Column(DateTime, default=func.now(), nullable=False)
    updatedAt = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    file = relationship("ContentFile", back_populates="blocks")
    progressEntries = relationship("UserContentProgress", back_populates="block")
    taskAttempts = relationship("TaskAttempt", back_populates="block")
    taskSolutions = relationship("TaskSolution", back_populates="block")

    __table_args__ = (Index("idx_contentblock_fileid", "fileId"),)


class UserContentProgress(Base):
    __tablename__ = "UserContentProgress"

    id = Column(String, primary_key=True)
    userId = Column(Integer, ForeignKey("User.id", ondelete="CASCADE"), nullable=False)
    blockId = Column(String, ForeignKey("ContentBlock.id", ondelete="CASCADE"), nullable=False)
    solvedCount = Column(Integer, default=0, nullable=False)

    createdAt = Column(DateTime, default=func.now(), nullable=False)
    updatedAt = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", back_populates="progress")
    block = relationship("ContentBlock", back_populates="progressEntries")

    __table_args__ = (
        Index("idx_usercontentprogress_blockid", "blockId"),
        Index("idx_usercontentprogress_userid_blockid", "userId", "blockId", unique=True),
    )


class TheoryCard(Base):
    __tablename__ = "TheoryCard"

    id = Column(String, primary_key=True)
    ankiGuid = Column(String, unique=True, nullable=False)
    cardType = Column(String, nullable=False)
    deck = Column(String, nullable=False)
    category = Column(String, nullable=False)
    subCategory = Column(String)
    questionBlock = Column(Text, nullable=False)
    answerBlock = Column(Text, nullable=False)
    tags: List[str] = Column(ARRAY(String), default=[], nullable=False)
    orderIndex = Column(Integer, default=0, nullable=False)

    createdAt = Column(DateTime, default=func.now(), nullable=False)
    updatedAt = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    progressEntries = relationship("UserTheoryProgress", back_populates="card")

    __table_args__ = (
        Index("idx_theorycard_category", "category"),
        Index("idx_theorycard_deck", "deck"),
    )


class UserTheoryProgress(Base):
    __tablename__ = "UserTheoryProgress"

    id = Column(String, primary_key=True)
    userId = Column(Integer, ForeignKey("User.id", ondelete="CASCADE"), nullable=False)
    cardId = Column(String, ForeignKey("TheoryCard.id", ondelete="CASCADE"), nullable=False)

    solvedCount = Column(Integer, default=0, nullable=False)

    easeFactor: Decimal = Column(DECIMAL(3, 2), default=2.50, nullable=False)
    interval = Column(Integer, default=1, nullable=False)
    dueDate = Column(DateTime)
    reviewCount = Column(Integer, default=0, nullable=False)
    lapseCount = Column(Integer, default=0, nullable=False)
    cardState: SQLEnum = Column(SQLEnum(CardState), default=CardState.NEW, nullable=False)
    learningStep = Column(Integer, default=0, nullable=False)
    lastReviewDate = Column(DateTime)

    createdAt = Column(DateTime, default=func.now(), nullable=False)
    updatedAt = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", back_populates="theoryProgress")
    card = relationship("TheoryCard", back_populates="progressEntries")

    __table_args__ = (
        Index("idx_usertheoryprogress_cardid", "cardId"),
        Index("idx_usertheoryprogress_duedate", "dueDate"),
        Index("idx_usertheoryprogress_cardstate", "cardState"),
        Index("idx_usertheoryprogress_userid_cardid", "userId", "cardId", unique=True),
    )


class CodeLanguage(str, Enum):
    PYTHON = "PYTHON"
    JAVASCRIPT = "JAVASCRIPT"
    TYPESCRIPT = "TYPESCRIPT"
    JAVA = "JAVA"
    CPP = "CPP"
    C = "C"
    GO = "GO"
    RUST = "RUST"
    PHP = "PHP"
    RUBY = "RUBY"


class ExecutionStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    TIMEOUT = "TIMEOUT"
    MEMORY_LIMIT = "MEMORY_LIMIT"


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
        Index("idx_usercodesolution_userid_blockid_languageid", "userId", "blockId", "languageId", unique=True),
    )


class UserCategoryProgress(Base):
    __tablename__ = "UserCategoryProgress"

    id = Column(String, primary_key=True)
    userId = Column(Integer, ForeignKey("User.id", ondelete="CASCADE"), nullable=False)
    
    mainCategory = Column(String, nullable=False)
    subCategory = Column(String, nullable=True)
    
    totalTasks = Column(Integer, default=0, nullable=False)
    completedTasks = Column(Integer, default=0, nullable=False)
    attemptedTasks = Column(Integer, default=0, nullable=False)
    
    averageAttempts = Column(DECIMAL(4, 2), default=0.0, nullable=False)
    totalTimeSpentMinutes = Column(Integer, default=0, nullable=False)
    successRate = Column(DECIMAL(5, 2), default=0.0, nullable=False)
    
    firstAttempt = Column(DateTime)
    lastActivity = Column(DateTime)
    
    createdAt = Column(DateTime, default=func.now(), nullable=False)
    updatedAt = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", back_populates="categoryProgress")

    __table_args__ = (
        Index("idx_usercategoryprogress_userid", "userId"),
        Index("idx_usercategoryprogress_maincategory", "mainCategory"),
        Index("idx_usercategoryprogress_subcategory", "subCategory"),
        Index("idx_usercategoryprogress_userid_maincategory_subcategory", "userId", "mainCategory", "subCategory", unique=True),
        Index("idx_usercategoryprogress_lastactivity", "lastActivity"),
    )


class TaskAttempt(Base):
    __tablename__ = "TaskAttempt"

    id = Column(String, primary_key=True)
    userId = Column(Integer, ForeignKey("User.id", ondelete="CASCADE"), nullable=False)
    blockId = Column(String, ForeignKey("ContentBlock.id", ondelete="CASCADE"), nullable=False)
    
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

    __table_args__ = (
        Index("idx_taskattempt_userid", "userId"),
        Index("idx_taskattempt_blockid", "blockId"),
        Index("idx_taskattempt_issuccessful", "isSuccessful"),
        Index("idx_taskattempt_createdat", "createdAt"),
        Index("idx_taskattempt_userid_blockid", "userId", "blockId"),
    )


class TaskSolution(Base):
    __tablename__ = "TaskSolution"

    id = Column(String, primary_key=True)
    userId = Column(Integer, ForeignKey("User.id", ondelete="CASCADE"), nullable=False)
    blockId = Column(String, ForeignKey("ContentBlock.id", ondelete="CASCADE"), nullable=False)
    
    finalCode = Column(Text, nullable=False)
    language = Column(String, nullable=False)
    
    totalAttempts = Column(Integer, nullable=False)
    timeToSolveMinutes = Column(Integer, nullable=False)
    
    firstAttempt = Column(DateTime, nullable=False)
    solvedAt = Column(DateTime, default=func.now(), nullable=False)
    
    createdAt = Column(DateTime, default=func.now(), nullable=False)
    updatedAt = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", back_populates="taskSolutions")
    block = relationship("ContentBlock", back_populates="taskSolutions")

    __table_args__ = (
        Index("idx_tasksolution_userid", "userId"),
        Index("idx_tasksolution_blockid", "blockId"),
        Index("idx_tasksolution_solvedat", "solvedAt"),
        Index("idx_tasksolution_userid_blockid", "userId", "blockId", unique=True),
    )


class LearningPath(Base):
    __tablename__ = "LearningPath"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    
    blockIds = Column(ARRAY(String), nullable=False)
    prerequisites = Column(ARRAY(String), default=[], nullable=False)
    
    difficulty = Column(String)
    estimatedHours = Column(Integer)
    tags = Column(ARRAY(String), default=[], nullable=False)
    
    isActive = Column(Boolean, default=True, nullable=False)
    orderIndex = Column(Integer, default=0, nullable=False)
    
    createdAt = Column(DateTime, default=func.now(), nullable=False)
    updatedAt = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    userProgress = relationship("UserPathProgress", back_populates="path")

    __table_args__ = (
        Index("idx_learningpath_isactive", "isActive"),
        Index("idx_learningpath_difficulty", "difficulty"),
    )


class UserPathProgress(Base):
    __tablename__ = "UserPathProgress"

    id = Column(String, primary_key=True)
    userId = Column(Integer, ForeignKey("User.id", ondelete="CASCADE"), nullable=False)
    pathId = Column(String, ForeignKey("LearningPath.id", ondelete="CASCADE"), nullable=False)
    
    currentBlockIndex = Column(Integer, default=0, nullable=False)
    completedBlockIds = Column(ARRAY(String), default=[], nullable=False)
    isCompleted = Column(Boolean, default=False, nullable=False)
    
    startedAt = Column(DateTime, default=func.now(), nullable=False)
    completedAt = Column(DateTime)
    lastActivity = Column(DateTime)
    
    createdAt = Column(DateTime, default=func.now(), nullable=False)
    updatedAt = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", back_populates="pathProgress")
    path = relationship("LearningPath", back_populates="userProgress")

    __table_args__ = (
        Index("idx_userpathprogress_userid", "userId"),
        Index("idx_userpathprogress_pathid", "pathId"),
        Index("idx_userpathprogress_userid_pathid", "userId", "pathId", unique=True),
        Index("idx_userpathprogress_lastactivity", "lastActivity"),
    )
