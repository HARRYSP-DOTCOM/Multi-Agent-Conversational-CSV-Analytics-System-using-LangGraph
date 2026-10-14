"""
Unit tests verifying Functional Programming concepts:
- map(), filter(), and functools.reduce()
- functools.partial() application
- List, Dictionary, and Set comprehensions
- itertools.groupby
- Pipeline chaining
"""

import unittest
from functools import partial
from utils.functional_tools import (
    apply_pipeline,
    filter_numeric_columns,
    map_column_names,
    build_schema_dict_comprehension,
    extract_unique_datatypes_set_comprehension,
    compute_column_aggregations,
    group_columns_by_type,
)


class TestFunctionalTools(unittest.TestCase):
    """Test suite for functional programming utilities."""

    def test_filter_numeric_columns(self):
        """Verifies higher-order `filter` extracts numeric columns."""
        metadata = [
            {"name": "id", "datatype": "int"},
            {"name": "name", "datatype": "string"},
            {"name": "salary", "datatype": "float"},
            {"name": "joined", "datatype": "date"},
        ]
        numeric_cols = filter_numeric_columns(metadata)
        self.assertEqual(numeric_cols, ["id", "salary"])

    def test_map_column_names(self):
        """Verifies higher-order `map` sanitizes column strings."""
        raw_cols = ["First Name", "Last-Name", "Annual Salary ", "Department"]
        sanitized = map_column_names(raw_cols)
        self.assertEqual(sanitized, ["first_name", "last_name", "annual_salary", "department"])

    def test_dict_and_set_comprehensions(self):
        """Verifies dictionary and set comprehensions."""
        metadata = [
            {"name": "age", "datatype": "int"},
            {"name": "score", "datatype": "float"},
            {"name": "grade", "datatype": "string"},
            {"name": "weight", "datatype": "float"},
        ]

        schema_dict = build_schema_dict_comprehension(metadata)
        self.assertEqual(schema_dict["age"], "int")
        self.assertEqual(schema_dict["grade"], "string")

        unique_types = extract_unique_datatypes_set_comprehension(metadata)
        self.assertEqual(unique_types, {"int", "float", "string"})

    def test_reduce_aggregations(self):
        """Verifies functools.reduce computes statistical sums."""
        numbers = [10.0, 20.0, 30.0, 40.0]
        summary = compute_column_aggregations(numbers)
        self.assertEqual(summary["sum"], 100.0)
        self.assertEqual(summary["mean"], 25.0)
        self.assertEqual(summary["min"], 10.0)
        self.assertEqual(summary["max"], 40.0)

    def test_partial_function_application(self):
        """Verifies functools.partial fixes prefix or arguments."""
        def format_metric(prefix: str, unit: str, val: float) -> str:
            return f"{prefix}: {val:.2f} {unit}"

        # Partial application fixing prefix and unit
        format_usd = partial(format_metric, "Total Revenue", "USD")
        self.assertEqual(format_usd(val=1250.5), "Total Revenue: 1250.50 USD")

    def test_pipeline_chaining(self):
        """Verifies reduce-based function pipeline composition."""
        raw_data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

        step1 = lambda numbers: [x for x in numbers if x % 2 == 0]      # Filter evens: [2, 4, 6, 8, 10]
        step2 = lambda numbers: [x * 10 for x in numbers]               # Multiply by 10: [20, 40, 60, 80, 100]
        step3 = lambda numbers: [x for x in numbers if x > 50]          # Filter > 50: [60, 80, 100]

        pipeline_result = list(apply_pipeline(raw_data, step1, step2, step3))
        self.assertEqual(pipeline_result, [60, 80, 100])

    def test_groupby(self):
        """Verifies itertools.groupby groups columns by data type."""
        metadata = [
            {"name": "id", "datatype": "int"},
            {"name": "age", "datatype": "int"},
            {"name": "salary", "datatype": "float"},
            {"name": "name", "datatype": "string"},
        ]
        grouped = group_columns_by_type(metadata)
        self.assertEqual(sorted(grouped["int"]), ["age", "id"])
        self.assertEqual(grouped["float"], ["salary"])
        self.assertEqual(grouped["string"], ["name"])


if __name__ == "__main__":
    unittest.main()
