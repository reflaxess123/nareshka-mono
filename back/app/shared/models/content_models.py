"""Content models - SQLAlchemy models for content management"""

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
    func,
)
from sqlalchemy.orm import relationship

from app.shared.database import Base


class ContentFile(Base):
    """
    Content file model - represents a file in the content system.
    """

    __tablename__ = "ContentFile"

    id = Column(String, primary_key=True)
    webdavPath = Column(
        String, unique=True, nullable=False, comment="Path to file in WebDAV"
    )
    mainCategory = Column(
        String, nullable=False, comment="Main category (e.g., JavaScript)"
    )
    subCategory = Column(
        String, nullable=False, comment="Subcategory (e.g., Arrays)"
    )
    lastFileHash = Column(
        String, comment="Hash of last file version for change tracking"
    )
    createdAt = Column(DateTime, default=func.now(), nullable=False)
    updatedAt = Column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )

    # Relationships
    blocks = relationship(
        "ContentBlock", back_populates="file", cascade="all, delete-orphan"
    )


class ContentBlock(Base):
    """
    Content block model - represents a section or lesson within a content file.
    """

    __tablename__ = "ContentBlock"

    id = Column(String, primary_key=True)
    fileId = Column(
        String,
        ForeignKey("ContentFile.id", ondelete="CASCADE"),
        nullable=False,
        comment="ID of the file this block belongs to",
    )

    # Content structure
    pathTitles = Column(JSON, nullable=False, comment="Navigation path titles")
    blockTitle = Column(String, nullable=False, comment="Block title")
    blockLevel = Column(Integer, nullable=False, comment="Block nesting level")
    orderInFile = Column(Integer, nullable=False, comment="Order in file")
    createdAt = Column(DateTime, default=func.now(), nullable=False)
    updatedAt = Column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )

    # Content data
    textContent = Column(Text, comment="Text content of the block")
    codeContent = Column(Text, comment="Code in the block")
    codeLanguage = Column(String, comment="Programming language of the code")
    isCodeFoldable = Column(
        Boolean, default=False, nullable=False, comment="Whether code can be folded"
    )
    codeFoldTitle = Column(String, comment="Title for folded code")

    # Extracted metadata
    extractedUrls: List[str] = Column(
        ARRAY(String), default=[], nullable=False, comment="URLs extracted from content"
    )
    companies: List[str] = Column(
        ARRAY(String),
        default=[],
        nullable=False,
        comment="Companies related to content",
    )
    rawBlockContentHash = Column(String, comment="Hash of raw block content")

    # Relationships
    file = relationship("ContentFile", back_populates="blocks")

    __table_args__ = (
        Index("idx_contentblock_fileid", "fileId"),
        Index("idx_contentblock_category", "fileId", "orderInFile"),
    )


class UserContentProgress(Base):
    """User progress tracking for content blocks"""
    
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
    
    # Relationships
    user = relationship("User", back_populates="progress")
    block = relationship("ContentBlock")