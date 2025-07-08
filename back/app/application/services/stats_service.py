from app.domain.repositories.stats_repository import StatsRepository
from app.domain.entities.stats_types import (
    UserStatsOverview,
    ContentStats,
    TheoryStats,
    RoadmapStats
)
from app.application.dto.stats_dto import (
    UserStatsOverviewDTO,
    ContentStatsDTO,
    TheoryStatsDTO,
    RoadmapStatsDTO
)


class StatsService:
    def __init__(self, stats_repository: StatsRepository):
        self.stats_repository = stats_repository

    async def get_user_stats_overview(self, user_id: int) -> UserStatsOverviewDTO:
        """Получение общей статистики пользователя"""
        
        stats = await self.stats_repository.get_user_stats_overview(user_id)
        
        return UserStatsOverviewDTO(
            userId=stats.userId,
            totalContentBlocks=stats.totalContentBlocks,
            solvedContentBlocks=stats.solvedContentBlocks,
            totalTheoryCards=stats.totalTheoryCards,
            reviewedTheoryCards=stats.reviewedTheoryCards,
            contentProgress=stats.contentProgress,
            theoryProgress=stats.theoryProgress,
            overallProgress={
                "totalItems": stats.overallProgress.totalItems,
                "completedItems": stats.overallProgress.completedItems,
                "percentage": stats.overallProgress.percentage,
                "contentPercentage": stats.overallProgress.contentPercentage,
                "theoryPercentage": stats.overallProgress.theoryPercentage
            }
        )

    async def get_content_stats(self, user_id: int) -> ContentStatsDTO:
        """Получение детальной статистики по контенту"""
        
        stats = await self.stats_repository.get_content_stats(user_id)
        
        # Преобразуем categories из dataclass в dict для JSON сериализации
        categories_dict = {}
        for category_name, category_stats in stats.categories.items():
            sub_categories_dict = {}
            for sub_name, sub_stats in category_stats.subCategories.items():
                blocks_list = []
                for block in sub_stats.blocks:
                    blocks_list.append({
                        "id": block.id,
                        "title": block.title,
                        "solveCount": block.solveCount,
                        "isSolved": block.isSolved
                    })
                
                sub_categories_dict[sub_name] = {
                    "total": sub_stats.total,
                    "solved": sub_stats.solved,
                    "percentage": sub_stats.percentage,
                    "averageSolveCount": sub_stats.averageSolveCount,
                    "blocks": blocks_list
                }
            
            categories_dict[category_name] = {
                "total": category_stats.total,
                "solved": category_stats.solved,
                "percentage": category_stats.percentage,
                "averageSolveCount": category_stats.averageSolveCount,
                "subCategories": sub_categories_dict
            }
        
        return ContentStatsDTO(
            categories=categories_dict,
            totalBlocks=stats.totalBlocks,
            solvedBlocks=stats.solvedBlocks,
            averageSolveCount=stats.averageSolveCount
        )

    async def get_theory_stats(self, user_id: int) -> TheoryStatsDTO:
        """Получение детальной статистики по теории"""
        
        stats = await self.stats_repository.get_theory_stats(user_id)
        
        # Преобразуем categories из dataclass в dict для JSON сериализации
        categories_dict = {}
        for category_name, category_stats in stats.categories.items():
            sub_categories_dict = {}
            for sub_name, sub_stats in category_stats.subCategories.items():
                cards_list = []
                for card in sub_stats.cards:
                    cards_list.append({
                        "id": card.id,
                        "question": card.question,
                        "reviewCount": card.reviewCount,
                        "isReviewed": card.isReviewed,
                        "cardState": card.cardState,
                        "easeFactor": card.easeFactor
                    })
                
                sub_categories_dict[sub_name] = {
                    "total": sub_stats.total,
                    "reviewed": sub_stats.reviewed,
                    "percentage": sub_stats.percentage,
                    "averageReviewCount": sub_stats.averageReviewCount,
                    "cards": cards_list
                }
            
            categories_dict[category_name] = {
                "total": category_stats.total,
                "reviewed": category_stats.reviewed,
                "percentage": category_stats.percentage,
                "averageReviewCount": category_stats.averageReviewCount,
                "subCategories": sub_categories_dict
            }
        
        return TheoryStatsDTO(
            categories=categories_dict,
            totalCards=stats.totalCards,
            reviewedCards=stats.reviewedCards,
            averageReviewCount=stats.averageReviewCount
        )

    async def get_roadmap_stats(self, user_id: int) -> RoadmapStatsDTO:
        """Получение roadmap статистики по категориям"""
        
        stats = await self.stats_repository.get_roadmap_stats(user_id)
        
        # Преобразуем categories из dataclass в dict для JSON сериализации
        categories_list = []
        for category in stats.categories:
            sub_categories_list = []
            for sub_cat in category.subCategories:
                sub_categories_list.append({
                    "name": sub_cat.name,
                    "contentProgress": sub_cat.contentProgress,
                    "theoryProgress": sub_cat.theoryProgress,
                    "overallProgress": sub_cat.overallProgress
                })
            
            categories_list.append({
                "name": category.name,
                "contentProgress": category.contentProgress,
                "theoryProgress": category.theoryProgress,
                "overallProgress": category.overallProgress,
                "contentStats": {
                    "total": category.contentStats.total,
                    "completed": category.contentStats.completed
                },
                "theoryStats": {
                    "total": category.theoryStats.total,
                    "completed": category.theoryStats.completed
                },
                "subCategories": sub_categories_list
            })
        
        return RoadmapStatsDTO(categories=categories_list) 