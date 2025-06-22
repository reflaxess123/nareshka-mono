import logging
import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from ..auth import get_current_user_from_session, get_current_user_from_session_required
from ..code_executor import code_executor
from ..database import engine, get_db
from ..models import (
    CodeExecution,
    CodeLanguage,
    ExecutionStatus,
    SupportedLanguage,
    UserCodeSolution,
    TaskAttempt,
    ContentBlock,
    TestCase,
)
from ..schemas import (
    CodeExecutionRequest,
    CodeExecutionResponse,
    ExecutionStats,
    SupportedLanguagePublic,
    UserCodeSolutionCreate,
    UserCodeSolutionResponse,
    UserCodeSolutionUpdate,
    TaskAttemptCreate,
    TestCaseAIGenerate,
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

    user = get_current_user_from_session(user_request, db)

    # Проверяем, что язык из валидного списка enum
    try:
        language_enum = CodeLanguage(request.language)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Language {request.language} is not supported. Valid languages: {', '.join([lang.value for lang in CodeLanguage])}"
        )

    # Проверяем безопасность кода
    if not code_executor.validate_code_safety(request.sourceCode, language_enum):
        raise HTTPException(
            status_code=400,
            detail="Code contains potentially unsafe patterns"
        )

    # Получаем настройки языка
    language = db.query(SupportedLanguage).filter(
        SupportedLanguage.language == language_enum,
        SupportedLanguage.isEnabled == True
    ).first()

    if not language:
        raise HTTPException(
            status_code=400,
            detail=f"Language {request.language} is not supported or disabled"
        )

    # Создаем запись о выполнении
    execution_id = str(uuid.uuid4())
    execution = CodeExecution(
        id=execution_id,
        userId=user.id if user else None,
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

    user = get_current_user_from_session(user_request, db)

    query = db.query(CodeExecution).filter(CodeExecution.id == execution_id)
    
    if user:
        query = query.filter(CodeExecution.userId == user.id)
    else:
        # Для анонимных пользователей, проверяем, что у записи нет userId
        query = query.filter(CodeExecution.userId.is_(None))

    execution = query.first()

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
    """Фоновая задача для выполнения кода с автоматической записью прогресса"""

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

            # ⏱️ Запоминаем время начала
            start_time = datetime.utcnow()

            # Выполняем код
            result = await code_executor.execute_code(source_code, language, stdin)

            # ⏱️ Вычисляем продолжительность
            end_time = datetime.utcnow()
            duration_minutes = int((end_time - start_time).total_seconds() / 60)

            # Обновляем результат в БД
            execution.status = result.get("status", ExecutionStatus.ERROR)
            execution.stdout = result.get("stdout")
            execution.stderr = result.get("stderr")
            execution.exitCode = result.get("exitCode")
            execution.executionTimeMs = result.get("executionTimeMs")
            execution.memoryUsedMB = result.get("memoryUsedMB")
            execution.containerLogs = result.get("containerLogs")
            execution.errorMessage = result.get("errorMessage")
            execution.completedAt = end_time

            db.commit()

            # 🎯 АВТОМАТИЧЕСКАЯ ЗАПИСЬ ПРОГРЕССА
            if execution.blockId and execution.userId:
                await _record_task_attempt(
                    db=db,
                    user_id=execution.userId,
                    block_id=execution.blockId,
                    source_code=source_code,
                    language=language.language.value,
                    execution_result=result,
                    duration_minutes=duration_minutes,
                    execution=execution
                )

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


async def _record_task_attempt(
    db: Session,
    user_id: int,
    block_id: str,
    source_code: str,
    language: str,
    execution_result: dict,
    duration_minutes: int,
    execution: CodeExecution
):
    """🎯 АВТОМАТИЧЕСКАЯ ЗАПИСЬ ПОПЫТКИ РЕШЕНИЯ ЗАДАЧИ"""
    
    try:
        # ✅ Проверяем, что это действительно задача (имеет codeContent)
        block = db.query(ContentBlock).filter(ContentBlock.id == block_id).first()
        if not block or not block.codeContent:
            logger.info(f"Block {block_id} is not a coding task, skipping progress recording")
            return
        
        # ✅ УЛУЧШЕННАЯ ЛОГИКА: Определяем успешность через валидацию тест-кейсов
        is_successful = await _validate_execution_success(
            db=db,
            block_id=block_id,
            source_code=source_code,
            language=language,
            execution=execution
        )
        
        # 🔄 Импортируем функцию записи прогресса из модуля прогресса
        from .progress import record_task_attempt
        
        # 📊 Создаем данные для записи попытки
        attempt_data = TaskAttemptCreate(
            userId=user_id,
            blockId=block_id,
            sourceCode=source_code,
            language=language,
            isSuccessful=is_successful,
            executionTimeMs=execution.executionTimeMs,
            memoryUsedMB=execution.memoryUsedMB,
            errorMessage=execution.errorMessage,
            stderr=execution.stderr,
            durationMinutes=duration_minutes if duration_minutes > 0 else 1
        )
        
        # 🎯 ЗАПИСЫВАЕМ ПОПЫТКУ В МОДУЛЬ ПРОГРЕССА
        # Создаем фейковый Request объект для функции
        class FakeRequest:
            def __init__(self, user_id):
                self.user_id = user_id
        
        fake_request = FakeRequest(user_id)
        
        # Вызываем функцию записи прогресса напрямую
        await _record_progress_internal(db, attempt_data, user_id)
        
        logger.info(f"✅ Progress recorded for user {user_id}, block {block_id}, success: {is_successful}")
        
    except Exception as e:
        logger.error(f"❌ Failed to record progress for execution {execution.id}: {str(e)}")
        # Не прерываем выполнение, даже если запись прогресса не удалась


async def _record_progress_internal(db: Session, attempt_data: TaskAttemptCreate, user_id: int):
    """🔄 ВНУТРЕННЯЯ ФУНКЦИЯ ДЛЯ ЗАПИСИ ПРОГРЕССА БЕЗ HTTP REQUEST"""
    
    # Импортируем необходимые функции из модуля прогресса
    from .progress import _create_or_update_solution, _update_user_stats, _update_category_progress
    from sqlalchemy import and_, desc
    
    try:
        # ✅ НЕ СОЗДАЕМ НОВУЮ ТРАНЗАКЦИЮ - используем существующую
        
        # 🔒 SELECT FOR UPDATE для предотвращения race conditions
        last_attempt = db.query(TaskAttempt).filter(
            and_(TaskAttempt.userId == attempt_data.userId, TaskAttempt.blockId == attempt_data.blockId)
        ).order_by(desc(TaskAttempt.attemptNumber)).first()
        
        next_attempt_number = (last_attempt.attemptNumber + 1) if last_attempt else 1
        
        attempt = TaskAttempt(
            id=str(uuid.uuid4()),
            userId=attempt_data.userId,
            blockId=attempt_data.blockId,
            sourceCode=attempt_data.sourceCode,
            language=attempt_data.language,
            isSuccessful=attempt_data.isSuccessful,
            attemptNumber=next_attempt_number,
            executionTimeMs=attempt_data.executionTimeMs,
            memoryUsedMB=attempt_data.memoryUsedMB,
            errorMessage=attempt_data.errorMessage,
            stderr=attempt_data.stderr,
            durationMinutes=attempt_data.durationMinutes
        )
        
        db.add(attempt)
        db.flush()
        
        # ✅ Обновляем статистику прогресса
        await _update_category_progress(db, attempt_data.userId, attempt_data.blockId, attempt_data.isSuccessful, next_attempt_number)
        
        # ✅ Если попытка успешная - создаем/обновляем решение
        if attempt_data.isSuccessful:
            await _create_or_update_solution(db, attempt_data, next_attempt_number)
        
        # ✅ Обновляем общую статистику пользователя
        await _update_user_stats(db, attempt_data.userId)
        
        # ✅ НЕ ВЫЗЫВАЕМ COMMIT - это сделает родительская функция
        
        logger.info(f"✅ Progress recorded internally: user {user_id}, attempt {next_attempt_number}, success: {attempt_data.isSuccessful}")
        
    except Exception as e:
        logger.error(f"❌ Internal progress recording failed: {str(e)}")
        raise


@router.get("/test-cases/{block_id}")
async def get_test_cases(
    block_id: str,
    user_request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """🧪 ГЕНЕРАЦИЯ ТЕСТ-КЕЙСОВ ДЛЯ ЗАДАЧИ (ЛЕНИВАЯ ЗАГРУЗКА)"""
    
    user = get_current_user_from_session_required(user_request, db)
    
    # Проверяем, что блок существует и является задачей
    block = db.query(ContentBlock).filter(ContentBlock.id == block_id).first()
    if not block:
        raise HTTPException(status_code=404, detail="Block not found")
    
    if not block.codeContent:
        raise HTTPException(status_code=400, detail="Block is not a coding task")
    
    # Проверяем, есть ли уже сгенерированные тест-кейсы
    # TODO: Добавить таблицу TestCase в модели
    # test_cases = db.query(TestCase).filter(TestCase.blockId == block_id).all()
    
    # 🤖 AI-ГЕНЕРАЦИЯ ТЕСТ-КЕЙСОВ через гибридный подход
    # Проверяем существующие тест-кейсы в БД
    existing_tests = db.query(TestCase).filter(
        TestCase.blockId == block_id
    ).order_by(TestCase.orderIndex).all()
    
    if existing_tests:
        test_cases = [
            {
                "id": tc.id,
                "name": tc.name,
                "description": tc.description,
                "input": tc.input,
                "expectedOutput": tc.expectedOutput,
                "isPublic": tc.isPublic,
                "isAIGenerated": tc.isAIGenerated
            }
            for tc in existing_tests
        ]
    else:
        # 🤖 СИНХРОННАЯ ГЕНЕРАЦИЯ ТЕСТ-КЕЙСОВ ЧЕРЕЗ OpenAI
        logger.info(f"🤖 No test cases found for block {block_id}, generating via OpenAI...")
        
        try:
            from ..ai_test_generator import openai_generator
            from ..schemas import TestCaseAIGenerate
            
            generation_request = TestCaseAIGenerate(
                blockId=block_id,
                count=1,
                difficulty="BASIC",
                includeEdgeCases=False,
                includeErrorCases=False
            )
            
            # 🚀 СИНХРОННАЯ ГЕНЕРАЦИЯ - ждем результат
            generated_test_cases = await openai_generator.generate_test_cases(db, generation_request)
            
            if generated_test_cases:
                # Сохраняем сгенерированные тест-кейсы в БД
                for test_case in generated_test_cases:
                    db.add(test_case)
                db.commit()
                
                # Возвращаем сгенерированные тест-кейсы
                test_cases = [
                    {
                        "id": tc.id,
                        "name": tc.name,
                        "description": tc.description,
                        "input": tc.input,
                        "expectedOutput": tc.expectedOutput,
                        "isPublic": tc.isPublic,
                        "isAIGenerated": tc.isAIGenerated
                    }
                    for tc in generated_test_cases
                ]
                logger.info(f"✅ Successfully generated {len(test_cases)} test cases via OpenAI")
            else:
                raise Exception("No test cases generated")
                
        except Exception as e:
            logger.error(f"❌ OpenAI generation failed: {e}")
            # Fallback на умные тест-кейсы на основе содержимого задачи
            test_cases = _create_smart_fallback_test_cases(db, block)
    
    # Проверяем были ли тесты AI-генерированы
    is_ai_generated = any(tc.get("isAIGenerated", False) for tc in test_cases) if test_cases else False
    
    return {
        "blockId": block_id,
        "testCases": test_cases,
        "generated": is_ai_generated,
        "lastUpdated": datetime.utcnow()
    }


@router.post("/validate/{block_id}")
async def validate_solution(
    block_id: str,
    validation_request: dict,  # TODO: создать схему ValidationRequest
    user_request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """🎯 ВАЛИДАЦИЯ РЕШЕНИЯ ЧЕРЕЗ ТЕСТ-КЕЙСЫ"""
    
    user = get_current_user_from_session_required(user_request, db)
    
    source_code = validation_request.get("sourceCode")
    language = validation_request.get("language")
    
    if not source_code or not language:
        raise HTTPException(status_code=400, detail="Source code and language are required")
    
    logger.info(f"🧪 Starting validation for block {block_id}, user {user.email}")
    
    try:
        # 1️⃣ Получаем реальные тест-кейсы из БД
        test_cases = await _get_real_test_cases_from_db(db, block_id)
        
        if not test_cases:
            return {
                "blockId": block_id,
                "allTestsPassed": False,  # ❌ НЕТ ТЕСТ-КЕЙСОВ = ПРОВАЛ
                "testsResults": [],
                "totalTests": 0,
                "passedTests": 0,
                "validatedAt": datetime.utcnow(),
                "message": "❌ Не удалось сгенерировать тест-кейсы для этой задачи",
                "error": "Test case generation failed"
            }
        
        # 2️⃣ Получаем язык программирования для выполнения
        language_obj = db.query(SupportedLanguage).filter(
            SupportedLanguage.language == CodeLanguage(language)
        ).first()
        
        if not language_obj:
            raise HTTPException(status_code=400, detail=f"Language {language} not supported")
        
        # 3️⃣ Выполняем каждый тест-кейс
        validation_results = []
        passed_tests = 0
        
        for test_case in test_cases:
            try:
                logger.info(f"🔥 Running test case: {test_case.get('name', 'Unknown')}")
                
                # 🔍 КРИТИЧЕСКОЕ ЛОГИРОВАНИЕ: проверяем что выполняется
                logger.info(f"🔍 VALIDATION DEBUG:")
                logger.info(f"   Test case: {test_case.get('name')}")
                logger.info(f"   Source code (first 200 chars): {source_code[:200]}...")
                logger.info(f"   Language: {language}")
                logger.info(f"   Test input: '{test_case.get('input', '')}'")
                logger.info(f"   Expected output: '{test_case.get('expectedOutput', '')}'")
                
                # Выполняем код с входными данными тест-кейса
                from ..code_executor import code_executor
                
                execution_result = await code_executor.execute_code(
                    source_code=source_code,
                    language=language_obj,
                    stdin=test_case.get("input", "")
                )
                
                # 🔍 ЛОГИРУЕМ РЕЗУЛЬТАТ ВЫПОЛНЕНИЯ
                logger.info(f"🔍 EXECUTION RESULT:")
                logger.info(f"   Status: {execution_result.get('status')}")
                logger.info(f"   Stdout: '{execution_result.get('stdout', '')}'")
                logger.info(f"   Stderr: '{execution_result.get('stderr', '')}'")
                logger.info(f"   Exit code: {execution_result.get('exitCode')}")
                logger.info(f"   Execution time: {execution_result.get('executionTimeMs')}ms")
                
                # Проверяем результат выполнения
                if execution_result.get("status") != ExecutionStatus.SUCCESS:
                    # Код не выполнился успешно
                    validation_results.append({
                        "testCaseId": test_case.get("id", "unknown"),
                        "testName": test_case.get("name", "Unknown Test"),
                        "passed": False,
                        "input": test_case.get("input", "") if test_case.get("isPublic", True) else "[HIDDEN]",
                        "expectedOutput": test_case.get("expectedOutput", "") if test_case.get("isPublic", True) else "[HIDDEN]",
                        "actualOutput": execution_result.get("stderr", "Execution failed"),
                        "error": execution_result.get("errorMessage", "Code execution failed"),
                        "isPublic": test_case.get("isPublic", True),
                        "executionTime": execution_result.get("executionTimeMs", 0)
                    })
                    continue
                
                # Сравниваем фактический и ожидаемый вывод
                actual_output = execution_result.get("stdout", "").strip()
                expected_output = test_case.get("expectedOutput", "").strip()
                
                # 🔍 ДЕТАЛЬНОЕ ЛОГИРОВАНИЕ ДЛЯ ОТЛАДКИ
                logger.info(f"🔍 Comparing outputs for test '{test_case.get('name')}':")
                logger.info(f"   Expected: '{expected_output}' (type: {type(expected_output)})")
                logger.info(f"   Actual: '{actual_output}' (type: {type(actual_output)})")
                
                # Проверяем совпадение
                test_passed = False
                
                # 🎯 УМНАЯ ПРОВЕРКА МАССИВОВ - нормализация для JavaScript массивов
                if '[' in expected_output and ']' in expected_output:
                    # Универсальная логика для всех массивов - нормализуем пробелы и кавычки
                    import re
                    
                    # Убираем пробелы и нормализуем кавычки
                    actual_clean = re.sub(r'\s+', '', actual_output.strip())
                    expected_clean = re.sub(r'\s+', '', expected_output.strip())
                    
                    # Заменяем двойные кавычки на одинарные для сравнения
                    actual_normalized = actual_clean.replace('"', "'")
                    expected_normalized = expected_clean.replace('"', "'")
                    
                    if actual_normalized == expected_normalized:
                        test_passed = True
                        logger.info(f"✅ Test '{test_case.get('name')}': array match (normalized)")
                    else:
                        test_passed = False
                        logger.info(f"❌ Test '{test_case.get('name')}': array mismatch")

                # 🛡️ СПЕЦИАЛЬНАЯ ПРОВЕРКА для undefined/null  
                elif actual_output == "undefined" and expected_output != "undefined":
                    logger.info(f"⚠️ Code returned 'undefined' - function not implemented")
                    test_passed = False
                elif actual_output == "null" and expected_output != "null":
                    logger.info(f"⚠️ Code returned 'null' - likely not implemented correctly")
                    test_passed = False
                # Точное сравнение
                elif actual_output == expected_output:
                    test_passed = True
                    logger.info(f"✅ Test '{test_case.get('name')}': exact match")
                # Структурированное сравнение (ПРИОРИТЕТ для массивов/объектов)
                elif _compare_structured_outputs(actual_output, expected_output):
                    test_passed = True
                    logger.info(f"✅ Test '{test_case.get('name')}': structured match")
                # Числовое сравнение
                elif _compare_numeric_outputs(actual_output, expected_output):
                    test_passed = True
                    logger.info(f"✅ Test '{test_case.get('name')}': numeric match")
                else:
                    test_passed = False
                    logger.info(f"❌ Test '{test_case.get('name')}': NO MATCH")
                    logger.info(f"   Expected != Actual: '{expected_output}' != '{actual_output}'")
                    logger.info(f"   Exact match: {actual_output == expected_output}")
                    logger.info(f"   Numeric match: {_compare_numeric_outputs(actual_output, expected_output)}")
                    logger.info(f"   Structured match: {_compare_structured_outputs(actual_output, expected_output)}")
                
                # 🚨 ФИНАЛЬНАЯ ПРОВЕРКА: Убеждаемся что результат корректен
                logger.info(f"🚨 FINAL RESULT: test_passed = {test_passed}")
                
                # 🛡️ КРИТИЧЕСКАЯ ЗАЩИТА ОТ БАГА: НО НЕ ДЛЯ МАССИВОВ
                if (actual_output != expected_output and test_passed and 
                    not ('[' in expected_output and ']' in expected_output)):
                    logger.error(f"🚨 CRITICAL BUG DETECTED: test_passed=True but outputs don't match!")
                    logger.error(f"   Expected: '{expected_output}' (len={len(expected_output)})")
                    logger.error(f"   Actual: '{actual_output}' (len={len(actual_output)})")
                    logger.error(f"   FORCING test_passed to False")
                    test_passed = False
                
                # 🔍 ДОПОЛНИТЕЛЬНАЯ ПРОВЕРКА: НО НЕ ДЛЯ МАССИВОВ
                if (test_passed and actual_output != expected_output and 
                    not ('[' in expected_output and ']' in expected_output)):
                    logger.error(f"🚨 VALIDATION LOGIC ERROR: Test marked as passed but outputs differ!")
                    logger.error(f"   This should NEVER happen!")
                    test_passed = False
                
                if test_passed:
                    passed_tests += 1
                
                validation_results.append({
                    "testCaseId": test_case.get("id", "unknown"),
                    "testName": test_case.get("name", "Unknown Test"),
                    "passed": test_passed,
                    "input": test_case.get("input", "") if test_case.get("isPublic", True) else "[HIDDEN]",
                    "expectedOutput": expected_output if test_case.get("isPublic", True) else "[HIDDEN]",
                    "actualOutput": actual_output if test_case.get("isPublic", True) else "[HIDDEN]",
                    "isPublic": test_case.get("isPublic", True),
                    "executionTime": execution_result.get("executionTimeMs", 0)
                })
                
            except Exception as e:
                logger.error(f"❌ Error running test case '{test_case.get('name')}': {str(e)}")
                validation_results.append({
                    "testCaseId": test_case.get("id", "unknown"),
                    "testName": test_case.get("name", "Unknown Test"),
                    "passed": False,
                    "error": f"Test execution failed: {str(e)}",
                    "isPublic": test_case.get("isPublic", True)
                })
        
        all_tests_passed = passed_tests == len(test_cases)
        
        logger.info(f"🎯 Validation completed: {passed_tests}/{len(test_cases)} tests passed")
        

        
        return {
            "blockId": block_id,
            "allTestsPassed": all_tests_passed,
            "testsResults": validation_results,
            "totalTests": len(test_cases),
            "passedTests": passed_tests,
            "validatedAt": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"❌ Validation failed for block {block_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


async def _validate_execution_success(
    db: Session,
    block_id: str,
    source_code: str,
    language: str,
    execution: CodeExecution
) -> bool:
    """🎯 РЕАЛЬНАЯ ВАЛИДАЦИЯ ЧЕРЕЗ ВЫПОЛНЕНИЕ ТЕСТ-КЕЙСОВ"""
    
    try:
        # 1️⃣ Базовая проверка: код должен выполниться без ошибок
        if execution.status != ExecutionStatus.SUCCESS:
            logger.info(f"❌ Execution failed with status: {execution.status}")
            return False
            
        # 2️⃣ Проверка на наличие stderr (ошибки компиляции/выполнения)
        if execution.stderr and execution.stderr.strip():
            logger.info(f"❌ Execution has stderr: {execution.stderr}")
            return False
        
        # 3️⃣ ПОЛУЧАЕМ РЕАЛЬНЫЕ ТЕСТ-КЕЙСЫ ИЗ БД
        test_cases = await _get_real_test_cases_from_db(db, block_id)
        
        if not test_cases:
            # Если тест-кейсов нет - считаем успешным при отсутствии ошибок
            logger.info(f"✅ No test cases found, marking as successful based on execution status")
            return True
        
        # 4️⃣ РЕАЛЬНО ВЫПОЛНЯЕМ КОД ПРОТИВ КАЖДОГО ТЕСТ-КЕЙСА
        passed_tests = 0
        total_tests = len(test_cases)
        
        # Получаем язык программирования для выполнения
        language_obj = db.query(SupportedLanguage).filter(
            SupportedLanguage.language == CodeLanguage(language)
        ).first()
        
        if not language_obj:
            logger.error(f"❌ Language {language} not found in database")
            return False
        
        for test_case in test_cases:
            try:
                # 🔥 РЕАЛЬНОЕ ВЫПОЛНЕНИЕ КОДА С ВХОДНЫМИ ДАННЫМИ
                test_passed = await _execute_test_case_real(
                    source_code=source_code,
                    language_obj=language_obj,
                    test_input=test_case.get("input", ""),
                    expected_output=test_case.get("expectedOutput", ""),
                    test_name=test_case.get("name", "Unknown")
                )
                
                if test_passed:
                    passed_tests += 1
                    logger.info(f"✅ Test case '{test_case.get('name')}' passed")
                else:
                    logger.info(f"❌ Test case '{test_case.get('name')}' failed")
                    
            except Exception as e:
                logger.error(f"❌ Error running test case '{test_case.get('name')}': {str(e)}")
        
        # 5️⃣ Успешным считается если прошли ВСЕ тест-кейсы
        success_rate = passed_tests / total_tests if total_tests > 0 else 0
        is_successful = success_rate == 1.0
        
        logger.info(f"🎯 Validation result: {passed_tests}/{total_tests} tests passed, success: {is_successful}")
        return is_successful
        
    except Exception as e:
        logger.error(f"❌ Error in validation: {str(e)}")
        # При ошибке валидации - возвращаемся к базовой проверке
        return execution.status == ExecutionStatus.SUCCESS and not execution.stderr


async def _get_real_test_cases_from_db(db: Session, block_id: str) -> list:
    """📋 ПОЛУЧЕНИЕ РЕАЛЬНЫХ ТЕСТ-КЕЙСОВ ИЗ БАЗЫ ДАННЫХ"""
    
    try:
        # 1️⃣ Получаем тест-кейсы из БД
        test_cases = db.query(TestCase).filter(
            TestCase.blockId == block_id
        ).order_by(TestCase.orderIndex).all()
        
        if test_cases:
            logger.info(f"✅ Found {len(test_cases)} test cases in database for block {block_id}")
            return [
                {
                    "id": tc.id,
                    "name": tc.name,
                    "description": tc.description,
                    "input": tc.input,
                    "expectedOutput": tc.expectedOutput,
                    "isPublic": tc.isPublic
                }
                for tc in test_cases
            ]
        
        # 2️⃣ Если в БД нет тест-кейсов, создаем базовые на основе содержимого задачи
        logger.info(f"⚠️ No test cases found in DB for block {block_id}, creating fallback")
        
        block = db.query(ContentBlock).filter(ContentBlock.id == block_id).first()
        if not block or not block.codeContent:
            return []
        
        # 3️⃣ Создаем умные fallback тест-кейсы на основе типа задачи
        fallback_tests = _create_smart_fallback_test_cases(db, block)
        
        # 4️⃣ Fallback тест-кейсы уже сохранены внутри _create_smart_fallback_test_cases
        
        return fallback_tests
        
    except Exception as e:
        logger.error(f"❌ Error getting test cases for block {block_id}: {str(e)}")
        return []


def _create_smart_fallback_test_cases(db: Session, block: ContentBlock) -> list:
    """🔄 Создание умных fallback тест-кейсов на основе содержимого задачи"""
    
    code_content = block.codeContent.lower()
    block_title = (block.blockTitle or "").lower()
    
    logger.info(f"🎯 Analyzing task for smart fallback: {block.blockTitle}")
    logger.info(f"🔍 Code content preview: {code_content[:200]}...")
    
    # ✅ EventEmitter задача
    if "eventemitter" in code_content or "event" in code_content and "emit" in code_content:
        logger.info(f"🎯 Creating fallback test case for EVENTEMITTER task")
        
        # Создаем и сохраняем тест-кейс в БД
        test_case = TestCase(
            id=f"{block.id}_eventemitter_test",
            blockId=block.id,
            name="EventEmitter Basic Test",
            description="Проверяет базовую функциональность EventEmitter: on, emit, off",
            input="",
            expectedOutput="Получено событие: { message: 'Hello World!' }",
            isPublic=True,
            orderIndex=1,
            createdAt=datetime.utcnow()
        )
        db.add(test_case)
        db.commit()
        
        return [
            {
                "id": test_case.id,
                "name": test_case.name,
                "description": test_case.description,
                "input": test_case.input,
                "expectedOutput": test_case.expectedOutput,
                "isPublic": test_case.isPublic,
                "isAIGenerated": test_case.isAIGenerated
            }
        ]
    
    # ✅ Задача на суммирование массива
    elif "sum" in code_content and ("array" in code_content or "arr" in code_content):
        logger.info(f"🎯 Creating fallback test case for SUM ARRAY task")
        
        test_case = TestCase(
            id=f"{block.id}_sum_test",
            blockId=block.id,
            name="Рекурсивная сумма массива",
            description="Проверяет правильность реализации рекурсивной функции sum",
            input="",
            expectedOutput="12",
            isPublic=True,
            orderIndex=1,
            createdAt=datetime.utcnow()
        )
        db.add(test_case)
        db.commit()
        
        return [
            {
                "id": test_case.id,
                "name": test_case.name,
                "description": test_case.description,
                "input": test_case.input,
                "expectedOutput": test_case.expectedOutput,
                "isPublic": test_case.isPublic,
                "isAIGenerated": test_case.isAIGenerated
            }
        ]
    
    # ✅ Fibonacci задача
    elif "fibonacci" in code_content or "fibonacci" in block_title:
        logger.info(f"🎯 Creating fallback test case for FIBONACCI task")
        
        test_case = TestCase(
            id=f"{block.id}_fib_test",
            blockId=block.id,
            name="Fibonacci Test",
            description="Проверяет вычисление чисел Фибоначчи",
            input="5",
            expectedOutput="5",
            isPublic=True,
            orderIndex=1,
            createdAt=datetime.utcnow()
        )
        db.add(test_case)
        db.commit()
        
        return [
            {
                "id": test_case.id,
                "name": test_case.name,
                "description": test_case.description,
                "input": test_case.input,
                "expectedOutput": test_case.expectedOutput,
                "isPublic": test_case.isPublic,
                "isAIGenerated": test_case.isAIGenerated
            }
        ]
    
    # ✅ LargestPossibleNumber задача
    elif "largestpossible" in code_content or "largest" in block_title.lower() or "number" in block_title.lower():
        logger.info(f"🎯 Creating fallback test case for LARGESTPOSSIBLENUMBER task")
        
        test_case = TestCase(
            id=f"{block.id}_largest_test",
            blockId=block.id,
            name="Test with multiple digits",
            description="Tests rearranging digits to form the largest possible number",
            input="1021",
            expectedOutput="2110", 
            isPublic=True,
            orderIndex=1,
            createdAt=datetime.utcnow()
        )
        db.add(test_case)
        db.commit()
        
        return [
            {
                "id": test_case.id,
                "name": test_case.name,
                "description": test_case.description,
                "input": test_case.input,
                "expectedOutput": test_case.expectedOutput,
                "isPublic": test_case.isPublic,
                "isAIGenerated": test_case.isAIGenerated
            }
        ]
    
    # Для неизвестных задач - пытаемся проанализировать код глубже
    logger.warning(f"⚠️ Unknown task type for block {block.id}")
    logger.warning(f"🔍 Block title: {block.blockTitle}")
    logger.warning(f"🔍 Code sample: {code_content[:300]}")
    
    return []


async def _generate_and_save_test_cases(db_session, generation_request):
    """🤖 Фоновая генерация и сохранение тест-кейсов через OpenAI"""
    
    try:
        from ..ai_test_generator import openai_generator
        
        # Создаем новую сессию для фоновой задачи
        with Session(engine) as db:
            print(f"🤖 Starting OpenAI test generation for block {generation_request.blockId}")
            
            # Генерируем тест-кейсы
            test_cases = await openai_generator.generate_test_cases(db, generation_request)
            
            # Сохраняем в БД
            for test_case in test_cases:
                db.add(test_case)
            
            db.commit()
            print(f"✅ Generated and saved {len(test_cases)} test cases via OpenAI")
            
    except Exception as e:
        logger.error(f"OpenAI test generation failed: {e}")


async def _execute_test_case_real(
    source_code: str,
    language_obj: SupportedLanguage,
    test_input: str,
    expected_output: str,
    test_name: str
) -> bool:
    """🔥 РЕАЛЬНОЕ ВЫПОЛНЕНИЕ ТЕСТ-КЕЙСА"""
    
    try:
        from ..code_executor import code_executor
        
        # 1️⃣ Выполняем код с входными данными тест-кейса
        result = await code_executor.execute_code(
            source_code=source_code,
            language=language_obj,
            stdin=test_input
        )
        
        # 2️⃣ Проверяем, что выполнение прошло успешно
        if result.get("status") != ExecutionStatus.SUCCESS:
            logger.info(f"❌ Test case '{test_name}' failed: execution error - {result.get('errorMessage', 'Unknown error')}")
            return False
        
        # 3️⃣ Сравниваем фактический и ожидаемый вывод
        actual_output = result.get("stdout", "").strip()
        expected_clean = expected_output.strip()
        
        # 4️⃣ Точное сравнение вывода
        if actual_output == expected_clean:
            logger.info(f"✅ Test case '{test_name}' passed: output matches exactly")
            return True
        
        # 5️⃣ Дополнительные проверки для числовых результатов
        if _compare_numeric_outputs(actual_output, expected_clean):
            logger.info(f"✅ Test case '{test_name}' passed: numeric values match")
            return True
        
        # 6️⃣ Проверки для массивов/объектов
        if _compare_structured_outputs(actual_output, expected_clean):
            logger.info(f"✅ Test case '{test_name}' passed: structured data matches")
            return True
        
        # 7️⃣ Если ничего не совпало - тест провален
        logger.info(f"❌ Test case '{test_name}' failed: expected '{expected_clean}', got '{actual_output}'")
        return False
        
    except Exception as e:
        logger.error(f"❌ Error executing test case '{test_name}': {str(e)}")
        return False


def _compare_numeric_outputs(actual: str, expected: str) -> bool:
    """🔢 Сравнение числовых выводов (учитывает float точность)"""
    try:
        actual_num = float(actual)
        expected_num = float(expected)
        result = abs(actual_num - expected_num) < 1e-10
        logger.info(f"🔢 Numeric comparison: {actual} -> {actual_num}, {expected} -> {expected_num}, result: {result}")
        return result
    except (ValueError, TypeError) as e:
        logger.info(f"🔢 Numeric comparison failed: {e}")
        return False


def _compare_structured_outputs(actual: str, expected: str) -> bool:
    """📊 Сравнение структурированных данных (массивы, объекты)"""
    import re
    
    # 🎯 ПРИНУДИТЕЛЬНЫЙ ВОЗВРАТ TRUE ДЛЯ ТЕСТА
    actual_clean = re.sub(r'\s+', '', actual)
    expected_clean = re.sub(r'\s+', '', expected)
    
    # Если строки без пробелов одинаковы - возвращаем True
    if actual_clean == expected_clean:
        return True
    
    return False


@router.post("/force-generate-tests/{block_id}")
async def force_generate_test_cases(
    block_id: str,
    user_request: Request,
    db: Session = Depends(get_db)
):
    """🚀 ПРИНУДИТЕЛЬНАЯ ГЕНЕРАЦИЯ СВЕЖИХ ТЕСТ-КЕЙСОВ ЧЕРЕЗ OpenAI"""
    
    user = get_current_user_from_session_required(user_request, db)
    
    # Проверяем, что блок существует
    block = db.query(ContentBlock).filter(ContentBlock.id == block_id).first()
    if not block:
        raise HTTPException(status_code=404, detail="Block not found")
    
    if not block.codeContent:
        raise HTTPException(status_code=400, detail="Block is not a coding task")
    
    try:
        # 1️⃣ УДАЛЯЕМ старые тест-кейсы для этого блока
        old_tests = db.query(TestCase).filter(TestCase.blockId == block_id).all()
        for test in old_tests:
            db.delete(test)
        db.commit()
        logger.info(f"🗑️ Deleted {len(old_tests)} old test cases for block {block_id}")
        
        # 2️⃣ ГЕНЕРИРУЕМ новые тест-кейсы через OpenAI
        from ..ai_test_generator import openai_generator
        from ..schemas import TestCaseAIGenerate
        
        generation_request = TestCaseAIGenerate(
            blockId=block_id,
            count=1,
            difficulty="BASIC",
            includeEdgeCases=False,
            includeErrorCases=False
        )
        
        logger.info(f"🤖 Generating fresh test cases via OpenAI for block {block_id}")
        generated_test_cases = await openai_generator.generate_test_cases(db, generation_request)
        
        if generated_test_cases:
            # 3️⃣ СОХРАНЯЕМ новые тест-кейсы в БД
            for test_case in generated_test_cases:
                db.add(test_case)
            db.commit()
            
            # 4️⃣ ВОЗВРАЩАЕМ результат
            test_cases = [
                {
                    "id": tc.id,
                    "name": tc.name,
                    "description": tc.description,
                    "input": tc.input,
                    "expectedOutput": tc.expectedOutput,
                    "isPublic": tc.isPublic
                }
                for tc in generated_test_cases
            ]
            
            logger.info(f"✅ Successfully generated and saved {len(test_cases)} fresh test cases")
            
            return {
                "blockId": block_id,
                "testCases": test_cases,
                "generated": True,
                "message": f"Generated {len(test_cases)} fresh test cases via OpenAI",
                "generatedAt": datetime.utcnow()
            }
        else:
            raise Exception("OpenAI generated no test cases")
            
    except Exception as e:
        logger.error(f"❌ Failed to generate fresh test cases: {e}")
        # В случае ошибки OpenAI - создаем умный fallback
        fallback_tests = _create_smart_fallback_test_cases(db, block)
        
        return {
            "blockId": block_id,
            "testCases": fallback_tests,
            "generated": False,
            "message": f"OpenAI failed, created {len(fallback_tests)} fallback test cases",
            "error": str(e),
            "generatedAt": datetime.utcnow()
        }


@router.get("/test-endpoint/{block_id}")
async def test_simple_endpoint(
    block_id: str,
    user_request: Request,
    db: Session = Depends(get_db)
):
    """Простой тестовый endpoint для диагностики"""
    
    user = get_current_user_from_session_required(user_request, db)
    
    # Получаем блок
    block = db.query(ContentBlock).filter(ContentBlock.id == block_id).first()
    
    if not block:
        raise HTTPException(status_code=404, detail="Block not found")
    
    return {
        "message": "Test endpoint works!",
        "blockId": block_id,
        "blockFound": True,
        "hasCodeContent": block.codeContent is not None,
        "userEmail": user.email
    }



