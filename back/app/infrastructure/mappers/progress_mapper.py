"""Маппер для Progress entities"""

from typing import List, Optional
from datetime import datetime

from ...domain.entities.progress import UserCategoryProgress as DomainUserCategoryProgress, LearningPath as DomainLearningPath, UserPathProgress as DomainUserPathProgress
from ...domain.entities.enums import ProgressStatus
from ..models.progress_models import UserCategoryProgress as InfraUserCategoryProgress
from ..models.learning_path_models import LearningPath as InfraLearningPath, UserPathProgress as InfraUserPathProgress


class ProgressMapper:
    """Маппер для конвертации Progress entities между domain и infrastructure слоями"""
    
    @staticmethod
    def user_category_progress_to_domain(infra_progress: InfraUserCategoryProgress) -> DomainUserCategoryProgress:
        """Конвертирует Infrastructure UserCategoryProgress в Domain UserCategoryProgress"""
        if not infra_progress:
            return None
            
        return DomainUserCategoryProgress(
            id=infra_progress.id,
            userId=infra_progress.userId,
            category=infra_progress.category,
            completedTasks=infra_progress.completedTasks,
            totalTasks=infra_progress.totalTasks,
            completedTheory=infra_progress.completedTheory,
            totalTheory=infra_progress.totalTheory,
            completedContent=infra_progress.completedContent,
            totalContent=infra_progress.totalContent,
            createdAt=infra_progress.createdAt,
            updatedAt=infra_progress.updatedAt
        )
    
    @staticmethod
    def user_category_progress_to_infrastructure(domain_progress: DomainUserCategoryProgress) -> InfraUserCategoryProgress:
        """Конвертирует Domain UserCategoryProgress в Infrastructure UserCategoryProgress"""
        if not domain_progress:
            return None
            
        return InfraUserCategoryProgress(
            id=domain_progress.id,
            userId=domain_progress.userId,
            category=domain_progress.category,
            completedTasks=domain_progress.completedTasks,
            totalTasks=domain_progress.totalTasks,
            completedTheory=domain_progress.completedTheory,
            totalTheory=domain_progress.totalTheory,
            completedContent=domain_progress.completedContent,
            totalContent=domain_progress.totalContent,
            createdAt=domain_progress.createdAt,
            updatedAt=domain_progress.updatedAt
        )
    
    @staticmethod
    def learning_path_to_domain(infra_path: InfraLearningPath) -> DomainLearningPath:
        """Конвертирует Infrastructure LearningPath в Domain LearningPath"""
        if not infra_path:
            return None
            
        return DomainLearningPath(
            id=infra_path.id,
            name=infra_path.name,
            description=infra_path.description,
            difficulty=infra_path.difficulty,
            estimatedTime=infra_path.estimatedTime,
            isActive=infra_path.isActive,
            createdAt=infra_path.createdAt,
            updatedAt=infra_path.updatedAt
        )
    
    @staticmethod
    def learning_path_to_infrastructure(domain_path: DomainLearningPath) -> InfraLearningPath:
        """Конвертирует Domain LearningPath в Infrastructure LearningPath"""
        if not domain_path:
            return None
            
        return InfraLearningPath(
            id=domain_path.id,
            name=domain_path.name,
            description=domain_path.description,
            difficulty=domain_path.difficulty,
            estimatedTime=domain_path.estimatedTime,
            isActive=domain_path.isActive,
            createdAt=domain_path.createdAt,
            updatedAt=domain_path.updatedAt
        )
    
    @staticmethod
    def user_path_progress_to_domain(infra_progress: InfraUserPathProgress) -> DomainUserPathProgress:
        """Конвертирует Infrastructure UserPathProgress в Domain UserPathProgress"""
        if not infra_progress:
            return None
            
        return DomainUserPathProgress(
            id=infra_progress.id,
            userId=infra_progress.userId,
            pathId=infra_progress.pathId,
            currentStep=infra_progress.currentStep,
            completedSteps=infra_progress.completedSteps,
            totalSteps=infra_progress.totalSteps,
            status=ProgressStatus(infra_progress.status.value) if infra_progress.status else ProgressStatus.NOT_STARTED,
            startedAt=infra_progress.startedAt,
            completedAt=infra_progress.completedAt,
            createdAt=infra_progress.createdAt,
            updatedAt=infra_progress.updatedAt
        )
    
    @staticmethod
    def user_path_progress_to_infrastructure(domain_progress: DomainUserPathProgress) -> InfraUserPathProgress:
        """Конвертирует Domain UserPathProgress в Infrastructure UserPathProgress"""
        if not domain_progress:
            return None
            
        return InfraUserPathProgress(
            id=domain_progress.id,
            userId=domain_progress.userId,
            pathId=domain_progress.pathId,
            currentStep=domain_progress.currentStep,
            completedSteps=domain_progress.completedSteps,
            totalSteps=domain_progress.totalSteps,
            status=domain_progress.status,
            startedAt=domain_progress.startedAt,
            completedAt=domain_progress.completedAt,
            createdAt=domain_progress.createdAt,
            updatedAt=domain_progress.updatedAt
        )
    
    @staticmethod
    def user_category_progress_list_to_domain(infra_progress: List[InfraUserCategoryProgress]) -> List[DomainUserCategoryProgress]:
        """Конвертирует список Infrastructure UserCategoryProgress в Domain UserCategoryProgress"""
        if not infra_progress:
            return []
        return [ProgressMapper.user_category_progress_to_domain(prog) for prog in infra_progress if prog]
    
    @staticmethod
    def learning_path_list_to_domain(infra_paths: List[InfraLearningPath]) -> List[DomainLearningPath]:
        """Конвертирует список Infrastructure LearningPaths в Domain LearningPaths"""
        if not infra_paths:
            return []
        return [ProgressMapper.learning_path_to_domain(path) for path in infra_paths if path]
    
    @staticmethod
    def user_path_progress_list_to_domain(infra_progress: List[InfraUserPathProgress]) -> List[DomainUserPathProgress]:
        """Конвертирует список Infrastructure UserPathProgress в Domain UserPathProgress"""
        if not infra_progress:
            return []
        return [ProgressMapper.user_path_progress_to_domain(prog) for prog in infra_progress if prog] 