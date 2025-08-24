"""
Base classes for shared entities
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.sql import func

from app.shared.database import AuditMixin, BaseModel


class SharedEntity(BaseModel, AuditMixin):
    """
    Base class for shared entities.

    Provides common fields and functionality for entities
    that are used across multiple features.
    """

    # Primary key (explicitly defined for clarity)
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Legacy timestamp fields for backward compatibility
    createdAt = Column(DateTime, default=func.now(), nullable=False)
    updatedAt = Column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.id})>"

    @property
    def created_datetime(self) -> Optional[datetime]:
        """Access created_at with legacy compatibility"""
        return self.createdAt

    @property
    def updated_datetime(self) -> Optional[datetime]:
        """Access updated_at with legacy compatibility"""
        return self.updatedAt
