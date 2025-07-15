"""Сервис для работы с редактором кода"""

import logging
import uuid
from datetime import datetime
from typing import List, Optional

from app.features.code_editor.repositories.code_editor_repository import CodeEditorRepository
from app.features.code_editor.dto.requests import (
    CodeExecutionRequest,
    UserCodeSolutionCreateRequest,
    UserCodeSolutionUpdateRequest,
    ValidationRequest,
)
from app.features.code_editor.dto.responses import (
    SupportedLanguageResponse,
    CodeExecutionResponse,
    UserCodeSolutionResponse,
    ExecutionStatsResponse,
    TestCaseResponse,
    TestCasesResponse,
    ValidationResultResponse,
    TestCaseExecutionResponse,
    HealthResponse,
)
from app.shared.models.code_execution_models import (
    CodeExecution,
    UserCodeSolution,
)
from app.shared.entities.enums import CodeLanguage, ExecutionStatus
from app.features.code_editor.exceptions.code_editor_exceptions import (
    UnsupportedLanguageError,
    CodeExecutionError,
    UnsafeCodeError,
    SolutionNotFoundError,
)

logger = logging.getLogger(__name__)


class CodeEditorService:
    """Сервис для работы с редактором кода"""

    def __init__(self, code_editor_repository: CodeEditorRepository):
        self.code_editor_repository = code_editor_repository

    async def get_supported_languages(self) -> List[SupportedLanguageResponse]:
        """Получение списка поддерживаемых языков"""
        logger.info("Получение поддерживаемых языков")
        
        try:
            languages = await self.code_editor_repository.get_supported_languages()
            
            return [
                SupportedLanguageResponse(
                    id=lang.id,
                    name=lang.name,
                    language=lang.language,
                    version=lang.version,
                    fileExtension=lang.fileExtension,
                    timeoutSeconds=lang.timeoutSeconds,
                    memoryLimitMB=lang.memoryLimitMB,
                    isEnabled=lang.isEnabled,
                )
                for lang in languages
            ]
            
        except Exception as e:
            logger.error(f"Ошибка при получении языков: {e}")
            raise

    async def execute_code(
        self, request: CodeExecutionRequest, user_id: Optional[int] = None
    ) -> CodeExecutionResponse:
        """Создание задачи на выполнение кода"""
        logger.info(f"Выполнение кода на языке {request.language}")
        
        try:
            # Проверяем, что язык поддерживается
            try:
                language_enum = CodeLanguage(request.language)
            except ValueError:
                raise UnsupportedLanguageError(request.language)

            # Проверяем безопасность кода
            if not await self.code_editor_repository.validate_code_safety(
                request.sourceCode, language_enum
            ):
                raise UnsafeCodeError("Код содержит потенциально опасные конструкции")

            # Получаем настройки языка
            language = await self.code_editor_repository.get_language_by_enum(language_enum)
            if not language:
                raise UnsupportedLanguageError(request.language)

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
                createdAt=datetime.now(),
            )

            # Сохраняем в БД
            created_execution = await self.code_editor_repository.create_code_execution(execution)

            # Выполняем код
            try:
                execution_result = await self.code_editor_repository.execute_code_with_language(
                    request.sourceCode, language, request.stdin
                )
                
                # Обновляем результат выполнения
                created_execution.status = ExecutionStatus.COMPLETED
                created_execution.stdout = execution_result.get('stdout')
                created_execution.stderr = execution_result.get('stderr')
                created_execution.exitCode = execution_result.get('exit_code')
                created_execution.executionTimeMs = execution_result.get('execution_time_ms')
                created_execution.memoryUsedMB = execution_result.get('memory_used_mb')
                created_execution.containerLogs = execution_result.get('container_logs')
                created_execution.completedAt = datetime.now()
                
                await self.code_editor_repository.update_code_execution(created_execution)
                
            except Exception as exec_error:
                # Отмечаем выполнение как failed
                created_execution.status = ExecutionStatus.FAILED
                created_execution.errorMessage = str(exec_error)
                created_execution.completedAt = datetime.now()
                
                await self.code_editor_repository.update_code_execution(created_execution)
                
                logger.warning(f"Ошибка выполнения кода: {exec_error}")

            return CodeExecutionResponse(
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
                completedAt=created_execution.completedAt,
            )

        except (UnsupportedLanguageError, UnsafeCodeError):
            raise
        except Exception as e:
            logger.error(f"Ошибка при выполнении кода: {e}")
            raise CodeExecutionError("", str(e))

    async def get_execution_result(
        self, execution_id: str, user_id: Optional[int] = None
    ) -> CodeExecutionResponse:
        """Получение результата выполнения"""
        logger.info(f"Получение результата выполнения {execution_id}")
        
        try:
            execution = await self.code_editor_repository.get_execution_by_id(execution_id)
            
            if not execution:
                raise CodeExecutionError(execution_id, "Выполнение не найдено")
                
            # Проверяем права доступа если указан пользователь
            if user_id and execution.userId != user_id:
                raise CodeExecutionError(execution_id, "Нет доступа к этому выполнению")

            return CodeExecutionResponse(
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
                completedAt=execution.completedAt,
            )

        except CodeExecutionError:
            raise
        except Exception as e:
            logger.error(f"Ошибка при получении результата: {e}")
            raise

    async def get_user_executions(
        self,
        user_id: int,
        block_id: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[CodeExecutionResponse]:
        """Получение истории выполнений пользователя"""
        logger.info(f"Получение истории выполнений пользователя {user_id}")
        
        try:
            executions = await self.code_editor_repository.get_user_executions(
                user_id, block_id, limit, offset
            )

            return [
                CodeExecutionResponse(
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
                    completedAt=execution.completedAt,
                )
                for execution in executions
            ]

        except Exception as e:
            logger.error(f"Ошибка при получении истории: {e}")
            raise

    async def save_solution(
        self, solution_data: UserCodeSolutionCreateRequest, user_id: int
    ) -> UserCodeSolutionResponse:
        """Сохранение решения пользователя"""
        logger.info(f"Сохранение решения пользователя {user_id} для блока {solution_data.blockId}")
        
        try:
            # Получаем язык
            language = await self.code_editor_repository.get_language_by_enum(solution_data.language)
            if not language:
                raise UnsupportedLanguageError(solution_data.language.value)

            # Проверяем существующее решение
            existing_solutions = await self.code_editor_repository.get_user_solutions_for_block(
                user_id, solution_data.blockId
            )
            
            # Если есть решение для этого языка, обновляем его
            existing_solution = None
            for sol in existing_solutions:
                if sol.languageId == language.id:
                    existing_solution = sol
                    break

            if existing_solution:
                existing_solution.sourceCode = solution_data.sourceCode
                existing_solution.isCompleted = solution_data.isCompleted
                existing_solution.updatedAt = datetime.now()
                
                updated_solution = await self.code_editor_repository.update_user_solution(existing_solution)
                solution = updated_solution
            else:
                # Создаем новое решение
                solution_id = str(uuid.uuid4())
                solution = UserCodeSolution(
                    id=solution_id,
                    userId=user_id,
                    blockId=solution_data.blockId,
                    languageId=language.id,
                    sourceCode=solution_data.sourceCode,
                    isCompleted=solution_data.isCompleted,
                    createdAt=datetime.now(),
                    updatedAt=datetime.now(),
                )
                
                solution = await self.code_editor_repository.create_user_solution(solution)

            return UserCodeSolutionResponse(
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
                updatedAt=solution.updatedAt,
            )

        except UnsupportedLanguageError:
            raise
        except Exception as e:
            logger.error(f"Ошибка при сохранении решения: {e}")
            raise

    async def get_block_solutions(
        self, user_id: int, block_id: str
    ) -> List[UserCodeSolutionResponse]:
        """Получение решений пользователя для блока"""
        logger.info(f"Получение решений пользователя {user_id} для блока {block_id}")
        
        try:
            solutions = await self.code_editor_repository.get_user_solutions_for_block(
                user_id, block_id
            )

            return [
                UserCodeSolutionResponse(
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
                    updatedAt=solution.updatedAt,
                )
                for solution in solutions
            ]

        except Exception as e:
            logger.error(f"Ошибка при получении решений: {e}")
            raise

    async def update_solution(
        self, solution_id: str, user_id: int, update_data: UserCodeSolutionUpdateRequest
    ) -> UserCodeSolutionResponse:
        """Обновление решения пользователя"""
        logger.info(f"Обновление решения {solution_id}")
        
        try:
            solution = await self.code_editor_repository.get_solution_by_id(solution_id)
            
            if not solution:
                raise SolutionNotFoundError(solution_id)
                
            if solution.userId != user_id:
                raise SolutionNotFoundError(solution_id, user_id)

            # Обновляем поля
            if update_data.sourceCode is not None:
                solution.sourceCode = update_data.sourceCode
            if update_data.isCompleted is not None:
                solution.isCompleted = update_data.isCompleted
                
            solution.updatedAt = datetime.now()

            updated_solution = await self.code_editor_repository.update_user_solution(solution)

            return UserCodeSolutionResponse(
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
                updatedAt=updated_solution.updatedAt,
            )

        except SolutionNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Ошибка при обновлении решения: {e}")
            raise

    async def get_execution_stats(self, user_id: int) -> ExecutionStatsResponse:
        """Получение статистики выполнений пользователя"""
        logger.info(f"Получение статистики выполнений для пользователя {user_id}")
        
        try:
            stats = await self.code_editor_repository.get_execution_stats(user_id)

            return ExecutionStatsResponse(
                totalExecutions=stats['totalExecutions'],
                successfulExecutions=stats['successfulExecutions'],
                averageExecutionTime=stats['averageExecutionTime'],
                languageStats=stats['languageStats'],
            )

        except Exception as e:
            logger.error(f"Ошибка при получении статистики: {e}")
            raise

    async def get_test_cases(
        self, block_id: str, user_id: Optional[int] = None
    ) -> TestCasesResponse:
        """Получение тест-кейсов для блока"""
        logger.info(f"Получение тест-кейсов для блока {block_id}")
        
        try:
            test_cases = await self.code_editor_repository.get_test_cases_for_block(block_id)

            # Фильтруем публичные тест-кейсы для неавторизованных пользователей
            if not user_id:
                test_cases = [tc for tc in test_cases if tc.isPublic]

            test_case_responses = [
                TestCaseResponse(
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
                    updatedAt=tc.updatedAt,
                )
                for tc in test_cases
            ]

            public_count = sum(1 for tc in test_cases if tc.isPublic)
            hidden_count = len(test_cases) - public_count

            return TestCasesResponse(
                blockId=block_id,
                testCases=test_case_responses,
                totalTests=len(test_cases),
                publicTests=public_count,
                hiddenTests=hidden_count,
                lastGenerated=None,  # TODO: Вычислить последнюю дату генерации
            )

        except Exception as e:
            logger.error(f"Ошибка при получении тест-кейсов: {e}")
            raise

    async def validate_solution(
        self, block_id: str, validation_request: ValidationRequest, user_id: int
    ) -> ValidationResultResponse:
        """Валидация решения против тест-кейсов"""
        logger.info(f"Валидация решения для блока {block_id}")
        
        try:
            # Получаем тест-кейсы
            test_cases = await self.code_editor_repository.get_test_cases_for_block(block_id)
            if not test_cases:
                logger.warning(f"Нет тест-кейсов для блока {block_id}")
                return ValidationResultResponse(
                    blockId=block_id,
                    sourceCode=validation_request.sourceCode,
                    language=validation_request.language.value,
                    allTestsPassed=True,
                    totalTests=0,
                    passedTests=0,
                    score=100.0,
                    validatedAt=datetime.now(),
                    testResults=[],
                )

            # Получаем язык
            language = await self.code_editor_repository.get_language_by_enum(validation_request.language)
            if not language:
                raise UnsupportedLanguageError(validation_request.language.value)

            # Выполняем тест-кейсы
            test_results = []
            passed_tests = 0
            total_weight = sum(tc.weight for tc in test_cases)

            for test_case in test_cases:
                try:
                    # Выполняем код с входными данными тест-кейса
                    execution_result = await self.code_editor_repository.execute_code_with_language(
                        validation_request.sourceCode, language, test_case.input
                    )
                    
                    actual_output = execution_result.get('stdout', '').strip()
                    expected_output = test_case.expectedOutput.strip()
                    passed = actual_output == expected_output
                    
                    if passed:
                        passed_tests += 1

                    test_result = TestCaseExecutionResponse(
                        testCaseId=test_case.id,
                        testName=test_case.name,
                        input=test_case.input,
                        expectedOutput=expected_output,
                        actualOutput=actual_output,
                        passed=passed,
                        executionTimeMs=execution_result.get('execution_time_ms'),
                        errorMessage=execution_result.get('stderr') if not passed else None,
                    )
                    test_results.append(test_result)

                except Exception as e:
                    test_result = TestCaseExecutionResponse(
                        testCaseId=test_case.id,
                        testName=test_case.name,
                        input=test_case.input,
                        expectedOutput=test_case.expectedOutput,
                        actualOutput="",
                        passed=False,
                        executionTimeMs=None,
                        errorMessage=str(e),
                    )
                    test_results.append(test_result)

            # Вычисляем финальный score
            if total_weight > 0:
                weighted_score = sum(
                    tc.weight for tc, result in zip(test_cases, test_results) if result.passed
                )
                score = (weighted_score / total_weight) * 100
            else:
                score = (passed_tests / len(test_cases)) * 100 if test_cases else 100

            all_tests_passed = passed_tests == len(test_cases)

            return ValidationResultResponse(
                blockId=block_id,
                sourceCode=validation_request.sourceCode,
                language=validation_request.language.value,
                allTestsPassed=all_tests_passed,
                totalTests=len(test_cases),
                passedTests=passed_tests,
                score=round(score, 2),
                validatedAt=datetime.now(),
                testResults=test_results,
            )

        except UnsupportedLanguageError:
            raise
        except Exception as e:
            logger.error(f"Ошибка при валидации решения: {e}")
            raise

    async def get_health_status(self) -> HealthResponse:
        """Получение статуса здоровья модуля"""
        logger.info("Проверка здоровья code_editor модуля")
        
        try:
            # Проверяем доступность языков
            languages = await self.code_editor_repository.get_supported_languages()
            
            # Проверяем общее количество выполнений (для статистики)
            # Здесь можно добавить более сложные проверки
            
            status = "healthy" if len(languages) > 0 else "unhealthy"
            
            return HealthResponse(
                status=status,
                module="code_editor",
                supportedLanguages=len(languages),
                totalExecutions=0,  # TODO: Получить реальную статистику
            )

        except Exception as e:
            logger.error(f"Ошибка при проверке здоровья: {e}")
            return HealthResponse(
                status="unhealthy",
                module="code_editor",
                supportedLanguages=0,
                totalExecutions=0,
            ) 

