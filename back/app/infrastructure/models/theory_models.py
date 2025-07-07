from typing import List
from decimal import Decimal
from sqlalchemy import (
    ARRAY,
    DECIMAL,
    Column,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database.connection import Base
from .enums import CardState


class TheoryCard(Base):
    __tablename__ = "TheoryCard"

    id = Column(String, primary_key=True)
    ankiGuid = Column(String, unique=True, nullable=False)
    cardType = Column(String, nullable=False)
    deck = Column(String, nullable=False)
    category = Column(String, nullable=False)
    subCategory = Column(String)
    questionBlock = Column(Text, nullable=False)
    answerBlock = Column(Text, nullable=False)
    tags: List[str] = Column(ARRAY(String), default=[], nullable=False)
    orderIndex = Column(Integer, default=0, nullable=False)

    createdAt = Column(DateTime, default=func.now(), nullable=False)
    updatedAt = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    progressEntries = relationship("UserTheoryProgress", back_populates="card")

    __table_args__ = (
        Index("idx_theorycard_category", "category"),
        Index("idx_theorycard_deck", "deck"),
    )


class UserTheoryProgress(Base):
    __tablename__ = "UserTheoryProgress"

    id = Column(String, primary_key=True)
    userId = Column(Integer, ForeignKey("User.id", ondelete="CASCADE"), nullable=False)
    cardId = Column(String, ForeignKey("TheoryCard.id", ondelete="CASCADE"), nullable=False)

    solvedCount = Column(Integer, default=0, nullable=False)

    easeFactor: Decimal = Column(DECIMAL(3, 2), default=2.50, nullable=False)
    interval = Column(Integer, default=1, nullable=False)
    dueDate = Column(DateTime)
    reviewCount = Column(Integer, default=0, nullable=False)
    lapseCount = Column(Integer, default=0, nullable=False)
    cardState: SQLEnum = Column(SQLEnum(CardState), default=CardState.NEW, nullable=False)
    learningStep = Column(Integer, default=0, nullable=False)
    lastReviewDate = Column(DateTime)

    createdAt = Column(DateTime, default=func.now(), nullable=False)
    updatedAt = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", back_populates="theoryProgress")
    card = relationship("TheoryCard", back_populates="progressEntries")

    __table_args__ = (
        Index("idx_usertheoryprogress_cardid", "cardId"),
        Index("idx_usertheoryprogress_duedate", "dueDate"),
        Index("idx_usertheoryprogress_cardstate", "cardState"),
        Index("idx_usertheoryprogress_userid_cardid", "userId", "cardId", unique=True),
    ) 