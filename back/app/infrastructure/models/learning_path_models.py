from typing import List
from sqlalchemy import (
    ARRAY,
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

from ..database.connection import Base


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
        Index("idx_learningpath_orderindex", "orderIndex"),
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