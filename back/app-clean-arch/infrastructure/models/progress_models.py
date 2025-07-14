from sqlalchemy import (
    DECIMAL,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.infrastructure.database.connection import Base


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
    updatedAt = Column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )

    user = relationship("User", back_populates="categoryProgress")

    __table_args__ = (
        Index("idx_usercategoryprogress_userid", "userId"),
        Index("idx_usercategoryprogress_maincategory", "mainCategory"),
        Index("idx_usercategoryprogress_subcategory", "subCategory"),
        Index(
            "idx_usercategoryprogress_userid_maincategory_subcategory",
            "userId",
            "mainCategory",
            "subCategory",
            unique=True,
        ),
    )
