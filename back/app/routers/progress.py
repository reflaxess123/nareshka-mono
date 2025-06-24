import uuid
from datetime import datetime, timedelta
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import and_, desc, func
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError

from ..auth import get_current_user_from_session_required
from ..database import get_db
from ..models import (
    ContentBlock,
    ContentFile,
    TaskAttempt,
    TaskSolution,
    User,
    UserCategoryProgress,
    UserContentProgress,
    UserPathProgress,
)
from ..schemas import (
    TaskAttemptCreate,
    TaskAttemptResponse,
    UserDetailedProgressResponse,
    CategoryProgressSummary,
    SimplifiedOverallStats,
    RecentActivityItem,
    ProgressAnalytics,
    GroupedCategoryProgress,
    SubCategoryProgress
)

router = APIRouter(prefix="/api/progress", tags=["Progress"])


async def get_unified_category_progress(db: Session, user_id: int):
    """Получает унифицированный прогресс по категориям для ВСЕХ существующих категорий и подкатегорий (по ContentFile)"""
    # Получаем все уникальные пары (mainCategory, subCategory) из ContentFile
    all_categories = db.query(
        ContentFile.mainCategory,
        ContentFile.subCategory
    ).filter(
        ContentFile.mainCategory != 'Test',
        ContentFile.subCategory != 'Test'
    ).distinct().all()

    category_summaries = []

    for main_category, sub_category in all_categories:
        # Общее количество задач в категории (с кодом)
        total_tasks = db.query(func.count(ContentBlock.id)).join(ContentFile).filter(
            ContentFile.mainCategory == main_category,
            ContentFile.subCategory == sub_category,
            ContentBlock.codeContent.isnot(None)
        ).scalar() or 0

        # Количество решённых задач (solvedCount > 0)
        completed_tasks = db.query(func.count(UserContentProgress.id)).filter(
            UserContentProgress.userId == user_id,
            UserContentProgress.solvedCount > 0
        ).join(ContentBlock).join(ContentFile).filter(
            ContentFile.mainCategory == main_category,
            ContentFile.subCategory == sub_category
        ).scalar() or 0

        # Количество задач, с которыми взаимодействовал пользователь
        attempted_tasks = db.query(func.count(UserContentProgress.id)).filter(
            UserContentProgress.userId == user_id
        ).join(ContentBlock).join(ContentFile).filter(
            ContentFile.mainCategory == main_category,
            ContentFile.subCategory == sub_category
        ).scalar() or 0

        # Рассчитываем процент завершения
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

        # Определяем статус
        status = "not_started"
        if completed_tasks > 0:
            if completion_rate >= 100:
                status = "completed"
            else:
                status = "in_progress"
        elif attempted_tasks > 0:
            status = "in_progress"

        # Добавляем ВСЕ категории (даже если нет задач с кодом)
        category_summaries.append(CategoryProgressSummary(
            mainCategory=main_category,
            subCategory=sub_category,
            totalTasks=total_tasks,
            completedTasks=completed_tasks,
            completionRate=float(completion_rate),
            status=status
        ))

    return category_summaries


async def get_simplified_overall_stats(db: Session, user_id: int):
    """Получает упрощенную общую статистику на основе UserContentProgress"""
    
    # Общее количество доступных задач (исключаем тестовые)
    total_available = db.query(func.count(ContentBlock.id)).join(ContentFile).filter(
        and_(
            ContentFile.mainCategory != 'Test',
            ContentFile.subCategory != 'Test',
            ContentBlock.codeContent.isnot(None)  # Только задачи с кодом
        )
    ).scalar() or 0
    
    # Количество решенных задач пользователем
    total_solved = db.query(func.count(UserContentProgress.id)).filter(
        and_(
            UserContentProgress.userId == user_id,
            UserContentProgress.solvedCount > 0
        )
    ).join(ContentBlock).join(ContentFile).filter(
        and_(
            ContentFile.mainCategory != 'Test',
            ContentFile.subCategory != 'Test'
        )
    ).scalar() or 0
    
    # Рассчитываем процент завершения
    completion_rate = (total_solved / total_available * 100) if total_available > 0 else 0
    
    return SimplifiedOverallStats(
        totalTasksSolved=total_solved,
        totalTasksAvailable=total_available,
        completionRate=float(completion_rate)
    )


