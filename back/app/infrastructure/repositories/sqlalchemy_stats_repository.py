from typing import Dict, List, Any
from sqlalchemy.orm import Session

from app.domain.repositories.stats_repository import StatsRepository
from app.domain.entities.stats_types import (
    UserStatsOverview,
    ContentStats,
    TheoryStats,
    RoadmapStats
)
from ..models import (
    ContentBlock,
    ContentFile,
    TheoryCard,
    UserContentProgress,
    UserTheoryProgress
)


class SQLAlchemyStatsRepository(StatsRepository):
    def __init__(self, db_session: Session):
        self.db_session = db_session

    async def get_user_stats_overview(self, user_id: int) -> UserStatsOverview:
        """Получение общей статистики пользователя"""
        
        # Получаем статистику по контенту
        content_blocks = self.db_session.query(ContentBlock).join(ContentFile).all()
        content_progress = self.db_session.query(UserContentProgress).filter(
            UserContentProgress.userId == user_id
        ).all()

        # Создаем словарь прогресса по блокам контента
        content_progress_dict = {
            progress.blockId: progress for progress in content_progress
        }

        # Обрабатываем статистику контента
        content_stats: Dict[str, Any] = {}
        total_content_blocks = 0
        solved_content_blocks = 0

        for block in content_blocks:
            category = block.file.mainCategory if block.file.mainCategory else "Unknown"
            sub_category = block.file.subCategory if block.file.subCategory else "General"

            progress = content_progress_dict.get(block.id)
            is_solved = progress and progress.solvedCount > 0

            total_content_blocks += 1
            if is_solved:
                solved_content_blocks += 1

            # Инициализируем категорию если её нет
            if category not in content_stats:
                content_stats[category] = {
                    "total": 0,
                    "completed": 0,
                    "percentage": 0,
                    "subCategories": {}
                }

            # Инициализируем подкатегорию если её нет
            if sub_category not in content_stats[category]["subCategories"]:
                content_stats[category]["subCategories"][sub_category] = {
                    "total": 0,
                    "completed": 0,
                    "percentage": 0
                }

            # Увеличиваем счетчики
            content_stats[category]["total"] += 1
            content_stats[category]["subCategories"][sub_category]["total"] += 1

            if is_solved:
                content_stats[category]["completed"] += 1
                content_stats[category]["subCategories"][sub_category]["completed"] += 1

        # Вычисляем проценты для контента
        for category in content_stats:
            if content_stats[category]["total"] > 0:
                content_stats[category]["percentage"] = round(
                    (content_stats[category]["completed"] / content_stats[category]["total"]) * 100, 2
                )

            for sub_category in content_stats[category]["subCategories"]:
                sub_cat = content_stats[category]["subCategories"][sub_category]
                if sub_cat["total"] > 0:
                    sub_cat["percentage"] = round((sub_cat["completed"] / sub_cat["total"]) * 100, 2)

        # Получаем статистику по теории
        theory_cards = self.db_session.query(TheoryCard).all()
        theory_progress = self.db_session.query(UserTheoryProgress).filter(
            UserTheoryProgress.userId == user_id
        ).all()

        # Создаем словарь прогресса по карточкам теории
        theory_progress_dict = {
            progress.cardId: progress for progress in theory_progress
        }

        # Обрабатываем статистику теории
        theory_stats: Dict[str, Any] = {}
        total_theory_cards = 0
        reviewed_theory_cards = 0

        for card in theory_cards:
            category = card.category if card.category else "Unknown"
            sub_category = card.subCategory if card.subCategory else "General"

            progress = theory_progress_dict.get(card.id)
            is_reviewed = progress and progress.reviewCount > 0

            total_theory_cards += 1
            if is_reviewed:
                reviewed_theory_cards += 1

            # Инициализируем категорию если её нет
            if category not in theory_stats:
                theory_stats[category] = {
                    "total": 0,
                    "completed": 0,
                    "percentage": 0,
                    "subCategories": {}
                }

            # Инициализируем подкатегорию если её нет
            if sub_category not in theory_stats[category]["subCategories"]:
                theory_stats[category]["subCategories"][sub_category] = {
                    "total": 0,
                    "completed": 0,
                    "percentage": 0
                }

            # Увеличиваем счетчики
            theory_stats[category]["total"] += 1
            theory_stats[category]["subCategories"][sub_category]["total"] += 1

            if is_reviewed:
                theory_stats[category]["completed"] += 1
                theory_stats[category]["subCategories"][sub_category]["completed"] += 1

        # Вычисляем проценты для теории
        for category in theory_stats:
            if theory_stats[category]["total"] > 0:
                theory_stats[category]["percentage"] = round(
                    (theory_stats[category]["completed"] / theory_stats[category]["total"]) * 100, 2
                )

            for sub_category in theory_stats[category]["subCategories"]:
                sub_cat = theory_stats[category]["subCategories"][sub_category]
                if sub_cat["total"] > 0:
                    sub_cat["percentage"] = round((sub_cat["completed"] / sub_cat["total"]) * 100, 2)

        # Вычисляем общий прогресс
        total_items = total_content_blocks + total_theory_cards
        completed_items = solved_content_blocks + reviewed_theory_cards

        overall_percentage = round((completed_items / total_items) * 100, 2) if total_items > 0 else 0
        content_percentage = round((solved_content_blocks / total_content_blocks) * 100, 2) if total_content_blocks > 0 else 0
        theory_percentage = round((reviewed_theory_cards / total_theory_cards) * 100, 2) if total_theory_cards > 0 else 0

        overall_progress = OverallProgressStats(
            totalItems=total_items,
            completedItems=completed_items,
            percentage=overall_percentage,
            contentPercentage=content_percentage,
            theoryPercentage=theory_percentage
        )

        return UserStatsOverview(
            userId=user_id,
            totalContentBlocks=total_content_blocks,
            solvedContentBlocks=solved_content_blocks,
            totalTheoryCards=total_theory_cards,
            reviewedTheoryCards=reviewed_theory_cards,
            contentProgress=content_stats,
            theoryProgress=theory_stats,
            overallProgress=overall_progress
        )

    async def get_content_stats(self, user_id: int) -> ContentStats:
        """Получение детальной статистики по контенту"""
        
        # Получаем все блоки контента с прогрессом
        blocks_with_progress = self.db_session.query(ContentBlock, UserContentProgress).join(
            ContentFile, ContentBlock.fileId == ContentFile.id
        ).outerjoin(
            UserContentProgress,
            (UserContentProgress.blockId == ContentBlock.id) &
            (UserContentProgress.userId == user_id)
        ).all()

        categories: Dict[str, CategoryContentStats] = {}
        total_blocks = 0
        solved_blocks = 0
        total_solve_count = 0

        for block, progress in blocks_with_progress:
            category = block.file.mainCategory if block.file.mainCategory else "Unknown"
            sub_category = block.file.subCategory if block.file.subCategory else "General"

            view_count = progress.solvedCount if progress else 0
            is_solved = view_count > 0

            total_blocks += 1
            total_solve_count += view_count
            if is_solved:
                solved_blocks += 1

            # Инициализируем категорию
            if category not in categories:
                categories[category] = CategoryContentStats(
                    total=0,
                    solved=0,
                    percentage=0,
                    averageSolveCount=0,
                    subCategories={}
                )

            # Инициализируем подкатегорию
            if sub_category not in categories[category].subCategories:
                categories[category].subCategories[sub_category] = SubCategoryContentStats(
                    total=0,
                    solved=0,
                    percentage=0,
                    averageSolveCount=0,
                    blocks=[]
                )

            # Обновляем счетчики
            categories[category].total += 1
            categories[category].subCategories[sub_category].total += 1

            if is_solved:
                categories[category].solved += 1
                categories[category].subCategories[sub_category].solved += 1

            # Добавляем блок в подкатегорию
            block_stats = ContentBlockStats(
                id=block.id,
                title=block.blockTitle or "Untitled",
                solveCount=view_count,
                isSolved=is_solved
            )
            categories[category].subCategories[sub_category].blocks.append(block_stats)

        # Вычисляем проценты и средние значения
        for category in categories:
            cat_data = categories[category]
            if cat_data.total > 0:
                cat_data.percentage = round((cat_data.solved / cat_data.total) * 100, 2)

                # Средний solve count для категории
                category_solve_count = sum(
                    sum(block.solveCount for block in sub_cat.blocks)
                    for sub_cat in cat_data.subCategories.values()
                )
                cat_data.averageSolveCount = round(category_solve_count / cat_data.total, 2)

            for sub_category in cat_data.subCategories:
                sub_cat = cat_data.subCategories[sub_category]
                if sub_cat.total > 0:
                    sub_cat.percentage = round((sub_cat.solved / sub_cat.total) * 100, 2)

                    # Средний solve count для подкатегории
                    sub_solve_count = sum(block.solveCount for block in sub_cat.blocks)
                    sub_cat.averageSolveCount = round(sub_solve_count / sub_cat.total, 2)

        average_solve_count = round(total_solve_count / total_blocks, 2) if total_blocks > 0 else 0

        return ContentStats(
            categories=categories,
            totalBlocks=total_blocks,
            solvedBlocks=solved_blocks,
            averageSolveCount=average_solve_count
        )

    async def get_theory_stats(self, user_id: int) -> TheoryStats:
        """Получение детальной статистики по теории"""
        
        # Получаем все карточки теории с прогрессом
        cards_with_progress = self.db_session.query(TheoryCard, UserTheoryProgress).outerjoin(
            UserTheoryProgress,
            (UserTheoryProgress.cardId == TheoryCard.id) &
            (UserTheoryProgress.userId == user_id)
        ).all()

        categories: Dict[str, CategoryTheoryStats] = {}
        total_cards = 0
        reviewed_cards = 0
        total_review_count = 0

        for card, progress in cards_with_progress:
            category = card.category if card.category else "Unknown"
            sub_category = card.subCategory if card.subCategory else "General"

            review_count = progress.reviewCount if progress else 0
            is_reviewed = review_count > 0
            card_state = progress.cardState if progress else "NEW"

            total_cards += 1
            total_review_count += review_count
            if is_reviewed:
                reviewed_cards += 1

            # Инициализируем категорию
            if category not in categories:
                categories[category] = CategoryTheoryStats(
                    total=0,
                    reviewed=0,
                    percentage=0,
                    averageReviewCount=0,
                    subCategories={}
                )

            # Инициализируем подкатегорию
            if sub_category not in categories[category].subCategories:
                categories[category].subCategories[sub_category] = SubCategoryTheoryStats(
                    total=0,
                    reviewed=0,
                    percentage=0,
                    averageReviewCount=0,
                    cards=[]
                )

            # Обновляем счетчики
            categories[category].total += 1
            categories[category].subCategories[sub_category].total += 1

            if is_reviewed:
                categories[category].reviewed += 1
                categories[category].subCategories[sub_category].reviewed += 1

            # Добавляем карточку в подкатегорию
            card_stats = TheoryCardStats(
                id=card.id,
                question=card.questionBlock[:100] + "..." if len(card.questionBlock or "") > 100 else card.questionBlock,
                reviewCount=review_count,
                isReviewed=is_reviewed,
                cardState=card_state,
                easeFactor=float(progress.easeFactor) if progress else 2.5
            )
            categories[category].subCategories[sub_category].cards.append(card_stats)

        # Вычисляем проценты и средние значения
        for category in categories:
            cat_data = categories[category]
            if cat_data.total > 0:
                cat_data.percentage = round((cat_data.reviewed / cat_data.total) * 100, 2)

                # Средний review count для категории
                category_review_count = sum(
                    sum(card.reviewCount for card in sub_cat.cards)
                    for sub_cat in cat_data.subCategories.values()
                )
                cat_data.averageReviewCount = round(category_review_count / cat_data.total, 2)

            for sub_category in cat_data.subCategories:
                sub_cat = cat_data.subCategories[sub_category]
                if sub_cat.total > 0:
                    sub_cat.percentage = round((sub_cat.reviewed / sub_cat.total) * 100, 2)

                    # Средний review count для подкатегории
                    sub_review_count = sum(card.reviewCount for card in sub_cat.cards)
                    sub_cat.averageReviewCount = round(sub_review_count / sub_cat.total, 2)

        average_review_count = round(total_review_count / total_cards, 2) if total_cards > 0 else 0

        return TheoryStats(
            categories=categories,
            totalCards=total_cards,
            reviewedCards=reviewed_cards,
            averageReviewCount=average_review_count
        )

    async def get_roadmap_stats(self, user_id: int) -> RoadmapStats:
        """Получение roadmap статистики по категориям"""
        
        # Получаем все категории из контента и теории
        content_categories = self.db_session.query(ContentFile.mainCategory, ContentFile.subCategory).distinct().order_by(
            ContentFile.mainCategory.asc(), ContentFile.subCategory.asc()
        ).all()

        theory_categories = self.db_session.query(TheoryCard.category, TheoryCard.subCategory).distinct().order_by(
            TheoryCard.category.asc(), TheoryCard.subCategory.asc()
        ).all()

        # Создаем множество всех уникальных категорий
        all_categories = set()
        for main_cat, _ in content_categories:
            if main_cat:
                all_categories.add(main_cat)
        for category, _ in theory_categories:
            if category:
                all_categories.add(category)

        roadmap_data = []

        for category_name in sorted(all_categories):
            # Получаем статистику по контенту для этой категории
            content_blocks = self.db_session.query(ContentBlock).join(ContentFile).filter(
                ContentFile.mainCategory == category_name
            ).all()

            # Получаем статистику по теории для этой категории
            theory_cards = self.db_session.query(TheoryCard).filter(
                TheoryCard.category == category_name
            ).all()

            # Получаем прогресс пользователя
            content_progress = self.db_session.query(UserContentProgress).filter(
                UserContentProgress.userId == user_id,
                UserContentProgress.blockId.in_([b.id for b in content_blocks])
            ).all() if content_blocks else []

            theory_progress = self.db_session.query(UserTheoryProgress).filter(
                UserTheoryProgress.userId == user_id,
                UserTheoryProgress.cardId.in_([c.id for c in theory_cards])
            ).all() if theory_cards else []

            # Создаем словари для быстрого поиска прогресса
            content_progress_dict = {p.blockId: p for p in content_progress}
            theory_progress_dict = {p.cardId: p for p in theory_progress}

            # Вычисляем общую статистику для категории
            content_total = len(content_blocks)
            content_completed = len([b for b in content_blocks
                                   if content_progress_dict.get(b.id) and content_progress_dict[b.id].solvedCount > 0])
            theory_total = len(theory_cards)
            theory_completed = len([c for c in theory_cards
                                  if theory_progress_dict.get(c.id) and theory_progress_dict[c.id].reviewCount > 0])

            content_progress_pct = round((content_completed / content_total) * 100) if content_total > 0 else 0
            theory_progress_pct = round((theory_completed / theory_total) * 100) if theory_total > 0 else 0
            total_items = content_total + theory_total
            total_completed_items = content_completed + theory_completed
            overall_progress_pct = round((total_completed_items / total_items) * 100) if total_items > 0 else 0

            category_data = CategoryRoadmapStats(
                name=category_name,
                contentProgress=content_progress_pct,
                theoryProgress=theory_progress_pct,
                overallProgress=overall_progress_pct,
                contentStats=ItemStats(
                    total=content_total,
                    completed=content_completed
                ),
                theoryStats=ItemStats(
                    total=theory_total,
                    completed=theory_completed
                ),
                subCategories=[]  # Упрощенная версия без подкатегорий
            )

            roadmap_data.append(category_data)

        return RoadmapStats(categories=roadmap_data)

    # Вспомогательные методы
    async def get_content_blocks_with_progress(self, user_id: int) -> List[Any]:
        return self.db_session.query(ContentBlock, UserContentProgress).join(
            ContentFile, ContentBlock.fileId == ContentFile.id
        ).outerjoin(
            UserContentProgress,
            (UserContentProgress.blockId == ContentBlock.id) &
            (UserContentProgress.userId == user_id)
        ).all()

    async def get_theory_cards_with_progress(self, user_id: int) -> List[Any]:
        return self.db_session.query(TheoryCard, UserTheoryProgress).outerjoin(
            UserTheoryProgress,
            (UserTheoryProgress.cardId == TheoryCard.id) &
            (UserTheoryProgress.userId == user_id)
        ).all()

    async def get_content_categories(self) -> List[tuple]:
        return self.db_session.query(ContentFile.mainCategory, ContentFile.subCategory).distinct().order_by(
            ContentFile.mainCategory.asc(), ContentFile.subCategory.asc()
        ).all()

    async def get_theory_categories(self) -> List[tuple]:
        return self.db_session.query(TheoryCard.category, TheoryCard.subCategory).distinct().order_by(
            TheoryCard.category.asc(), TheoryCard.subCategory.asc()
        ).all()

    async def get_content_blocks_by_category(self, category: str) -> List[Any]:
        return self.db_session.query(ContentBlock).join(ContentFile).filter(
            ContentFile.mainCategory == category
        ).all()

    async def get_theory_cards_by_category(self, category: str) -> List[Any]:
        return self.db_session.query(TheoryCard).filter(
            TheoryCard.category == category
        ).all()

    async def get_user_content_progress_for_blocks(self, user_id: int, block_ids: List[str]) -> List[Any]:
        return self.db_session.query(UserContentProgress).filter(
            UserContentProgress.userId == user_id,
            UserContentProgress.blockId.in_(block_ids)
        ).all()

    async def get_user_theory_progress_for_cards(self, user_id: int, card_ids: List[str]) -> List[Any]:
        return self.db_session.query(UserTheoryProgress).filter(
            UserTheoryProgress.userId == user_id,
            UserTheoryProgress.cardId.in_(card_ids)
        ).all() 