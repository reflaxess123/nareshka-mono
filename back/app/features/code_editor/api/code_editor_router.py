"""API роутер для работы с редактором кода"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.features.code_editor.services.code_editor_service import CodeEditorService
from app.shared.database import get_session
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
    TestCasesResponse,
    ValidationResultResponse,
    HealthResponse,
)
from app.features.code_editor.exceptions.code_editor_exceptions import (
    UnsupportedLanguageError,
    CodeExecutionError,
    UnsafeCodeError,
    SolutionNotFoundError,
)
from app.shared.dependencies import get_current_user_optional, get_current_user_required

logger = logging.getLogger(__name__)

router = APIRouter()


def get_code_editor_service(db: Session = Depends(get_session)) -> CodeEditorService:
    """Dependency injection для CodeEditorService"""
    from app.features.code_editor.repositories.code_editor_repository import CodeEditorRepository
    
    repository = CodeEditorRepository(db)
    return CodeEditorService(repository)


@router.get("/languages", response_model=List[SupportedLanguageResponse])
async def get_supported_languages(
    code_editor_service: CodeEditorService = Depends(get_code_editor_service),
):
    """Получение списка поддерживаемых языков программирования"""
    logger.info("API: Получение поддерживаемых языков")
    
    try:
        languages = await code_editor_service.get_supported_languages()
        logger.info(f"API: Получено {len(languages)} языков")
        return languages
        
    except Exception as e:
        logger.error(f"API: Ошибка при получении языков: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get supported languages: {str(e)}",
        )


@router.post("/execute", response_model=CodeExecutionResponse)
async def execute_code(
    request: CodeExecutionRequest,
    code_editor_service: CodeEditorService = Depends(get_code_editor_service),
    user=Depends(get_current_user_optional),
):
    """Выполнение кода в изолированной среде"""
    logger.info(f"API: Выполнение кода на языке {request.language}")
    
    try:
        user_id = user.id if user else None
        execution = await code_editor_service.execute_code(request, user_id)
        
        logger.info(f"API: Код выполнен, ID: {execution.id}")
        return execution
        
    except UnsupportedLanguageError as e:
        logger.warning(f"API: Неподдерживаемый язык: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except UnsafeCodeError as e:
        logger.warning(f"API: Небезопасный код: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"API: Ошибка при выполнении кода: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute code: {str(e)}",
        )


@router.get("/executions/{execution_id}", response_model=CodeExecutionResponse)
async def get_execution_result(
    execution_id: str,
    code_editor_service: CodeEditorService = Depends(get_code_editor_service),
    user=Depends(get_current_user_optional),
):
    """Получение результата выполнения кода"""
    logger.info(f"API: Получение результата выполнения {execution_id}")
    
    try:
        user_id = user.id if user else None
        execution = await code_editor_service.get_execution_result(execution_id, user_id)
        
        logger.info(f"API: Результат получен для {execution_id}")
        return execution
        
    except CodeExecutionError as e:
        logger.warning(f"API: Ошибка выполнения: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"API: Ошибка при получении результата: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get execution result: {str(e)}",
        )


@router.get("/executions", response_model=List[CodeExecutionResponse])
async def get_user_executions(
    code_editor_service: CodeEditorService = Depends(get_code_editor_service),
    blockId: Optional[str] = None,
    user=Depends(get_current_user_optional),
):
    """Получение истории выполнений пользователя"""
    logger.info("API: Получение истории выполнений")
    
    try:
        if not user:
            return []
            
        executions = await code_editor_service.get_user_executions(
            user.id, blockId
        )
        
        logger.info(f"API: Получено {len(executions)} выполнений")
        return executions
        
    except Exception as e:
        logger.error(f"API: Ошибка при получении истории: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user executions: {str(e)}",
        )


@router.post("/solutions", response_model=UserCodeSolutionResponse)
async def save_solution(
    solution: UserCodeSolutionCreateRequest,
    code_editor_service: CodeEditorService = Depends(get_code_editor_service),
    user=Depends(get_current_user_required),
):
    """Сохранение решения пользователя"""
    logger.info(f"API: Сохранение решения для блока {solution.blockId}")
    
    try:
        saved_solution = await code_editor_service.save_solution(solution, user.id)
        
        logger.info(f"API: Решение сохранено: {saved_solution.id}")
        return saved_solution
        
    except UnsupportedLanguageError as e:
        logger.warning(f"API: Неподдерживаемый язык: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"API: Ошибка при сохранении решения: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save solution: {str(e)}",
        )


@router.get("/solutions/{block_id}", response_model=List[UserCodeSolutionResponse])
async def get_block_solutions(
    block_id: str,
    code_editor_service: CodeEditorService = Depends(get_code_editor_service),
    user=Depends(get_current_user_required),
):
    """Получение решений пользователя для блока"""
    logger.info(f"API: Получение решений для блока {block_id}")
    
    try:
        solutions = await code_editor_service.get_block_solutions(user.id, block_id)
        
        logger.info(f"API: Получено {len(solutions)} решений")
        return solutions
        
    except Exception as e:
        logger.error(f"API: Ошибка при получении решений: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get block solutions: {str(e)}",
        )


@router.put("/solutions/{solution_id}", response_model=UserCodeSolutionResponse)
async def update_solution(
    solution_id: str,
    solution_update: UserCodeSolutionUpdateRequest,
    code_editor_service: CodeEditorService = Depends(get_code_editor_service),
    user=Depends(get_current_user_required),
):
    """Обновление решения пользователя"""
    logger.info(f"API: Обновление решения {solution_id}")
    
    try:
        updated_solution = await code_editor_service.update_solution(
            solution_id, user.id, solution_update
        )
        
        logger.info(f"API: Решение обновлено: {solution_id}")
        return updated_solution
        
    except SolutionNotFoundError as e:
        logger.warning(f"API: Решение не найдено: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"API: Ошибка при обновлении решения: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update solution: {str(e)}",
        )


@router.get("/stats", response_model=ExecutionStatsResponse)
async def get_execution_stats(
    code_editor_service: CodeEditorService = Depends(get_code_editor_service),
    user=Depends(get_current_user_required),
):
    """Получение статистики выполнений пользователя"""
    logger.info(f"API: Получение статистики для пользователя {user.id}")
    
    try:
        stats = await code_editor_service.get_execution_stats(user.id)
        
        logger.info(f"API: Статистика получена: {stats.totalExecutions} выполнений")
        return stats
        
    except Exception as e:
        logger.error(f"API: Ошибка при получении статистики: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get execution stats: {str(e)}",
        )


@router.get("/test_cases/{block_id}", response_model=TestCasesResponse)
async def get_test_cases(
    block_id: str,
    code_editor_service: CodeEditorService = Depends(get_code_editor_service),
    user=Depends(get_current_user_optional),
):
    """Получение тест-кейсов для блока"""
    logger.info(f"API: Получение тест-кейсов для блока {block_id}")
    
    try:
        user_id = user.id if user else None
        test_cases = await code_editor_service.get_test_cases(block_id, user_id)
        
        logger.info(f"API: Получено {test_cases.totalTests} тест-кейсов")
        return test_cases
        
    except Exception as e:
        logger.error(f"API: Ошибка при получении тест-кейсов: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get test cases: {str(e)}",
        )


@router.post("/validate/{block_id}", response_model=ValidationResultResponse)
async def validate_solution(
    block_id: str,
    validation_request: ValidationRequest,
    code_editor_service: CodeEditorService = Depends(get_code_editor_service),
    user=Depends(get_current_user_required),
):
    """Валидация решения против тест-кейсов"""
    logger.info(f"API: Валидация решения для блока {block_id}")
    
    try:
        validation_result = await code_editor_service.validate_solution(
            block_id, validation_request, user.id
        )
        
        logger.info(f"API: Валидация завершена: {validation_result.passedTests}/{validation_result.totalTests}")
        return validation_result
        
    except UnsupportedLanguageError as e:
        logger.warning(f"API: Неподдерживаемый язык: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"API: Ошибка при валидации: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate solution: {str(e)}",
        )


@router.get("/health", response_model=HealthResponse)
async def health_check(
    code_editor_service: CodeEditorService = Depends(get_code_editor_service),
):
    """Проверка здоровья модуля редактора кода"""
    logger.info("API: Проверка здоровья code_editor модуля")
    
    try:
        health_status = await code_editor_service.get_health_status()
        logger.info("API: Проверка здоровья завершена")
        return health_status
        
    except Exception as e:
        logger.error(f"API: Ошибка при проверке здоровья: {e}")
        return HealthResponse(
            status="unhealthy",
            module="code_editor",
            supportedLanguages=0,
            totalExecutions=0,
        ) 


