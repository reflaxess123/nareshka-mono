"""Исключения stats feature"""

from .stats_exceptions import (
    StatsAggregationError,
    StatsCalculationError,
    StatsDataNotFoundError,
    StatsError,
    StatsPermissionError,
)

__all__ = [
    "StatsError",
    "StatsCalculationError",
    "StatsDataNotFoundError",
    "StatsAggregationError",
    "StatsPermissionError",
]
