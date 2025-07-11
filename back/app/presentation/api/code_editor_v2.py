from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status

from app.application.dto.code_editor_dto import (
    CodeExecutionRequestDTO,
    CodeExecutionResponseDTO,
    ExecutionStatsDTO,
    SupportedLanguageResponseDTO,
    TestCasesResponseDTO,
    UserCodeSolutionCreateDTO,
    UserCodeSolutionResponseDTO,
    UserCodeSolutionUpdateDTO,
    ValidationRequestDTO,
    ValidationResultDTO,
)
from app.application.services.code_editor_service import CodeEditorService
from app.shared.dependencies import (
    get_code_editor_service,
    get_current_user_optional,
    get_current_user_required,
)

router = APIRouter()


@router.get("/languages", response_model=List[SupportedLanguageResponseDTO])
async def get_supported_languages(
    code_editor_service: CodeEditorService = Depends(get_code_editor_service),
):
    """Получение списка поддерживаемых языков программирования"""

    try:
        languages = await code_editor_service.get_supported_languages()
        return languages
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get supported languages: {str(e)}",
        ) from e


@router.post("/execute", response_model=CodeExecutionResponseDTO)
async def execute_code(
    request: CodeExecutionRequestDTO,
    code_editor_service: CodeEditorService = Depends(get_code_editor_service),
    user=Depends(get_current_user_optional),
):
    """Выполнение кода в изолированной среде"""

    # Пользователь получен через DI (может быть None для анонимных)
    user_id = user.id if user else None

    try:
        result = await code_editor_service.execute_code(request, user_id)

        # TODO: Добавить фоновую задачу для выполнения кода
        # background_tasks.add_task(_execute_code_background, result.id)

        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute code: {str(e)}",
        ) from e


@router.get("/executions/{execution_id}", response_model=CodeExecutionResponseDTO)
async def get_execution_result(
    execution_id: str,
    code_editor_service: CodeEditorService = Depends(get_code_editor_service),
    user=Depends(get_current_user_optional),
):
    """Получение результата выполнения кода"""

    # Пользователь получен через DI (может быть None для анонимных)
    user_id = user.id if user else None

    try:
        result = await code_editor_service.get_execution_result(execution_id, user_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get execution result: {str(e)}",
        ) from e


@router.get("/executions", response_model=List[CodeExecutionResponseDTO])
async def get_user_executions(
    code_editor_service: CodeEditorService = Depends(get_code_editor_service),
    blockId: Optional[str] = None,
    user=Depends(get_current_user_optional),
):
    """Получение истории выполнений пользователя"""

    # Пользователь получен через DI (обязательно авторизован)
    user_id = user.id if user else None

    try:
        executions = await code_editor_service.get_user_executions(user_id, blockId)
        return executions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user executions: {str(e)}",
        ) from e


@router.post("/solutions", response_model=UserCodeSolutionResponseDTO)
async def save_solution(
    solution: UserCodeSolutionCreateDTO,
    code_editor_service: CodeEditorService = Depends(get_code_editor_service),
    user=Depends(get_current_user_required),
):
    """Сохранение решения пользователя"""

    # Пользователь получен через DI (обязательно авторизован)

    try:
        result = await code_editor_service.save_solution(solution, user.id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save solution: {str(e)}",
        ) from e


@router.get("/solutions/{block_id}", response_model=List[UserCodeSolutionResponseDTO])
async def get_block_solutions(
    block_id: str,
    code_editor_service: CodeEditorService = Depends(get_code_editor_service),
    user=Depends(get_current_user_required),
):
    """Получение решений пользователя для конкретного блока"""

    # Пользователь получен через DI (обязательно авторизован)

    try:
        solutions = await code_editor_service.get_block_solutions(block_id, user.id)
        return solutions
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get block solutions: {str(e)}",
        ) from e


@router.put("/solutions/{solution_id}", response_model=UserCodeSolutionResponseDTO)
async def update_solution(
    solution_id: str,
    solution_update: UserCodeSolutionUpdateDTO,
    code_editor_service: CodeEditorService = Depends(get_code_editor_service),
    user=Depends(get_current_user_required),
):
    """Обновление решения пользователя"""

    # Пользователь получен через DI (обязательно авторизован)

    try:
        result = await code_editor_service.update_solution(
            solution_id, user.id, solution_update
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update solution: {str(e)}",
        ) from e


@router.get("/stats", response_model=ExecutionStatsDTO)
async def get_execution_stats(
    code_editor_service: CodeEditorService = Depends(get_code_editor_service),
    user=Depends(get_current_user_required),
):
    """Получение статистики выполнения кода пользователя"""

    # Пользователь получен через DI (обязательно авторизован)

    try:
        stats = await code_editor_service.get_execution_stats(user.id)
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get execution stats: {str(e)}",
        ) from e


@router.get("/test_cases/{block_id}", response_model=TestCasesResponseDTO)
async def get_test_cases(
    block_id: str,
    code_editor_service: CodeEditorService = Depends(get_code_editor_service),
    user=Depends(get_current_user_optional),
):
    """Получение тест-кейсов для блока"""

    # Пользователь получен через DI (может быть None)
    user_id = user.id if user else None

    try:
        test_cases = await code_editor_service.get_test_cases(block_id, user_id)

        total_tests = len(test_cases)
        public_tests = sum(1 for tc in test_cases if tc.isPublic)
        hidden_tests = total_tests - public_tests

        return TestCasesResponseDTO(
            blockId=block_id,
            testCases=test_cases,
            totalTests=total_tests,
            publicTests=public_tests,
            hiddenTests=hidden_tests,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get test cases: {str(e)}",
        ) from e


@router.post("/validate/{block_id}", response_model=ValidationResultDTO)
async def validate_solution(
    block_id: str,
    validation_request: ValidationRequestDTO,
    code_editor_service: CodeEditorService = Depends(get_code_editor_service),
    user=Depends(get_current_user_required),
):
    """Валидация решения против тест-кейсов"""

    # Пользователь получен через DI (обязательно авторизован)

    try:
        result = await code_editor_service.validate_solution(
            block_id, validation_request, user.id
        )

        # TODO: Записать результаты валидации в прогресс пользователя
        # background_tasks.add_task(_record_validation_progress, user.id, block_id, result)

        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate solution: {str(e)}",
        ) from e


@router.get("/health")
async def health_check():
    """Проверка работоспособности Code Editor API"""
    return {"status": "healthy", "module": "code_editor"}
