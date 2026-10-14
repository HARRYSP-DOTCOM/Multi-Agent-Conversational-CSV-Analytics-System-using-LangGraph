"""
Unit tests verifying Concurrency and Multithreading:
- concurrent.futures.ThreadPoolExecutor usage
- Parallel worker execution and as_completed
- Thread synchronization with threading.Lock
- dataset_read_lock context manager
"""

import unittest
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from core.context_managers import dataset_read_lock
from services.dataset_loader import DatasetLoader
import pandas as pd


class TestConcurrency(unittest.TestCase):
    """Test suite for concurrent execution and synchronization."""

    def test_thread_pool_executor_parallel_tasks(self):
        """Verifies concurrent task execution with ThreadPoolExecutor."""
        def worker_task(task_id: int) -> int:
            time.sleep(0.01)
            return task_id * 10

        results = []
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(worker_task, i) for i in range(5)]
            for future in as_completed(futures):
                results.append(future.result())

        self.assertEqual(sorted(results), [0, 10, 20, 30, 40])

    def test_thread_synchronization_lock(self):
        """Verifies race conditions are prevented using threading.Lock."""
        shared_counter = 0
        lock = threading.Lock()

        def increment_counter():
            nonlocal shared_counter
            for _ in range(100):
                with dataset_read_lock(lock):
                    current = shared_counter
                    time.sleep(0.0001)  # Context switch opportunity
                    shared_counter = current + 1

        threads = [threading.Thread(target=increment_counter) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # 5 threads * 100 increments = 500 without race condition
        self.assertEqual(shared_counter, 500)


if __name__ == "__main__":
    unittest.main()
