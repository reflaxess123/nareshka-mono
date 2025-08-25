"""Task types для внутреннего использования в services и repositories."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.shared.models.enums import CodeLanguage


class TaskType(BaseModel):
    """Тип задачи"""

    name: str
    display_name: str
    description: Optional[str] = None


class TaskCategory(BaseModel):
    """Категория задач"""

    main_category: str
    sub_category: Optional[str] = None
    task_count: int = 0


class TaskCompany(BaseModel):
    """Компания из задач"""

    company: str
    task_count: int = 0


class Task(BaseModel):
    """Задача/задание"""

    id: str
    title: str
    description: Optional[str] = None
    main_category: str
    sub_category: Optional[str] = None
    item_type: str  # 'content_block' или 'theory_quiz'
    difficulty: Optional[str] = None
    companies: List[str] = []
    tags: List[str] = []
    code_content: Optional[str] = None
    code_language: Optional[CodeLanguage] = None
    is_solved: bool = False
    progress_percentage: float = 0.0
    order_in_file: int = 0
    current_user_solved_count: int = 0  # Количество решений пользователя

    # Дополнительные поля для content_block
    file_id: Optional[str] = None
    file_path: Optional[str] = None
    path_titles: List[str] = []
    block_level: Optional[int] = None
    text_content: Optional[str] = None
    is_code_foldable: Optional[bool] = None
    code_fold_title: Optional[str] = None
    extracted_urls: List[str] = []

    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_content_block(cls, block, progress=None):
        """Создание Task из ContentBlock"""
        # Получаем данные из связи с файлом
        main_category = "Общее"
        sub_category = None

        if hasattr(block, "file") and block.file:
            main_category = block.file.mainCategory
            sub_category = block.file.subCategory

        # Маппинг языков программирования
        language_mapping = {
            "js": CodeLanguage.JAVASCRIPT,
            "javascript": CodeLanguage.JAVASCRIPT,
            "ts": CodeLanguage.TYPESCRIPT,
            "typescript": CodeLanguage.TYPESCRIPT,
            "py": CodeLanguage.PYTHON,
            "python": CodeLanguage.PYTHON,
            "java": CodeLanguage.JAVA,
            "cpp": CodeLanguage.CPP,
            "c++": CodeLanguage.CPP,
            "c": CodeLanguage.C,
            "go": CodeLanguage.GO,
            "rust": CodeLanguage.RUST,
            "php": CodeLanguage.PHP,
            "ruby": CodeLanguage.RUBY,
            "rb": CodeLanguage.RUBY,
        }

        code_language = None
        if block.codeLanguage:
            code_language = language_mapping.get(block.codeLanguage.lower())
            if not code_language:
                try:
                    code_language = CodeLanguage(block.codeLanguage.upper())
                except ValueError:
                    code_language = None

        return cls(
            id=block.id,
            title=block.blockTitle or "Без названия",
            description=block.textContent,
            main_category=main_category,
            sub_category=sub_category,
            item_type="content_block",
            difficulty=None,
            companies=block.companies or [],
            tags=[],
            code_content=block.codeContent,
            code_language=code_language,
            is_solved=progress.solvedCount > 0 if progress else False,
            progress_percentage=min(progress.solvedCount * 100.0, 100.0)
            if progress
            else 0.0,
            order_in_file=block.orderInFile,
            created_at=block.createdAt,
            updated_at=block.updatedAt,
        )

    @classmethod
    def from_theory_card(cls, card, progress=None):
        """Создание Task из TheoryCard"""
        return cls(
            id=card.id,
            title=card.questionBlock or "Теория",
            description=card.answerBlock,
            main_category=card.category,
            sub_category=card.subCategory,
            item_type="theory_quiz",
            difficulty=None,
            companies=[],
            tags=[],
            code_content=None,
            code_language=None,
            is_solved=progress.solvedCount > 0 if progress else False,
            progress_percentage=min(progress.solvedCount * 100.0, 100.0)
            if progress
            else 0.0,
            order_in_file=card.orderIndex if hasattr(card, "orderIndex") else 0,
            created_at=card.createdAt,
            updated_at=card.updatedAt,
        )
