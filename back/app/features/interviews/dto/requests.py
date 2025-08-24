"""Request DTO для interviews API"""

from typing import Optional

from pydantic import BaseModel


class InterviewFiltersRequest(BaseModel):
    """Фильтры для поиска интервью"""

    company: Optional[str] = None
    technology: Optional[str] = None
    difficulty: Optional[int] = None
    stage: Optional[int] = None
    search: Optional[str] = None


class PaginationRequest(BaseModel):
    """Параметры пагинации"""

    page: int = 1
    limit: int = 20
