"""Маппер для Execution entities"""

from typing import List, Optional
from datetime import datetime

from ...domain.entities.execution import SupportedLanguage as DomainSupportedLanguage, CodeExecution as DomainCodeExecution, UserCodeSolution as DomainUserCodeSolution
from ...domain.entities.enums import ExecutionStatus, CodeLanguage
from ..models.code_execution_models import SupportedLanguage as InfraSupportedLanguage, CodeExecution as InfraCodeExecution, UserCodeSolution as InfraUserCodeSolution


class ExecutionMapper:
    """Маппер для конвертации Execution entities между domain и infrastructure слоями"""
    
    @staticmethod
    def supported_language_to_domain(infra_language: InfraSupportedLanguage) -> DomainSupportedLanguage:
        """Конвертирует Infrastructure SupportedLanguage в Domain SupportedLanguage"""
        if not infra_language:
            return None
            
        return DomainSupportedLanguage(
            id=infra_language.id,
            name=infra_language.name,
            language=CodeLanguage(infra_language.language.value) if infra_language.language else CodeLanguage.PYTHON,
            version=infra_language.version,
            dockerImage=infra_language.dockerImage,
            compileCommand=infra_language.compileCommand,
            runCommand=infra_language.runCommand,
            isActive=infra_language.isActive,
            createdAt=infra_language.createdAt,
            updatedAt=infra_language.updatedAt
        )
    
    @staticmethod
    def supported_language_to_infrastructure(domain_language: DomainSupportedLanguage) -> InfraSupportedLanguage:
        """Конвертирует Domain SupportedLanguage в Infrastructure SupportedLanguage"""
        if not domain_language:
            return None
            
        return InfraSupportedLanguage(
            id=domain_language.id,
            name=domain_language.name,
            language=domain_language.language,
            version=domain_language.version,
            dockerImage=domain_language.dockerImage,
            compileCommand=domain_language.compileCommand,
            runCommand=domain_language.runCommand,
            isActive=domain_language.isActive,
            createdAt=domain_language.createdAt,
            updatedAt=domain_language.updatedAt
        )
    
    @staticmethod
    def code_execution_to_domain(infra_execution: InfraCodeExecution) -> DomainCodeExecution:
        """Конвертирует Infrastructure CodeExecution в Domain CodeExecution"""
        if not infra_execution:
            return None
            
        return DomainCodeExecution(
            id=infra_execution.id,
            userId=infra_execution.userId,
            languageId=infra_execution.languageId,
            code=infra_execution.code,
            input=infra_execution.input,
            output=infra_execution.output,
            error=infra_execution.error,
            executionTime=infra_execution.executionTime,
            memory=infra_execution.memory,
            status=ExecutionStatus(infra_execution.status.value) if infra_execution.status else ExecutionStatus.PENDING,
            createdAt=infra_execution.createdAt,
            updatedAt=infra_execution.updatedAt
        )
    
    @staticmethod
    def code_execution_to_infrastructure(domain_execution: DomainCodeExecution) -> InfraCodeExecution:
        """Конвертирует Domain CodeExecution в Infrastructure CodeExecution"""
        if not domain_execution:
            return None
            
        return InfraCodeExecution(
            id=domain_execution.id,
            userId=domain_execution.userId,
            languageId=domain_execution.languageId,
            code=domain_execution.code,
            input=domain_execution.input,
            output=domain_execution.output,
            error=domain_execution.error,
            executionTime=domain_execution.executionTime,
            memory=domain_execution.memory,
            status=domain_execution.status,
            createdAt=domain_execution.createdAt,
            updatedAt=domain_execution.updatedAt
        )
    
    @staticmethod
    def user_code_solution_to_domain(infra_solution: InfraUserCodeSolution) -> DomainUserCodeSolution:
        """Конвертирует Infrastructure UserCodeSolution в Domain UserCodeSolution"""
        if not infra_solution:
            return None
            
        return DomainUserCodeSolution(
            id=infra_solution.id,
            userId=infra_solution.userId,
            taskId=infra_solution.taskId,
            code=infra_solution.code,
            languageId=infra_solution.languageId,
            createdAt=infra_solution.createdAt,
            updatedAt=infra_solution.updatedAt
        )
    
    @staticmethod
    def user_code_solution_to_infrastructure(domain_solution: DomainUserCodeSolution) -> InfraUserCodeSolution:
        """Конвертирует Domain UserCodeSolution в Infrastructure UserCodeSolution"""
        if not domain_solution:
            return None
            
        return InfraUserCodeSolution(
            id=domain_solution.id,
            userId=domain_solution.userId,
            taskId=domain_solution.taskId,
            code=domain_solution.code,
            languageId=domain_solution.languageId,
            createdAt=domain_solution.createdAt,
            updatedAt=domain_solution.updatedAt
        )
    
    @staticmethod
    def supported_language_list_to_domain(infra_languages: List[InfraSupportedLanguage]) -> List[DomainSupportedLanguage]:
        """Конвертирует список Infrastructure SupportedLanguages в Domain SupportedLanguages"""
        if not infra_languages:
            return []
        return [ExecutionMapper.supported_language_to_domain(lang) for lang in infra_languages if lang]
    
    @staticmethod
    def code_execution_list_to_domain(infra_executions: List[InfraCodeExecution]) -> List[DomainCodeExecution]:
        """Конвертирует список Infrastructure CodeExecutions в Domain CodeExecutions"""
        if not infra_executions:
            return []
        return [ExecutionMapper.code_execution_to_domain(exec) for exec in infra_executions if exec]
    
    @staticmethod
    def user_code_solution_list_to_domain(infra_solutions: List[InfraUserCodeSolution]) -> List[DomainUserCodeSolution]:
        """Конвертирует список Infrastructure UserCodeSolutions в Domain UserCodeSolutions"""
        if not infra_solutions:
            return []
        return [ExecutionMapper.user_code_solution_to_domain(sol) for sol in infra_solutions if sol] 