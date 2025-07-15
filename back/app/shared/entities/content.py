"""
Shared Content Entities - основные модели контента

Используются в нескольких features для ссылок на контент.
Модели без cross-feature relationships для обеспечения изоляции features.
"""

from typing import List
from sqlalchemy import (
    ARRAY,
    JSON,
    Boolean,
    Column,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.shared.database import Base, AuditMixin


class ContentFile(Base, AuditMixin):
    """
    Shared ContentFile entity for cross-feature usage.
    
    Представляет один файл в WebDAV системе с контентом для обучения.
    NO CROSS-FEATURE RELATIONSHIPS - features should use repositories for data access.
    """
    __tablename__ = "ContentFile"

    id = Column(String, primary_key=True)
    webdavPath = Column(String, unique=True, nullable=False, comment="Путь к файлу в WebDAV")
    mainCategory = Column(String, nullable=False, comment="Основная категория (например, JavaScript)")
    subCategory = Column(String, nullable=False, comment="Подкатегория (например, Arrays)")
    lastFileHash = Column(String, comment="Хэш последней версии файла для отслеживания изменений")

    # Internal content feature relationship is allowed
    blocks = relationship("ContentBlock", back_populates="file", cascade="all, delete-orphan")

    class Config:
        from_attributes = True


class ContentBlock(Base, AuditMixin):
    """
    Shared ContentBlock entity for cross-feature usage.
    
    Представляет отдельный раздел или урок внутри файла контента.
    NO CROSS-FEATURE RELATIONSHIPS - features should use repositories for data access.
    """
    __tablename__ = "ContentBlock"

    id = Column(String, primary_key=True)
    fileId = Column(
        String, 
        ForeignKey("ContentFile.id", ondelete="CASCADE"), 
        nullable=False,
        comment="ID файла, к которому принадлежит блок"
    )
    
    # Content structure
    pathTitles = Column(JSON, nullable=False, comment="Путь заголовков для навигации")
    blockTitle = Column(String, nullable=False, comment="Заголовок блока")
    blockLevel = Column(Integer, nullable=False, comment="Уровень вложенности блока")
    orderInFile = Column(Integer, nullable=False, comment="Порядок блока в файле")

    # Content data
    textContent = Column(Text, comment="Текстовое содержимое блока")
    codeContent = Column(Text, comment="Код в блоке")
    codeLanguage = Column(String, comment="Язык программирования кода")
    isCodeFoldable = Column(Boolean, default=False, nullable=False, comment="Можно ли свернуть код")
    codeFoldTitle = Column(String, comment="Заголовок для свернутого кода")

    # Extracted metadata
    extractedUrls: List[str] = Column(
        ARRAY(String), 
        default=[], 
        nullable=False,
        comment="Извлеченные из контента URL"
    )
    companies: List[str] = Column(
        ARRAY(String), 
        default=[], 
        nullable=False,
        comment="Компании, связанные с контентом"
    )
    rawBlockContentHash = Column(String, comment="Хэш исходного содержимого блока")

    # Internal content feature relationship is allowed
    file = relationship("ContentFile", back_populates="blocks")
    
    # NO CROSS-FEATURE RELATIONSHIPS - для обеспечения изоляции features
    # Features должны использовать repositories для получения связанных данных:
    # - progress feature для получения ContentBlockProgress
    # - task feature для получения TaskAttempt, TaskSolution
    # - code_editor feature для получения связанных данных
    
    __table_args__ = (
        Index("idx_contentblock_fileid", "fileId"),
        Index("idx_contentblock_category", "fileId", "orderInFile"),
    )

    class Config:
        from_attributes = True 


