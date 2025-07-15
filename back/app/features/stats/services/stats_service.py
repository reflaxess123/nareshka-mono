"""Сервис для работы со статистикой"""

import logging
from typing import Dict, Any

from app.features.stats.repositories.stats_repository import StatsRepository
from app.features.stats.dto.responses import (
    UserStatsOverviewResponse,
    ContentStatsResponse,
    TheoryStatsResponse,
    RoadmapStatsResponse,
    StatsHealthResponse,
)
from app.features.stats.exceptions.stats_exceptions import (
    StatsDataNotFoundError,
    StatsCalculationError,
)

logger = logging.getLogger(__name__)


class StatsService:
    """Сервис для работы со статистикой"""

    def __init__(self, stats_repository: StatsRepository):
        self.stats_repository = stats_repository

    async def get_user_stats_overview(self, user_id: int) -> UserStatsOverviewResponse:
        """Получение общей статистики пользователя"""
        logger.info(f"Получение общей статистики для пользователя {user_id}")
        
        try:
            stats_data = await self.stats_repository.get_user_stats_overview(user_id)
            
            if not stats_data:
                raise StatsDataNotFoundError(user_id, "overview")
            
            return UserStatsOverviewResponse(
                userId=stats_data["userId"],
                totalContentBlocks=stats_data["totalContentBlocks"],
                solvedContentBlocks=stats_data["solvedContentBlocks"],
                totalTheoryCards=stats_data["totalTheoryCards"],
                reviewedTheoryCards=stats_data["reviewedTheoryCards"],
                contentProgress=stats_data["contentProgress"],
                theoryProgress=stats_data["theoryProgress"],
                overallProgress=stats_data["overallProgress"],
            )
            
        except StatsDataNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Ошибка получения общей статистики: {str(e)}")
            raise StatsCalculationError("user_overview", str(e))

    async def get_content_stats(self, user_id: int) -> ContentStatsResponse:
        """Получение детальной статистики по контенту"""
        logger.info(f"Получение статистики контента для пользователя {user_id}")
        
        try:
            stats_data = await self.stats_repository.get_content_stats(user_id)
            
            if not stats_data:
                raise StatsDataNotFoundError(user_id, "content")

            return ContentStatsResponse(
                categories=stats_data["categories"],
                totalBlocks=stats_data["totalBlocks"],
                solvedBlocks=stats_data["solvedBlocks"],
                averageSolveCount=stats_data["averageSolveCount"],
            )
            
        except StatsDataNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Ошибка получения статистики контента: {str(e)}")
            raise StatsCalculationError("content", str(e))

    async def get_theory_stats(self, user_id: int) -> TheoryStatsResponse:
        """Получение детальной статистики по теории"""
        logger.info(f"Получение статистики теории для пользователя {user_id}")
        
        try:
            stats_data = await self.stats_repository.get_theory_stats(user_id)
            
            if not stats_data:
                raise StatsDataNotFoundError(user_id, "theory")

            return TheoryStatsResponse(
                categories=stats_data["categories"],
                totalCards=stats_data["totalCards"],
                reviewedCards=stats_data["reviewedCards"],
                averageReviewCount=stats_data["averageReviewCount"],
            )
            
        except StatsDataNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Ошибка получения статистики теории: {str(e)}")
            raise StatsCalculationError("theory", str(e))

    async def get_roadmap_stats(self, user_id: int) -> RoadmapStatsResponse:
        """Получение roadmap статистики по категориям"""
        logger.info(f"Получение roadmap статистики для пользователя {user_id}")
        
        try:
            stats_data = await self.stats_repository.get_roadmap_stats(user_id)
            
            if not stats_data:
                raise StatsDataNotFoundError(user_id, "roadmap")

            return RoadmapStatsResponse(
                categories=stats_data["categories"]
            )
            
        except StatsDataNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Ошибка получения roadmap статистики: {str(e)}")
            raise StatsCalculationError("roadmap", str(e))

    async def get_stats_health(self) -> StatsHealthResponse:
        """Проверка работоспособности Stats API"""
        logger.info("Проверка работоспособности stats service")
        
        return StatsHealthResponse(
            status="healthy",
            module="stats"
        )

    # Дополнительные методы для получения специфических данных

    async def get_user_progress_summary(self, user_id: int) -> Dict[str, Any]:
        """Получение краткого резюме прогресса пользователя"""
        logger.info(f"Получение краткого резюме для пользователя {user_id}")
        
        try:
            overview = await self.get_user_stats_overview(user_id)
            
            summary = {
                "userId": overview.userId,
                "totalProgress": overview.overallProgress.get("percentage", 0),
                "contentProgress": overview.overallProgress.get("contentPercentage", 0),
                "theoryProgress": overview.overallProgress.get("theoryPercentage", 0),
                "completedItems": overview.overallProgress.get("completedItems", 0),
                "totalItems": overview.overallProgress.get("totalItems", 0),
                "contentSummary": {
                    "solved": overview.solvedContentBlocks,
                    "total": overview.totalContentBlocks,
                },
                "theorySummary": {
                    "reviewed": overview.reviewedTheoryCards,
                    "total": overview.totalTheoryCards,
                },
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Ошибка получения краткого резюме: {str(e)}")
            raise StatsCalculationError("progress_summary", str(e))

    async def get_category_comparison(self, user_id: int) -> Dict[str, Any]:
        """Получение сравнения прогресса по категориям"""
        logger.info(f"Получение сравнения категорий для пользователя {user_id}")
        
        try:
            content_stats = await self.get_content_stats(user_id)
            theory_stats = await self.get_theory_stats(user_id)
            
            comparison = {}
            
            # Сравниваем категории из контента
            for category_name, category_data in content_stats.categories.items():
                if category_name not in comparison:
                    comparison[category_name] = {}
                
                comparison[category_name]["content"] = {
                    "total": category_data.get("total", 0),
                    "completed": category_data.get("solved", 0),
                    "percentage": category_data.get("percentage", 0),
                }
            
            # Добавляем категории из теории
            for category_name, category_data in theory_stats.categories.items():
                if category_name not in comparison:
                    comparison[category_name] = {}
                
                comparison[category_name]["theory"] = {
                    "total": category_data.get("total", 0),
                    "completed": category_data.get("reviewed", 0),
                    "percentage": category_data.get("percentage", 0),
                }
            
            # Вычисляем общий прогресс по категориям
            for category_name in comparison:
                content_perc = comparison[category_name].get("content", {}).get("percentage", 0)
                theory_perc = comparison[category_name].get("theory", {}).get("percentage", 0)
                
                # Если есть данные только по одному типу, используем их
                if content_perc > 0 and theory_perc == 0:
                    overall_perc = content_perc
                elif theory_perc > 0 and content_perc == 0:
                    overall_perc = theory_perc
                else:
                    # Если есть данные по обоим типам, усредняем
                    overall_perc = (content_perc + theory_perc) / 2
                
                comparison[category_name]["overall"] = {
                    "percentage": round(overall_perc, 2)
                }
            
            return {
                "userId": user_id,
                "categories": comparison,
                "totalCategories": len(comparison),
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения сравнения категорий: {str(e)}")
            raise StatsCalculationError("category_comparison", str(e)) 


