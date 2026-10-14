"""
Unit tests verifying Custom Exception Hierarchy:
- Base exception inheritance (CSVAnalyticsError)
- Domain specific subclassing (DataIngestionError, AgentExecutionError)
- Custom attributes (error_code, details, timestamp)
- Rich string representations (__str__, __repr__)
- Exception chaining (raise ... from ...)
"""

import unittest
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
    ConfigurationError,
)


class TestCustomExceptions(unittest.TestCase):
    """Test suite for domain exception tree."""

    def test_base_exception_inheritance(self):
        """Verifies that all domain exceptions derive from CSVAnalyticsError and Exception."""
        err = DatasetNotFoundError("/path/to/missing.csv")
        self.assertIsInstance(err, CSVAnalyticsError)
        self.assertIsInstance(err, DataIngestionError)
        self.assertIsInstance(err, Exception)

    def test_custom_attributes_and_string_representation(self):
        """Verifies error_code, details dictionary, and string formatting."""
        err = ColumnNotFoundError("revenue", ["id", "price", "quantity"])
        self.assertEqual(err.error_code, "COLUMN_NOT_FOUND")
        self.assertEqual(err.details["column_name"], "revenue")
        self.assertIn("revenue", str(err))
        self.assertIn("COLUMN_NOT_FOUND", repr(err))

    def test_exception_chaining(self):
        """Verifies explicit exception chaining using `raise ... from ...`."""
        try:
            try:
                int("not_a_number")
            except ValueError as original_error:
                raise InvalidCSVFormatError("data.csv", "Could not parse number") from original_error
        except InvalidCSVFormatError as caught:
            self.assertIsNotNone(caught.__cause__)
            self.assertIsInstance(caught.__cause__, ValueError)

    def test_agent_execution_exceptions(self):
        """Verifies agent-specific execution errors."""
        query_err = QueryGenerationError("query_agent", "Summarize total profit", "Ollama connection refused")
        self.assertEqual(query_err.agent_name, "query_agent")
        self.assertEqual(query_err.error_code, "QUERY_GEN_FAILED")

        code_err = CodeExecutionError("analysis_agent", "df['unknown'].sum()", "KeyError: 'unknown'")
        self.assertEqual(code_err.agent_name, "analysis_agent")
        self.assertEqual(code_err.error_code, "CODE_EXECUTION_FAILED")


if __name__ == "__main__":
    unittest.main()
