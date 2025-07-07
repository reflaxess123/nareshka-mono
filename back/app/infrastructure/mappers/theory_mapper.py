"""Маппер для Theory entities"""

from typing import List, Optional
from datetime import datetime

from ...domain.entities.theory import TheoryCard as DomainTheoryCard, UserTheoryProgress as DomainUserTheoryProgress
from ...domain.entities.enums import CardState, ProgressStatus
from ..models.theory_models import TheoryCard as InfraTheoryCard, UserTheoryProgress as InfraUserTheoryProgress


class TheoryMapper:
    """Маппер для конвертации Theory entities между domain и infrastructure слоями"""
    
    @staticmethod
    def theory_card_to_domain(infra_theory_card: InfraTheoryCard) -> DomainTheoryCard:
        """Конвертирует Infrastructure TheoryCard в Domain TheoryCard"""
        if not infra_theory_card:
            return None
            
        return DomainTheoryCard(
            id=infra_theory_card.id,
            ankiGuid=infra_theory_card.ankiGuid,
            cardType=infra_theory_card.cardType,
            deck=infra_theory_card.deck,
            category=infra_theory_card.category,
            subCategory=infra_theory_card.subCategory,
            questionBlock=infra_theory_card.questionBlock,
            answerBlock=infra_theory_card.answerBlock,
            tags=infra_theory_card.tags or [],
            orderIndex=infra_theory_card.orderIndex,
            createdAt=infra_theory_card.createdAt,
            updatedAt=infra_theory_card.updatedAt
        )
    
    @staticmethod
    def theory_card_to_infrastructure(domain_theory_card: DomainTheoryCard) -> InfraTheoryCard:
        """Конвертирует Domain TheoryCard в Infrastructure TheoryCard"""
        if not domain_theory_card:
            return None
            
        return InfraTheoryCard(
            id=domain_theory_card.id,
            ankiGuid=domain_theory_card.ankiGuid,
            cardType=domain_theory_card.cardType,
            deck=domain_theory_card.deck,
            category=domain_theory_card.category,
            subCategory=domain_theory_card.subCategory,
            questionBlock=domain_theory_card.questionBlock,
            answerBlock=domain_theory_card.answerBlock,
            tags=domain_theory_card.tags or [],
            orderIndex=domain_theory_card.orderIndex,
            createdAt=domain_theory_card.createdAt,
            updatedAt=domain_theory_card.updatedAt
        )
    
    @staticmethod
    def user_theory_progress_to_domain(infra_progress: InfraUserTheoryProgress) -> DomainUserTheoryProgress:
        """Конвертирует Infrastructure UserTheoryProgress в Domain UserTheoryProgress"""
        if not infra_progress:
            return None
            
        return DomainUserTheoryProgress(
            id=infra_progress.id,
            userId=infra_progress.userId,
            cardId=infra_progress.cardId,
            solvedCount=infra_progress.solvedCount,
            easeFactor=infra_progress.easeFactor,
            interval=infra_progress.interval,
            dueDate=infra_progress.dueDate,
            reviewCount=infra_progress.reviewCount,
            lapseCount=infra_progress.lapseCount,
            cardState=infra_progress.cardState,
            learningStep=infra_progress.learningStep,
            lastReviewDate=infra_progress.lastReviewDate,
            createdAt=infra_progress.createdAt,
            updatedAt=infra_progress.updatedAt
        )
    
    @staticmethod
    def user_theory_progress_to_infrastructure(domain_progress: DomainUserTheoryProgress) -> InfraUserTheoryProgress:
        """Конвертирует Domain UserTheoryProgress в Infrastructure UserTheoryProgress"""
        if not domain_progress:
            return None
            
        return InfraUserTheoryProgress(
            id=domain_progress.id,
            userId=domain_progress.userId,
            cardId=domain_progress.cardId,
            solvedCount=domain_progress.solvedCount,
            easeFactor=domain_progress.easeFactor,
            interval=domain_progress.interval,
            dueDate=domain_progress.dueDate,
            reviewCount=domain_progress.reviewCount,
            lapseCount=domain_progress.lapseCount,
            cardState=domain_progress.cardState,
            learningStep=domain_progress.learningStep,
            lastReviewDate=domain_progress.lastReviewDate,
            createdAt=domain_progress.createdAt,
            updatedAt=domain_progress.updatedAt
        )
    
    @staticmethod
    def theory_card_list_to_domain(infra_cards: List[InfraTheoryCard]) -> List[DomainTheoryCard]:
        """Конвертирует список Infrastructure TheoryCards в Domain TheoryCards"""
        if not infra_cards:
            return []
        return [TheoryMapper.theory_card_to_domain(card) for card in infra_cards if card]
    
    @staticmethod
    def user_theory_progress_list_to_domain(infra_progress: List[InfraUserTheoryProgress]) -> List[DomainUserTheoryProgress]:
        """Конвертирует список Infrastructure UserTheoryProgress в Domain UserTheoryProgress"""
        if not infra_progress:
            return []
        return [TheoryMapper.user_theory_progress_to_domain(progress) for progress in infra_progress if progress] 