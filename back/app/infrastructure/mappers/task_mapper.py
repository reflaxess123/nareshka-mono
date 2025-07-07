"""Маппер для Task entities"""

from typing import List, Optional
from datetime import datetime

from ...domain.entities.task import TaskAttempt as DomainTaskAttempt, TaskSolution as DomainTaskSolution
from ..models.task_models import TaskAttempt as InfraTaskAttempt, TaskSolution as InfraTaskSolution


class TaskMapper:
    """Маппер для конвертации Task entities между domain и infrastructure слоями"""
    
    @staticmethod
    def task_attempt_to_domain(infra_attempt: InfraTaskAttempt) -> DomainTaskAttempt:
        """Конвертирует Infrastructure TaskAttempt в Domain TaskAttempt"""
        if not infra_attempt:
            return None
            
        return DomainTaskAttempt(
            id=infra_attempt.id,
            userId=infra_attempt.userId,
            taskId=infra_attempt.blockId,
            code=infra_attempt.sourceCode,
            languageId=infra_attempt.language,
            result="success" if infra_attempt.isSuccessful else "failed",
            error=infra_attempt.errorMessage,
            executionTime=infra_attempt.executionTimeMs,
            memory=infra_attempt.memoryUsedMB,
            createdAt=infra_attempt.createdAt,
            updatedAt=infra_attempt.createdAt
        )
    
    @staticmethod
    def task_attempt_to_infrastructure(domain_attempt: DomainTaskAttempt) -> InfraTaskAttempt:
        """Конвертирует Domain TaskAttempt в Infrastructure TaskAttempt"""
        if not domain_attempt:
            return None
            
        return InfraTaskAttempt(
            id=domain_attempt.id,
            userId=domain_attempt.userId,
            blockId=domain_attempt.taskId,
            sourceCode=domain_attempt.code,
            language=domain_attempt.languageId,
            isSuccessful=domain_attempt.result == "success" if domain_attempt.result else False,
            errorMessage=domain_attempt.error,
            executionTimeMs=domain_attempt.executionTime,
            memoryUsedMB=domain_attempt.memory,
            attemptNumber=1,
            createdAt=domain_attempt.createdAt
        )
    
    @staticmethod
    def task_solution_to_domain(infra_solution: InfraTaskSolution) -> DomainTaskSolution:
        """Конвертирует Infrastructure TaskSolution в Domain TaskSolution"""
        if not infra_solution:
            return None
            
        return DomainTaskSolution(
            id=infra_solution.id,
            userId=infra_solution.userId,
            taskId=infra_solution.blockId,
            code=infra_solution.finalCode,
            languageId=infra_solution.language,
            createdAt=infra_solution.createdAt,
            updatedAt=infra_solution.updatedAt
        )
    
    @staticmethod
    def task_solution_to_infrastructure(domain_solution: DomainTaskSolution) -> InfraTaskSolution:
        """Конвертирует Domain TaskSolution в Infrastructure TaskSolution"""
        if not domain_solution:
            return None
            
        return InfraTaskSolution(
            id=domain_solution.id,
            userId=domain_solution.userId,
            blockId=domain_solution.taskId,
            finalCode=domain_solution.code,
            language=domain_solution.languageId,
            totalAttempts=1,
            timeToSolveMinutes=0,
            firstAttempt=domain_solution.createdAt or datetime.utcnow(),
            solvedAt=domain_solution.updatedAt or datetime.utcnow(),
            createdAt=domain_solution.createdAt,
            updatedAt=domain_solution.updatedAt
        )
    
    @staticmethod
    def task_attempt_list_to_domain(infra_attempts: List[InfraTaskAttempt]) -> List[DomainTaskAttempt]:
        """Конвертирует список Infrastructure TaskAttempts в Domain TaskAttempts"""
        if not infra_attempts:
            return []
        return [TaskMapper.task_attempt_to_domain(attempt) for attempt in infra_attempts if attempt]
    
    @staticmethod
    def task_solution_list_to_domain(infra_solutions: List[InfraTaskSolution]) -> List[DomainTaskSolution]:
        """Конвертирует список Infrastructure TaskSolutions в Domain TaskSolutions"""
        if not infra_solutions:
            return []
        return [TaskMapper.task_solution_to_domain(solution) for solution in infra_solutions if solution] 