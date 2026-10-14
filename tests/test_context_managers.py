"""
Unit tests verifying Context Management protocols:
- Class-based context managers (__enter__ and __exit__)
- Generator-based context managers (@contextlib.contextmanager)
- Exception capture and conditional suppression
- Resource management and guaranteed cleanup (temp directories)
"""

import unittest
import os
import time
from core.context_managers import (
    BenchmarkTimer,
    temporary_directory_scope,
    BenchmarkResult,
)


class TestContextManagers(unittest.TestCase):
    """Test suite for context managers."""

    def test_class_based_benchmark_timer_success(self):
        """Verifies BenchmarkTimer records execution duration on successful block exit."""
        with BenchmarkTimer("test_block") as timer:
            self.assertIsInstance(timer, BenchmarkResult)
            time.sleep(0.02)

        self.assertTrue(timer.success)
        self.assertGreater(timer.elapsed_seconds, 0.01)
        self.assertIsNone(timer.exception_caught)

    def test_class_based_benchmark_timer_exception_suppressed(self):
        """Verifies BenchmarkTimer captures and suppresses exception when requested."""
        with BenchmarkTimer("failing_block", suppress_exceptions=True) as timer:
            raise KeyError("Simulated missing dataset column")

        self.assertFalse(timer.success)
        self.assertIn("Simulated missing dataset column", timer.exception_caught)

    def test_class_based_benchmark_timer_exception_propagates(self):
        """Verifies BenchmarkTimer lets exception bubble up when suppress_exceptions=False."""
        with self.assertRaises(IndexError):
            with BenchmarkTimer("failing_block", suppress_exceptions=False):
                raise IndexError("Index out of range")

    def test_generator_based_temporary_directory_scope(self):
        """Verifies temporary directory is created and deleted after exiting with block."""
        created_path = None
        with temporary_directory_scope(prefix="test_scope_") as temp_dir:
            created_path = temp_dir
            self.assertTrue(os.path.isdir(temp_dir))
            # Create a test file inside the temp directory
            sample_file = os.path.join(temp_dir, "sample.txt")
            with open(sample_file, "w") as f:
                f.write("temporary data")
            self.assertTrue(os.path.exists(sample_file))

        # After exiting context manager, directory must be automatically cleaned up
        self.assertFalse(os.path.exists(created_path))


if __name__ == "__main__":
    unittest.main()
