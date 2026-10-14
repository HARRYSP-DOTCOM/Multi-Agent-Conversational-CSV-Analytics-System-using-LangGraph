"""
Core package for CSV Analytics Multi-Agent System.

This package contains foundational architectural components demonstrating
advanced Python concepts:
- Abstract Base Classes (ABC) and Object-Oriented Design
- Custom Exception Hierarchies
- Advanced Metaprogramming & Decorators
- Class-based and Generator-based Context Managers
- Immutable Models and Data Structures (Dataclasses, NamedTuples, Enums)
- Centralized Logging Infrastructure
"""

__version__ = "2.0.0"
__author__ = "CSV Analytics Agent Team"

from core.enums import (
    QueryIntent,
    AgentRoute,
    ExecutionStatus,
    DataType,
    AggregationType,
)
from core.exceptions import (
    CSVAnalyticsError,
    DataIngestionError,
    DatasetNotFoundError,
    InvalidCSVFormatError,
    EmptyDatasetError,
    ColumnNotFoundError,
    AgentExecutionError,
    QueryGenerationError,
    CodeExecutionError,
    RouteSelectionError,
    ConfigurationError,
)
from core.decorators import (
    retry,
    timing_profiler,
    memoize,
    validate_non_empty,
)
from core.context_managers import (
    BenchmarkTimer,
    temporary_directory_scope,
    dataset_read_lock,
)
from core.models import (
    ColumnProfile,
    DatasetManifest,
    ExecutionReport,
    TokenStat,
    DatasetContainer,
)
from core.base_agent import BaseAgent
from core.base_service import BaseService

__all__ = [
    "QueryIntent",
    "AgentRoute",
    "ExecutionStatus",
    "DataType",
    "AggregationType",
    "CSVAnalyticsError",
    "DataIngestionError",
    "DatasetNotFoundError",
    "InvalidCSVFormatError",
    "EmptyDatasetError",
    "ColumnNotFoundError",
    "AgentExecutionError",
    "QueryGenerationError",
    "CodeExecutionError",
    "RouteSelectionError",
    "ConfigurationError",
    "retry",
    "timing_profiler",
    "memoize",
    "validate_non_empty",
    "BenchmarkTimer",
    "temporary_directory_scope",
    "dataset_read_lock",
    "ColumnProfile",
    "DatasetManifest",
    "ExecutionReport",
    "TokenStat",
    "DatasetContainer",
    "BaseAgent",
    "BaseService",
]
