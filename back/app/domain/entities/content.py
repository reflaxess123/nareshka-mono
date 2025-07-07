"""Сущности контента"""

from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass, field


@dataclass
class ContentFile:
    """Доменная сущность файла контента"""
    id: str
    webdavPath: str
    mainCategory: str
    subCategory: str
    lastFileHash: Optional[str]
    createdAt: datetime
    updatedAt: datetime


@dataclass
class ContentBlock:
    """Доменная сущность блока контента"""
    id: str
    fileId: str
    pathTitles: List[str]
    blockTitle: str
    blockLevel: int
    orderInFile: int
    textContent: Optional[str]
    codeContent: Optional[str]
    codeLanguage: Optional[str]
    isCodeFoldable: bool
    codeFoldTitle: Optional[str]
    extractedUrls: List[str] = field(default_factory=list)
    companies: List[str] = field(default_factory=list)
    rawBlockContentHash: Optional[str] = None
    createdAt: datetime = None
    updatedAt: datetime = None


@dataclass
class UserContentProgress:
    """Доменная сущность прогресса пользователя по контенту"""
    id: str
    userId: int
    blockId: str
    solvedCount: int
    createdAt: datetime
    updatedAt: datetime 