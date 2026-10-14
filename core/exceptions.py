"""
Custom exception hierarchy for the CSV Analytics Multi-Agent System.

Demonstrates:
- Object-Oriented Exception hierarchy design (Base -> Domain -> Specific)
- Custom attributes (`error_code`, `timestamp`, `details`)
- Overriding `__str__` and `__repr__` for rich debugging
- Exception chaining support (`raise SubException from OriginalException`)
"""

import time
from typing import Optional, Dict, Any


class CSVAnalyticsError(Exception):
    """
    Root base exception for all domain-specific errors in this application.
    Enables callers to catch any application exception using a single broad handler.
    """

    def __init__(
        self,
        message: str,
        error_code: str = "GENERIC_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.timestamp = time.time()

    def __str__(self) -> str:
        base_msg = f"[{self.error_code}] {self.message}"
        if self.details:
            base_msg += f" | Details: {self.details}"
        return base_msg

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(error_code={self.error_code!r}, "
            f"message={self.message!r}, details={self.details!r})"
        )


# ============================================================================
# Data Ingestion & Dataset Exceptions
# ============================================================================


class DataIngestionError(CSVAnalyticsError):
    """Base exception for errors during dataset loading, parsing, or profiling."""

    def __init__(
        self,
        message: str,
        error_code: str = "INGESTION_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, error_code, details)


class DatasetNotFoundError(DataIngestionError):
    """Raised when a requested CSV file does not exist on disk."""

    def __init__(self, filepath: str) -> None:
        super().__init__(
            message=f"Dataset file not found at: {filepath}",
            error_code="DATASET_NOT_FOUND",
            details={"filepath": filepath},
        )


class InvalidCSVFormatError(DataIngestionError):
    """Raised when a file cannot be parsed as valid CSV tabular data."""

    def __init__(self, filepath: str, reason: str) -> None:
        super().__init__(
            message=f"Invalid CSV structure in '{filepath}': {reason}",
            error_code="INVALID_CSV_FORMAT",
            details={"filepath": filepath, "reason": reason},
        )


class EmptyDatasetError(DataIngestionError):
    """Raised when a CSV file is completely empty or has zero rows."""

    def __init__(self, dataset_name: str) -> None:
        super().__init__(
            message=f"Dataset '{dataset_name}' contains zero rows or columns.",
            error_code="EMPTY_DATASET",
            details={"dataset_name": dataset_name},
        )


class ColumnNotFoundError(DataIngestionError):
    """Raised when a requested column does not exist in the dataset."""

    def __init__(self, column_name: str, available_columns: list) -> None:
        super().__init__(
            message=f"Column '{column_name}' not found. Available columns: {available_columns}",
            error_code="COLUMN_NOT_FOUND",
            details={"column_name": column_name, "available_columns": available_columns},
        )


# ============================================================================
# Agent Workflow & Execution Exceptions
# ============================================================================


class AgentExecutionError(CSVAnalyticsError):
    """Base exception for failures during agent workflow processing."""

    def __init__(
        self,
        message: str,
        agent_name: str,
        error_code: str = "AGENT_EXECUTION_ERROR",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        details = details or {}
        details["agent_name"] = agent_name
        super().__init__(message, error_code, details)
        self.agent_name = agent_name


class QueryGenerationError(AgentExecutionError):
    """Raised when the Query Agent or LLM fails to synthesize executable code."""

    def __init__(self, agent_name: str, prompt: str, underlying_error: Optional[str] = None) -> None:
        super().__init__(
            message="Failed to generate executable analytics code from query.",
            agent_name=agent_name,
            error_code="QUERY_GEN_FAILED",
            details={"prompt_preview": prompt[:120], "underlying_error": underlying_error},
        )


class CodeExecutionError(AgentExecutionError):
    """Raised when generated code fails during sandbox execution."""

    def __init__(self, agent_name: str, code: str, traceback_str: str) -> None:
        super().__init__(
            message="Sandbox execution failed with runtime error.",
            agent_name=agent_name,
            error_code="CODE_EXECUTION_FAILED",
            details={"code_snippet": code[:150], "traceback": traceback_str},
        )


class RouteSelectionError(AgentExecutionError):
    """Raised when the Planner cannot decide on a viable workflow route."""

    def __init__(self, agent_name: str, question: str) -> None:
        super().__init__(
            message=f"Planner could not determine route for question: '{question}'",
            agent_name=agent_name,
            error_code="ROUTE_SELECTION_FAILED",
            details={"question": question},
        )


# ============================================================================
# System Configuration & Embedding Exceptions
# ============================================================================


class ConfigurationError(CSVAnalyticsError):
    """Raised when environment variables or necessary configurations are missing."""

    def __init__(self, missing_param: str) -> None:
        super().__init__(
            message=f"Missing required configuration parameter: {missing_param}",
            error_code="MISSING_CONFIGURATION",
            details={"missing_param": missing_param},
        )


class EmbeddingError(CSVAnalyticsError):
    """Raised when semantic vector indexing or lookup fails."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            message=message,
            error_code="EMBEDDING_FAILURE",
            details=details,
        )
