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
from app.domain.entities.code_editor import (
    SupportedLanguage as SupportedLanguageEntity,
    CodeExecution as CodeExecutionEntity,
    UserCodeSolution as UserCodeSolutionEntity,
    TestCaseExecution,
    ValidationResult,
    ExecutionStats
)
from app.domain.entities.progress import TestCase as TestCaseEntity
from app.domain.entities.enums import CodeLanguage, ExecutionStatus
from app.models import (
    SupportedLanguage as SupportedLanguageModel,
    CodeExecution as CodeExecutionModel,
    UserCodeSolution as UserCodeSolutionModel,
    TestCase as TestCaseModel,
    ContentBlock,
    User
)

logger = logging.getLogger(__name__)


class SQLAlchemyCodeEditorRepository(CodeEditorRepository):
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def _supported_language_to_entity(self, model: SupportedLanguageModel) -> SupportedLanguageEntity:
        return SupportedLanguageEntity(
            id=model.id,
            name=model.name,
            language=model.language,
            version=model.version,
            dockerImage=model.dockerImage,
            fileExtension=model.fileExtension,
            runCommand=model.runCommand,
            timeoutSeconds=model.timeoutSeconds,
            memoryLimitMB=model.memoryLimitMB,
            isEnabled=model.isEnabled,
            createdAt=model.createdAt,
            updatedAt=model.updatedAt,
            compileCommand=model.compileCommand
        )

    def _code_execution_to_entity(self, model: CodeExecutionModel) -> CodeExecutionEntity:
        return CodeExecutionEntity(
            id=model.id,
            languageId=model.languageId,
            sourceCode=model.sourceCode,
            status=model.status,
            createdAt=model.createdAt,
            userId=model.userId,
            blockId=model.blockId,
            stdin=model.stdin,
            stdout=model.stdout,
            stderr=model.stderr,
            exitCode=model.exitCode,
            executionTimeMs=model.executionTimeMs,
            memoryUsedMB=model.memoryUsedMB,
            containerLogs=model.containerLogs,
            errorMessage=model.errorMessage,
            completedAt=model.completedAt
        )

    def _user_solution_to_entity(self, model: UserCodeSolutionModel) -> UserCodeSolutionEntity:
        return UserCodeSolutionEntity(
            id=model.id,
            userId=model.userId,
            blockId=model.blockId,
            languageId=model.languageId,
            sourceCode=model.sourceCode,
            isCompleted=model.isCompleted,
            executionCount=model.executionCount,
            successfulExecutions=model.successfulExecutions,
            createdAt=model.createdAt,
            updatedAt=model.updatedAt,
            lastExecutionId=model.lastExecutionId
        )

    def _test_case_to_entity(self, model: TestCaseModel) -> TestCaseEntity:
        return TestCaseEntity(
            id=model.id,
            blockId=model.blockId,
            name=model.name,
            expectedOutput=model.expectedOutput,
            isPublic=model.isPublic,
            difficulty=model.difficulty,
            weight=model.weight,
            timeoutSeconds=model.timeoutSeconds,
            isActive=model.isActive,
            orderIndex=model.orderIndex,
            isAIGenerated=model.isAIGenerated,
            executionCount=model.executionCount,
            passRate=model.passRate,
            createdAt=model.createdAt,
            updatedAt=model.updatedAt,
            description=model.description,
            input=model.input,
            generationPrompt=model.generationPrompt,
            generatedAt=model.generatedAt,
            generationModel=model.generationModel
        )

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
        
        return [self._supported_language_to_entity(lang) for lang in db_languages]

    async def get_language_by_id(self, language_id: str) -> Optional[SupportedLanguageEntity]:
        db_language = self.db_session.query(SupportedLanguageModel).filter(
            SupportedLanguageModel.id == language_id
        ).first()
        return self._supported_language_to_entity(db_language) if db_language else None

    async def get_language_by_enum(self, language: CodeLanguage) -> Optional[SupportedLanguageEntity]:
        db_language = self.db_session.query(SupportedLanguageModel).filter(
            SupportedLanguageModel.language == language,
            SupportedLanguageModel.isEnabled == True
        ).first()
        return self._supported_language_to_entity(db_language) if db_language else None

    # CodeExecution methods
    async def create_code_execution(self, execution: CodeExecutionEntity) -> CodeExecutionEntity:
        db_execution = CodeExecutionModel(
            id=execution.id,
            userId=execution.userId,
            blockId=execution.blockId,
            languageId=execution.languageId,
            sourceCode=execution.sourceCode,
            stdin=execution.stdin,
            status=execution.status
        )
        self.db_session.add(db_execution)
        self.db_session.commit()
        self.db_session.refresh(db_execution)
        return self._code_execution_to_entity(db_execution)

    async def update_code_execution(self, execution: CodeExecutionEntity) -> CodeExecutionEntity:
        db_execution = self.db_session.query(CodeExecutionModel).filter(
            CodeExecutionModel.id == execution.id
        ).first()
        
        if db_execution:
            db_execution.status = execution.status
            db_execution.stdout = execution.stdout
            db_execution.stderr = execution.stderr
            db_execution.exitCode = execution.exitCode
            db_execution.executionTimeMs = execution.executionTimeMs
            db_execution.memoryUsedMB = execution.memoryUsedMB
            db_execution.containerLogs = execution.containerLogs
            db_execution.errorMessage = execution.errorMessage
            db_execution.completedAt = execution.completedAt
            
            self.db_session.commit()
            self.db_session.refresh(db_execution)
            return self._code_execution_to_entity(db_execution)
        
        raise ValueError(f"CodeExecution with id {execution.id} not found")

    async def get_execution_by_id(self, execution_id: str) -> Optional[CodeExecutionEntity]:
        db_execution = self.db_session.query(CodeExecutionModel).filter(
            CodeExecutionModel.id == execution_id
        ).first()
        return self._code_execution_to_entity(db_execution) if db_execution else None

    async def get_user_executions(self, user_id: int, block_id: Optional[str] = None, limit: int = 20, offset: int = 0) -> List[CodeExecutionEntity]:
        query = self.db_session.query(CodeExecutionModel).filter(
            CodeExecutionModel.userId == user_id
        )
        
        if block_id:
            query = query.filter(CodeExecutionModel.blockId == block_id)
        
        db_executions = query.order_by(desc(CodeExecutionModel.createdAt)).offset(offset).limit(limit).all()
        return [self._code_execution_to_entity(execution) for execution in db_executions]

    async def get_execution_by_id_and_user(self, execution_id: str, user_id: Optional[int]) -> Optional[CodeExecutionEntity]:
        query = self.db_session.query(CodeExecutionModel).filter(
            CodeExecutionModel.id == execution_id
        )
        
        if user_id:
            query = query.filter(CodeExecutionModel.userId == user_id)
        else:
            # Для анонимных пользователей
            query = query.filter(CodeExecutionModel.userId.is_(None))
        
        db_execution = query.first()
        return self._code_execution_to_entity(db_execution) if db_execution else None

    # UserCodeSolution methods
    async def create_user_solution(self, solution: UserCodeSolutionEntity) -> UserCodeSolutionEntity:
        db_solution = UserCodeSolutionModel(
            id=solution.id,
            userId=solution.userId,
            blockId=solution.blockId,
            languageId=solution.languageId,
            sourceCode=solution.sourceCode,
            isCompleted=solution.isCompleted,
            executionCount=solution.executionCount,
            successfulExecutions=solution.successfulExecutions,
            lastExecutionId=solution.lastExecutionId
        )
        self.db_session.add(db_solution)
        self.db_session.commit()
        self.db_session.refresh(db_solution)
        return self._user_solution_to_entity(db_solution)

    async def update_user_solution(self, solution: UserCodeSolutionEntity) -> UserCodeSolutionEntity:
        db_solution = self.db_session.query(UserCodeSolutionModel).filter(
            UserCodeSolutionModel.id == solution.id
        ).first()
        
        if db_solution:
            db_solution.sourceCode = solution.sourceCode
            db_solution.isCompleted = solution.isCompleted
            db_solution.executionCount = solution.executionCount
            db_solution.successfulExecutions = solution.successfulExecutions
            db_solution.lastExecutionId = solution.lastExecutionId
            db_solution.updatedAt = datetime.now()
            
            self.db_session.commit()
            self.db_session.refresh(db_solution)
            return self._user_solution_to_entity(db_solution)
        
        raise ValueError(f"UserCodeSolution with id {solution.id} not found")

    async def get_solution_by_id(self, solution_id: str) -> Optional[UserCodeSolutionEntity]:
        db_solution = self.db_session.query(UserCodeSolutionModel).filter(
            UserCodeSolutionModel.id == solution_id
        ).first()
        return self._user_solution_to_entity(db_solution) if db_solution else None

    async def get_solution_by_user_and_block(self, user_id: int, block_id: str, language_id: str) -> Optional[UserCodeSolutionEntity]:
        db_solution = self.db_session.query(UserCodeSolutionModel).filter(
            UserCodeSolutionModel.userId == user_id,
            UserCodeSolutionModel.blockId == block_id,
            UserCodeSolutionModel.languageId == language_id
        ).first()
        return self._user_solution_to_entity(db_solution) if db_solution else None

    async def get_user_solutions_for_block(self, user_id: int, block_id: str) -> List[UserCodeSolutionEntity]:
        db_solutions = self.db_session.query(UserCodeSolutionModel).filter(
            UserCodeSolutionModel.userId == user_id,
            UserCodeSolutionModel.blockId == block_id
        ).all()
        return [self._user_solution_to_entity(solution) for solution in db_solutions]

    async def get_solution_by_id_and_user(self, solution_id: str, user_id: int) -> Optional[UserCodeSolutionEntity]:
        db_solution = self.db_session.query(UserCodeSolutionModel).filter(
            UserCodeSolutionModel.id == solution_id,
            UserCodeSolutionModel.userId == user_id
        ).first()
        return self._user_solution_to_entity(db_solution) if db_solution else None

    # TestCase methods
    async def get_test_cases_for_block(self, block_id: str) -> List[TestCaseEntity]:
        db_test_cases = self.db_session.query(TestCaseModel).filter(
            TestCaseModel.blockId == block_id,
            TestCaseModel.isActive == True
        ).order_by(TestCaseModel.orderIndex).all()
        return [self._test_case_to_entity(tc) for tc in db_test_cases]

    async def get_public_test_cases_for_block(self, block_id: str) -> List[TestCaseEntity]:
        db_test_cases = self.db_session.query(TestCaseModel).filter(
            TestCaseModel.blockId == block_id,
            TestCaseModel.isActive == True,
            TestCaseModel.isPublic == True
        ).order_by(TestCaseModel.orderIndex).all()
        return [self._test_case_to_entity(tc) for tc in db_test_cases]

    async def create_test_case(self, test_case: TestCaseEntity) -> TestCaseEntity:
        db_test_case = TestCaseModel(
            id=test_case.id,
            blockId=test_case.blockId,
            name=test_case.name,
            description=test_case.description,
            input=test_case.input,
            expectedOutput=test_case.expectedOutput,
            isPublic=test_case.isPublic,
            difficulty=test_case.difficulty,
            weight=test_case.weight,
            timeoutSeconds=test_case.timeoutSeconds,
            isActive=test_case.isActive,
            orderIndex=test_case.orderIndex,
            isAIGenerated=test_case.isAIGenerated,
            executionCount=test_case.executionCount,
            passRate=test_case.passRate,
            generationPrompt=test_case.generationPrompt,
            generatedAt=test_case.generatedAt,
            generationModel=test_case.generationModel
        )
        self.db_session.add(db_test_case)
        self.db_session.commit()
        self.db_session.refresh(db_test_case)
        return self._test_case_to_entity(db_test_case)

    async def update_test_case_stats(self, test_case_id: str, execution_count: int, pass_rate: float) -> None:
        db_test_case = self.db_session.query(TestCaseModel).filter(
            TestCaseModel.id == test_case_id
        ).first()
        
        if db_test_case:
            db_test_case.executionCount = execution_count
            db_test_case.passRate = pass_rate
            db_test_case.updatedAt = datetime.now()
            self.db_session.commit()

    # Content methods
    async def get_content_block_by_id(self, block_id: str) -> Optional[Dict[str, Any]]:
        db_block = self.db_session.query(ContentBlock).filter(
            ContentBlock.id == block_id
        ).first()
        
        if db_block:
            return {
                "id": db_block.id,
                "blockTitle": db_block.blockTitle,
                "textContent": db_block.textContent,
                "codeContent": db_block.codeContent,
                "codeLanguage": db_block.codeLanguage
            }
        return None

    # Заглушки для сложных методов - будут реализованы во второй части
    async def get_execution_stats(self, user_id: int) -> ExecutionStats:
        # Будет реализовано позже
        return ExecutionStats(
            totalExecutions=0,
            successfulExecutions=0,
            averageExecutionTime=0.0,
            languageStats=[]
        )

    async def get_execution_count_by_user(self, user_id: int) -> int:
        return self.db_session.query(CodeExecutionModel).filter(
            CodeExecutionModel.userId == user_id
        ).count()

    async def get_successful_execution_count_by_user(self, user_id: int) -> int:
        return self.db_session.query(CodeExecutionModel).filter(
            CodeExecutionModel.userId == user_id,
            CodeExecutionModel.status == ExecutionStatus.SUCCESS
        ).count()

    async def get_average_execution_time(self, user_id: int) -> float:
        avg_time = self.db_session.query(func.avg(CodeExecutionModel.executionTimeMs)).filter(
            CodeExecutionModel.userId == user_id,
            CodeExecutionModel.status == ExecutionStatus.SUCCESS
        ).scalar()
        return float(avg_time) if avg_time else 0.0

    async def get_language_stats_by_user(self, user_id: int) -> List[Dict[str, Any]]:
        # Заглушка - будет реализовано позже
        return []

    # Заглушки для сложных методов валидации
    async def validate_code_safety(self, source_code: str, language: CodeLanguage) -> bool:
        # Простая проверка на опасные паттерны
        dangerous_patterns = [
            r'import\s+os',
            r'import\s+subprocess',
            r'import\s+sys',
            r'exec\s*\(',
            r'eval\s*\(',
            r'__import__',
            r'open\s*\(',
            r'file\s*\(',
            r'input\s*\(',
            r'raw_input\s*\('
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, source_code, re.IGNORECASE):
                return False
        
        return True

    async def execute_code_with_language(self, source_code: str, language: SupportedLanguageEntity, stdin: Optional[str] = None) -> Dict[str, Any]:
        # Заглушка - будет интегрирована с code_executor
        return {
            "status": ExecutionStatus.SUCCESS,
            "stdout": "Mock output",
            "stderr": "",
            "exitCode": 0,
            "executionTimeMs": 100,
            "memoryUsedMB": 10.0
        }

    async def execute_test_case(self, source_code: str, language: SupportedLanguageEntity, test_input: str, expected_output: str, test_name: str) -> TestCaseExecution:
        # Заглушка - будет реализовано позже
        return TestCaseExecution(
            testCaseId="test",
            testName=test_name,
            input=test_input,
            expectedOutput=expected_output,
            actualOutput="Mock output",
            passed=True
        )

    async def generate_test_cases_ai(self, block_id: str, count: int = 3) -> List[TestCaseEntity]:
        # Заглушка - будет реализовано позже
        return []

    async def compare_outputs(self, actual: str, expected: str, test_name: str = "Unknown") -> bool:
        # Простое сравнение с нормализацией пробелов
        return actual.strip() == expected.strip() 