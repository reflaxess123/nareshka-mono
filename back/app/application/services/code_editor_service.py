import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.domain.repositories.code_editor_repository import CodeEditorRepository
from app.domain.entities.code_editor_types import (
    SupportedLanguage,
    CodeExecution,
    UserCodeSolution,
    TestCaseExecution,
    ValidationResult,
    ExecutionStats
)
from app.domain.entities.progress_types import TestCase
from app.domain.entities.enums import CodeLanguage, ExecutionStatus
from app.application.dto.code_editor_dto import (
    SupportedLanguageResponseDTO,
    CodeExecutionRequestDTO,
    CodeExecutionResponseDTO,
    UserCodeSolutionCreateDTO,
    UserCodeSolutionUpdateDTO,
    UserCodeSolutionResponseDTO,
    ExecutionStatsDTO,
    TestCaseResponseDTO,
    ValidationRequestDTO,
    ValidationResultDTO
)


class CodeEditorService:
    def __init__(self, code_editor_repository: CodeEditorRepository):
        self.code_editor_repository = code_editor_repository

    async def get_supported_languages(self) -> List[SupportedLanguageResponseDTO]:
        """Получение списка поддерживаемых языков"""
        
        languages = await self.code_editor_repository.get_supported_languages()
        
        return [
            SupportedLanguageResponseDTO(
                id=lang.id,
                name=lang.name,
                language=lang.language,
                version=lang.version,
                fileExtension=lang.fileExtension,
                timeoutSeconds=lang.timeoutSeconds,
                memoryLimitMB=lang.memoryLimitMB,
                isEnabled=lang.isEnabled
            )
            for lang in languages
        ]

    async def execute_code(self, request: CodeExecutionRequestDTO, user_id: Optional[int] = None) -> CodeExecutionResponseDTO:
        """Создание задачи на выполнение кода"""
        
        # Проверяем, что язык поддерживается
        try:
            language_enum = CodeLanguage(request.language)
        except ValueError:
            raise ValueError(f"Language {request.language} is not supported")
        
        # Проверяем безопасность кода
        if not await self.code_editor_repository.validate_code_safety(request.sourceCode, language_enum):
            raise ValueError("Code contains potentially unsafe patterns")
        
        # Получаем настройки языка
        language = await self.code_editor_repository.get_language_by_enum(language_enum)
        if not language:
            raise ValueError(f"Language {request.language} is not supported or disabled")
        
        # Создаем запись о выполнении
        execution_id = str(uuid.uuid4())
        execution = CodeExecution(
            id=execution_id,
            userId=user_id,
            blockId=request.blockId,
            languageId=language.id,
            sourceCode=request.sourceCode,
            stdin=request.stdin,
            status=ExecutionStatus.PENDING,
            createdAt=datetime.now()
        )
        
        # Сохраняем в БД
        created_execution = await self.code_editor_repository.create_code_execution(execution)
        
        # TODO: Запустить выполнение в фоне через BackgroundTasks
        
        return CodeExecutionResponseDTO(
            id=created_execution.id,
            userId=created_execution.userId,
            blockId=created_execution.blockId,
            languageId=created_execution.languageId,
            sourceCode=created_execution.sourceCode,
            stdin=created_execution.stdin,
            status=created_execution.status,
            stdout=created_execution.stdout,
            stderr=created_execution.stderr,
            exitCode=created_execution.exitCode,
            executionTimeMs=created_execution.executionTimeMs,
            memoryUsedMB=created_execution.memoryUsedMB,
            containerLogs=created_execution.containerLogs,
            errorMessage=created_execution.errorMessage,
            createdAt=created_execution.createdAt,
            completedAt=created_execution.completedAt
        )

    async def get_execution_result(self, execution_id: str, user_id: Optional[int] = None) -> CodeExecutionResponseDTO:
        """Получение результата выполнения кода"""
        
        execution = await self.code_editor_repository.get_execution_by_id_and_user(execution_id, user_id)
        
        if not execution:
            raise ValueError("Execution not found")
        
        return CodeExecutionResponseDTO(
            id=execution.id,
            userId=execution.userId,
            blockId=execution.blockId,
            languageId=execution.languageId,
            sourceCode=execution.sourceCode,
            stdin=execution.stdin,
            status=execution.status,
            stdout=execution.stdout,
            stderr=execution.stderr,
            exitCode=execution.exitCode,
            executionTimeMs=execution.executionTimeMs,
            memoryUsedMB=execution.memoryUsedMB,
            containerLogs=execution.containerLogs,
            errorMessage=execution.errorMessage,
            createdAt=execution.createdAt,
            completedAt=execution.completedAt
        )

    async def get_user_executions(self, user_id: int, block_id: Optional[str] = None, limit: int = 20, offset: int = 0) -> List[CodeExecutionResponseDTO]:
        """Получение истории выполнений пользователя"""
        
        executions = await self.code_editor_repository.get_user_executions(user_id, block_id, limit, offset)
        
        return [
            CodeExecutionResponseDTO(
                id=execution.id,
                userId=execution.userId,
                blockId=execution.blockId,
                languageId=execution.languageId,
                sourceCode=execution.sourceCode,
                stdin=execution.stdin,
                status=execution.status,
                stdout=execution.stdout,
                stderr=execution.stderr,
                exitCode=execution.exitCode,
                executionTimeMs=execution.executionTimeMs,
                memoryUsedMB=execution.memoryUsedMB,
                containerLogs=execution.containerLogs,
                errorMessage=execution.errorMessage,
                createdAt=execution.createdAt,
                completedAt=execution.completedAt
            )
            for execution in executions
        ]

    async def save_solution(self, solution_data: UserCodeSolutionCreateDTO, user_id: int) -> UserCodeSolutionResponseDTO:
        """Сохранение решения пользователя"""
        
        # Получаем языковые настройки
        language = await self.code_editor_repository.get_language_by_enum(solution_data.language)
        if not language:
            raise ValueError(f"Language {solution_data.language} is not supported")
        
        # Проверяем, существует ли уже решение
        existing_solution = await self.code_editor_repository.get_solution_by_user_and_block(
            user_id, solution_data.blockId, language.id
        )
        
        if existing_solution:
            # Обновляем существующее решение
            existing_solution.sourceCode = solution_data.sourceCode
            existing_solution.isCompleted = solution_data.isCompleted
            updated_solution = await self.code_editor_repository.update_user_solution(existing_solution)
        else:
            # Создаем новое решение
            solution_id = str(uuid.uuid4())
            new_solution = UserCodeSolution(
                id=solution_id,
                userId=user_id,
                blockId=solution_data.blockId,
                languageId=language.id,
                sourceCode=solution_data.sourceCode,
                isCompleted=solution_data.isCompleted,
                executionCount=0,
                successfulExecutions=0,
                createdAt=datetime.now(),
                updatedAt=datetime.now()
            )
            updated_solution = await self.code_editor_repository.create_user_solution(new_solution)
        
        return UserCodeSolutionResponseDTO(
            id=updated_solution.id,
            userId=updated_solution.userId,
            blockId=updated_solution.blockId,
            languageId=updated_solution.languageId,
            sourceCode=updated_solution.sourceCode,
            isCompleted=updated_solution.isCompleted,
            executionCount=updated_solution.executionCount,
            successfulExecutions=updated_solution.successfulExecutions,
            lastExecutionId=updated_solution.lastExecutionId,
            createdAt=updated_solution.createdAt,
            updatedAt=updated_solution.updatedAt
        )

    async def get_block_solutions(self, user_id: int, block_id: str) -> List[UserCodeSolutionResponseDTO]:
        """Получение решений пользователя для блока"""
        
        solutions = await self.code_editor_repository.get_user_solutions_for_block(user_id, block_id)
        
        return [
            UserCodeSolutionResponseDTO(
                id=solution.id,
                userId=solution.userId,
                blockId=solution.blockId,
                languageId=solution.languageId,
                sourceCode=solution.sourceCode,
                isCompleted=solution.isCompleted,
                executionCount=solution.executionCount,
                successfulExecutions=solution.successfulExecutions,
                lastExecutionId=solution.lastExecutionId,
                createdAt=solution.createdAt,
                updatedAt=solution.updatedAt
            )
            for solution in solutions
        ]

    async def update_solution(self, solution_id: str, user_id: int, update_data: UserCodeSolutionUpdateDTO) -> UserCodeSolutionResponseDTO:
        """Обновление решения пользователя"""
        
        solution = await self.code_editor_repository.get_solution_by_id_and_user(solution_id, user_id)
        if not solution:
            raise ValueError("Solution not found")
        
        # Обновляем поля
        if update_data.sourceCode is not None:
            solution.sourceCode = update_data.sourceCode
        if update_data.isCompleted is not None:
            solution.isCompleted = update_data.isCompleted
        
        updated_solution = await self.code_editor_repository.update_user_solution(solution)
        
        return UserCodeSolutionResponseDTO(
            id=updated_solution.id,
            userId=updated_solution.userId,
            blockId=updated_solution.blockId,
            languageId=updated_solution.languageId,
            sourceCode=updated_solution.sourceCode,
            isCompleted=updated_solution.isCompleted,
            executionCount=updated_solution.executionCount,
            successfulExecutions=updated_solution.successfulExecutions,
            lastExecutionId=updated_solution.lastExecutionId,
            createdAt=updated_solution.createdAt,
            updatedAt=updated_solution.updatedAt
        )

    async def get_execution_stats(self, user_id: int) -> ExecutionStatsDTO:
        """Получение статистики выполнения пользователя"""
        
        total_executions = await self.code_editor_repository.get_execution_count_by_user(user_id)
        successful_executions = await self.code_editor_repository.get_successful_execution_count_by_user(user_id)
        average_execution_time = await self.code_editor_repository.get_average_execution_time(user_id)
        language_stats = await self.code_editor_repository.get_language_stats_by_user(user_id)
        
        return ExecutionStatsDTO(
            totalExecutions=total_executions,
            successfulExecutions=successful_executions,
            averageExecutionTime=average_execution_time,
            languageStats=language_stats
        )

    async def get_test_cases(self, block_id: str, user_id: Optional[int] = None) -> List[TestCaseResponseDTO]:
        """Получение тест-кейсов для блока"""
        
        # Для обычных пользователей показываем только публичные тест-кейсы
        if user_id:
            test_cases = await self.code_editor_repository.get_public_test_cases_for_block(block_id)
        else:
            test_cases = await self.code_editor_repository.get_test_cases_for_block(block_id)
        
        return [
            TestCaseResponseDTO(
                id=tc.id,
                blockId=tc.blockId,
                name=tc.name,
                description=tc.description,
                input=tc.input,
                expectedOutput=tc.expectedOutput,
                isPublic=tc.isPublic,
                difficulty=tc.difficulty,
                weight=tc.weight,
                timeoutSeconds=tc.timeoutSeconds,
                isActive=tc.isActive,
                orderIndex=tc.orderIndex,
                isAIGenerated=tc.isAIGenerated,
                generationPrompt=tc.generationPrompt,
                generatedAt=tc.generatedAt,
                generationModel=tc.generationModel,
                executionCount=tc.executionCount,
                passRate=tc.passRate,
                createdAt=tc.createdAt,
                updatedAt=tc.updatedAt
            )
            for tc in test_cases
        ]

    async def validate_solution(self, block_id: str, validation_request: ValidationRequestDTO, user_id: int) -> ValidationResultDTO:
        """Валидация решения против тест-кейсов"""
        
        # Получаем тест-кейсы
        test_cases = await self.code_editor_repository.get_test_cases_for_block(block_id)
        
        if not test_cases:
            raise ValueError("No test cases found for this block")
        
        # Получаем язык
        language = await self.code_editor_repository.get_language_by_enum(validation_request.language)
        if not language:
            raise ValueError(f"Language {validation_request.language} is not supported")
        
        # Выполняем тест-кейсы
        test_results = []
        passed_tests = 0
        
        for test_case in test_cases:
            try:
                result = await self.code_editor_repository.execute_test_case(
                    validation_request.sourceCode,
                    language,
                    test_case.input,
                    test_case.expectedOutput,
                    test_case.name
                )
                test_results.append(result)
                if result.passed:
                    passed_tests += 1
            except Exception as e:
                # Если тест-кейс упал с ошибкой
                test_results.append(TestCaseExecution(
                    testCaseId=test_case.id,
                    testName=test_case.name,
                    input=test_case.input,
                    expectedOutput=test_case.expectedOutput,
                    actualOutput="",
                    passed=False,
                    errorMessage=str(e)
                ))
        
        # Рассчитываем результат
        total_tests = len(test_cases)
        all_tests_passed = passed_tests == total_tests
        score = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        return ValidationResultDTO(
            blockId=block_id,
            sourceCode=validation_request.sourceCode,
            language=validation_request.language.value,
            allTestsPassed=all_tests_passed,
            totalTests=total_tests,
            passedTests=passed_tests,
            score=score,
            validatedAt=datetime.now(),
            testResults=test_results
        ) 