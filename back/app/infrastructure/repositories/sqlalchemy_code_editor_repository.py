#!/usr/bin/env python3
"""Реализация репозитория для работы с редактором кода через SQLAlchemy"""

import logging
import uuid
import re
import json
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy import desc, func, and_
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError

from app.domain.repositories.code_editor_repository import CodeEditorRepository
from ...domain.entities.code_editor import (
    SupportedLanguage as SupportedLanguageEntity,
    CodeExecution as CodeExecutionEntity,
    UserCodeSolution as UserCodeSolutionEntity,
    TestCaseExecution,
    ValidationResult,
    ExecutionStats
)
from ...domain.entities.test_case import TestCase as TestCaseEntity
from ...domain.entities.enums import CodeLanguage, ExecutionStatus
from ..models.code_execution_models import (
    SupportedLanguage as SupportedLanguageModel,
    CodeExecution as CodeExecutionModel,
    UserCodeSolution as UserCodeSolutionModel
)
from ..models.test_case_models import TestCase as TestCaseModel
from ..models.content_models import ContentBlock
from ..models.user_models import User
from ..mappers.execution_mapper import ExecutionMapper
from ..mappers.test_case_mapper import TestCaseMapper

logger = logging.getLogger(__name__)


class SQLAlchemyCodeEditorRepository(CodeEditorRepository):
    def __init__(self, db_session: Session):
        self.db_session = db_session

    # SupportedLanguage methods
    async def get_supported_languages(self) -> List[SupportedLanguageEntity]:
        db_languages = self.db_session.query(SupportedLanguageModel).filter(
            SupportedLanguageModel.isEnabled == True
        ).all()
        
        if not db_languages:
            # Fallback для базовых языков если не настроены в БД
            return [
                SupportedLanguageEntity(
                    id="python39",
                    name="Python 3.9",
                    language=CodeLanguage.PYTHON,
                    version="3.9",
                    dockerImage="python:3.9-alpine",
                    fileExtension=".py",
                    runCommand="python3 {file}",
                    timeoutSeconds=10,
                    memoryLimitMB=128,
                    isEnabled=True,
                    createdAt=datetime.now(),
                    updatedAt=datetime.now()
                ),
                SupportedLanguageEntity(
                    id="node18",
                    name="Node.js 18",
                    language=CodeLanguage.JAVASCRIPT,
                    version="18",
                    dockerImage="node:18-alpine",
                    fileExtension=".js",
                    runCommand="node {file}",
                    timeoutSeconds=10,
                    memoryLimitMB=128,
                    isEnabled=True,
                    createdAt=datetime.now(),
                    updatedAt=datetime.now()
                )
            ]
        
        return ExecutionMapper.supported_language_list_to_domain(db_languages)

    async def get_language_by_id(self, language_id: str) -> Optional[SupportedLanguageEntity]:
        db_language = self.db_session.query(SupportedLanguageModel).filter(
            SupportedLanguageModel.id == language_id
        ).first()
        return ExecutionMapper.supported_language_to_domain(db_language) if db_language else None

    async def get_language_by_enum(self, language: CodeLanguage) -> Optional[SupportedLanguageEntity]:
        db_language = self.db_session.query(SupportedLanguageModel).filter(
            SupportedLanguageModel.language == language,
            SupportedLanguageModel.isEnabled == True
        ).first()
        return ExecutionMapper.supported_language_to_domain(db_language) if db_language else None

    # CodeExecution methods
    async def create_code_execution(self, execution: CodeExecutionEntity) -> CodeExecutionEntity:
        db_execution = ExecutionMapper.code_execution_to_infrastructure(execution)
        self.db_session.add(db_execution)
        self.db_session.commit()
        self.db_session.refresh(db_execution)
        return ExecutionMapper.code_execution_to_domain(db_execution)

    async def update_code_execution(self, execution: CodeExecutionEntity) -> CodeExecutionEntity:
        db_execution = self.db_session.query(CodeExecutionModel).filter(
            CodeExecutionModel.id == execution.id
        ).first()
        
        if db_execution:
            db_execution.status = execution.status
            db_execution.output = execution.output
            db_execution.error = execution.error
            db_execution.executionTime = execution.executionTime
            db_execution.memory = execution.memory
            db_execution.updatedAt = execution.updatedAt or datetime.utcnow()
            
            self.db_session.commit()
            return ExecutionMapper.code_execution_to_domain(db_execution)
        
        return None

    async def get_execution_by_id(self, execution_id: str) -> Optional[CodeExecutionEntity]:
        db_execution = self.db_session.query(CodeExecutionModel).filter(
            CodeExecutionModel.id == execution_id
        ).first()
        return ExecutionMapper.code_execution_to_domain(db_execution) if db_execution else None

    async def get_user_executions(self, user_id: int, block_id: Optional[str] = None, limit: int = 20, offset: int = 0) -> List[CodeExecutionEntity]:
        query = self.db_session.query(CodeExecutionModel).filter(
            CodeExecutionModel.userId == user_id
        )
        
        if block_id:
            query = query.filter(CodeExecutionModel.blockId == block_id)
        
        db_executions = query.order_by(desc(CodeExecutionModel.createdAt)).offset(offset).limit(limit).all()
        return ExecutionMapper.code_execution_list_to_domain(db_executions)

    async def get_execution_by_id_and_user(self, execution_id: str, user_id: Optional[int]) -> Optional[CodeExecutionEntity]:
        query = self.db_session.query(CodeExecutionModel).filter(
            CodeExecutionModel.id == execution_id
        )
        
        if user_id is not None:
            query = query.filter(CodeExecutionModel.userId == user_id)
        
        db_execution = query.first()
        return ExecutionMapper.code_execution_to_domain(db_execution) if db_execution else None

    # UserCodeSolution methods
    async def create_user_solution(self, solution: UserCodeSolutionEntity) -> UserCodeSolutionEntity:
        db_solution = ExecutionMapper.user_code_solution_to_infrastructure(solution)
        self.db_session.add(db_solution)
        self.db_session.commit()
        self.db_session.refresh(db_solution)
        return ExecutionMapper.user_code_solution_to_domain(db_solution)

    async def update_user_solution(self, solution: UserCodeSolutionEntity) -> UserCodeSolutionEntity:
        db_solution = self.db_session.query(UserCodeSolutionModel).filter(
            UserCodeSolutionModel.id == solution.id
        ).first()
        
        if db_solution:
            db_solution.code = solution.code
            db_solution.languageId = solution.languageId
            db_solution.updatedAt = solution.updatedAt or datetime.utcnow()
            
            self.db_session.commit()
            return ExecutionMapper.user_code_solution_to_domain(db_solution)
        
        return None

    async def get_solution_by_id(self, solution_id: str) -> Optional[UserCodeSolutionEntity]:
        db_solution = self.db_session.query(UserCodeSolutionModel).filter(
            UserCodeSolutionModel.id == solution_id
        ).first()
        return ExecutionMapper.user_code_solution_to_domain(db_solution) if db_solution else None

    async def get_solution_by_user_and_block(self, user_id: int, block_id: str, language_id: str) -> Optional[UserCodeSolutionEntity]:
        db_solution = self.db_session.query(UserCodeSolutionModel).filter(
            UserCodeSolutionModel.userId == user_id,
            UserCodeSolutionModel.blockId == block_id,
            UserCodeSolutionModel.languageId == language_id
        ).first()
        return ExecutionMapper.user_code_solution_to_domain(db_solution) if db_solution else None

    async def get_user_solutions_for_block(self, user_id: int, block_id: str) -> List[UserCodeSolutionEntity]:
        db_solutions = self.db_session.query(UserCodeSolutionModel).filter(
            UserCodeSolutionModel.userId == user_id,
            UserCodeSolutionModel.blockId == block_id
        ).all()
        return ExecutionMapper.user_code_solution_list_to_domain(db_solutions)

    async def get_solution_by_id_and_user(self, solution_id: str, user_id: int) -> Optional[UserCodeSolutionEntity]:
        db_solution = self.db_session.query(UserCodeSolutionModel).filter(
            UserCodeSolutionModel.id == solution_id,
            UserCodeSolutionModel.userId == user_id
        ).first()
        return ExecutionMapper.user_code_solution_to_domain(db_solution) if db_solution else None

    # TestCase methods
    async def get_test_cases_for_block(self, block_id: str) -> List[TestCaseEntity]:
        db_test_cases = self.db_session.query(TestCaseModel).filter(
            TestCaseModel.blockId == block_id,
            TestCaseModel.isActive == True
        ).order_by(TestCaseModel.orderIndex).all()
        return TestCaseMapper.test_case_list_to_domain(db_test_cases)

    async def get_public_test_cases_for_block(self, block_id: str) -> List[TestCaseEntity]:
        db_test_cases = self.db_session.query(TestCaseModel).filter(
            TestCaseModel.blockId == block_id,
            TestCaseModel.isActive == True,
            TestCaseModel.isPublic == True
        ).order_by(TestCaseModel.orderIndex).all()
        return TestCaseMapper.test_case_list_to_domain(db_test_cases)

    async def create_test_case(self, test_case: TestCaseEntity) -> TestCaseEntity:
        db_test_case = TestCaseMapper.test_case_to_infrastructure(test_case)
        self.db_session.add(db_test_case)
        self.db_session.commit()
        self.db_session.refresh(db_test_case)
        return TestCaseMapper.test_case_to_domain(db_test_case)

    async def update_test_case_stats(self, test_case_id: str, execution_count: int, pass_rate: float) -> None:
        db_test_case = self.db_session.query(TestCaseModel).filter(
            TestCaseModel.id == test_case_id
        ).first()
        
        if db_test_case:
            db_test_case.executionCount = execution_count
            db_test_case.passRate = pass_rate
            db_test_case.updatedAt = datetime.utcnow()
            self.db_session.commit()

    async def get_content_block_by_id(self, block_id: str) -> Optional[Dict[str, Any]]:
        db_block = self.db_session.query(ContentBlock).filter(
            ContentBlock.id == block_id
        ).first()
        
        if db_block:
            return {
                "id": db_block.id,
                "title": db_block.blockTitle,
                "content": db_block.textContent,
                "codeContent": db_block.codeContent,
                "codeLanguage": db_block.codeLanguage,
                "pathTitles": db_block.pathTitles,
                "blockLevel": db_block.blockLevel,
                "orderInFile": db_block.orderInFile,
                "companies": db_block.companies,
                "extractedUrls": db_block.extractedUrls
            }
        
        return None

    # Statistics methods
    async def get_execution_stats(self, user_id: int) -> ExecutionStats:
        """Получение статистики выполнения кода для пользователя"""
        total_count = await self.get_execution_count_by_user(user_id)
        successful_count = await self.get_successful_execution_count_by_user(user_id)
        avg_time = await self.get_average_execution_time(user_id)
        
        success_rate = (successful_count / total_count * 100) if total_count > 0 else 0.0
        
        return ExecutionStats(
            totalExecutions=total_count,
            successfulExecutions=successful_count,
            averageExecutionTime=avg_time,
            languageStats=[]
        )

    async def get_execution_count_by_user(self, user_id: int) -> int:
        return self.db_session.query(func.count(CodeExecutionModel.id)).filter(
            CodeExecutionModel.userId == user_id
        ).scalar() or 0

    async def get_successful_execution_count_by_user(self, user_id: int) -> int:
        return self.db_session.query(func.count(CodeExecutionModel.id)).filter(
            CodeExecutionModel.userId == user_id,
            CodeExecutionModel.status == ExecutionStatus.SUCCESS
        ).scalar() or 0

    async def get_average_execution_time(self, user_id: int) -> float:
        result = self.db_session.query(func.avg(CodeExecutionModel.executionTimeMs)).filter(
            CodeExecutionModel.userId == user_id,
            CodeExecutionModel.executionTimeMs.isnot(None)
        ).scalar()
        return float(result) if result else 0.0

    async def get_language_stats_by_user(self, user_id: int) -> List[Dict[str, Any]]:
        """Получение статистики по языкам программирования для пользователя"""
        results = self.db_session.query(
            CodeExecutionModel.languageId,
            func.count(CodeExecutionModel.id).label('total_executions'),
            func.count(CodeExecutionModel.id).filter(CodeExecutionModel.status == ExecutionStatus.SUCCESS).label('successful_executions'),
            func.avg(CodeExecutionModel.executionTimeMs).label('avg_execution_time')
        ).filter(
            CodeExecutionModel.userId == user_id
        ).group_by(
            CodeExecutionModel.languageId
        ).all()
        
        stats = []
        for result in results:
            success_rate = (result.successful_executions / result.total_executions * 100) if result.total_executions > 0 else 0.0
            stats.append({
                'languageId': result.languageId,
                'totalExecutions': result.total_executions,
                'successfulExecutions': result.successful_executions,
                'successRate': success_rate,
                'averageExecutionTime': float(result.avg_execution_time) if result.avg_execution_time else 0.0
            })
        
        return stats

    # Code execution methods (заглушки для совместимости)
    async def execute_code_with_language(self, source_code: str, language: SupportedLanguageEntity, stdin: Optional[str] = None) -> Dict[str, Any]:
        """Выполнение кода с заданным языком (заглушка)"""
        logger.warning(f"execute_code_with_language called but not implemented - using mock result")
        return {
            "status": ExecutionStatus.SUCCESS,
            "output": "Mock execution result",
            "error": None,
            "executionTime": 0.5,
            "memory": 1024
        }

    async def execute_test_case(self, source_code: str, language: SupportedLanguageEntity, test_input: str, expected_output: str, test_name: str) -> TestCaseExecution:
        """Выполнение тест-кейса (заглушка)"""
        logger.warning(f"execute_test_case called but not implemented - using mock result")
        return TestCaseExecution(
            testCaseId="mock",
            testName=test_name,
            input=test_input,
            expectedOutput=expected_output,
            actualOutput=expected_output,
            passed=True,
            executionTimeMs=500,
            errorMessage=None
        )

    async def generate_test_cases_ai(self, block_id: str, count: int = 3) -> List[TestCaseEntity]:
        """Генерация тест-кейсов через AI (заглушка)"""
        logger.warning(f"generate_test_cases_ai called but not implemented - returning empty list")
        return []

    # Utility methods
    async def validate_code_safety(self, source_code: str, language: CodeLanguage) -> bool:
        """Простая проверка на опасные паттерны"""
        dangerous_patterns = {
            CodeLanguage.PYTHON: [
                r'import\s+os', r'import\s+subprocess', r'import\s+sys',
                r'eval\s*\(', r'exec\s*\(', r'__import__\s*\(',
                r'open\s*\(', r'file\s*\(', r'input\s*\(',
                r'raw_input\s*\('
            ],
            CodeLanguage.JAVASCRIPT: [
                r'require\s*\(', r'process\s*\.', r'global\s*\.',
                r'eval\s*\(', r'Function\s*\(', r'setTimeout\s*\(',
                r'setInterval\s*\('
            ]
        }
        
        patterns = dangerous_patterns.get(language, [])
        for pattern in patterns:
            if re.search(pattern, source_code, re.IGNORECASE):
                logger.warning(f"Dangerous pattern detected: {pattern}")
                return False
        
        return True

    async def compare_outputs(self, actual: str, expected: str, test_name: str = "Unknown") -> bool:
        """Простое сравнение с нормализацией пробелов"""
        actual_normalized = actual.strip().replace('\r\n', '\n').replace('\r', '\n')
        expected_normalized = expected.strip().replace('\r\n', '\n').replace('\r', '\n')
        return actual_normalized == expected_normalized 