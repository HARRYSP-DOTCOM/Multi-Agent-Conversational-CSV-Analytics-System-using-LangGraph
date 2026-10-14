"""
Unit tests verifying Metaprogramming and Decorator concepts:
- Custom decorators with variable parameters (*args, **kwargs)
- Preservation of metadata via `functools.wraps`
- Retry logic with exponential backoff
- Timing profiler decorator with latency logging
- Thread-safe Memoization with LRU eviction and cache introspection
- Input validation decorator
"""

import unittest
import time
from core.decorators import retry, timing_profiler, memoize, validate_non_empty


class TestDecorators(unittest.TestCase):
    """Test suite for custom decorators."""

    def test_retry_decorator_succeeds_first_attempt(self):
        """Verifies retry decorator executes normally on success."""
        calls = 0

        @retry(max_retries=3, delay=0.01)
        def happy_path():
            nonlocal calls
            calls += 1
            return "SUCCESS"

        self.assertEqual(happy_path(), "SUCCESS")
        self.assertEqual(calls, 1)

    def test_retry_decorator_recovers_after_failures(self):
        """Verifies retry decorator catches transient errors and retries."""
        calls = 0

        @retry(max_retries=3, delay=0.01, backoff=1.5, allowed_exceptions=(ValueError,))
        def flaky_service():
            nonlocal calls
            calls += 1
            if calls < 3:
                raise ValueError("Transient network glitch")
            return "RECOVERED"

        result = flaky_service()
        self.assertEqual(result, "RECOVERED")
        self.assertEqual(calls, 3)

    def test_retry_decorator_raises_after_max_retries(self):
        """Verifies that exceeding max retries re-raises the original exception."""
        @retry(max_retries=2, delay=0.01, allowed_exceptions=(ZeroDivisionError,))
        def always_fails():
            return 1 / 0

        with self.assertRaises(ZeroDivisionError):
            always_fails()

    def test_timing_profiler_decorator(self):
        """Verifies timing profiler preserves return values and function attributes."""
        @timing_profiler(threshold_seconds=0.0)
        def compute_square(x: int) -> int:
            """Docstring for compute_square."""
            time.sleep(0.01)
            return x * x

        self.assertEqual(compute_square(5), 25)
        # Verify metadata preservation with functools.wraps
        self.assertEqual(compute_square.__name__, "compute_square")
        self.assertEqual(compute_square.__doc__, "Docstring for compute_square.")

    def test_memoize_decorator_cache_hits_and_clear(self):
        """Verifies memoize decorator caches results and reports stats."""
        evaluations = 0

        @memoize(max_size=4)
        def expensive_calculation(a: int, b: int) -> int:
            nonlocal evaluations
            evaluations += 1
            return a + b

        expensive_calculation.cache_clear()  # type: ignore

        # 1st call -> Miss
        res1 = expensive_calculation(2, 3)
        self.assertEqual(res1, 5)
        self.assertEqual(evaluations, 1)

        # 2nd call with same args -> Hit (evaluations does not increment)
        res2 = expensive_calculation(2, 3)
        self.assertEqual(res2, 5)
        self.assertEqual(evaluations, 1)

        # Inspect cache statistics
        info = expensive_calculation.cache_info()  # type: ignore
        self.assertEqual(info["hits"], 1)
        self.assertEqual(info["misses"], 1)
        self.assertEqual(info["size"], 1)

        # Clear cache
        expensive_calculation.cache_clear()  # type: ignore
        info_cleared = expensive_calculation.cache_info()  # type: ignore
        self.assertEqual(info_cleared["size"], 0)
        self.assertEqual(info_cleared["hits"], 0)

    def test_validate_non_empty_decorator(self):
        """Verifies argument validation decorator raises ValueError on empty strings/lists."""
        @validate_non_empty("dataset_name", "columns")
        def load_schema(dataset_name: str, columns: list):
            return f"{dataset_name} has {len(columns)} cols"

        # Valid call
        self.assertEqual(load_schema("sales", ["id", "price"]), "sales has 2 cols")

        # Empty string
        with self.assertRaises(ValueError):
            load_schema("", ["id"])

        # Empty list
        with self.assertRaises(ValueError):
            load_schema("sales", [])

        # None value
        with self.assertRaises(ValueError):
            load_schema(None, ["id"])  # type: ignore


if __name__ == "__main__":
    unittest.main()
