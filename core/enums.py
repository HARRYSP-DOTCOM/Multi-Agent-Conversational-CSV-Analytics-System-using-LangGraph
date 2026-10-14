"""
Domain enumerations representing system states, routes, data types, and intents.

Demonstrates:
- Standard library `enum.Enum` inheritance
- `enum.auto()` usage
- Multi-inheritance with `str` for JSON-serializable string enums
- Enum methods and introspection
"""

from enum import Enum, auto
from typing import List, Set


class QueryIntent(str, Enum):
    """
    Categorizes the analytical intent derived from a user's question.
    Inherits from (str, Enum) to ensure automatic JSON serialization.
    """
    DYNAMIC = "dynamic"
    METRIC = "metric"
    AGGREGATION = "aggregation"
    FILTER = "filter"
    COMPARISON = "comparison"
    UNKNOWN = "unknown"

    @classmethod
    def list_values(cls) -> List[str]:
        """Returns all enum string values."""
        return [intent.value for intent in cls]


class AgentRoute(str, Enum):
    """
    Routing targets decided by the Planner Agent.
    """
    CSV = "csv"
    WEB = "web"
    HYBRID = "hybrid"
    CACHED = "cached"

    def is_external(self) -> bool:
        """Determines if the route requires external network access."""
        return self in (AgentRoute.WEB, AgentRoute.HYBRID)


class ExecutionStatus(str, Enum):
    """
    Status of sandboxed code execution or query processing.
    """
    SUCCESS = "success"
    ERROR = "error"
    RETRYING = "retrying"
    TIMEOUT = "timeout"
    SKIPPED = "skipped"


class DataType(str, Enum):
    """
    Simplified column data types recognized across analytics pipelines.
    """
    INTEGER = "int"
    FLOAT = "float"
    STRING = "string"
    DATETIME = "date"
    BOOLEAN = "boolean"
    UNKNOWN = "unknown"

    @property
    def is_numeric(self) -> bool:
        """Check if the data type is numeric."""
        return self in (DataType.INTEGER, DataType.FLOAT)


class AggregationType(str, Enum):
    """
    Supported statistical aggregation operations.
    """
    SUM = "sum"
    MEAN = "mean"
    COUNT = "count"
    MIN = "min"
    MAX = "max"
    MEDIAN = "median"
    STD = "std"

    @classmethod
    def supported_operations(cls) -> Set[str]:
        """Returns a set of all valid aggregation string names."""
        return {item.value for item in cls}