async def get_recent_activity(db: Session, user_id: int, limit: int = 10):
    """Получает недавнюю активность с названиями задач"""
    
    # Получаем недавние попытки с информацией о блоках
    recent_attempts = db.query(
        TaskAttempt.id,
        TaskAttempt.blockId,
        TaskAttempt.isSuccessful,
        TaskAttempt.createdAt,
        ContentBlock.blockTitle,
        ContentFile.mainCategory,
        ContentFile.subCategory
    ).join(ContentBlock, TaskAttempt.blockId == ContentBlock.id).join(
        ContentFile, ContentBlock.fileId == ContentFile.id
    ).filter(
        TaskAttempt.userId == user_id
    ).order_by(desc(TaskAttempt.createdAt)).limit(limit).all()
    
    activity_items = []
    for attempt in recent_attempts:
        activity_items.append(RecentActivityItem(
            id=attempt.id,
            blockId=attempt.blockId,
            blockTitle=attempt.blockTitle,
            category=attempt.mainCategory,
            subCategory=attempt.subCategory,
            isSuccessful=attempt.isSuccessful,
            activityType="attempt",
            timestamp=attempt.createdAt
        ))
    
    return activity_items


@router.get("/user/my/detailed", response_model=UserDetailedProgressResponse)
async def get_my_detailed_progress(
    request: Request,
    db: Session = Depends(get_db)
):
    """Получение детального прогресса текущего пользователя"""
    
    current_user = get_current_user_from_session_required(request, db)
    
    user_id = current_user.id
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Получаем упрощенную общую статистику на основе UserContentProgress
    overall_stats = await get_simplified_overall_stats(db, user_id)
    
    # Получаем прогресс по категориям
    category_summaries = await get_unified_category_progress(db, user_id)
    
    # Группируем категории по основным категориям
    grouped_categories = group_categories_by_main(category_summaries)
    
    # Получаем недавнюю активность с названиями задач
    recent_activity = await get_recent_activity(db, user_id, limit=10)
    
    return UserDetailedProgressResponse(
        userId=user_id,
        lastActivityDate=user.lastActivityDate,
        overallStats=overall_stats,
        categoryProgress=category_summaries,
        groupedCategoryProgress=grouped_categories or [],
        recentActivity=recent_activity
    )


@router.get("/user/{user_id}/detailed", response_model=UserDetailedProgressResponse)
async def get_user_detailed_progress(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db)
):
    """Получение детального прогресса пользователя"""
    
    current_user = get_current_user_from_session_required(request, db)
    
    if current_user.role != "ADMIN" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Получаем упрощенную общую статистику на основе UserContentProgress
    overall_stats = await get_simplified_overall_stats(db, user_id)
    
    # Получаем прогресс по категориям
    category_summaries = await get_unified_category_progress(db, user_id)
    
    # Группируем категории по основным категориям
    grouped_categories = group_categories_by_main(category_summaries)
    
    # Получаем недавнюю активность с названиями задач
    recent_activity = await get_recent_activity(db, user_id, limit=10)
    
    return UserDetailedProgressResponse(
        userId=user_id,
        lastActivityDate=user.lastActivityDate,
        overallStats=overall_stats,
        categoryProgress=category_summaries,
        groupedCategoryProgress=grouped_categories or [],
        recentActivity=recent_activity
    )


