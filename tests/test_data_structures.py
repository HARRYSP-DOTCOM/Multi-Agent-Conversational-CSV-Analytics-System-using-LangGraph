"""
Unit tests verifying Data Structures and Typing:
- NamedTuples (TokenStat, DatasetFingerprint)
- Dataclasses with frozen=True and slots=True
- Custom DatasetContainer with rich Magic / Dunder methods:
    __len__, __getitem__, __contains__, __iter__, __repr__, __str__, __eq__
- Encapsulated properties with validation (@property and @setter)
- Advanced collections (defaultdict, Counter, deque)
- Enums (DataType, AgentRoute, ExecutionStatus)
"""

import unittest
from collections import defaultdict, Counter, deque
from dataclasses import FrozenInstanceError
import pandas as pd

from core.models import (
    TokenStat,
    DatasetFingerprint,
    ColumnProfile,
    DatasetManifest,
    DatasetContainer,
)
from core.enums import DataType, AgentRoute, ExecutionStatus, QueryIntent


class TestDataStructures(unittest.TestCase):
    """Test suite for domain data models and standard collections."""

    def test_namedtuple_creation_and_field_access(self):
        """Verifies namedtuple creation and attribute access."""
        stat = TokenStat(token="revenue", frequency=42, is_stop_word=False)
        self.assertEqual(stat.token, "revenue")
        self.assertEqual(stat.frequency, 42)
        self.assertFalse(stat.is_stop_word)

        fingerprint = DatasetFingerprint("sales.csv", "abc123hash", 1024, 1600000000.0)
        self.assertEqual(fingerprint.filename, "sales.csv")
        self.assertEqual(fingerprint.byte_size, 1024)

    def test_dataclass_immutability(self):
        """Verifies frozen dataclass prevents attribute mutation."""
        profile = ColumnProfile(
            name="age",
            data_type=DataType.INTEGER,
            missing_count=0,
            unique_count=50,
            min_value=18,
            max_value=75,
            mean_value=35.5,
        )
        self.assertEqual(profile.name, "age")
        self.assertEqual(profile.data_type, DataType.INTEGER)

        # Attempting to mutate a frozen dataclass must raise FrozenInstanceError
        with self.assertRaises(FrozenInstanceError):
            profile.name = "new_age"  # type: ignore

    def test_dataset_container_dunder_methods(self):
        """Verifies all magic methods of DatasetContainer."""
        df = pd.DataFrame({
            "employee": ["Alice", "Bob", "Charlie"],
            "salary": [70000, 85000, 92000],
            "department": ["Eng", "Sales", "Eng"],
        })
        container = DatasetContainer("staff", df)

        # __len__
        self.assertEqual(len(container), 3)

        # __getitem__ for column string
        salaries = container["salary"]
        self.assertEqual(list(salaries), [70000, 85000, 92000])

        # __getitem__ for row integer
        first_row = container[0]
        self.assertEqual(first_row["employee"], "Alice")

        # __contains__ ('in' operator)
        self.assertTrue("salary" in container)
        self.assertFalse("bonus" in container)

        # __iter__ (iterates over column names)
        cols = [col for col in container]
        self.assertEqual(cols, ["employee", "salary", "department"])

        # __repr__ and __str__
        self.assertIn("DatasetContainer(name='staff'", repr(container))
        self.assertIn("Dataset 'staff' [3 rows x 3 cols]", str(container))

        # __eq__
        container2 = DatasetContainer("staff", df)
        self.assertEqual(container, container2)

    def test_dataset_container_property_validation(self):
        """Verifies @property and @setter validation on DatasetContainer."""
        df = pd.DataFrame({"x": [1, 2, 3]})
        container = DatasetContainer("valid_name", df)

        # Valid rename
        container.name = "updated_name"
        self.assertEqual(container.name, "updated_name")

        # Empty string rejection
        with self.assertRaises(ValueError):
            container.name = ""

        # Whitespace rejection
        with self.assertRaises(ValueError):
            container.name = "   "

    def test_collections_defaultdict_counter_deque(self):
        """Verifies usage of advanced collections: defaultdict, Counter, and deque."""
        # defaultdict
        dept_members = defaultdict(list)
        dept_members["Eng"].append("Alice")
        dept_members["Eng"].append("Charlie")
        dept_members["Sales"].append("Bob")
        self.assertEqual(len(dept_members["Eng"]), 2)
        self.assertEqual(len(dept_members["Marketing"]), 0)  # auto-creates empty list

        # Counter
        types = Counter(["int", "float", "int", "string", "int", "string"])
        self.assertEqual(types["int"], 3)
        self.assertEqual(types.most_common(1)[0], ("int", 3))

        # deque with maxlen (rolling history window)
        rolling_queries = deque(maxlen=3)
        rolling_queries.append("query 1")
        rolling_queries.append("query 2")
        rolling_queries.append("query 3")
        rolling_queries.append("query 4")  # "query 1" drops off
        self.assertEqual(len(rolling_queries), 3)
        self.assertEqual(rolling_queries[0], "query 2")
        self.assertEqual(rolling_queries[-1], "query 4")

    def test_enums(self):
        """Verifies enum behaviors and helper methods."""
        self.assertTrue(DataType.INTEGER.is_numeric)
        self.assertTrue(DataType.FLOAT.is_numeric)
        self.assertFalse(DataType.STRING.is_numeric)

        self.assertTrue(AgentRoute.WEB.is_external())
        self.assertTrue(AgentRoute.HYBRID.is_external())
        self.assertFalse(AgentRoute.CSV.is_external())


if __name__ == "__main__":
    unittest.main()
