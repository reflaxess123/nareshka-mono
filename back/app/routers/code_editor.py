import logging
import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from ..auth import get_current_user_from_session_required
from ..code_executor import code_executor
from ..database import engine, get_db
from ..models import (
    CodeExecution,
    CodeLanguage,
    ExecutionStatus,
    SupportedLanguage,
    UserCodeSolution,
)
from ..schemas import (
    CodeExecutionRequest,
    CodeExecutionResponse,
    ExecutionStats,
    SupportedLanguagePublic,
    UserCodeSolutionCreate,
    UserCodeSolutionResponse,
    UserCodeSolutionUpdate,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/code-editor", tags=["Code Editor"])


@router.get("/languages", response_model=List[SupportedLanguagePublic])
async def get_supported_languages(db: Session = Depends(get_db)):
    """Получение списка поддерживаемых языков программирования"""

    languages = db.query(SupportedLanguage).filter(
        SupportedLanguage.isEnabled == True
    ).all()

    if not languages:
        # Если языки не настроены в БД, возвращаем базовые
        return [
            {
                "id": "python39",
                "name": "Python 3.9",
                "language": CodeLanguage.PYTHON,
                "version": "3.9",
                "fileExtension": ".py",
                "timeoutSeconds": 10,
                "memoryLimitMB": 128,
                "isEnabled": True
            },
            {
                "id": "node18",
                "name": "Node.js 18",
                "language": CodeLanguage.JAVASCRIPT,
                "version": "18",
                "fileExtension": ".js",
                "timeoutSeconds": 10,
                "memoryLimitMB": 128,
                "isEnabled": True
            }
        ]

    return languages


@router.post("/execute", response_model=CodeExecutionResponse)
async def execute_code(
    request: CodeExecutionRequest,
    background_tasks: BackgroundTasks,
    user_request: Request,
    db: Session = Depends(get_db)
):
    """Выполнение кода в изолированной среде"""

    user = get_current_user_from_session_required(user_request, db)

    # Проверяем безопасность кода
    if not code_executor.validate_code_safety(request.sourceCode, request.language):
        raise HTTPException(
            status_code=400,
            detail="Code contains potentially unsafe patterns"
        )

    # Получаем настройки языка
    language = db.query(SupportedLanguage).filter(
        SupportedLanguage.language == request.language,
        SupportedLanguage.isEnabled == True
    ).first()

    if not language:
        raise HTTPException(
            status_code=400,
            detail=f"Language {request.language} is not supported"
        )

    # Создаем запись о выполнении
    execution_id = str(uuid.uuid4())
    execution = CodeExecution(
        id=execution_id,
        userId=user.id,
        blockId=request.blockId,
        languageId=language.id,
        sourceCode=request.sourceCode,
        stdin=request.stdin,
        status=ExecutionStatus.PENDING
    )

    db.add(execution)
    db.commit()
    db.refresh(execution)

    # Запускаем выполнение в фоне
    background_tasks.add_task(
        _execute_code_background,
        execution_id, language.id, request.sourceCode, request.stdin
    )

    return execution


@router.get("/executions/{execution_id}", response_model=CodeExecutionResponse)
async def get_execution_result(
    execution_id: str,
    user_request: Request,
    db: Session = Depends(get_db)
):
    """Получение результата выполнения кода"""

    user = get_current_user_from_session_required(user_request, db)

    execution = db.query(CodeExecution).filter(
        CodeExecution.id == execution_id,
        CodeExecution.userId == user.id
    ).first()

    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")

    return execution


@router.get("/executions", response_model=List[CodeExecutionResponse])
async def get_user_executions(
    user_request: Request,
    db: Session = Depends(get_db),
    blockId: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
):
    """Получение истории выполнений пользователя"""

    user = get_current_user_from_session_required(user_request, db)

    query = db.query(CodeExecution).filter(CodeExecution.userId == user.id)

    if blockId:
        query = query.filter(CodeExecution.blockId == blockId)

    executions = query.order_by(desc(CodeExecution.createdAt)).offset(offset).limit(limit).all()

    return executions


@router.post("/solutions", response_model=UserCodeSolutionResponse)
async def save_solution(
    solution: UserCodeSolutionCreate,
    user_request: Request,
    db: Session = Depends(get_db)
):
    """Сохранение решения пользователя"""

    user = get_current_user_from_session_required(user_request, db)

    # Получаем языковые настройки
    language = db.query(SupportedLanguage).filter(
        SupportedLanguage.language == solution.language
    ).first()

    if not language:
        raise HTTPException(
            status_code=400,
            detail=f"Language {solution.language} is not supported"
        )

    # Проверяем, существует ли уже решение для этой задачи и языка
    existing_solution = db.query(UserCodeSolution).filter(
        UserCodeSolution.userId == user.id,
        UserCodeSolution.blockId == solution.blockId,
        UserCodeSolution.languageId == language.id
    ).first()

    if existing_solution:
        # Обновляем существующее решение
        existing_solution.sourceCode = solution.sourceCode
        existing_solution.isCompleted = solution.isCompleted
        existing_solution.updatedAt = datetime.utcnow()
        db.commit()
        db.refresh(existing_solution)
        return existing_solution
    else:
        # Создаем новое решение
        solution_id = str(uuid.uuid4())
        new_solution = UserCodeSolution(
            id=solution_id,
            userId=user.id,
            blockId=solution.blockId,
            languageId=language.id,
            sourceCode=solution.sourceCode,
            isCompleted=solution.isCompleted
        )

        db.add(new_solution)
        db.commit()
        db.refresh(new_solution)
        return new_solution


@router.get("/solutions/{block_id}", response_model=List[UserCodeSolutionResponse])
async def get_block_solutions(
    block_id: str,
    user_request: Request,
    db: Session = Depends(get_db)
):
    """Получение решений пользователя для конкретного блока"""

    user = get_current_user_from_session_required(user_request, db)

    solutions = db.query(UserCodeSolution).filter(
        UserCodeSolution.userId == user.id,
        UserCodeSolution.blockId == block_id
    ).all()

    return solutions


@router.put("/solutions/{solution_id}", response_model=UserCodeSolutionResponse)
async def update_solution(
    solution_id: str,
    solution_update: UserCodeSolutionUpdate,
    user_request: Request,
    db: Session = Depends(get_db)
):
    """Обновление решения пользователя"""

    user = get_current_user_from_session_required(user_request, db)

    solution = db.query(UserCodeSolution).filter(
        UserCodeSolution.id == solution_id,
        UserCodeSolution.userId == user.id
    ).first()

    if not solution:
        raise HTTPException(status_code=404, detail="Solution not found")

    # Обновляем поля
    if solution_update.sourceCode is not None:
        solution.sourceCode = solution_update.sourceCode

    if solution_update.isCompleted is not None:
        solution.isCompleted = solution_update.isCompleted

    solution.updatedAt = datetime.utcnow()

    db.commit()
    db.refresh(solution)

    return solution


@router.get("/stats", response_model=ExecutionStats)
async def get_execution_stats(
    user_request: Request,
    db: Session = Depends(get_db)
):
    """Получение статистики выполнения кода пользователя"""

    user = get_current_user_from_session_required(user_request, db)

    # Общая статистика
    total_executions = db.query(CodeExecution).filter(
        CodeExecution.userId == user.id
    ).count()

    successful_executions = db.query(CodeExecution).filter(
        CodeExecution.userId == user.id,
        CodeExecution.status == ExecutionStatus.SUCCESS
    ).count()

    # Средние время выполнения
    avg_time_result = db.query(func.avg(CodeExecution.executionTimeMs)).filter(
        CodeExecution.userId == user.id,
        CodeExecution.status == ExecutionStatus.SUCCESS
    ).scalar()

    average_execution_time = float(avg_time_result) if avg_time_result else 0.0

    # Статистика по языкам
    language_stats = db.query(
        SupportedLanguage.name,
        SupportedLanguage.language,
        func.count(CodeExecution.id).label("count")
    ).join(
        CodeExecution, SupportedLanguage.id == CodeExecution.languageId
    ).filter(
        CodeExecution.userId == user.id
    ).group_by(
        SupportedLanguage.name, SupportedLanguage.language
    ).all()

    language_stats_list = [
        {
            "language": stat.language,
            "name": stat.name,
            "executions": stat.count
        }
        for stat in language_stats
    ]

    return {
        "totalExecutions": total_executions,
        "successfulExecutions": successful_executions,
        "averageExecutionTime": average_execution_time,
        "languageStats": language_stats_list
    }


async def _execute_code_background(
    execution_id: str,
    language_id: str,
    source_code: str,
    stdin: Optional[str] = None
):
    """Фоновая задача для выполнения кода"""

    # Создаем новую сессию для фоновой задачи
    with Session(engine) as db:
        try:
            # Получаем объект языка в новой сессии
            language = db.query(SupportedLanguage).filter(
                SupportedLanguage.id == language_id
            ).first()

            if not language:
                logger.error(f"Language {language_id} not found")
                return

            # Обновляем статус на "выполняется"
            execution = db.query(CodeExecution).filter(
                CodeExecution.id == execution_id
            ).first()

            if not execution:
                logger.error(f"Execution {execution_id} not found")
                return

            execution.status = ExecutionStatus.RUNNING
            db.commit()

            # Выполняем код
            result = await code_executor.execute_code(source_code, language, stdin)

            # Обновляем результат в БД
            execution.status = result.get("status", ExecutionStatus.ERROR)
            execution.stdout = result.get("stdout")
            execution.stderr = result.get("stderr")
            execution.exitCode = result.get("exitCode")
            execution.executionTimeMs = result.get("executionTimeMs")
            execution.memoryUsedMB = result.get("memoryUsedMB")
            execution.containerLogs = result.get("containerLogs")
            execution.errorMessage = result.get("errorMessage")
            execution.completedAt = datetime.utcnow()

            db.commit()

            # Обновляем статистику решения, если оно привязано к блоку
            if execution.blockId:
                solution = db.query(UserCodeSolution).filter(
                    UserCodeSolution.userId == execution.userId,
                    UserCodeSolution.blockId == execution.blockId,
                    UserCodeSolution.languageId == language.id
                ).first()

                if solution:
                    solution.executionCount += 1
                    if execution.status == ExecutionStatus.SUCCESS:
                        solution.successfulExecutions += 1
                    solution.lastExecutionId = execution_id
                    db.commit()

            logger.info(f"Code execution {execution_id} completed successfully")

        except Exception as e:
            logger.error(f"Background execution {execution_id} failed: {str(e)}")

            # Обновляем статус на ошибку
            execution = db.query(CodeExecution).filter(
                CodeExecution.id == execution_id
            ).first()

            if execution:
                execution.status = ExecutionStatus.ERROR
                execution.errorMessage = str(e)
                execution.completedAt = datetime.utcnow()
                db.commit()
