import uuid
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import and_, desc, func
from sqlalchemy.orm import Session, joinedload

from ..auth import get_current_user_from_session_required
from ..database import get_db
from ..models import (
    ContentBlock,
    ContentFile,
    TaskAttempt,
    TaskSolution,
    User,
    UserCategoryProgress,
    UserPathProgress,
)
from ..schemas import (
    TaskAttemptCreate,
    TaskAttemptResponse,
    UserDetailedProgressResponse,
    CategoryProgressSummary,
    ProgressAnalytics
)

router = APIRouter(prefix="/api/progress", tags=["Progress"])


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
    
    total_attempts = db.query(func.count(TaskAttempt.id)).filter(TaskAttempt.userId == user_id).scalar() or 0
    successful_attempts = db.query(func.count(TaskAttempt.id)).filter(
        and_(TaskAttempt.userId == user_id, TaskAttempt.isSuccessful == True)
    ).scalar() or 0
    
    overall_stats = {
        "totalAttempts": total_attempts,
        "successfulAttempts": successful_attempts,
        "successRate": (successful_attempts / total_attempts * 100) if total_attempts > 0 else 0,
        "totalTimeSpent": db.query(func.sum(TaskAttempt.durationMinutes)).filter(TaskAttempt.userId == user_id).scalar() or 0
    }
    
    category_progress = db.query(UserCategoryProgress).filter(
        UserCategoryProgress.userId == user_id
    ).all()
    
    category_summaries = []
    for progress in category_progress:
        completion_rate = (progress.completedTasks / progress.totalTasks * 100) if progress.totalTasks > 0 else 0
        
        status = "not_started"
        if progress.attemptedTasks > 0:
            if completion_rate >= 90:
                status = "completed"
            elif progress.averageAttempts > 3:
                status = "struggling"
            else:
                status = "in_progress"
        
        category_summaries.append(CategoryProgressSummary(
            mainCategory=progress.mainCategory,
            subCategory=progress.subCategory,
            totalTasks=progress.totalTasks,
            completedTasks=progress.completedTasks,
            attemptedTasks=progress.attemptedTasks,
            completionRate=float(completion_rate),
            averageAttempts=float(progress.averageAttempts),
            totalTimeSpent=progress.totalTimeSpentMinutes,
            lastActivity=progress.lastActivity,
            status=status
        ))
    
    recent_attempts = db.query(TaskAttempt).filter(
        TaskAttempt.userId == user_id
    ).order_by(desc(TaskAttempt.createdAt)).limit(10).all()
    
    recent_solutions = db.query(TaskSolution).filter(
        TaskSolution.userId == user_id
    ).order_by(desc(TaskSolution.solvedAt)).limit(10).all()
    
    learning_paths = db.query(UserPathProgress).filter(
        UserPathProgress.userId == user_id
    ).options(joinedload(UserPathProgress.path)).all()
    
    return UserDetailedProgressResponse(
        userId=user_id,
        totalTasksSolved=user.totalTasksSolved or 0,
        lastActivityDate=user.lastActivityDate,
        overallStats=overall_stats,
        categoryProgress=category_summaries,
        recentAttempts=recent_attempts,
        recentSolutions=recent_solutions,
        learningPaths=learning_paths
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
    
    total_attempts = db.query(func.count(TaskAttempt.id)).filter(TaskAttempt.userId == user_id).scalar() or 0
    successful_attempts = db.query(func.count(TaskAttempt.id)).filter(
        and_(TaskAttempt.userId == user_id, TaskAttempt.isSuccessful == True)
    ).scalar() or 0
    
    overall_stats = {
        "totalAttempts": total_attempts,
        "successfulAttempts": successful_attempts,
        "successRate": (successful_attempts / total_attempts * 100) if total_attempts > 0 else 0,
        "totalTimeSpent": db.query(func.sum(TaskAttempt.durationMinutes)).filter(TaskAttempt.userId == user_id).scalar() or 0
    }
    
    category_progress = db.query(UserCategoryProgress).filter(
        UserCategoryProgress.userId == user_id
    ).all()
    
    category_summaries = []
    for progress in category_progress:
        completion_rate = (progress.completedTasks / progress.totalTasks * 100) if progress.totalTasks > 0 else 0
        
        status = "not_started"
        if progress.attemptedTasks > 0:
            if completion_rate >= 90:
                status = "completed"
            elif progress.averageAttempts > 3:
                status = "struggling"
            else:
                status = "in_progress"
        
        category_summaries.append(CategoryProgressSummary(
            mainCategory=progress.mainCategory,
            subCategory=progress.subCategory,
            totalTasks=progress.totalTasks,
            completedTasks=progress.completedTasks,
            attemptedTasks=progress.attemptedTasks,
            completionRate=float(completion_rate),
            averageAttempts=float(progress.averageAttempts),
            totalTimeSpent=progress.totalTimeSpentMinutes,
            lastActivity=progress.lastActivity,
            status=status
        ))
    
    recent_attempts = db.query(TaskAttempt).filter(
        TaskAttempt.userId == user_id
    ).order_by(desc(TaskAttempt.createdAt)).limit(10).all()
    
    recent_solutions = db.query(TaskSolution).filter(
        TaskSolution.userId == user_id
    ).order_by(desc(TaskSolution.solvedAt)).limit(10).all()
    
    learning_paths = db.query(UserPathProgress).filter(
        UserPathProgress.userId == user_id
    ).options(joinedload(UserPathProgress.path)).all()
    
    return UserDetailedProgressResponse(
        userId=user_id,
        totalTasksSolved=user.totalTasksSolved or 0,
        lastActivityDate=user.lastActivityDate,
        overallStats=overall_stats,
        categoryProgress=category_summaries,
        recentAttempts=recent_attempts,
        recentSolutions=recent_solutions,
        learningPaths=learning_paths
    )


@router.post("/attempts", response_model=TaskAttemptResponse)
async def record_task_attempt(
    attempt_data: TaskAttemptCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Записать попытку решения задачи"""
    
    current_user = get_current_user_from_session_required(request, db)
    
    if current_user.id != attempt_data.userId:
        if current_user.role != "ADMIN":
            raise HTTPException(status_code=403, detail="Can only record attempts for yourself")
    
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
    
    if attempt_data.isSuccessful:
        await _create_or_update_solution(db, attempt_data, next_attempt_number)
        await _update_user_stats(db, attempt_data.userId)
    else:
        await _update_user_stats(db, attempt_data.userId)
    
    await _update_category_progress(db, attempt_data.userId, attempt_data.blockId, attempt_data.isSuccessful)
    
    db.commit()
    db.refresh(attempt)
    
    return attempt


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
    """Создает или обновляет решение задачи"""
    
    existing_solution = db.query(TaskSolution).filter(
        and_(TaskSolution.userId == attempt_data.userId, TaskSolution.blockId == attempt_data.blockId)
    ).first()
    
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
            firstAttempt=datetime.now()
        )
        db.add(solution)


async def _update_user_stats(db: Session, user_id: int):
    """Обновляет общую статистику пользователя"""
    
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        total_solved = db.query(func.count(TaskSolution.id)).filter(TaskSolution.userId == user_id).scalar() or 0
        
        user.totalTasksSolved = total_solved
        user.lastActivityDate = datetime.now()


async def _update_category_progress(db: Session, user_id: int, block_id: str, is_successful: bool):
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
    ).first()
    
    if not progress:
        total_tasks = db.query(func.count(ContentBlock.id)).join(ContentFile).filter(
            and_(
                ContentFile.mainCategory == main_category,
                ContentFile.subCategory == sub_category
            )
        ).scalar() or 0
        
        progress = UserCategoryProgress(
            id=str(uuid.uuid4()),
            userId=user_id,
            mainCategory=main_category,
            subCategory=sub_category,
            totalTasks=total_tasks,
            firstAttempt=datetime.now(),
            attemptedTasks=1,
            completedTasks=1 if is_successful else 0
        )
        db.add(progress)
    else:
        existing_attempts = db.query(func.count(TaskAttempt.id)).filter(
            and_(TaskAttempt.userId == user_id, TaskAttempt.blockId == block_id)
        ).scalar() or 0
        
        if existing_attempts == 1:
            progress.attemptedTasks += 1
            if is_successful:
                progress.completedTasks += 1
    
    progress.lastActivity = datetime.now()
    
    if progress.attemptedTasks > 0:
        progress.averageAttempts = 1.0
        progress.successRate = float(progress.completedTasks) / float(progress.attemptedTasks) * 100


@router.get("/health")
async def health_check():
    return {"status": "ok"} 