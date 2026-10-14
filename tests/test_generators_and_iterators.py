"""
Unit tests verifying Generators, Iterators, and Streaming:
- Generator functions using `yield`
- Custom iterator protocol (iter() and next())
- Itertools utilities (islice, chunking)
- Generator expressions vs List comprehensions (Lazy evaluation vs Eager evaluation)
- StopIteration semantics
"""

import unittest
import types
from utils.functional_tools import chunk_iterable
from core.models import DatasetContainer
import pandas as pd


class TestGeneratorsAndIterators(unittest.TestCase):
    """Test suite for generators and iterator protocol."""

    def test_chunk_iterable_is_generator(self):
        """Verifies chunk_iterable returns a generator type object."""
        gen = chunk_iterable([1, 2, 3, 4, 5], chunk_size=2)
        self.assertIsInstance(gen, types.GeneratorType)

    def test_chunk_iterable_streaming_batches(self):
        """Verifies chunk_iterable produces expected batches using next()."""
        gen = chunk_iterable(range(1, 8), chunk_size=3)

        # 1st yield
        self.assertEqual(next(gen), [1, 2, 3])
        # 2nd yield
        self.assertEqual(next(gen), [4, 5, 6])
        # 3rd yield (partial chunk)
        self.assertEqual(next(gen), [7])

        # Generator exhausted -> StopIteration
        with self.assertRaises(StopIteration):
            next(gen)

    def test_dataset_container_stream_chunks_generator(self):
        """Verifies DatasetContainer.stream_chunks() yields DataFrame slices."""
        df = pd.DataFrame({"id": list(range(25)), "val": list(range(100, 125))})
        container = DatasetContainer("large_data", df)

        chunks = list(container.stream_chunks(chunk_size=10))
        self.assertEqual(len(chunks), 3)
        self.assertEqual(len(chunks[0]), 10)
        self.assertEqual(len(chunks[1]), 10)
        self.assertEqual(len(chunks[2]), 5)

    def test_generator_expression_lazy_evaluation(self):
        """
        Verifies difference between Lazy generator expression and Eager list comprehension.
        """
        evaluated_indices = []

        def side_effect(x):
            evaluated_indices.append(x)
            return x * 2

        # Generator expression: does NOT evaluate until consumed
        gen_expr = (side_effect(x) for x in range(5))
        self.assertEqual(len(evaluated_indices), 0)  # Nothing evaluated yet!

        # Consume only 2 elements
        first = next(gen_expr)
        second = next(gen_expr)
        self.assertEqual(first, 0)
        self.assertEqual(second, 2)
        self.assertEqual(evaluated_indices, [0, 1])  # Only 2 elements processed!

        # List comprehension: Eagerly evaluates ALL elements immediately
        evaluated_indices.clear()
        eager_list = [side_effect(x) for x in range(5)]
        self.assertEqual(len(evaluated_indices), 5)  # All 5 evaluated immediately
        self.assertEqual(eager_list, [0, 2, 4, 6, 8])


if __name__ == "__main__":
    unittest.main()
