from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal
from sqlalchemy import desc, func, and_
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError

from app.domain.repositories.progress_repository import ProgressRepository
from app.domain.entities.progress import (
    TaskAttempt, 
    TaskSolution, 
    UserCategoryProgress, 
    LearningPath, 
    UserPathProgress,
    TestCase,
    TestValidationResult
)
from ..models import (
    TaskAttempt as TaskAttemptModel,
    TaskSolution as TaskSolutionModel,
    UserCategoryProgress as UserCategoryProgressModel,
    LearningPath as LearningPathModel,
    UserPathProgress as UserPathProgressModel,
    TestCase as TestCaseModel,
    TestValidationResult as TestValidationResultModel,
    ContentBlock,
    ContentFile,
    UserContentProgress,
    User
)


class SQLAlchemyProgressRepository(ProgressRepository):
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def _task_attempt_to_entity(self, model: TaskAttemptModel) -> TaskAttempt:
        return TaskAttempt(
            id=model.id,
            userId=model.userId,
            blockId=model.blockId,
            sourceCode=model.sourceCode,
            language=model.language,
            isSuccessful=model.isSuccessful,
            attemptNumber=model.attemptNumber,
            createdAt=model.createdAt,
            executionTimeMs=model.executionTimeMs,
            memoryUsedMB=model.memoryUsedMB,
            errorMessage=model.errorMessage,
            stderr=model.stderr,
            durationMinutes=model.durationMinutes
        )

    def _task_solution_to_entity(self, model: TaskSolutionModel) -> TaskSolution:
        return TaskSolution(
            id=model.id,
            userId=model.userId,
            blockId=model.blockId,
            finalCode=model.finalCode,
            language=model.language,
            totalAttempts=model.totalAttempts,
            timeToSolveMinutes=model.timeToSolveMinutes,
            firstAttempt=model.firstAttempt,
            solvedAt=model.solvedAt,
            createdAt=model.createdAt,
            updatedAt=model.updatedAt
        )

    def _category_progress_to_entity(self, model: UserCategoryProgressModel) -> UserCategoryProgress:
        return UserCategoryProgress(
            id=model.id,
            userId=model.userId,
            mainCategory=model.mainCategory,
            subCategory=model.subCategory,
            totalTasks=model.totalTasks,
            completedTasks=model.completedTasks,
            attemptedTasks=model.attemptedTasks,
            averageAttempts=model.averageAttempts,
            totalTimeSpentMinutes=model.totalTimeSpentMinutes,
            successRate=model.successRate,
            firstAttempt=model.firstAttempt,
            lastActivity=model.lastActivity,
            createdAt=model.createdAt,
            updatedAt=model.updatedAt
        )

    # TaskAttempt methods
    async def create_task_attempt(self, attempt: TaskAttempt) -> TaskAttempt:
        db_attempt = TaskAttemptModel(
            id=attempt.id,
            userId=attempt.userId,
            blockId=attempt.blockId,
            sourceCode=attempt.sourceCode,
            language=attempt.language,
            isSuccessful=attempt.isSuccessful,
            attemptNumber=attempt.attemptNumber,
            executionTimeMs=attempt.executionTimeMs,
            memoryUsedMB=attempt.memoryUsedMB,
            errorMessage=attempt.errorMessage,
            stderr=attempt.stderr,
            durationMinutes=attempt.durationMinutes
        )
        self.db_session.add(db_attempt)
        self.db_session.commit()
        self.db_session.refresh(db_attempt)
        return self._task_attempt_to_entity(db_attempt)

    async def get_task_attempt_by_id(self, attempt_id: str) -> Optional[TaskAttempt]:
        db_attempt = self.db_session.query(TaskAttemptModel).filter(TaskAttemptModel.id == attempt_id).first()
        return self._task_attempt_to_entity(db_attempt) if db_attempt else None

    async def get_task_attempts_by_user_and_block(self, user_id: int, block_id: str) -> List[TaskAttempt]:
        db_attempts = self.db_session.query(TaskAttemptModel).filter(
            TaskAttemptModel.userId == user_id,
            TaskAttemptModel.blockId == block_id
        ).order_by(desc(TaskAttemptModel.createdAt)).all()
        return [self._task_attempt_to_entity(attempt) for attempt in db_attempts]

    async def get_recent_task_attempts(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        recent_attempts = self.db_session.query(
            TaskAttemptModel.id,
            TaskAttemptModel.blockId,
            TaskAttemptModel.isSuccessful,
            TaskAttemptModel.createdAt,
            ContentBlock.blockTitle,
            ContentFile.mainCategory,
            ContentFile.subCategory
        ).join(ContentBlock, TaskAttemptModel.blockId == ContentBlock.id).join(
            ContentFile, ContentBlock.fileId == ContentFile.id
        ).filter(
            TaskAttemptModel.userId == user_id
        ).order_by(desc(TaskAttemptModel.createdAt)).limit(limit).all()
        
        return [
            {
                "id": attempt.id,
                "blockId": attempt.blockId,
                "blockTitle": attempt.blockTitle,
                "category": attempt.mainCategory,
                "subCategory": attempt.subCategory,
                "isSuccessful": attempt.isSuccessful,
                "activityType": "attempt",
                "timestamp": attempt.createdAt
            }
            for attempt in recent_attempts
        ]

    async def get_next_attempt_number(self, user_id: int, block_id: str) -> int:
        max_attempt = self.db_session.query(func.max(TaskAttemptModel.attemptNumber)).filter(
            TaskAttemptModel.userId == user_id,
            TaskAttemptModel.blockId == block_id
        ).scalar()
        return (max_attempt or 0) + 1

    # TaskSolution methods
    async def create_task_solution(self, solution: TaskSolution) -> TaskSolution:
        db_solution = TaskSolutionModel(
            id=solution.id,
            userId=solution.userId,
            blockId=solution.blockId,
            finalCode=solution.finalCode,
            language=solution.language,
            totalAttempts=solution.totalAttempts,
            timeToSolveMinutes=solution.timeToSolveMinutes,
            firstAttempt=solution.firstAttempt,
            solvedAt=solution.solvedAt
        )
        self.db_session.add(db_solution)
        self.db_session.commit()
        self.db_session.refresh(db_solution)
        return self._task_solution_to_entity(db_solution)

    async def update_task_solution(self, solution: TaskSolution) -> TaskSolution:
        db_solution = self.db_session.query(TaskSolutionModel).filter(TaskSolutionModel.id == solution.id).first()
        if db_solution:
            db_solution.finalCode = solution.finalCode
            db_solution.language = solution.language
            db_solution.totalAttempts = solution.totalAttempts
            db_solution.timeToSolveMinutes = solution.timeToSolveMinutes
            db_solution.solvedAt = solution.solvedAt
            self.db_session.commit()
            self.db_session.refresh(db_solution)
            return self._task_solution_to_entity(db_solution)
        raise ValueError(f"TaskSolution with id {solution.id} not found")

    async def get_task_solution_by_user_and_block(self, user_id: int, block_id: str) -> Optional[TaskSolution]:
        db_solution = self.db_session.query(TaskSolutionModel).filter(
            TaskSolutionModel.userId == user_id,
            TaskSolutionModel.blockId == block_id
        ).first()
        return self._task_solution_to_entity(db_solution) if db_solution else None

    # UserCategoryProgress methods
    async def create_category_progress(self, progress: UserCategoryProgress) -> UserCategoryProgress:
        db_progress = UserCategoryProgressModel(
            id=progress.id,
            userId=progress.userId,
            mainCategory=progress.mainCategory,
            subCategory=progress.subCategory,
            totalTasks=progress.totalTasks,
            completedTasks=progress.completedTasks,
            attemptedTasks=progress.attemptedTasks,
            averageAttempts=progress.averageAttempts,
            totalTimeSpentMinutes=progress.totalTimeSpentMinutes,
            successRate=progress.successRate,
            firstAttempt=progress.firstAttempt,
            lastActivity=progress.lastActivity
        )
        self.db_session.add(db_progress)
        self.db_session.commit()
        self.db_session.refresh(db_progress)
        return self._category_progress_to_entity(db_progress)

    async def update_category_progress(self, progress: UserCategoryProgress) -> UserCategoryProgress:
        db_progress = self.db_session.query(UserCategoryProgressModel).filter(
            UserCategoryProgressModel.id == progress.id
        ).first()
        if db_progress:
            db_progress.totalTasks = progress.totalTasks
            db_progress.completedTasks = progress.completedTasks
            db_progress.attemptedTasks = progress.attemptedTasks
            db_progress.averageAttempts = progress.averageAttempts
            db_progress.totalTimeSpentMinutes = progress.totalTimeSpentMinutes
            db_progress.successRate = progress.successRate
            db_progress.lastActivity = progress.lastActivity
            self.db_session.commit()
            self.db_session.refresh(db_progress)
            return self._category_progress_to_entity(db_progress)
        raise ValueError(f"UserCategoryProgress with id {progress.id} not found")

    async def get_category_progress_by_user_and_category(self, user_id: int, main_category: str, sub_category: Optional[str] = None) -> Optional[UserCategoryProgress]:
        query = self.db_session.query(UserCategoryProgressModel).filter(
            UserCategoryProgressModel.userId == user_id,
            UserCategoryProgressModel.mainCategory == main_category
        )
        if sub_category:
            query = query.filter(UserCategoryProgressModel.subCategory == sub_category)
        
        db_progress = query.first()
        return self._category_progress_to_entity(db_progress) if db_progress else None

    async def get_unified_category_progress(self, user_id: int) -> List[Dict[str, Any]]:
        # Получаем все уникальные пары (mainCategory, subCategory) из ContentFile
        all_categories = self.db_session.query(
            ContentFile.mainCategory,
            ContentFile.subCategory
        ).filter(
            ContentFile.mainCategory != 'Test',
            ContentFile.subCategory != 'Test'
        ).distinct().all()

        category_summaries = []

        for main_category, sub_category in all_categories:
            # Общее количество задач в категории (с кодом)
            total_tasks = self.db_session.query(func.count(ContentBlock.id)).join(
                ContentFile, ContentBlock.fileId == ContentFile.id
            ).filter(
                ContentFile.mainCategory == main_category,
                ContentFile.subCategory == sub_category,
                ContentBlock.codeContent.isnot(None)
            ).scalar() or 0

            # Количество решённых задач (solvedCount > 0) - ТОЛЬКО задачи с кодом
            completed_tasks = self.db_session.query(func.count(UserContentProgress.id)).filter(
                UserContentProgress.userId == user_id,
                UserContentProgress.solvedCount > 0
            ).join(
                ContentBlock, UserContentProgress.blockId == ContentBlock.id
            ).join(
                ContentFile, ContentBlock.fileId == ContentFile.id
            ).filter(
                ContentFile.mainCategory == main_category,
                ContentFile.subCategory == sub_category,
                ContentBlock.codeContent.isnot(None)
            ).scalar() or 0

            # Количество задач, с которыми взаимодействовал пользователь
            attempted_tasks = self.db_session.query(func.count(UserContentProgress.id)).filter(
                UserContentProgress.userId == user_id
            ).join(
                ContentBlock, UserContentProgress.blockId == ContentBlock.id
            ).join(
                ContentFile, ContentBlock.fileId == ContentFile.id
            ).filter(
                ContentFile.mainCategory == main_category,
                ContentFile.subCategory == sub_category,
                ContentBlock.codeContent.isnot(None)
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

            category_summaries.append({
                "mainCategory": main_category,
                "subCategory": sub_category,
                "totalTasks": total_tasks,
                "completedTasks": completed_tasks,
                "completionRate": float(completion_rate),
                "status": status
            })

        return category_summaries

    # LearningPath methods (простые заглушки для полноты)
    async def create_learning_path(self, path: LearningPath) -> LearningPath:
        # Заглушка - LearningPath пока не используется активно
        return path

    async def get_learning_path_by_id(self, path_id: str) -> Optional[LearningPath]:
        return None

    async def get_active_learning_paths(self) -> List[LearningPath]:
        return []

    # UserPathProgress methods (простые заглушки)
    async def create_path_progress(self, progress: UserPathProgress) -> UserPathProgress:
        return progress

    async def update_path_progress(self, progress: UserPathProgress) -> UserPathProgress:
        return progress

    async def get_path_progress_by_user_and_path(self, user_id: int, path_id: str) -> Optional[UserPathProgress]:
        return None

    # TestCase methods (простые заглушки)
    async def create_test_case(self, test_case: TestCase) -> TestCase:
        return test_case

    async def get_test_cases_by_block_id(self, block_id: str) -> List[TestCase]:
        return []

    async def get_public_test_cases_by_block_id(self, block_id: str) -> List[TestCase]:
        return []

    # TestValidationResult methods (простые заглушки)
    async def create_test_validation_result(self, result: TestValidationResult) -> TestValidationResult:
        return result

    async def get_test_validation_results_by_attempt_id(self, attempt_id: str) -> List[TestValidationResult]:
        return []

    # Analytics methods
    async def get_overall_stats(self, user_id: int) -> Dict[str, Any]:
        # Общее количество доступных задач (исключаем тестовые)
        total_available = self.db_session.query(func.count(ContentBlock.id)).join(
            ContentFile, ContentBlock.fileId == ContentFile.id
        ).filter(
            and_(
                ContentFile.mainCategory != 'Test',
                ContentFile.subCategory != 'Test',
                ContentBlock.codeContent.isnot(None)
            )
        ).scalar() or 0
        
        # Количество решенных задач пользователем
        total_solved = self.db_session.query(func.count(UserContentProgress.id)).filter(
            and_(
                UserContentProgress.userId == user_id,
                UserContentProgress.solvedCount > 0
            )
        ).join(
            ContentBlock, UserContentProgress.blockId == ContentBlock.id
        ).join(
            ContentFile, ContentBlock.fileId == ContentFile.id
        ).filter(
            and_(
                ContentFile.mainCategory != 'Test',
                ContentFile.subCategory != 'Test',
                ContentBlock.codeContent.isnot(None)
            )
        ).scalar() or 0
        
        # Рассчитываем процент завершения
        completion_rate = (total_solved / total_available * 100) if total_available > 0 else 0
        
        return {
            "totalTasksSolved": total_solved,
            "totalTasksAvailable": total_available,
            "completionRate": float(completion_rate)
        }

    async def get_progress_analytics(self) -> Dict[str, Any]:
        # Общая аналитика по всем пользователям
        total_users = self.db_session.query(func.count(User.id)).scalar() or 0
        
        # Активные пользователи (с хотя бы одним решением)
        active_users = self.db_session.query(func.count(User.id.distinct())).join(
            UserContentProgress, User.id == UserContentProgress.userId
        ).filter(UserContentProgress.solvedCount > 0).scalar() or 0
        
        # Общее количество решенных задач
        total_solved = self.db_session.query(func.sum(UserContentProgress.solvedCount)).scalar() or 0
        
        # Средние задачи на пользователя
        avg_tasks = float(total_solved / total_users) if total_users > 0 else 0
        
        # Популярные категории с правильными JOIN
        popular_categories = self.db_session.query(
            ContentFile.mainCategory,
            func.count(UserContentProgress.id).label('count')
        ).join(
            ContentBlock, ContentFile.id == ContentBlock.fileId
        ).join(
            UserContentProgress, ContentBlock.id == UserContentProgress.blockId
        ).filter(
            UserContentProgress.solvedCount > 0
        ).group_by(ContentFile.mainCategory).order_by(desc('count')).limit(5).all()
        
        return {
            "totalUsers": total_users,
            "activeUsers": active_users,
            "totalTasksSolved": total_solved,
            "averageTasksPerUser": avg_tasks,
            "mostPopularCategories": [
                {"category": cat, "count": count} for cat, count in popular_categories
            ],
            "strugglingAreas": []  # Заглушка
        }

    async def sync_user_content_progress(self, user_id: int, block_id: str) -> None:
        # Синхронизация прогресса с решениями
        solution = self.db_session.query(TaskSolutionModel).filter(
            TaskSolutionModel.userId == user_id,
            TaskSolutionModel.blockId == block_id
        ).first()
        
        if solution:
            progress = self.db_session.query(UserContentProgress).filter(
                UserContentProgress.userId == user_id,
                UserContentProgress.blockId == block_id
            ).first()
            
            if not progress:
                progress = UserContentProgress(
                    userId=user_id,
                    blockId=block_id,
                    solvedCount=1
                )
                self.db_session.add(progress)
            else:
                progress.solvedCount = max(progress.solvedCount, 1)
            
            self.db_session.commit()

    async def update_user_stats(self, user_id: int) -> None:
        # Обновляем общую статистику пользователя
        total_solved = self.db_session.query(func.sum(UserContentProgress.solvedCount)).filter(
            UserContentProgress.userId == user_id
        ).scalar() or 0
        
        user = self.db_session.query(User).filter(User.id == user_id).first()
        if user:
            user.totalTasksSolved = total_solved
            user.lastActivityDate = datetime.now()
            self.db_session.commit() 