@router.post("/attempts", response_model=TaskAttemptResponse)
async def record_task_attempt(
    attempt_data: TaskAttemptCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Записать попытку решения задачи с транзакционной безопасностью"""
    
    current_user = get_current_user_from_session_required(request, db)
    
    if current_user.id != attempt_data.userId:
        if current_user.role != "ADMIN":
            raise HTTPException(status_code=403, detail="Can only record attempts for yourself")
    
    try:
        db.begin()
        
        last_attempt = db.query(TaskAttempt).filter(
            and_(TaskAttempt.userId == attempt_data.userId, TaskAttempt.blockId == attempt_data.blockId)
        ).order_by(desc(TaskAttempt.attemptNumber)).with_for_update().first()
        
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
        
        await _update_category_progress(db, attempt_data.userId, attempt_data.blockId, attempt_data.isSuccessful, next_attempt_number)
        
        if attempt_data.isSuccessful:
            await _create_or_update_solution(db, attempt_data, next_attempt_number)
        
        await _update_user_stats(db, attempt_data.userId)
        
        db.commit()
        db.refresh(attempt)
        
        return attempt
        
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Database integrity error: {str(e)}")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to record attempt: {str(e)}")


@router.get("/analytics", response_model=ProgressAnalytics)
async def get_progress_analytics(
    request: Request,
    db: Session = Depends(get_db)
):
    """Получение аналитики по прогрессу (только для админов)"""
    
    current_user = get_current_user_from_session_required(request, db)
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    total_users = db.query(func.count(User.id)).scalar() or 0
    
    thirty_days_ago = datetime.now() - timedelta(days=30)
    active_users = db.query(func.count(User.id)).filter(
        User.lastActivityDate >= thirty_days_ago
    ).scalar() or 0
    
    total_tasks_solved = db.query(func.sum(User.totalTasksSolved)).scalar() or 0
    average_tasks_per_user = (total_tasks_solved / total_users) if total_users > 0 else 0
    
    popular_categories = db.query(
        UserCategoryProgress.mainCategory,
        UserCategoryProgress.subCategory,
        func.sum(UserCategoryProgress.completedTasks).label('total_completed')
    ).group_by(UserCategoryProgress.mainCategory, UserCategoryProgress.subCategory).order_by(
        desc('total_completed')
    ).limit(10).all()
    
    struggling_areas = db.query(
        UserCategoryProgress.mainCategory,
        UserCategoryProgress.subCategory,
        func.avg(UserCategoryProgress.averageAttempts).label('avg_attempts')
    ).group_by(UserCategoryProgress.mainCategory, UserCategoryProgress.subCategory).having(
        func.avg(UserCategoryProgress.averageAttempts) > 3
    ).order_by(desc('avg_attempts')).limit(10).all()
    
    return ProgressAnalytics(
        totalUsers=total_users,
        activeUsers=active_users,
        totalTasksSolved=total_tasks_solved,
        averageTasksPerUser=average_tasks_per_user,
        mostPopularCategories=[{"mainCategory": main_cat, "subCategory": sub_cat, "completed": completed} for main_cat, sub_cat, completed in popular_categories],
        strugglingAreas=[{"mainCategory": main_cat, "subCategory": sub_cat, "averageAttempts": float(avg_attempts)} for main_cat, sub_cat, avg_attempts in struggling_areas]
    )


async def _create_or_update_solution(db: Session, attempt_data: TaskAttemptCreate, attempt_number: int):
    """Создает или обновляет решение задачи и синхронизирует с UserContentProgress"""
    
    existing_solution = db.query(TaskSolution).filter(
        and_(TaskSolution.userId == attempt_data.userId, TaskSolution.blockId == attempt_data.blockId)
    ).with_for_update().first()
    
    if existing_solution:
        if attempt_number < existing_solution.totalAttempts:
            existing_solution.finalCode = attempt_data.sourceCode
            existing_solution.language = attempt_data.language
            existing_solution.totalAttempts = attempt_number
            existing_solution.solvedAt = datetime.now()
            existing_solution.timeToSolveMinutes = attempt_data.durationMinutes or 0
    else:
        solution = TaskSolution(
            id=str(uuid.uuid4()),
            userId=attempt_data.userId,
            blockId=attempt_data.blockId,
            finalCode=attempt_data.sourceCode,
            language=attempt_data.language,
            totalAttempts=attempt_number,
            timeToSolveMinutes=attempt_data.durationMinutes or 0,
            firstAttempt=datetime.now(),
            solvedAt=datetime.now()
        )
        db.add(solution)
        
        # ИСПРАВЛЕНИЕ: автоматически обновляем UserContentProgress при решении задачи
        await _sync_user_content_progress_with_solution(db, attempt_data.userId, attempt_data.blockId)


async def _sync_user_content_progress_with_solution(db: Session, user_id: int, block_id: str):
    """Синхронизирует UserContentProgress с созданием TaskSolution"""
    
    # Проверяем, есть ли уже запись UserContentProgress
    progress = db.query(UserContentProgress).filter(
        and_(
            UserContentProgress.userId == user_id,
            UserContentProgress.blockId == block_id
        )
    ).first()
    
    if progress:
        # Если solvedCount = 0, устанавливаем его в 1 (задача решена через CodeEditor)
        if progress.solvedCount == 0:
            progress.solvedCount = 1
    else:
        # Создаем новую запись с solvedCount = 1
        progress = UserContentProgress(
            id=str(uuid.uuid4()),
            userId=user_id,
            blockId=block_id,
            solvedCount=1
        )
        db.add(progress)


async def _update_user_stats(db: Session, user_id: int):
    """Обновляет общую статистику пользователя на основе UserContentProgress"""
    
    user = db.query(User).filter(User.id == user_id).with_for_update().first()
    if user:    
        # ИСПРАВЛЕНИЕ: используем UserContentProgress для единообразия
        total_solved = db.query(func.count(UserContentProgress.id)).filter(
            and_(
                UserContentProgress.userId == user_id,
                UserContentProgress.solvedCount > 0
            )
        ).join(ContentBlock).join(ContentFile).filter(
            and_(
                ContentFile.mainCategory != 'Test',
                ContentFile.subCategory != 'Test'
            )
        ).scalar() or 0
        
        user.totalTasksSolved = total_solved
        user.lastActivityDate = datetime.now()


async def _update_category_progress(db: Session, user_id: int, block_id: str, is_successful: bool, attempt_number: int):
    """Обновляет прогресс пользователя по категории"""
    
    block = db.query(ContentBlock).options(joinedload(ContentBlock.file)).filter(ContentBlock.id == block_id).first()
    if not block or not block.file:
        return
    
    main_category = block.file.mainCategory
    sub_category = block.file.subCategory
    
    progress = db.query(UserCategoryProgress).filter(
        and_(
            UserCategoryProgress.userId == user_id, 
            UserCategoryProgress.mainCategory == main_category,
            UserCategoryProgress.subCategory == sub_category
        )
    ).with_for_update().first()
    
    if not progress:
        total_tasks = db.query(func.count(ContentBlock.id)).join(ContentFile).filter(
            and_(
                ContentFile.mainCategory == main_category,
                ContentFile.subCategory == sub_category,
                ContentBlock.codeContent.isnot(None)
            )
        ).scalar() or 0
        
        has_solved_this_task = db.query(TaskSolution).filter(
            and_(TaskSolution.userId == user_id, TaskSolution.blockId == block_id)
        ).first() is not None
        
        progress = UserCategoryProgress(
            id=str(uuid.uuid4()),
            userId=user_id,
            mainCategory=main_category,
            subCategory=sub_category,
            totalTasks=total_tasks,
            firstAttempt=datetime.now(),
            attemptedTasks=1,
            completedTasks=1 if (is_successful and not has_solved_this_task) else 0
        )
        db.add(progress)
        
    else:
        
        previous_attempts_count = db.query(func.count(TaskAttempt.id)).filter(
            and_(TaskAttempt.userId == user_id, TaskAttempt.blockId == block_id)
        ).scalar() or 0
        
        if previous_attempts_count == 1:
            progress.attemptedTasks += 1
        
        if is_successful:
            has_solved_before = db.query(TaskSolution).filter(
                and_(TaskSolution.userId == user_id, TaskSolution.blockId == block_id)
            ).first() is not None
            
            if not has_solved_before:
                progress.completedTasks += 1
    
    progress
    if progress.attemptedTasks > 0:
        all_attempts = db.query(TaskAttempt).join(ContentBlock).join(ContentFile).filter(
            and_(
                TaskAttempt.userId == user_id,
                ContentFile.mainCategory == main_category,
                ContentFile.subCategory == sub_category
            )
        ).all()
        
        if all_attempts:
            task_attempts = {}
            for attempt in all_attempts:
                task_id = attempt.blockId
                if task_id not in task_attempts:
                    task_attempts[task_id] = 0
                task_attempts[task_id] += 1
            
            total_task_attempts = sum(task_attempts.values())
            unique_tasks_attempted = len(task_attempts.keys())
            progress.averageAttempts = total_task_attempts / unique_tasks_attempted if unique_tasks_attempted > 0 else 1.0
            
            progress.successRate = float(progress.completedTasks) / float(progress.attemptedTasks) * 100
            
            total_time = sum([a.durationMinutes for a in all_attempts if a.durationMinutes]) or 0
            progress.totalTimeSpentMinutes = total_time


def group_categories_by_main(category_summaries: List[CategoryProgressSummary]) -> List[GroupedCategoryProgress]:
    grouped = {}
    for category in category_summaries:
        main_category = category.mainCategory
        if main_category not in grouped:
            grouped[main_category] = {
                'mainCategory': main_category,
                'totalTasks': 0,
                'completedTasks': 0,
                'subCategories': []
            }
        grouped[main_category]['subCategories'].append(SubCategoryProgress(
            subCategory=category.subCategory or 'Общие',
            totalTasks=category.totalTasks,
            completedTasks=category.completedTasks,
            completionRate=category.completionRate,
            status=category.status
        ))
        grouped[main_category]['totalTasks'] += category.totalTasks
        grouped[main_category]['completedTasks'] += category.completedTasks
    result = []
    for main_category, data in grouped.items():
        total_tasks = data['totalTasks']
        completed_tasks = data['completedTasks']
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        status = "not_started"
        if completed_tasks > 0:
            if completion_rate >= 100:
                status = "completed"
            else:
                status = "in_progress"
        result.append(GroupedCategoryProgress(
            mainCategory=main_category,
            totalTasks=total_tasks,
            completedTasks=completed_tasks,
            completionRate=float(completion_rate),
            status=status,
            subCategories=data['subCategories']
        ))
    result.sort(key=lambda x: x.mainCategory)
    return result


@router.get("/health")
async def health_check():
    return {"status": "ok"} 