import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal

from app.domain.repositories.progress_repository import ProgressRepository
from app.domain.entities.progress_types import TaskAttempt, TaskSolution
from app.domain.entities.progress_types import UserCategoryProgress
from app.application.dto.progress_dto import (
    TaskAttemptCreateDTO, 
    TaskAttemptResponseDTO,
    UserDetailedProgressResponseDTO,
    SimplifiedOverallStatsDTO,
    CategoryProgressSummaryDTO,
    RecentActivityItemDTO,
    GroupedCategoryProgressDTO,
    SubCategoryProgressDTO,
    ProgressAnalyticsDTO
)


class ProgressService:
    def __init__(self, progress_repository: ProgressRepository):
        self.progress_repository = progress_repository

    async def create_task_attempt(self, attempt_data: TaskAttemptCreateDTO) -> TaskAttemptResponseDTO:
        """Создание попытки решения задачи"""
        
        # Получаем номер попытки
        attempt_number = await self.progress_repository.get_next_attempt_number(
            attempt_data.userId, 
            attempt_data.blockId
        )
        
        # Создаем entity
        attempt = TaskAttempt(
            id=str(uuid.uuid4()),
            userId=attempt_data.userId,
            taskId=attempt_data.blockId,  # blockId -> taskId
            code=attempt_data.sourceCode,  # sourceCode -> code
            languageId=attempt_data.language,  # language -> languageId
            result="success" if attempt_data.isSuccessful else "failed",  # isSuccessful -> result
            error=attempt_data.errorMessage,  # errorMessage -> error
            executionTime=attempt_data.executionTimeMs,  # executionTimeMs -> executionTime
            memory=attempt_data.memoryUsedMB,  # memoryUsedMB -> memory
            createdAt=datetime.now(),
            updatedAt=datetime.now()
        )
        
        # Сохраняем попытку
        created_attempt = await self.progress_repository.create_task_attempt(attempt)
        
        # Если попытка успешна, создаем или обновляем решение
        if attempt_data.isSuccessful:
            await self._create_or_update_solution(attempt_data, attempt_number)
            
            # Синхронизируем прогресс пользователя
            await self.progress_repository.sync_user_content_progress(
                attempt_data.userId, 
                attempt_data.blockId
            )
            
            # Обновляем общую статистику пользователя
            await self.progress_repository.update_user_stats(attempt_data.userId)
            
            # Обновляем прогресс по категориям
            await self._update_category_progress(
                attempt_data.userId, 
                attempt_data.blockId, 
                attempt_data.isSuccessful, 
                attempt_number
            )
        
        return TaskAttemptResponseDTO(
            id=created_attempt.id,
            userId=created_attempt.userId,
            blockId=created_attempt.taskId,  # taskId -> blockId для DTO
            sourceCode=created_attempt.code,  # code -> sourceCode для DTO
            language=created_attempt.languageId,  # languageId -> language для DTO
            isSuccessful=created_attempt.result == "success",  # result -> isSuccessful для DTO
            attemptNumber=1,  # Значение по умолчанию
            createdAt=created_attempt.createdAt,
            executionTimeMs=created_attempt.executionTime,  # executionTime -> executionTimeMs для DTO
            memoryUsedMB=created_attempt.memory,  # memory -> memoryUsedMB для DTO
            errorMessage=created_attempt.error,  # error -> errorMessage для DTO
            stderr=None,  # Не используется в новой модели
            durationMinutes=None  # Не используется в новой модели
        )

    async def get_user_detailed_progress(self, user_id: int) -> UserDetailedProgressResponseDTO:
        """Получение детального прогресса пользователя"""
        
        # Общая статистика
        overall_stats_data = await self.progress_repository.get_overall_stats(user_id)
        overall_stats = SimplifiedOverallStatsDTO(
            totalTasksSolved=overall_stats_data["totalTasksSolved"],
            totalTasksAvailable=overall_stats_data["totalTasksAvailable"],
            completionRate=overall_stats_data["completionRate"]
        )
        
        # Прогресс по категориям
        category_progress_data = await self.progress_repository.get_unified_category_progress(user_id)
        category_summaries = [
            CategoryProgressSummaryDTO(
                mainCategory=cat["mainCategory"],
                subCategory=cat["subCategory"],
                totalTasks=cat["totalTasks"],
                completedTasks=cat["completedTasks"],
                completionRate=cat["completionRate"],
                status=cat["status"]
            )
            for cat in category_progress_data
        ]
        
        # Группировка по основным категориям
        grouped_categories = self._group_categories_by_main(category_summaries)
        
        # Недавняя активность
        recent_activity_data = await self.progress_repository.get_recent_task_attempts(user_id, 10)
        recent_activity = [
            RecentActivityItemDTO(
                id=activity["id"],
                blockId=activity["blockId"],
                blockTitle=activity["blockTitle"],
                category=activity["category"],
                subCategory=activity["subCategory"],
                isSuccessful=activity["isSuccessful"],
                activityType=activity["activityType"],
                timestamp=activity["timestamp"]
            )
            for activity in recent_activity_data
        ]
        
        return UserDetailedProgressResponseDTO(
            userId=user_id,
            lastActivityDate=None,  # Можно добавить позже
            overallStats=overall_stats,
            categoryProgress=category_summaries,
            groupedCategoryProgress=grouped_categories,
            recentActivity=recent_activity
        )

    async def get_progress_analytics(self) -> ProgressAnalyticsDTO:
        """Получение аналитики прогресса"""
        
        analytics_data = await self.progress_repository.get_progress_analytics()
        
        return ProgressAnalyticsDTO(
            totalUsers=analytics_data["totalUsers"],
            activeUsers=analytics_data["activeUsers"],
            totalTasksSolved=analytics_data["totalTasksSolved"],
            averageTasksPerUser=analytics_data["averageTasksPerUser"],
            mostPopularCategories=analytics_data["mostPopularCategories"],
            strugglingAreas=analytics_data["strugglingAreas"]
        )

    def _group_categories_by_main(self, category_summaries: List[CategoryProgressSummaryDTO]) -> List[GroupedCategoryProgressDTO]:
        """Группировка категорий по основным категориям"""
        
        grouped = {}
        
        for summary in category_summaries:
            main_cat = summary.mainCategory
            
            if main_cat not in grouped:
                grouped[main_cat] = {
                    "mainCategory": main_cat,
                    "totalTasks": 0,
                    "completedTasks": 0,
                    "subCategories": []
                }
            
            grouped[main_cat]["totalTasks"] += summary.totalTasks
            grouped[main_cat]["completedTasks"] += summary.completedTasks
            grouped[main_cat]["subCategories"].append(
                SubCategoryProgressDTO(
                    subCategory=summary.subCategory or "",
                    totalTasks=summary.totalTasks,
                    completedTasks=summary.completedTasks,
                    completionRate=summary.completionRate,
                    status=summary.status
                )
            )
        
        # Рассчитываем процент завершения и статус для основных категорий
        result = []
        for main_cat, data in grouped.items():
            completion_rate = (data["completedTasks"] / data["totalTasks"] * 100) if data["totalTasks"] > 0 else 0
            
            status = "not_started"
            if data["completedTasks"] > 0:
                if completion_rate >= 100:
                    status = "completed"
                else:
                    status = "in_progress"
            
            result.append(GroupedCategoryProgressDTO(
                mainCategory=main_cat,
                totalTasks=data["totalTasks"],
                completedTasks=data["completedTasks"],
                completionRate=completion_rate,
                status=status,
                subCategories=data["subCategories"]
            ))
        
        return result

    async def _create_or_update_solution(self, attempt_data: TaskAttemptCreateDTO, attempt_number: int) -> None:
        """Создание или обновление решения задачи"""
        
        existing_solution = await self.progress_repository.get_task_solution_by_user_and_block(
            attempt_data.userId, 
            attempt_data.blockId
        )
        
        if existing_solution:
            # Обновляем существующее решение
            existing_solution.code = attempt_data.sourceCode  # finalCode -> code
            existing_solution.languageId = attempt_data.language  # language -> languageId
            existing_solution.updatedAt = datetime.now()
            
            await self.progress_repository.update_task_solution(existing_solution)
        else:
            # Создаем новое решение
            new_solution = TaskSolution(
                id=str(uuid.uuid4()),
                userId=attempt_data.userId,
                taskId=attempt_data.blockId,  # blockId -> taskId
                code=attempt_data.sourceCode,  # finalCode -> code
                languageId=attempt_data.language,  # language -> languageId
                createdAt=datetime.now(),
                updatedAt=datetime.now()
            )
            
            await self.progress_repository.create_task_solution(new_solution)

    async def _update_category_progress(self, user_id: int, block_id: str, is_successful: bool, attempt_number: int) -> None:
        """Обновление прогресса по категориям"""
        
        # Получаем информацию о блоке и категории
        # Пока используем заглушку - можно расширить позже
        pass 