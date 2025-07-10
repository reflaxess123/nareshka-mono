#!/usr/bin/env python3
"""Реализация репозитория для работы с редактором кода через SQLAlchemy"""

import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.domain.entities.code_editor_types import (
    CodeExecution as CodeExecutionEntity,
    ExecutionStats,
    SupportedLanguage as SupportedLanguageEntity,
    TestCaseExecution,
    UserCodeSolution as UserCodeSolutionEntity,
)
from app.domain.entities.enums import CodeLanguage, ExecutionStatus
from app.domain.entities.progress_types import TestCase as TestCaseEntity
from app.domain.repositories.code_editor_repository import CodeEditorRepository
from app.infrastructure.models.code_execution_models import (
    CodeExecution as CodeExecutionModel,
    SupportedLanguage as SupportedLanguageModel,
)
from app.infrastructure.models.content_models import ContentBlock
from app.infrastructure.models.test_case_models import TestCase as TestCaseModel

logger = logging.getLogger(__name__)


class SQLAlchemyCodeEditorRepository(CodeEditorRepository):
    def __init__(self, db_session: Session):
        self.db_session = db_session

    # SupportedLanguage methods
    async def get_supported_languages(self) -> List[SupportedLanguageEntity]:
        db_languages = (
            self.db_session.query(SupportedLanguageModel)
            .filter(SupportedLanguageModel.isEnabled is True)
            .all()
        )

        if not db_languages:
            # Fallback для базовых языков если не настроены в БД
            return [
                SupportedLanguageEntity(
                    id="python39",
                    name="Python 3.9",
                    language=CodeLanguage.PYTHON,
                    version="3.9",
                    file_extension=".py",
                    docker_image="python:3.9-alpine",
                    run_command="python3 {file}",
                    timeout_seconds=10,
                    memory_limit_mb=128,
                    is_enabled=True,
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                ),
                SupportedLanguageEntity(
                    id="node18",
                    name="Node.js 18",
                    language=CodeLanguage.JAVASCRIPT,
                    version="18",
                    file_extension=".js",
                    docker_image="node:18-alpine",
                    run_command="node {file}",
                    timeout_seconds=10,
                    memory_limit_mb=128,
                    is_enabled=True,
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                ),
            ]

        return [
            self._map_supported_language_to_domain(db_lang) for db_lang in db_languages
        ]

    def _map_supported_language_to_domain(
        self, db_language: SupportedLanguageModel
    ) -> SupportedLanguageEntity:
        """Преобразует модель БД SupportedLanguage в доменную сущность"""
        return SupportedLanguageEntity(
            id=db_language.id,
            name=db_language.name,
            language=db_language.language,
            version=db_language.version,
            file_extension=db_language.fileExtension,
            docker_image=db_language.dockerImage,
            compile_command=db_language.compileCommand,
            run_command=db_language.runCommand,
            timeout_seconds=db_language.timeoutSeconds,
            memory_limit_mb=db_language.memoryLimitMB,
            is_enabled=db_language.isEnabled,
            created_at=db_language.createdAt,
            updated_at=db_language.updatedAt,
        )

    async def get_language_by_id(
        self, language_id: str
    ) -> Optional[SupportedLanguageEntity]:
        db_language = (
            self.db_session.query(SupportedLanguageModel)
            .filter(SupportedLanguageModel.id == language_id)
            .first()
        )
        return (
            self._map_supported_language_to_domain(db_language) if db_language else None
        )

    async def get_language_by_enum(
        self, language: CodeLanguage
    ) -> Optional[SupportedLanguageEntity]:
        db_language = (
            self.db_session.query(SupportedLanguageModel)
            .filter(
                SupportedLanguageModel.language == language,
                SupportedLanguageModel.isEnabled is True,
            )
            .first()
        )
        return (
            self._map_supported_language_to_domain(db_language) if db_language else None
        )

    # CodeExecution methods
    async def create_code_execution(
        self, execution: CodeExecutionEntity
    ) -> CodeExecutionEntity:
        # Заглушка - функциональность пока не реализована
        logger.warning("create_code_execution called but not fully implemented")
        return execution

    async def update_code_execution(
        self, execution: CodeExecutionEntity
    ) -> CodeExecutionEntity:
        logger.warning("update_code_execution called but not fully implemented")
        return execution

    async def get_execution_by_id(
        self, execution_id: str
    ) -> Optional[CodeExecutionEntity]:
        logger.warning("get_execution_by_id called but not fully implemented")
        return None

    async def get_user_executions(
        self,
        user_id: int,
        block_id: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[CodeExecutionEntity]:
        logger.warning("get_user_executions called but not fully implemented")
        return []

    async def get_execution_by_id_and_user(
        self, execution_id: str, user_id: Optional[int]
    ) -> Optional[CodeExecutionEntity]:
        logger.warning("get_execution_by_id_and_user called but not fully implemented")
        return None

    # UserCodeSolution methods
    async def create_user_solution(
        self, solution: UserCodeSolutionEntity
    ) -> UserCodeSolutionEntity:
        logger.warning("create_user_solution called but not fully implemented")
        return solution

    async def update_user_solution(
        self, solution: UserCodeSolutionEntity
    ) -> UserCodeSolutionEntity:
        logger.warning("update_user_solution called but not fully implemented")
        return solution

    async def get_solution_by_id(
        self, solution_id: str
    ) -> Optional[UserCodeSolutionEntity]:
        logger.warning("get_solution_by_id called but not fully implemented")
        return None

    async def get_solution_by_user_and_block(
        self, user_id: int, block_id: str, language_id: str
    ) -> Optional[UserCodeSolutionEntity]:
        logger.warning(
            "get_solution_by_user_and_block called but not fully implemented"
        )
        return None

    async def get_user_solutions_for_block(
        self, user_id: int, block_id: str
    ) -> List[UserCodeSolutionEntity]:
        logger.warning("get_user_solutions_for_block called but not fully implemented")
        return []

    async def get_solution_by_id_and_user(
        self, solution_id: str, user_id: int
    ) -> Optional[UserCodeSolutionEntity]:
        logger.warning("get_solution_by_id_and_user called but not fully implemented")
        return None

    # TestCase methods
    async def get_test_cases_for_block(self, block_id: str) -> List[TestCaseEntity]:
        logger.warning("get_test_cases_for_block called but not fully implemented")
        return []

    async def get_public_test_cases_for_block(
        self, block_id: str
    ) -> List[TestCaseEntity]:
        logger.warning(
            "get_public_test_cases_for_block called but not fully implemented"
        )
        return []

    async def create_test_case(self, test_case: TestCaseEntity) -> TestCaseEntity:
        logger.warning("create_test_case called but not fully implemented")
        return test_case

    async def update_test_case_stats(
        self, test_case_id: str, execution_count: int, pass_rate: float
    ) -> None:
        db_test_case = (
            self.db_session.query(TestCaseModel)
            .filter(TestCaseModel.id == test_case_id)
            .first()
        )

        if db_test_case:
            db_test_case.executionCount = execution_count
            db_test_case.passRate = pass_rate
            db_test_case.updatedAt = datetime.utcnow()
            self.db_session.commit()

    async def get_content_block_by_id(self, block_id: str) -> Optional[Dict[str, Any]]:
        db_block = (
            self.db_session.query(ContentBlock)
            .filter(ContentBlock.id == block_id)
            .first()
        )

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
                "extractedUrls": db_block.extractedUrls,
            }

        return None

    # Statistics methods
    async def get_execution_stats(self, user_id: int) -> ExecutionStats:
        """Получение статистики выполнения кода для пользователя"""
        total_count = await self.get_execution_count_by_user(user_id)
        successful_count = await self.get_successful_execution_count_by_user(user_id)
        avg_time = await self.get_average_execution_time(user_id)

        (successful_count / total_count * 100) if total_count > 0 else 0.0

        return ExecutionStats(
            totalExecutions=total_count,
            successfulExecutions=successful_count,
            averageExecutionTime=avg_time,
            languageStats=[],
        )

    async def get_execution_count_by_user(self, user_id: int) -> int:
        return (
            self.db_session.query(func.count(CodeExecutionModel.id))
            .filter(CodeExecutionModel.userId == user_id)
            .scalar()
            or 0
        )

    async def get_successful_execution_count_by_user(self, user_id: int) -> int:
        return (
            self.db_session.query(func.count(CodeExecutionModel.id))
            .filter(
                CodeExecutionModel.userId == user_id,
                CodeExecutionModel.status == ExecutionStatus.SUCCESS,
            )
            .scalar()
            or 0
        )

    async def get_average_execution_time(self, user_id: int) -> float:
        result = (
            self.db_session.query(func.avg(CodeExecutionModel.executionTimeMs))
            .filter(
                CodeExecutionModel.userId == user_id,
                CodeExecutionModel.executionTimeMs.isnot(None),
            )
            .scalar()
        )
        return float(result) if result else 0.0

    async def get_language_stats_by_user(self, user_id: int) -> List[Dict[str, Any]]:
        """Получение статистики по языкам программирования для пользователя"""
        results = (
            self.db_session.query(
                CodeExecutionModel.languageId,
                func.count(CodeExecutionModel.id).label("total_executions"),
                func.count(CodeExecutionModel.id)
                .filter(CodeExecutionModel.status == ExecutionStatus.SUCCESS)
                .label("successful_executions"),
                func.avg(CodeExecutionModel.executionTimeMs).label(
                    "avg_execution_time"
                ),
            )
            .filter(CodeExecutionModel.userId == user_id)
            .group_by(CodeExecutionModel.languageId)
            .all()
        )

        stats = []
        for result in results:
            success_rate = (
                (result.successful_executions / result.total_executions * 100)
                if result.total_executions > 0
                else 0.0
            )
            stats.append(
                {
                    "languageId": result.languageId,
                    "totalExecutions": result.total_executions,
                    "successfulExecutions": result.successful_executions,
                    "successRate": success_rate,
                    "averageExecutionTime": float(result.avg_execution_time)
                    if result.avg_execution_time
                    else 0.0,
                }
            )

        return stats

    # Code execution methods (заглушки для совместимости)
    async def execute_code_with_language(
        self,
        source_code: str,
        language: SupportedLanguageEntity,
        stdin: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Выполнение кода с заданным языком (заглушка)"""
        logger.warning(
            "execute_code_with_language called but not implemented - using mock result"
        )
        return {
            "status": ExecutionStatus.SUCCESS,
            "output": "Mock execution result",
            "error": None,
            "executionTime": 0.5,
            "memory": 1024,
        }

    async def execute_test_case(
        self,
        source_code: str,
        language: SupportedLanguageEntity,
        test_input: str,
        expected_output: str,
        test_name: str,
    ) -> TestCaseExecution:
        """Выполнение тест-кейса (заглушка)"""
        logger.warning(
            "execute_test_case called but not implemented - using mock result"
        )
        return TestCaseExecution(
            testCaseId="mock",
            testName=test_name,
            input=test_input,
            expectedOutput=expected_output,
            actualOutput=expected_output,
            passed=True,
            executionTimeMs=500,
            errorMessage=None,
        )

    async def generate_test_cases_ai(
        self, block_id: str, count: int = 3
    ) -> List[TestCaseEntity]:
        """Генерация тест-кейсов через AI (заглушка)"""
        logger.warning(
            "generate_test_cases_ai called but not implemented - returning empty list"
        )
        return []

    # Utility methods
    async def validate_code_safety(
        self, source_code: str, language: CodeLanguage
    ) -> bool:
        """Простая проверка на опасные паттерны"""
        dangerous_patterns = {
            CodeLanguage.PYTHON: [
                r"import\s+os",
                r"import\s+subprocess",
                r"import\s+sys",
                r"eval\s*\(",
                r"exec\s*\(",
                r"__import__\s*\(",
                r"open\s*\(",
                r"file\s*\(",
                r"input\s*\(",
                r"raw_input\s*\(",
            ],
            CodeLanguage.JAVASCRIPT: [
                r"require\s*\(",
                r"process\s*\.",
                r"global\s*\.",
                r"eval\s*\(",
                r"Function\s*\(",
                r"setTimeout\s*\(",
                r"setInterval\s*\(",
            ],
        }

        patterns = dangerous_patterns.get(language, [])
        for pattern in patterns:
            if re.search(pattern, source_code, re.IGNORECASE):
                logger.warning(f"Dangerous pattern detected: {pattern}")
                return False

        return True

    async def compare_outputs(
        self, actual: str, expected: str, test_name: str = "Unknown"
    ) -> bool:
        """Простое сравнение с нормализацией пробелов"""
        actual_normalized = actual.strip().replace("\r\n", "\n").replace("\r", "\n")
        expected_normalized = expected.strip().replace("\r\n", "\n").replace("\r", "\n")
        return actual_normalized == expected_normalized
