"""
Унифицированная пагинация для API
"""

from typing import Any, Dict, Generic, List, Optional, TypeVar

from fastapi import Query
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import (
    Query as SQLQuery,
)

from app.core.logging import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Параметры пагинации"""

    page: int = Field(1, ge=1, description="Номер страницы")
    limit: int = Field(10, ge=1, le=100, description="Количество элементов на странице")

    @field_validator("page")
    def validate_page(cls, v):
        if v < 1:
            raise ValueError("Page must be greater than 0")
        return v

    @field_validator("limit")
    def validate_limit(cls, v):
        if v < 1:
            raise ValueError("Limit must be greater than 0")
        if v > 100:
            raise ValueError("Limit must be less than or equal to 100")
        return v

    @property
    def offset(self) -> int:
        """Вычисляет offset для запроса"""
        return (self.page - 1) * self.limit


class PaginatedResponse(BaseModel, Generic[T]):
    """Ответ с пагинацией"""

    items: List[T] = Field(description="Список элементов")
    total: int = Field(description="Общее количество элементов")
    page: int = Field(description="Текущая страница")
    limit: int = Field(description="Количество элементов на странице")
    pages: int = Field(description="Общее количество страниц")
    has_next: bool = Field(description="Есть ли следующая страница")
    has_prev: bool = Field(description="Есть ли предыдущая страница")

    @classmethod
    def create(
        cls, items: List[T], total: int, pagination: PaginationParams
    ) -> "PaginatedResponse[T]":
        """Создать пагинированный ответ"""
        pages = (total + pagination.limit - 1) // pagination.limit if total > 0 else 1

        return cls(
            items=items,
            total=total,
            page=pagination.page,
            limit=pagination.limit,
            pages=pages,
            has_next=pagination.page < pages,
            has_prev=pagination.page > 1,
        )


class PaginationHelper:
    """Помощник для работы с пагинацией"""

    @staticmethod
    def paginate_query(
        query: SQLQuery, pagination: PaginationParams
    ) -> tuple[List[Any], int]:
        """
        Пагинировать SQLAlchemy запрос

        Args:
            query: SQLAlchemy запрос
            pagination: Параметры пагинации

        Returns:
            Tuple из (элементы, общее количество)
        """
        # Получаем общее количество
        total = query.count()

        # Применяем пагинацию
        items = query.offset(pagination.offset).limit(pagination.limit).all()

        logger.debug(
            "Query paginated",
            extra={
                "total": total,
                "page": pagination.page,
                "limit": pagination.limit,
                "items_count": len(items),
            },
        )

        return items, total

    @staticmethod
    def paginate_list(
        items: List[T], pagination: PaginationParams
    ) -> tuple[List[T], int]:
        """
        Пагинировать список в памяти

        Args:
            items: Список элементов
            pagination: Параметры пагинации

        Returns:
            Tuple из (элементы, общее количество)
        """
        total = len(items)
        start = pagination.offset
        end = start + pagination.limit

        paginated_items = items[start:end]

        logger.debug(
            "List paginated",
            extra={
                "total": total,
                "page": pagination.page,
                "limit": pagination.limit,
                "items_count": len(paginated_items),
            },
        )

        return paginated_items, total

    @staticmethod
    def create_response(
        items: List[T], total: int, pagination: PaginationParams
    ) -> PaginatedResponse[T]:
        """Создать пагинированный ответ"""
        return PaginatedResponse.create(items, total, pagination)


def create_pagination_dependency():
    """Создать dependency для пагинации"""

    def get_pagination_params(
        page: int = Query(1, ge=1, description="Номер страницы"),
        limit: int = Query(
            10, ge=1, le=100, description="Количество элементов на странице"
        ),
    ) -> PaginationParams:
        return PaginationParams(page=page, limit=limit)

    return get_pagination_params


# Готовый dependency для использования в роутерах
PaginationDep = create_pagination_dependency()


class SortingParams(BaseModel):
    """Параметры сортировки"""

    sort_by: str = Field("id", description="Поле для сортировки")
    sort_order: str = Field("asc", description="Порядок сортировки (asc/desc)")

    @field_validator("sort_order")
    def validate_sort_order(cls, v):
        if v.lower() not in ["asc", "desc"]:
            raise ValueError('Sort order must be either "asc" or "desc"')
        return v.lower()


class FilterParams(BaseModel):
    """Базовые параметры фильтрации"""

    search: Optional[str] = Field(None, description="Строка поиска")

    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать в словарь, исключив None значения"""
        return {k: v for k, v in self.dict().items() if v is not None}


class PaginatedQueryBuilder:
    """Строитель для создания пагинированных запросов"""

    def __init__(self, query: SQLQuery):
        self.query = query
        self.filters = {}
        self.sorting = None

    def add_filter(self, field: str, value: Any, operator: str = "eq"):
        """Добавить фильтр"""
        self.filters[field] = (value, operator)
        return self

    def add_search(self, search_fields: List[str], search_term: str):
        """Добавить поиск по нескольким полям"""
        if search_term:
            from sqlalchemy import or_

            search_conditions = []
            for field in search_fields:
                # Предполагаем, что поле - это атрибут модели
                search_conditions.append(
                    getattr(self.query.column_descriptions[0]["entity"], field).ilike(
                        f"%{search_term}%"
                    )
                )

            if search_conditions:
                self.query = self.query.filter(or_(*search_conditions))

        return self

    def add_sorting(self, sort_by: str, sort_order: str):
        """Добавить сортировку"""
        self.sorting = (sort_by, sort_order)
        return self

    def build(self, pagination: PaginationParams) -> PaginatedResponse:
        """Построить и выполнить запрос"""
        # Применяем фильтры
        for field, (value, operator) in self.filters.items():
            # Простая реализация фильтрации
            if operator == "eq":
                self.query = self.query.filter(
                    getattr(self.query.column_descriptions[0]["entity"], field) == value
                )
            elif operator == "in":
                self.query = self.query.filter(
                    getattr(self.query.column_descriptions[0]["entity"], field).in_(
                        value
                    )
                )

        # Применяем сортировку
        if self.sorting:
            sort_by, sort_order = self.sorting
            column = getattr(self.query.column_descriptions[0]["entity"], sort_by)
            if sort_order == "desc":
                self.query = self.query.order_by(column.desc())
            else:
                self.query = self.query.order_by(column.asc())

        # Применяем пагинацию
        items, total = PaginationHelper.paginate_query(self.query, pagination)

        return PaginationHelper.create_response(items, total, pagination)


# Utility функции для создания стандартных dependency
def create_sorting_dependency(
    default_sort_by: str = "id", allowed_fields: Optional[List[str]] = None
):
    """Создать dependency для сортировки"""

    def get_sorting_params(
        sort_by: str = Query(default_sort_by, description="Поле для сортировки"),
        sort_order: str = Query("asc", description="Порядок сортировки (asc/desc)"),
    ) -> SortingParams:
        # Проверяем, что поле разрешено для сортировки
        if allowed_fields and sort_by not in allowed_fields:
            raise ValueError(
                f"Sorting by '{sort_by}' is not allowed. Allowed fields: {allowed_fields}"
            )

        return SortingParams(sort_by=sort_by, sort_order=sort_order)

    return get_sorting_params


def create_filter_dependency(filter_model: type):
    """Создать dependency для фильтрации"""

    def get_filter_params() -> filter_model:
        return filter_model()

    return get_filter_params
