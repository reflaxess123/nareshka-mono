"""
Content Feature Request DTOs

Модели запросов для API endpoints контента.
"""

from typing import Literal

from pydantic import BaseModel, Field


class ProgressAction(BaseModel):
    """Действие для обновления прогресса пользователя по контенту"""

    action: Literal["increment", "decrement"] = Field(
        ..., description="Тип действия: increment (увеличить) или decrement (уменьшить)"
    )



