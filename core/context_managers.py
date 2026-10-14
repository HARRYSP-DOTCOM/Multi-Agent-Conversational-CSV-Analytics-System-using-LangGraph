"""
Context managers illustrating the Python context management protocol.

Demonstrates:
- Class-based Context Manager protocol (`__enter__` and `__exit__`)
- Exception handling and suppression semantics inside `__exit__`
- Generator-based Context Managers using `@contextlib.contextmanager`
- Guaranteed cleanup patterns (`finally` blocks)
- Resource acquisition and lock synchronization
"""

import os
import sys
import time
import shutil
import tempfile
import threading
from contextlib import contextmanager
from typing import Optional, Generator, Any, Type
from dataclasses import dataclass


@dataclass
class BenchmarkResult:
    """Stores benchmark metrics populated upon context manager exit."""
    start_time: float = 0.0
    end_time: float = 0.0
    elapsed_seconds: float = 0.0
    exception_caught: Optional[str] = None
    success: bool = False

    def __str__(self) -> str:
        status = "SUCCESS" if self.success else f"FAILED ({self.exception_caught})"
        return f"BenchmarkResult(elapsed={self.elapsed_seconds:.4f}s, status={status})"


class BenchmarkTimer:
    """
    Class-based context manager that records elapsed wall-clock time and
    captures runtime exceptions without crashing the enclosing scope if suppress_exceptions=True.

    Demonstrates:
    - Implementing `__enter__` to return a state holder
    - Implementing `__exit__` with (exc_type, exc_val, exc_tb) parameters
    - Truthy return from `__exit__` to suppress exceptions conditionally
    """

    def __init__(self, label: str = "Block", suppress_exceptions: bool = False) -> None:
        self.label = label
        self.suppress_exceptions = suppress_exceptions
        self.result = BenchmarkResult()

    def __enter__(self) -> BenchmarkResult:
        self.result.start_time = time.perf_counter()
        return self.result

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[Any],
    ) -> bool:
        self.result.end_time = time.perf_counter()
        self.result.elapsed_seconds = self.result.end_time - self.result.start_time

        if exc_type is not None:
            self.result.success = False
            self.result.exception_caught = str(exc_val)
            # If suppress_exceptions is True, return True to swallow exception
            return self.suppress_exceptions

        self.result.success = True
        return False


@contextmanager
def temporary_directory_scope(prefix: str = "analytics_tmp_") -> Generator[str, None, None]:
    """
    Generator-based context manager for safe creation and automatic cleanup of temporary directories.

    Demonstrates:
    - `@contextlib.contextmanager` generator protocol
    - Using `yield` to transfer control to caller
    - Using `finally` to ensure deletion even if errors occur
    """
    temp_dir = tempfile.mkdtemp(prefix=prefix)
    try:
        yield temp_dir
    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)


@contextmanager
def dataset_read_lock(lock: threading.Lock, timeout: float = 5.0) -> Generator[bool, None, None]:
    """
    Generator context manager for thread-safe dataset access with timeout.

    Demonstrates:
    - Concurrency synchronization with locks
    - Safe acquisition and release in `finally`
    """
    acquired = lock.acquire(timeout=timeout)
    try:
        yield acquired
    finally:
        if acquired:
            lock.release()


@contextmanager
def suppress_stdout_stderr() -> Generator[None, None, None]:
    """
    Context manager to temporarily silence stdout and stderr (useful during noisy C-extension operations).
    """
    null_fds = [os.open(os.devnull, os.O_RDWR) for _ in range(2)]
    save_fds = [os.dup(1), os.dup(2)]
    try:
        os.dup2(null_fds[0], 1)
        os.dup2(null_fds[1], 2)
        yield
    finally:
        os.dup2(save_fds[0], 1)
        os.dup2(save_fds[1], 2)
        for fd in null_fds + save_fds:
            os.close(fd)
