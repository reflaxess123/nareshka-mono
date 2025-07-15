"""Сервис для работы с заданиями"""

import logging
from typing import List, Optional

from app.features.task.repositories.task_repository import TaskRepository
from app.features.task.dto.requests import (
    TaskAttemptCreateRequest,
    TaskSolutionCreateRequest,
    TaskFilterRequest,
)
from app.features.task.dto.responses import (
    TaskResponse,
    TasksListResponse,
    TaskCategoriesResponse,
    TaskCompaniesResponse,
    TaskAttemptResponse,
    TaskSolutionResponse,
)
from app.features.task.exceptions.task_exceptions import (
    TaskNotFoundError,
    TaskValidationError,
    TaskAttemptError,
    TaskSolutionError,
)

logger = logging.getLogger(__name__)


class TaskService:
    """Сервис для работы с заданиями"""

    def __init__(self, task_repository: TaskRepository):
        self.task_repository = task_repository

    async def get_tasks(
        self,
        page: int = 1,
        limit: int = 10,
        main_categories: Optional[List[str]] = None,
        sub_categories: Optional[List[str]] = None,
        search_query: Optional[str] = None,
        sort_by: str = "orderInFile",
        sort_order: str = "asc",
        item_type: Optional[str] = None,
        only_unsolved: Optional[bool] = None,
        companies: Optional[List[str]] = None,
        user_id: Optional[int] = None,
    ) -> TasksListResponse:
        """Получение объединенного списка заданий с пагинацией и фильтрацией"""
        logger.info(f"Получение заданий: page={page}, limit={limit}, categories={main_categories}")
        
        try:
            # Преобразуем старый параметр companies в список
            if companies and isinstance(companies, str):
                companies = [c.strip() for c in companies.split(",") if c.strip()]

            tasks, total = await self.task_repository.get_tasks(
                page=page,
                limit=limit,
                main_categories=main_categories,
                sub_categories=sub_categories,
                search_query=search_query,
                sort_by=sort_by,
                sort_order=sort_order,
                item_type=item_type,
                only_unsolved=only_unsolved,
                companies=companies,
                user_id=user_id,
            )

            # Преобразуем в DTO
            task_responses = []
            for task in tasks:
                task_response = TaskResponse(
                    id=task.id,
                    type=task.item_type,
                    title=task.title,
                    description=task.description,
                    category=task.main_category,
                    subCategory=task.sub_category,
                    fileId=getattr(task, 'file_id', None),
                    pathTitles=getattr(task, 'path_titles', None),
                    blockLevel=getattr(task, 'block_level', None),
                    orderInFile=getattr(task, 'order_in_file', None),
                    textContent=getattr(task, 'text_content', None),
                    codeContent=getattr(task, 'code_content', None),
                    codeLanguage=getattr(task, 'code_language', None),
                    isCodeFoldable=getattr(task, 'is_code_foldable', None),
                    codeFoldTitle=getattr(task, 'code_fold_title', None),
                    extractedUrls=getattr(task, 'extracted_urls', None),
                    companies=getattr(task, 'companies', None),
                    questionBlock=getattr(task, 'question_block', None),
                    answerBlock=getattr(task, 'answer_block', None),
                    tags=getattr(task, 'tags', None),
                    orderIndex=getattr(task, 'order_index', None),
                    currentUserSolvedCount=getattr(task, 'current_user_solved_count', 0),
                    createdAt=getattr(task, 'createdAt', None),
                    updatedAt=getattr(task, 'updatedAt', None),
                )
                task_responses.append(task_response)

            logger.info(f"Найдено {total} заданий, возвращено {len(task_responses)}")
            return TasksListResponse.create(task_responses, total, page, limit)
            
        except Exception as e:
            logger.error(f"Ошибка при получении заданий: {str(e)}")
            raise

    async def get_task_categories(self) -> TaskCategoriesResponse:
        """Получение списка категорий заданий"""
        logger.info("Получение категорий заданий")
        
        try:
            categories = await self.task_repository.get_task_categories()
            
            # Преобразуем в DTO
            category_responses = []
            for category in categories:
                category_response = {
                    "name": category.name,
                    "subCategories": category.subCategories,
                                "totalCount": category.totalCount,
            "contentBlockCount": category.contentBlockCount,
            "theoryQuizCount": category.theoryQuizCount,
                }
                category_responses.append(category_response)
            
            logger.info(f"Найдено {len(category_responses)} категорий")
            return TaskCategoriesResponse(categories=category_responses)
            
        except Exception as e:
            logger.error(f"Ошибка при получении категорий: {str(e)}")
            raise

    async def get_task_companies(
        self,
        main_categories: Optional[List[str]] = None,
        sub_categories: Optional[List[str]] = None,
    ) -> TaskCompaniesResponse:
        """Получение списка компаний из заданий"""
        logger.info(f"Получение компаний: categories={main_categories}, subcategories={sub_categories}")
        
        try:
            companies = await self.task_repository.get_task_companies(
                main_categories=main_categories, 
                sub_categories=sub_categories
            )
            
            # Преобразуем в DTO
            company_responses = []
            for company in companies:
                company_response = {
                    "name": company.name,
                    "count": company.count,
                }
                company_responses.append(company_response)
            
            logger.info(f"Найдено {len(company_responses)} компаний")
            return TaskCompaniesResponse(companies=company_responses)
            
        except Exception as e:
            logger.error(f"Ошибка при получении компаний: {str(e)}")
            raise

    async def create_task_attempt(
        self, user_id: int, request: TaskAttemptCreateRequest
    ) -> TaskAttemptResponse:
        """Создание попытки решения задачи"""
        logger.info(f"Создание попытки пользователя {user_id} для блока {request.blockId}")
        
        try:
            # Валидация данных
            if not request.sourceCode.strip():
                raise TaskValidationError("sourceCode", "Исходный код не может быть пустым")
                
            if not request.language.strip():
                raise TaskValidationError("language", "Язык программирования обязателен")

            attempt = await self.task_repository.create_task_attempt(
                user_id=user_id,
                blockId=request.blockId,
                sourceCode=request.sourceCode,
                language=request.language,
                isSuccessful=request.isSuccessful,
                attemptNumber=request.attemptNumber,
                executionTimeMs=request.executionTimeMs,
                memoryUsedMB=request.memoryUsedMB,
                errorMessage=request.errorMessage,
                stderr=request.stderr,
                durationMinutes=request.durationMinutes,
            )

            logger.info(f"Попытка {attempt.id} создана для пользователя {user_id}")
            return TaskAttemptResponse.from_orm(attempt)
            
        except Exception as e:
            logger.error(f"Ошибка при создании попытки: {str(e)}")
            raise

    async def create_task_solution(
        self, user_id: int, request: TaskSolutionCreateRequest
    ) -> TaskSolutionResponse:
        """Создание решения задачи"""
        logger.info(f"Создание решения пользователя {user_id} для блока {request.blockId}")
        
        try:
            # Валидация данных
            if not request.finalCode.strip():
                raise TaskValidationError("finalCode", "Финальный код не может быть пустым")
                
            if not request.language.strip():
                raise TaskValidationError("language", "Язык программирования обязателен")
                
            if request.totalAttempts <= 0:
                raise TaskValidationError("totalAttempts", "Количество попыток должно быть больше 0")

            solution = await self.task_repository.create_task_solution(
                user_id=user_id,
                blockId=request.blockId,
                finalCode=request.finalCode,
                language=request.language,
                totalAttempts=request.totalAttempts,
                timeToSolveMinutes=request.timeToSolveMinutes,
                firstAttempt=request.firstAttempt,
                solvedAt=request.solvedAt,
            )

            logger.info(f"Решение {solution.id} создано для пользователя {user_id}")
            return TaskSolutionResponse.from_orm(solution)
            
        except Exception as e:
            logger.error(f"Ошибка при создании решения: {str(e)}")
            raise

    async def get_user_task_attempts(
        self, user_id: int, block_id: Optional[str] = None
    ) -> List[TaskAttemptResponse]:
        """Получение попыток пользователя"""
        logger.info(f"Получение попыток пользователя {user_id}, block_id={block_id}")
        
        try:
            attempts = await self.task_repository.get_user_task_attempts(user_id, block_id)
            
            attempt_responses = [TaskAttemptResponse.from_orm(attempt) for attempt in attempts]
            
            logger.info(f"Найдено {len(attempt_responses)} попыток")
            return attempt_responses
            
        except Exception as e:
            logger.error(f"Ошибка при получении попыток: {str(e)}")
            raise

    async def get_user_task_solutions(
        self, user_id: int, block_id: Optional[str] = None
    ) -> List[TaskSolutionResponse]:
        """Получение решений пользователя"""
        logger.info(f"Получение решений пользователя {user_id}, block_id={block_id}")
        
        try:
            solutions = await self.task_repository.get_user_task_solutions(user_id, block_id)
            
            solution_responses = [TaskSolutionResponse.from_orm(solution) for solution in solutions]
            
            logger.info(f"Найдено {len(solution_responses)} решений")
            return solution_responses
            
        except Exception as e:
            logger.error(f"Ошибка при получении решений: {str(e)}")
            raise 


