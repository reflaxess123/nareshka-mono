"""Маппер для TestCase entities"""

from typing import List, Optional
from datetime import datetime

from ...domain.entities.test_case import TestCase as DomainTestCase, TestValidationResult as DomainTestValidationResult
from ..models.test_case_models import TestCase as InfraTestCase, TestValidationResult as InfraTestValidationResult


class TestCaseMapper:
    """Маппер для конвертации TestCase entities между domain и infrastructure слоями"""
    
    @staticmethod
    def test_case_to_domain(infra_test_case: InfraTestCase) -> DomainTestCase:
        """Конвертирует Infrastructure TestCase в Domain TestCase"""
        if not infra_test_case:
            return None
            
        return DomainTestCase(
            id=infra_test_case.id,
            blockId=infra_test_case.blockId,
            name=infra_test_case.name,
            description=infra_test_case.description,
            input=infra_test_case.input,
            expectedOutput=infra_test_case.expectedOutput,
            isPublic=infra_test_case.isPublic,
            difficulty=infra_test_case.difficulty,
            weight=infra_test_case.weight,
            timeoutSeconds=infra_test_case.timeoutSeconds,
            isAIGenerated=infra_test_case.isAIGenerated,
            generationPrompt=infra_test_case.generationPrompt,
            generatedAt=infra_test_case.generatedAt,
            generationModel=infra_test_case.generationModel,
            executionCount=infra_test_case.executionCount,
            passRate=infra_test_case.passRate,
            isActive=infra_test_case.isActive,
            orderIndex=infra_test_case.orderIndex,
            createdAt=infra_test_case.createdAt,
            updatedAt=infra_test_case.updatedAt
        )
    
    @staticmethod
    def test_case_to_infrastructure(domain_test_case: DomainTestCase) -> InfraTestCase:
        """Конвертирует Domain TestCase в Infrastructure TestCase"""
        if not domain_test_case:
            return None
            
        return InfraTestCase(
            id=domain_test_case.id,
            blockId=domain_test_case.blockId,
            name=domain_test_case.name,
            description=domain_test_case.description,
            input=domain_test_case.input,
            expectedOutput=domain_test_case.expectedOutput,
            isPublic=domain_test_case.isPublic,
            difficulty=domain_test_case.difficulty,
            weight=domain_test_case.weight,
            timeoutSeconds=domain_test_case.timeoutSeconds,
            isAIGenerated=domain_test_case.isAIGenerated,
            generationPrompt=domain_test_case.generationPrompt,
            generatedAt=domain_test_case.generatedAt,
            generationModel=domain_test_case.generationModel,
            executionCount=domain_test_case.executionCount,
            passRate=domain_test_case.passRate,
            isActive=domain_test_case.isActive,
            orderIndex=domain_test_case.orderIndex,
            createdAt=domain_test_case.createdAt,
            updatedAt=domain_test_case.updatedAt
        )
    
    @staticmethod
    def test_validation_result_to_domain(infra_result: InfraTestValidationResult) -> DomainTestValidationResult:
        """Конвертирует Infrastructure TestValidationResult в Domain TestValidationResult"""
        if not infra_result:
            return None
            
        return DomainTestValidationResult(
            id=infra_result.id,
            testCaseId=infra_result.testCaseId,
            attemptId=infra_result.attemptId,
            passed=infra_result.passed,
            actualOutput=infra_result.actualOutput,
            executionTimeMs=infra_result.executionTimeMs,
            errorMessage=infra_result.errorMessage,
            outputMatch=infra_result.outputMatch,
            outputSimilarity=infra_result.outputSimilarity,
            createdAt=infra_result.createdAt
        )
    
    @staticmethod
    def test_validation_result_to_infrastructure(domain_result: DomainTestValidationResult) -> InfraTestValidationResult:
        """Конвертирует Domain TestValidationResult в Infrastructure TestValidationResult"""
        if not domain_result:
            return None
            
        return InfraTestValidationResult(
            id=domain_result.id,
            testCaseId=domain_result.testCaseId,
            attemptId=domain_result.attemptId,
            passed=domain_result.passed,
            actualOutput=domain_result.actualOutput,
            executionTimeMs=domain_result.executionTimeMs,
            errorMessage=domain_result.errorMessage,
            outputMatch=domain_result.outputMatch,
            outputSimilarity=domain_result.outputSimilarity,
            createdAt=domain_result.createdAt
        )
    
    @staticmethod
    def test_case_list_to_domain(infra_test_cases: List[InfraTestCase]) -> List[DomainTestCase]:
        """Конвертирует список Infrastructure TestCases в Domain TestCases"""
        if not infra_test_cases:
            return []
        return [TestCaseMapper.test_case_to_domain(test_case) for test_case in infra_test_cases if test_case]
    
    @staticmethod
    def test_validation_result_list_to_domain(infra_results: List[InfraTestValidationResult]) -> List[DomainTestValidationResult]:
        """Конвертирует список Infrastructure TestValidationResults в Domain TestValidationResults"""
        if not infra_results:
            return []
        return [TestCaseMapper.test_validation_result_to_domain(result) for result in infra_results if result] 