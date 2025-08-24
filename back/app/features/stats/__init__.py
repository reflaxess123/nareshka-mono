"""Stats Feature"""

# DTOs
from app.features.stats.dto.responses import (
    ContentBlockStatsResponse,
    ContentStatsResponse,
    OverallProgressResponse,
    RoadmapStatsResponse,
    StatsHealthResponse,
    TheoryCardStatsResponse,
    TheoryStatsResponse,
    UserStatsOverviewResponse,
)

# Exceptions
from app.features.stats.exceptions.stats_exceptions import (
    StatsAggregationError,
    StatsCalculationError,
    StatsDataNotFoundError,
    StatsError,
    StatsPermissionError,
)

# Repository
from app.features.stats.repositories.stats_repository import StatsRepository

# Services
from app.features.stats.services.stats_service import StatsService

# Router импортируется напрямую в main.py для избежания циклических импортов

__all__ = [
    # DTOs Responses
    "UserStatsOverviewResponse",
    "ContentStatsResponse",
    "TheoryStatsResponse",
    "RoadmapStatsResponse",
    "OverallProgressResponse",
    "ContentBlockStatsResponse",
    "TheoryCardStatsResponse",
    "StatsHealthResponse",
    # Services
    "StatsService",
    # Repository
    "StatsRepository",
    # Exceptions
    "StatsError",
    "StatsCalculationError",
    "StatsDataNotFoundError",
    "StatsAggregationError",
    "StatsPermissionError",
]
