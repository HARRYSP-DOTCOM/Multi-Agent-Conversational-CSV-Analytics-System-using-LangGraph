"""
Dataset Loader Service.

Demonstrates:
- Object-Oriented inheritance (`BaseService`)
- Modern filesystem handling with `pathlib.Path`
- Concurrency with `concurrent.futures.ThreadPoolExecutor`
- Custom Exceptions (`DatasetNotFoundError`, `InvalidCSVFormatError`, `EmptyDatasetError`)
- Standard library `hashlib` for SHA-256 data fingerprinting
- Python Generator function with `yield` for chunked streaming
- Advanced collections: `collections.defaultdict` and `collections.Counter`
- Decorators: `@timing_profiler` and `@retry`
- Complete backwards compatibility with existing methods and signatures
"""

import hashlib
from collections import defaultdict, Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Optional, Generator, Union, Any, Tuple
import pandas as pd

from core.base_service import BaseService
from core.decorators import timing_profiler, retry
from core.exceptions import (
    DatasetNotFoundError,
    InvalidCSVFormatError,
    EmptyDatasetError,
)
from core.models import DatasetContainer, DatasetFingerprint


class DatasetLoader(BaseService):
    """
    Service responsible for discovering, streaming, fingerprinting, and loading CSV datasets.
    Inherits from `BaseService` to adhere to the core service contract.
    """

    def __init__(self, data_directory: Union[str, Path] = "uploads", max_workers: int = 4) -> None:
        super().__init__(service_name="dataset_loader")
        self._data_directory = Path(data_directory)
        self._max_workers = max_workers
        self._cache: Dict[str, pd.DataFrame] = {}
        self._ensure_directory()
        self._initialized = True

    # --- Property Getters and Setters ---

    @property
    def data_directory(self) -> Path:
        """Returns the data directory as a Path object."""
        return self._data_directory

    @data_directory.setter
    def data_directory(self, new_dir: Union[str, Path]) -> None:
        """Sets and creates data directory with validation."""
        path = Path(new_dir)
        self._data_directory = path
        self._ensure_directory()

    def _ensure_directory(self) -> None:
        """Private helper using pathlib.Path.mkdir."""
        self._data_directory.mkdir(parents=True, exist_ok=True)

    # --- File Discovery using pathlib and comprehensions ---

    def discover_csv_files(self) -> List[str]:
        """
        Discovers all CSV files in the data directory using Path.glob and list comprehension.

        Returns:
            List of CSV filenames (e.g. ['sales.csv', 'customers.csv']).
        """
        if not self._data_directory.exists():
            return []
        # List comprehension with pathlib.Path
        return [p.name for p in self._data_directory.glob("*.csv") if p.is_file()]

    # --- SHA-256 Data Fingerprinting using hashlib ---

    @staticmethod
    def calculate_file_hash(filepath: Union[str, Path], chunk_size: int = 65536) -> str:
        """
        Computes SHA-256 checksum of a file in binary chunks.
        Demonstrates `hashlib.sha256` and binary stream chunking.
        """
        path = Path(filepath)
        if not path.is_file():
            raise DatasetNotFoundError(str(path))

        hasher = hashlib.sha256()
        with path.open("rb") as f:
            while chunk := f.read(chunk_size):
                hasher.update(chunk)
        return hasher.hexdigest()

    def get_fingerprint(self, filename: str) -> DatasetFingerprint:
        """Generates structured namedtuple fingerprint for a file."""
        path = self._data_directory / filename
        if not path.exists():
            raise DatasetNotFoundError(str(path))

        stat = path.stat()
        file_hash = self.calculate_file_hash(path)
        return DatasetFingerprint(
            filename=filename,
            sha256_hash=file_hash,
            byte_size=stat.st_size,
            modified_time=stat.st_mtime,
        )

    # --- Generator Function with `yield` for Memory-Efficient Streaming ---

    def stream_csv_chunks(
        self,
        filepath: Union[str, Path],
        chunk_size: int = 1000,
    ) -> Generator[pd.DataFrame, None, None]:
        """
        Yields sequential slices of a CSV file using Pandas chunksize and Python `yield`.
        Demonstrates the generator protocol for handling datasets that exceed RAM.
        """
        path = Path(filepath)
        if not path.exists():
            raise DatasetNotFoundError(str(path))

        try:
            with pd.read_csv(path, chunksize=chunk_size) as reader:
                for chunk in reader:
                    yield chunk
        except pd.errors.EmptyDataError as err:
            raise EmptyDatasetError(path.stem) from err
        except pd.errors.ParserError as err:
            raise InvalidCSVFormatError(str(path), str(err)) from err

    # --- Single Dataset Loader with Custom Exceptions & Retry Decorator ---

    @retry(max_retries=2, delay=0.2, allowed_exceptions=(pd.errors.DtypeWarning,))
    def load_single_csv(self, file_path: Union[str, Path]) -> Tuple[str, pd.DataFrame]:
        """
        Loads an individual CSV file, validates contents, and returns (dataset_name, dataframe).
        Raises custom exceptions upon failure.
        """
        path = Path(file_path)
        if not path.exists():
            raise DatasetNotFoundError(str(path))

        dataset_name = path.stem
        try:
            df = pd.read_csv(path)
        except pd.errors.EmptyDataError as err:
            raise EmptyDatasetError(dataset_name) from err
        except Exception as err:
            raise InvalidCSVFormatError(str(path), str(err)) from err

        if df.empty:
            raise EmptyDatasetError(dataset_name)

        return dataset_name, df

    # --- Concurrent Multi-Dataset Loading with ThreadPoolExecutor ---

    @timing_profiler(threshold_seconds=0.01)
    def load_datasets(self, use_containers: bool = False) -> Dict[str, Any]:
        """
        Loads all CSV files concurrently using `concurrent.futures.ThreadPoolExecutor`.
        Maintains 100% backwards compatibility by returning a dict of {name: DataFrame}.

        Args:
            use_containers: If True, wraps DataFrames in rich `DatasetContainer` instances.

        Returns:
            Dictionary mapping dataset name to pd.DataFrame (or DatasetContainer).
        """
        csv_files = self.discover_csv_files()
        if not csv_files:
            return {}

        results: Dict[str, Any] = {}

        # Parallel dataset loading across threads
        with ThreadPoolExecutor(max_workers=min(self._max_workers, len(csv_files) or 1)) as executor:
            future_to_file = {
                executor.submit(self.load_single_csv, self._data_directory / file_name): file_name
                for file_name in csv_files
            }

            for future in as_completed(future_to_file):
                file_name = future_to_file[future]
                try:
                    dataset_name, df = future.result()
                    if use_containers:
                        results[dataset_name] = DatasetContainer(dataset_name, df)
                    else:
                        results[dataset_name] = df
                except Exception as exc:
                    self._logger.warning(f"Could not load {file_name}: {exc}")

        self._cache = {k: (v.dataframe if isinstance(v, DatasetContainer) else v) for k, v in results.items()}
        return results

    # --- Analytics & Summaries with collections.Counter and defaultdict ---

    def get_dataset_summary(self, datasets: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """
        Generates metadata summaries using dictionary comprehension and collections.Counter.
        """
        summaries: Dict[str, Any] = {}
        for name, df in datasets.items():
            # collections.Counter to tally column datatypes
            dtype_counts = Counter(str(t) for t in df.dtypes)
            summaries[name] = {
                "rows": int(df.shape[0]),
                "columns": int(df.shape[1]),
                "column_names": list(df.columns),
                "datatype_breakdown": dict(dtype_counts),
            }
        return summaries

    def group_files_by_extension(self) -> Dict[str, List[str]]:
        """
        Demonstrates `collections.defaultdict` to group all directory entries by file extension.
        """
        extension_map: defaultdict[str, List[str]] = defaultdict(list)
        for entry in self._data_directory.iterdir():
            if entry.is_file():
                ext = entry.suffix.lower() or "no_extension"
                extension_map[ext].append(entry.name)
        return dict(extension_map)

    def health_check(self) -> Dict[str, Any]:
        """Concrete implementation of BaseService.health_check."""
        return {
            "service": self.service_name,
            "status": "HEALTHY",
            "directory_exists": self._data_directory.exists(),
            "csv_count": len(self.discover_csv_files()),
        }