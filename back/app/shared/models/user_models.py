from sqlalchemy import (
    Column,
    DateTime,
    Enum as SQLEnum,
    Integer,
    String,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.shared.database.connection import Base

from .enums import UserRole


class User(Base):
    __tablename__ = "User"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role: SQLEnum = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    createdAt = Column(DateTime, default=func.now(), nullable=False)
    updatedAt = Column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )

    totalTasksSolved = Column(Integer, default=0, server_default="0", nullable=False)
    lastActivityDate = Column(DateTime, nullable=True)

    progress = relationship("UserContentProgress", back_populates="user")
    theoryProgress = relationship("UserTheoryProgress", back_populates="user")
    categoryProgress = relationship("UserCategoryProgress", back_populates="user")
    taskSolutions = relationship("TaskSolution", back_populates="user")
    pathProgress = relationship("UserPathProgress", back_populates="user")

    class Config:
        from_attributes = True
