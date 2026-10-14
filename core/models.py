"""
Domain data models, containers, and immutable structures.

Demonstrates:
- Python `@dataclass` with `frozen=True` and `slots=True` for memory efficiency and immutability
- Standard library `collections.namedtuple`
- Rich Magic/Dunder methods (`__len__`, `__getitem__`, `__contains__`, `__iter__`, `__repr__`, `__str__`, `__eq__`)
- Managed attributes with `@property` and `@setter` (Encapsulation and validation)
- Custom generator methods using `yield` for memory-efficient chunk streaming
"""

import time
from collections import namedtuple
from dataclasses import dataclass, field, asdict
from typing import (
    List,
    Dict,
    Any,
    Optional,
    Generator,
    Union,
    Iterator,
)
import pandas as pd
from core.enums import DataType, ExecutionStatus

# ============================================================================
# NamedTuples (Lightweight Immutable Records)
# ============================================================================

TokenStat = namedtuple("TokenStat", ["token", "frequency", "is_stop_word"])
DatasetFingerprint = namedtuple("DatasetFingerprint", ["filename", "sha256_hash", "byte_size", "modified_time"])


# ============================================================================
# Dataclasses (Strongly Typed Structural Models)
# ============================================================================


@dataclass(frozen=True, slots=True)
class ColumnProfile:
    """
    Immutable representation of an individual column profile.
    Demonstrates frozen dataclass with slots for fast attribute access and immutability.
    """
    name: str
    data_type: DataType
    missing_count: int
    unique_count: int
    min_value: Optional[Union[float, int, str]] = None
    max_value: Optional[Union[float, int, str]] = None
    mean_value: Optional[float] = None
    top_values: List[Any] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert dataclass to standard JSON-serializable dictionary."""
        d = asdict(self)
        d["data_type"] = self.data_type.value
        return d


@dataclass(frozen=True, slots=True)
class DatasetManifest:
    """
    Immutable manifest detailing dataset dimensions, profiles, and fingerprint.
    """
    dataset_name: str
    row_count: int
    column_count: int
    columns: List[ColumnProfile]
    sha256_hash: str
    created_at: float = field(default_factory=time.time)

    def get_column(self, name: str) -> Optional[ColumnProfile]:
        """Case-insensitive column lookup."""
        target = name.strip().lower()
        for col in self.columns:
            if col.name.strip().lower() == target:
                return col
        return None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dataset": self.dataset_name,
            "row_count": self.row_count,
            "column_count": self.column_count,
            "columns": [c.to_dict() for c in self.columns],
            "sha256_hash": self.sha256_hash,
            "created_at": self.created_at,
        }


@dataclass
class ExecutionReport:
    """
    Mutable status report captured after executing generated code.
    """
    status: ExecutionStatus
    duration_seconds: float
    output_type: str
    result_data: Any = None
    error_message: Optional[str] = None
    retry_attempt: int = 0

    @property
    def is_success(self) -> bool:
        """Property getter checking if execution succeeded."""
        return self.status == ExecutionStatus.SUCCESS


# ============================================================================
# Rich Object-Oriented Container with Dunder / Magic Methods
# ============================================================================


class DatasetContainer:
    """
    Encapsulated data container wrapping a Pandas DataFrame.

    Demonstrates:
    - Encapsulation with protected attributes (`_name`, `_df`)
    - Property getters and setters with validation (`@property`, `@name.setter`)
    - Magic Dunder methods:
        - `__len__`: enables `len(dataset)`
        - `__getitem__`: enables `dataset['column_name']` and `dataset[row_idx]`
        - `__contains__`: enables `'sales' in dataset`
        - `__iter__`: enables `for column in dataset:`
        - `__repr__` and `__str__`: canonical and friendly string representation
        - `__eq__`: value-based comparison
    - Generator method with `yield` for chunked streaming
    """

    def __init__(self, name: str, dataframe: pd.DataFrame) -> None:
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Dataset name must be a non-empty string.")
        if not isinstance(dataframe, pd.DataFrame):
            raise TypeError("dataframe parameter must be an instance of pandas.DataFrame.")

        self._name = name.strip()
        self._df = dataframe.copy()
        self._created_at = time.time()

    # --- Property Getters & Setters ---

    @property
    def name(self) -> str:
        """Returns the dataset name."""
        return self._name

    @name.setter
    def name(self, new_name: str) -> None:
        """Sets dataset name with validation."""
        if not isinstance(new_name, str) or not new_name.strip():
            raise ValueError("New dataset name must be a non-empty string.")
        self._name = new_name.strip()

    @property
    def dataframe(self) -> pd.DataFrame:
        """Returns the internal pandas DataFrame."""
        return self._df

    @property
    def shape(self) -> tuple:
        """Returns (rows, columns) dimensions."""
        return self._df.shape

    @property
    def columns(self) -> List[str]:
        """Returns list of column names."""
        return list(self._df.columns)

    # --- Magic / Dunder Methods ---

    def __len__(self) -> int:
        """Enables `len(container)` returning the number of rows."""
        return len(self._df)

    def __getitem__(self, key: Union[str, int]) -> Any:
        """
        Enables indexing:
        - If key is string: returns DataFrame column Series
        - If key is int: returns row as Series
        """
        if isinstance(key, str):
            return self._df[key]
        elif isinstance(key, int):
            return self._df.iloc[key]
        raise TypeError(f"Invalid key type: {type(key)}. Expected str or int.")

    def __contains__(self, column_name: str) -> bool:
        """Enables `'col' in container` testing for column existence."""
        if not isinstance(column_name, str):
            return False
        return column_name in self._df.columns

    def __iter__(self) -> Iterator[str]:
        """Enables iterating over columns: `for col in container:`."""
        return iter(self._df.columns)

    def __repr__(self) -> str:
        """Official representation for debugging."""
        return (
            f"DatasetContainer(name={self._name!r}, "
            f"rows={len(self._df)}, columns={len(self._df.columns)})"
        )

    def __str__(self) -> str:
        """User-friendly representation."""
        return f"Dataset '{self._name}' [{len(self._df)} rows x {len(self._df.columns)} cols]"

    def __eq__(self, other: Any) -> bool:
        """Equality comparison between dataset containers."""
        if not isinstance(other, DatasetContainer):
            return False
        return self._name == other._name and self._df.equals(other._df)

    # --- Generator Method using `yield` ---

    def stream_chunks(self, chunk_size: int = 100) -> Generator[pd.DataFrame, None, None]:
        """
        Memory-efficient generator yielding DataFrame slices of size `chunk_size`.
        Demonstrates the Python `yield` generator protocol for streaming big datasets.
        """
        if chunk_size <= 0:
            raise ValueError("chunk_size must be a positive integer.")

        total_rows = len(self._df)
        for start_idx in range(0, total_rows, chunk_size):
            end_idx = min(start_idx + chunk_size, total_rows)
            yield self._df.iloc[start_idx:end_idx]

    def summary(self) -> Dict[str, Any]:
        """Returns structured dictionary summary of dataset."""
        return {
            "name": self._name,
            "rows": len(self._df),
            "columns": list(self._df.columns),
            "memory_usage_bytes": int(self._df.memory_usage(deep=True).sum()),
        }
