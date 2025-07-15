from typing import List

from sqlalchemy import (
    ARRAY,
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.shared.database.connection import Base


class ContentFile(Base):
    __tablename__ = "ContentFile"

    id = Column(String, primary_key=True)
    webdavPath = Column(String, unique=True, nullable=False)
    mainCategory = Column(String, nullable=False)
    subCategory = Column(String, nullable=False)
    lastFileHash = Column(String)
    createdAt = Column(DateTime, default=func.now(), nullable=False)
    updatedAt = Column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )

    blocks = relationship("ContentBlock", back_populates="file")

    class Config:
        from_attributes = True


class ContentBlock(Base):
    __tablename__ = "ContentBlock"

    id = Column(String, primary_key=True)
    fileId = Column(
        String, ForeignKey("ContentFile.id", ondelete="CASCADE"), nullable=False
    )
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
    updatedAt = Column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )

    file = relationship("ContentFile", back_populates="blocks")
    progressEntries = relationship("UserContentProgress", back_populates="block")
    taskAttempts = relationship("TaskAttempt", back_populates="block")
    taskSolutions = relationship("TaskSolution", back_populates="block")
    testCases = relationship("TestCase", back_populates="block")

    __table_args__ = (Index("idx_contentblock_fileid", "fileId"),)

    class Config:
        from_attributes = True


class UserContentProgress(Base):
    __tablename__ = "UserContentProgress"

    id = Column(String, primary_key=True)
    userId = Column(Integer, ForeignKey("User.id", ondelete="CASCADE"), nullable=False)
    blockId = Column(
        String, ForeignKey("ContentBlock.id", ondelete="CASCADE"), nullable=False
    )
    solvedCount = Column(Integer, default=0, nullable=False)

    createdAt = Column(DateTime, default=func.now(), nullable=False)
    updatedAt = Column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )

    user = relationship("User", back_populates="progress")
    block = relationship("ContentBlock", back_populates="progressEntries")

    __table_args__ = (
        Index("idx_usercontentprogress_blockid", "blockId"),
        Index(
            "idx_usercontentprogress_userid_blockid", "userId", "blockId", unique=True
        ),
    )

    class Config:
        from_attributes = True


