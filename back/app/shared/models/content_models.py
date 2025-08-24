from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.shared.database.connection import Base

# Модели ContentFile и ContentBlock перенесены в app.shared.entities.content
# Оставлено для совместимости, не использовать в основной архитектуре.


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
    block = relationship("ContentBlock")

    __table_args__ = (
        Index("idx_usercontentprogress_blockid", "blockId"),
        Index(
            "idx_usercontentprogress_userid_blockid", "userId", "blockId", unique=True
        ),
    )

    class Config:
        from_attributes = True
