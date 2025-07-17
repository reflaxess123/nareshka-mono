"""Репозиторий для работы со статистикой"""

import logging
from typing import Any, Dict, List
from datetime import datetime

from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from app.shared.entities.content import ContentBlock, ContentFile
from app.shared.models.content_models import UserContentProgress
from app.shared.models.theory_models import (
    TheoryCard, 
    UserTheoryProgress,
)
from app.shared.entities.enums import CardState
from app.features.stats.exceptions.stats_exceptions import (
    StatsCalculationError,
    StatsDataNotFoundError,
    StatsAggregationError,
)

logger = logging.getLogger(__name__)


class StatsRepository:
    """Репозиторий для работы со статистикой"""

    def __init__(self, session: Session):
        self.session = session

    async def get_user_stats_overview(self, user_id: int) -> Dict[str, Any]:
        """Получение общей статистики пользователя"""
        logger.info(f"Получение общей статистики для пользователя {user_id}")
        
        try:
            # Статистика контента
            content_stats = await self._get_content_overview_stats(user_id)
            
            # Статистика теории
            theory_stats = await self._get_theory_overview_stats(user_id)
            
            # Общий прогресс
            total_items = content_stats["total"] + theory_stats["total"]
            completed_items = content_stats["completed"] + theory_stats["completed"]
            
            overall_progress = {
                "totalItems": total_items,
                "completedItems": completed_items,
                "percentage": round((completed_items / total_items * 100) if total_items > 0 else 0, 2),
                "contentPercentage": content_stats["percentage"],
                "theoryPercentage": theory_stats["percentage"],
            }

            return {
                "userId": user_id,
                "totalContentBlocks": content_stats["total"],
                "solvedContentBlocks": content_stats["completed"],
                "totalTheoryCards": theory_stats["total"],
                "reviewedTheoryCards": theory_stats["completed"],
                "contentProgress": content_stats["detailed"],
                "theoryProgress": theory_stats["detailed"],
                "overallProgress": overall_progress,
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения общей статистики: {str(e)}")
            raise StatsCalculationError("user_overview", str(e))

    async def _get_content_overview_stats(self, user_id: int) -> Dict[str, Any]:
        """Получение обзорной статистики контента"""
        
        # Получаем все блоки контента
        content_blocks = (
            self.session.query(ContentBlock)
            .join(ContentFile)
            .options(joinedload(ContentBlock.file))
            .all()
        )

        # Получаем прогресс пользователя
        content_progress = (
            self.session.query(UserContentProgress)
                            .filter(UserContentProgress.userId == user_id)
            .all()
        )

        progress_dict = {p.blockId: p for p in content_progress}

        # Агрегируем статистику
        stats_by_category = {}
        total_blocks = 0
        solved_blocks = 0

        for block in content_blocks:
            category = block.file.mainCategory if block.file else "Unknown"
            sub_category = block.file.subCategory if block.file else "General"
            
            progress = progress_dict.get(block.id)
            is_solved = progress and progress.solvedCount > 0

            total_blocks += 1
            if is_solved:
                solved_blocks += 1

            # Инициализация категории
            if category not in stats_by_category:
                stats_by_category[category] = {
                    "total": 0,
                    "completed": 0,
                    "percentage": 0,
                    "subCategories": {},
                }

            # Инициализация подкатегории
            if sub_category not in stats_by_category[category]["subCategories"]:
                stats_by_category[category]["subCategories"][sub_category] = {
                    "total": 0,
                    "completed": 0,
                    "percentage": 0,
                }

            # Увеличиваем счетчики
            stats_by_category[category]["total"] += 1
            stats_by_category[category]["subCategories"][sub_category]["total"] += 1

            if is_solved:
                stats_by_category[category]["completed"] += 1
                stats_by_category[category]["subCategories"][sub_category]["completed"] += 1

        # Вычисляем проценты
        for category_data in stats_by_category.values():
            if category_data["total"] > 0:
                category_data["percentage"] = round(
                    category_data["completed"] / category_data["total"] * 100, 2
                )
            
            for sub_data in category_data["subCategories"].values():
                if sub_data["total"] > 0:
                    sub_data["percentage"] = round(
                        sub_data["completed"] / sub_data["total"] * 100, 2
                    )

        return {
            "total": total_blocks,
            "completed": solved_blocks,
            "percentage": round((solved_blocks / total_blocks * 100) if total_blocks > 0 else 0, 2),
            "detailed": stats_by_category,
        }

    async def _get_theory_overview_stats(self, user_id: int) -> Dict[str, Any]:
        """Получение обзорной статистики теории"""
        
        # Получаем все карточки теории
        theory_cards = (
            self.session.query(TheoryCard)
            .filter(
                ~TheoryCard.category.ilike("%QUIZ%"),
                ~TheoryCard.category.ilike("%ПРАКТИКА%"),
            )
            .all()
        )

        # Получаем прогресс пользователя
        theory_progress = (
            self.session.query(UserTheoryProgress)
            .filter(UserTheoryProgress.userId == user_id)
            .all()
        )

        progress_dict = {p.cardId: p for p in theory_progress}

        # Агрегируем статистику
        stats_by_category = {}
        total_cards = 0
        reviewed_cards = 0

        for card in theory_cards:
            category = card.category
            sub_category = card.subCategory or "General"
            
            progress = progress_dict.get(card.id)
            is_reviewed = progress and progress.reviewCount > 0

            total_cards += 1
            if is_reviewed:
                reviewed_cards += 1

            # Инициализация категории
            if category not in stats_by_category:
                stats_by_category[category] = {
                    "total": 0,
                    "completed": 0,
                    "percentage": 0,
                    "subCategories": {},
                }

            # Инициализация подкатегории
            if sub_category not in stats_by_category[category]["subCategories"]:
                stats_by_category[category]["subCategories"][sub_category] = {
                    "total": 0,
                    "completed": 0,
                    "percentage": 0,
                }

            # Увеличиваем счетчики
            stats_by_category[category]["total"] += 1
            stats_by_category[category]["subCategories"][sub_category]["total"] += 1

            if is_reviewed:
                stats_by_category[category]["completed"] += 1
                stats_by_category[category]["subCategories"][sub_category]["completed"] += 1

        # Вычисляем проценты
        for category_data in stats_by_category.values():
            if category_data["total"] > 0:
                category_data["percentage"] = round(
                    category_data["completed"] / category_data["total"] * 100, 2
                )
            
            for sub_data in category_data["subCategories"].values():
                if sub_data["total"] > 0:
                    sub_data["percentage"] = round(
                        sub_data["completed"] / sub_data["total"] * 100, 2
                    )

        return {
            "total": total_cards,
            "completed": reviewed_cards,
            "percentage": round((reviewed_cards / total_cards * 100) if total_cards > 0 else 0, 2),
            "detailed": stats_by_category,
        }

    async def get_content_stats(self, user_id: int) -> Dict[str, Any]:
        """Получение детальной статистики по контенту"""
        logger.info(f"Получение детальной статистики контента для пользователя {user_id}")
        
        try:
            content_stats = await self._get_detailed_content_stats(user_id)
            return content_stats
            
        except Exception as e:
            logger.error(f"Ошибка получения статистики контента: {str(e)}")
            raise StatsCalculationError("content_detailed", str(e))

    async def _get_detailed_content_stats(self, user_id: int) -> Dict[str, Any]:
        """Получение подробной статистики контента с блоками"""
        
        # Получаем блоки с прогрессом
        blocks_query = (
            self.session.query(ContentBlock, UserContentProgress)
            .join(ContentFile)
            .outerjoin(
                UserContentProgress,
                                (ContentBlock.id == UserContentProgress.blockId) &
                (UserContentProgress.userId == user_id)
            )
            .options(joinedload(ContentBlock.file))
        )

        blocks_data = blocks_query.all()

        # Агрегируем детальную статистику
        categories = {}
        total_blocks = 0
        solved_blocks = 0
        total_solve_count = 0
        solved_count = 0

        for block, progress in blocks_data:
            category = block.file.mainCategory if block.file else "Unknown"
            sub_category = block.file.subCategory if block.file else "General"
            
            solve_count = progress.solvedCount if progress else 0
            is_solved = solve_count > 0

            total_blocks += 1
            if is_solved:
                solved_blocks += 1
                total_solve_count += solve_count
                solved_count += 1

            # Инициализация структуры
            if category not in categories:
                categories[category] = {
                    "total": 0,
                    "solved": 0,
                    "percentage": 0,
                    "averageSolveCount": 0,
                    "subCategories": {},
                }

            if sub_category not in categories[category]["subCategories"]:
                categories[category]["subCategories"][sub_category] = {
                    "total": 0,
                    "solved": 0,
                    "percentage": 0,
                    "averageSolveCount": 0,
                    "blocks": [],
                }

            # Добавляем блок
            block_info = {
                "id": block.id,
                "title": block.file.webdavPath.split("/")[-1] if block.file else "Untitled",
                "solveCount": solve_count,
                "isSolved": is_solved,
            }

            categories[category]["subCategories"][sub_category]["blocks"].append(block_info)

            # Обновляем счетчики
            categories[category]["total"] += 1
            categories[category]["subCategories"][sub_category]["total"] += 1

            if is_solved:
                categories[category]["solved"] += 1
                categories[category]["subCategories"][sub_category]["solved"] += 1

        # Вычисляем проценты и средние
        for category_data in categories.values():
            if category_data["total"] > 0:
                category_data["percentage"] = round(
                    category_data["solved"] / category_data["total"] * 100, 2
                )
                solved_in_category = sum(
                    block["solveCount"] 
                    for sub_data in category_data["subCategories"].values()
                    for block in sub_data["blocks"]
                    if block["isSolved"]
                )
                category_data["averageSolveCount"] = round(
                    solved_in_category / category_data["solved"] if category_data["solved"] > 0 else 0, 2
                )
            
            for sub_data in category_data["subCategories"].values():
                if sub_data["total"] > 0:
                    sub_data["percentage"] = round(
                        sub_data["solved"] / sub_data["total"] * 100, 2
                    )
                    solved_in_sub = sum(
                        block["solveCount"] for block in sub_data["blocks"] if block["isSolved"]
                    )
                    sub_data["averageSolveCount"] = round(
                        solved_in_sub / sub_data["solved"] if sub_data["solved"] > 0 else 0, 2
                    )

        return {
            "categories": categories,
            "totalBlocks": total_blocks,
            "solvedBlocks": solved_blocks,
            "averageSolveCount": round(
                total_solve_count / solved_count if solved_count > 0 else 0, 2
            ),
        }

    async def get_theory_stats(self, user_id: int) -> Dict[str, Any]:
        """Получение детальной статистики по теории"""
        logger.info(f"Получение детальной статистики теории для пользователя {user_id}")
        
        try:
            theory_stats = await self._get_detailed_theory_stats(user_id)
            return theory_stats
            
        except Exception as e:
            logger.error(f"Ошибка получения статистики теории: {str(e)}")
            raise StatsCalculationError("theory_detailed", str(e))

    async def _get_detailed_theory_stats(self, user_id: int) -> Dict[str, Any]:
        """Получение подробной статистики теории с карточками"""
        
        # Получаем карточки с прогрессом
        cards_query = (
            self.session.query(TheoryCard, UserTheoryProgress)
            .filter(
                ~TheoryCard.category.ilike("%QUIZ%"),
                ~TheoryCard.category.ilike("%ПРАКТИКА%"),
            )
            .outerjoin(
                UserTheoryProgress,
                (TheoryCard.id == UserTheoryProgress.cardId) & 
                (UserTheoryProgress.userId == user_id)
            )
        )

        cards_data = cards_query.all()

        # Агрегируем детальную статистику
        categories = {}
        total_cards = 0
        reviewed_cards = 0
        total_review_count = 0
        reviewed_count = 0

        for card, progress in cards_data:
            category = card.category
            sub_category = card.subCategory or "General"
            
            review_count = progress.reviewCount if progress else 0
            is_reviewed = review_count > 0
            card_state = progress.cardState.value if progress and progress.cardState else "NEW"
            ease_factor = float(progress.easeFactor) if progress and progress.easeFactor else 2.5

            total_cards += 1
            if is_reviewed:
                reviewed_cards += 1
                total_review_count += review_count
                reviewed_count += 1

            # Инициализация структуры
            if category not in categories:
                categories[category] = {
                    "total": 0,
                    "reviewed": 0,
                    "percentage": 0,
                    "averageReviewCount": 0,
                    "subCategories": {},
                }

            if sub_category not in categories[category]["subCategories"]:
                categories[category]["subCategories"][sub_category] = {
                    "total": 0,
                    "reviewed": 0,
                    "percentage": 0,
                    "averageReviewCount": 0,
                    "cards": [],
                }

            # Добавляем карточку
            card_info = {
                "id": card.id,
                "question": card.questionBlock[:100] + "..." if len(card.questionBlock) > 100 else card.questionBlock,
                "reviewCount": review_count,
                "isReviewed": is_reviewed,
                "cardState": card_state,
                "easeFactor": ease_factor,
            }

            categories[category]["subCategories"][sub_category]["cards"].append(card_info)

            # Обновляем счетчики
            categories[category]["total"] += 1
            categories[category]["subCategories"][sub_category]["total"] += 1

            if is_reviewed:
                categories[category]["reviewed"] += 1
                categories[category]["subCategories"][sub_category]["reviewed"] += 1

        # Вычисляем проценты и средние
        for category_data in categories.values():
            if category_data["total"] > 0:
                category_data["percentage"] = round(
                    category_data["reviewed"] / category_data["total"] * 100, 2
                )
                reviewed_in_category = sum(
                    card["reviewCount"] 
                    for sub_data in category_data["subCategories"].values()
                    for card in sub_data["cards"]
                    if card["isReviewed"]
                )
                category_data["averageReviewCount"] = round(
                    reviewed_in_category / category_data["reviewed"] if category_data["reviewed"] > 0 else 0, 2
                )
            
            for sub_data in category_data["subCategories"].values():
                if sub_data["total"] > 0:
                    sub_data["percentage"] = round(
                        sub_data["reviewed"] / sub_data["total"] * 100, 2
                    )
                    reviewed_in_sub = sum(
                        card["reviewCount"] for card in sub_data["cards"] if card["isReviewed"]
                    )
                    sub_data["averageReviewCount"] = round(
                        reviewed_in_sub / sub_data["reviewed"] if sub_data["reviewed"] > 0 else 0, 2
                    )

        return {
            "categories": categories,
            "totalCards": total_cards,
            "reviewedCards": reviewed_cards,
            "averageReviewCount": round(
                total_review_count / reviewed_count if reviewed_count > 0 else 0, 2
            ),
        }

    async def get_roadmap_stats(self, user_id: int) -> Dict[str, Any]:
        """Получение roadmap статистики по категориям"""
        logger.info(f"Получение roadmap статистики для пользователя {user_id}")
        
        try:
            content_overview = await self._get_content_overview_stats(user_id)
            theory_overview = await self._get_theory_overview_stats(user_id)
            
            # Объединяем категории из content и theory
            all_categories = set()
            all_categories.update(content_overview["detailed"].keys())
            all_categories.update(theory_overview["detailed"].keys())
            
            roadmap_categories = []
            
            for category in sorted(all_categories):
                content_data = content_overview["detailed"].get(category, {
                    "total": 0, "completed": 0, "percentage": 0, "subCategories": {}
                })
                theory_data = theory_overview["detailed"].get(category, {
                    "total": 0, "completed": 0, "percentage": 0, "subCategories": {}
                })
                
                # Объединяем подкатегории
                all_subcategories = set()
                all_subcategories.update(content_data.get("subCategories", {}).keys())
                all_subcategories.update(theory_data.get("subCategories", {}).keys())
                
                subcategories = []
                for subcategory in sorted(all_subcategories):
                    content_sub = content_data.get("subCategories", {}).get(subcategory, {
                        "total": 0, "completed": 0, "percentage": 0
                    })
                    theory_sub = theory_data.get("subCategories", {}).get(subcategory, {
                        "total": 0, "completed": 0, "percentage": 0
                    })
                    
                    subcategories.append({
                        "name": subcategory,
                        "contentProgress": content_sub["percentage"],
                        "theoryProgress": theory_sub["percentage"],
                        "overallProgress": round(
                            (content_sub["percentage"] + theory_sub["percentage"]) / 2, 2
                        ) if content_sub["total"] > 0 or theory_sub["total"] > 0 else 0,
                    })
                
                category_info = {
                    "name": category,
                    "contentProgress": content_data["percentage"],
                    "theoryProgress": theory_data["percentage"],
                    "overallProgress": round(
                        (content_data["percentage"] + theory_data["percentage"]) / 2, 2
                    ) if content_data["total"] > 0 or theory_data["total"] > 0 else 0,
                    "contentStats": {
                        "total": content_data["total"],
                        "completed": content_data["completed"],
                    },
                    "theoryStats": {
                        "total": theory_data["total"],
                        "completed": theory_data["completed"],
                    },
                    "subCategories": subcategories,
                }
                
                roadmap_categories.append(category_info)
            
            return {
                "categories": roadmap_categories,
            }
            
        except Exception as e:
            logger.error(f"Ошибка получения roadmap статистики: {str(e)}")
            raise StatsCalculationError("roadmap", str(e)) 



