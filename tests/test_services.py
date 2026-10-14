"""
Unit tests verifying Services:
- DatasetLoader filesystem traversal with pathlib.Path
- SHA-256 file fingerprinting with hashlib
- CSV streaming generator with yield
- Parallel column profiling with ThreadPoolExecutor
- ContextGenerator metadata synthesis
- Custom exception handling (DatasetNotFoundError, EmptyDatasetError)
"""

import unittest
from pathlib import Path
import pandas as pd
from services.dataset_loader import DatasetLoader
from services.context_generator import ContextGenerator
from core.context_managers import temporary_directory_scope
from core.exceptions import DatasetNotFoundError, EmptyDatasetError


class TestServices(unittest.TestCase):
    """Test suite covering DatasetLoader and ContextGenerator services."""

    def test_dataset_loader_fingerprinting_and_streaming(self):
        """Verifies CSV writing, SHA-256 hashing, and chunked streaming."""
        with temporary_directory_scope(prefix="test_loader_") as temp_dir:
            temp_path = Path(temp_dir)
            csv_file = temp_path / "mock_sales.csv"

            # Create test dataframe
            df = pd.DataFrame({
                "transaction_id": list(range(1, 101)),
                "amount": [i * 12.5 for i in range(1, 101)],
                "category": ["A", "B", "C", "D"] * 25,
            })
            df.to_csv(csv_file, index=False)

            loader = DatasetLoader(data_directory=temp_dir)

            # Test discovery
            discovered = loader.discover_csv_files()
            self.assertIn("mock_sales.csv", discovered)

            # Test SHA-256 fingerprinting
            fingerprint = loader.get_fingerprint("mock_sales.csv")
            self.assertEqual(fingerprint.filename, "mock_sales.csv")
            self.assertTrue(len(fingerprint.sha256_hash) == 64)  # Valid SHA-256 length

            # Test streaming generator with yield
            chunks = list(loader.stream_csv_chunks(csv_file, chunk_size=30))
            self.assertEqual(len(chunks), 4)  # 30, 30, 30, 10
            self.assertEqual(len(chunks[0]), 30)
            self.assertEqual(len(chunks[-1]), 10)

    def test_dataset_loader_exceptions(self):
        """Verifies DatasetNotFoundError and EmptyDatasetError."""
        with temporary_directory_scope(prefix="test_err_") as temp_dir:
            temp_path = Path(temp_dir)
            loader = DatasetLoader(data_directory=temp_dir)

            # Non-existent file
            with self.assertRaises(DatasetNotFoundError):
                loader.load_single_csv(temp_path / "does_not_exist.csv")

            # Empty file
            empty_file = temp_path / "empty.csv"
            empty_file.touch()
            with self.assertRaises(EmptyDatasetError):
                loader.load_single_csv(empty_file)

    def test_context_generator_parallel_profiling(self):
        """Verifies parallel profiling with ThreadPoolExecutor."""
        with temporary_directory_scope(prefix="test_ctx_") as temp_dir:
            generator = ContextGenerator(output_directory=temp_dir)

            df = pd.DataFrame({
                "user_id": [1, 2, 3, 4, 5],
                "score": [88.5, 92.0, 79.5, 95.0, 85.0],
                "active": [True, False, True, True, False],
                "role": ["admin", "user", "user", "editor", "user"],
            })

            context = generator.generate_context("users", df)
            self.assertEqual(context["dataset"], "users")
            self.assertEqual(context["row_count"], 5)
            self.assertEqual(context["column_count"], 4)
            self.assertIn("profiling_duration_sec", context)

            saved_path = generator.save_context(context)
            self.assertTrue(Path(saved_path).exists())


if __name__ == "__main__":
    unittest.main()
