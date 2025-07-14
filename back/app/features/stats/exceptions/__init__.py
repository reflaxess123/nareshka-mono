"""Исключения stats feature"""

from .stats_exceptions import (
    StatsError,
    StatsCalculationError,
    StatsDataNotFoundError,
    StatsAggregationError,
    StatsPermissionError,
)

__all__ = [
    "StatsError",
    "StatsCalculationError", 
    "StatsDataNotFoundError",
    "StatsAggregationError",
    "StatsPermissionError",
] 



