from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import Column, DateTime, func
from sqlalchemy.orm import as_declarative, declared_attr

from app.core.logging import get_logger

logger = get_logger(__name__)


@as_declarative()
class BaseModel:
    """
    Base model for all database entities with common fields and methods.
    """

    id: Any
    __name__: str

    # Common timestamps
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    @declared_attr
    def __tablename__(cls) -> str:
        """Generate table name from class name."""
        return cls.__name__.lower()

    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance to dictionary."""
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }

    def update_from_dict(
        self, data: Dict[str, Any], exclude: Optional[set] = None
    ) -> None:
        """Update model instance from dictionary."""
        exclude = exclude or {"id", "created_at"}

        for key, value in data.items():
            if key not in exclude and hasattr(self, key):
                setattr(self, key, value)

        logger.debug(
            f"Updated {self.__class__.__name__} with data",
            extra={
                "model": self.__class__.__name__,
                "updated_fields": list(data.keys()),
            },
        )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={getattr(self, 'id', None)})>"


class AuditMixin:
    """
    Mixin for models that need audit trail (created_by, updated_by).
    """

    created_by = Column("created_by", nullable=True)
    updated_by = Column("updated_by", nullable=True)


class SoftDeleteMixin:
    """
    Mixin for models that support soft deletion.
    """

    deleted_at = Column(DateTime(timezone=True), nullable=True)
    is_deleted = Column("is_deleted", default=False, nullable=False)

    def soft_delete(self, user_id: Optional[str] = None) -> None:
        """Mark record as deleted."""
        self.deleted_at = datetime.utcnow()
        self.is_deleted = True
        if hasattr(self, "updated_by") and user_id:
            self.updated_by = user_id

        logger.info(
            f"Soft deleted {self.__class__.__name__}",
            extra={
                "model": self.__class__.__name__,
                "model_id": getattr(self, "id", None),
                "deleted_by": user_id,
            },
        )

    def restore(self, user_id: Optional[str] = None) -> None:
        """Restore soft deleted record."""
        self.deleted_at = None
        self.is_deleted = False
        if hasattr(self, "updated_by") and user_id:
            self.updated_by = user_id

        logger.info(
            f"Restored {self.__class__.__name__}",
            extra={
                "model": self.__class__.__name__,
                "model_id": getattr(self, "id", None),
                "restored_by": user_id,
            },
        )


# For backward compatibility with existing code
Base = BaseModel
