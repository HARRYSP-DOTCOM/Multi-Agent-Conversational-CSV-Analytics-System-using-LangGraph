"""
Context Generator Service.

Demonstrates:
- Object-Oriented design inheriting from `BaseService`
- Dataclass models (`ColumnProfile`, `DatasetManifest`) and Enums (`DataType`)
- Concurrency with `concurrent.futures.ThreadPoolExecutor` for parallel column profiling
- Custom Context Manager (`BenchmarkTimer`) for performance tracking
- File system handling with `pathlib.Path`
- 100% backwards-compatible outputs and signatures
"""

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Dict, Any, Tuple, Optional, Union, List
import pandas as pd
from pandas.api.types import (
    is_bool_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_integer_dtype,
)

from core.base_service import BaseService
from core.enums import DataType
from core.models import ColumnProfile, DatasetManifest
from core.context_managers import BenchmarkTimer


class ContextGenerator(BaseService):
    """
    Generates rich dataset metadata, data dictionary profiles, and summary statistics.
    Inherits from `BaseService` and utilizes parallel execution for column profiling.
    """

    def __init__(self, output_directory: Union[str, Path] = "contexts", max_workers: int = 4) -> None:
        super().__init__(service_name="context_generator")
        self._output_directory = Path(output_directory)
        self._max_workers = max_workers
        self._ensure_directory()
        self._initialized = True

    @property
    def output_directory(self) -> Path:
        """Returns the output directory as a Path."""
        return self._output_directory

    def _ensure_directory(self) -> None:
        """Ensures destination directory exists."""
        self._output_directory.mkdir(parents=True, exist_ok=True)

    def detect_datatype(self, series: pd.Series) -> str:
        """
        Converts pandas series dtypes into simplified domain datatype strings.
        Maps directly to `DataType` enum values.
        """
        if is_bool_dtype(series):
            return DataType.BOOLEAN.value
        if is_numeric_dtype(series):
            if is_integer_dtype(series):
                return DataType.INTEGER.value
            return DataType.FLOAT.value
        if is_datetime64_any_dtype(series):
            return DataType.DATETIME.value
        return DataType.STRING.value

    def try_parse_date(self, series: pd.Series) -> Tuple[bool, Optional[pd.Series]]:
        """
        Tests whether a string column can be parsed into dates.
        Demonstrates `try ... except` error handling.
        """
        try:
            non_null = series.dropna()
            if non_null.empty:
                return False, None
            parsed = pd.to_datetime(non_null, errors="raise")
            return True, parsed
        except (ValueError, TypeError, OverflowError):
            return False, None

    def profile_column(self, series: pd.Series) -> Dict[str, Any]:
        """
        Profiles a single column and returns a serializable dictionary profile.
        """
        datatype_str = self.detect_datatype(series)
        dtype_enum = DataType(datatype_str)

        missing_count = int(series.isna().sum())
        non_null_series = series.dropna()
        unique_count = int(non_null_series.nunique()) if not non_null_series.empty else 0

        min_val: Optional[Union[float, int, str]] = None
        max_val: Optional[Union[float, int, str]] = None
        mean_val: Optional[float] = None
        top_values: List[Any] = []

        if dtype_enum.is_numeric and not non_null_series.empty:
            min_val = float(non_null_series.min())
            max_val = float(non_null_series.max())
            mean_val = float(non_null_series.mean())
        elif dtype_enum == DataType.STRING and not non_null_series.empty:
            is_date, parsed_dates = self.try_parse_date(non_null_series)
            if is_date and parsed_dates is not None:
                datatype_str = DataType.DATETIME.value
                return {
                    "name": series.name,
                    "datatype": datatype_str,
                    "missing_values": missing_count,
                    "format": "YYYY-MM-DD",
                    "min": str(parsed_dates.min().date()),
                    "max": str(parsed_dates.max().date()),
                }

            top_values = non_null_series.value_counts().head(5).index.tolist()

        # Build strongly typed ColumnProfile model
        profile_model = ColumnProfile(
            name=str(series.name),
            data_type=DataType(datatype_str),
            missing_count=missing_count,
            unique_count=unique_count,
            min_value=min_val,
            max_value=max_val,
            mean_value=mean_val,
            top_values=top_values,
        )

        # Output dictionary formatted for existing system compatibility
        profile_dict = {
            "name": profile_model.name,
            "datatype": profile_model.data_type.value,
            "missing_values": profile_model.missing_count,
            "unique_count": profile_model.unique_count,
        }
        if min_val is not None:
            profile_dict["min"] = min_val
        if max_val is not None:
            profile_dict["max"] = max_val
        if mean_val is not None:
            profile_dict["mean"] = mean_val
        if top_values:
            profile_dict["top_values"] = top_values

        return profile_dict

    def generate_context(self, dataset_name: str, dataframe: pd.DataFrame) -> Dict[str, Any]:
        """
        Profiles an entire dataset concurrently using ThreadPoolExecutor and BenchmarkTimer.

        Demonstrates:
        - Class-based Context Manager `BenchmarkTimer`
        - Concurrency with `ThreadPoolExecutor.map`
        - Backward-compatible context dictionary
        """
        with BenchmarkTimer(label=f"Profile_{dataset_name}") as timer:
            # Parallel column profiling
            columns = list(dataframe.columns)
            with ThreadPoolExecutor(max_workers=min(self._max_workers, len(columns) or 1)) as executor:
                column_profiles = list(executor.map(lambda c: self.profile_column(dataframe[c]), columns))

        context = {
            "dataset": dataset_name,
            "row_count": int(dataframe.shape[0]),
            "column_count": int(dataframe.shape[1]),
            "columns": column_profiles,
            "profiling_duration_sec": round(timer.elapsed_seconds, 4),
        }
        return context

    def save_context(self, context: Dict[str, Any]) -> str:
        """
        Persists generated context metadata to JSON file using pathlib.Path.
        """
        self._ensure_directory()
        filename = f"{context['dataset']}_context.json"
        filepath = self._output_directory / filename

        with filepath.open("w", encoding="utf-8") as file:
            json.dump(context, file, indent=4)

        return str(filepath)

    def health_check(self) -> Dict[str, Any]:
        """BaseService health check implementation."""
        return {
            "service": self.service_name,
            "status": "HEALTHY",
            "output_directory": str(self._output_directory),
        }