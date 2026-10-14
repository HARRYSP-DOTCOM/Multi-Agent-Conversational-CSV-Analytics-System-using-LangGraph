"""
Custom decorators demonstrating advanced Python metaprogramming and closures.

Demonstrates:
- Decorator pattern with variable parameters
- Preservation of function metadata via `functools.wraps`
- Thread-safe caching with LRU eviction and cache introspection (`cache_info`)
- Execution profiling with wall-clock timing (`time.perf_counter`)
- Exponential backoff retry logic for resilience
- Input argument validation
"""

import time
import logging
from collections import OrderedDict
from functools import wraps
from threading import Lock
from typing import Callable, Any, Type, Tuple, Optional, Dict

logger = logging.getLogger("csv_agent.decorators")


def retry(
    max_retries: int = 3,
    delay: float = 0.5,
    backoff: float = 2.0,
    allowed_exceptions: Tuple[Type[BaseException], ...] = (Exception,),
) -> Callable:
    """
    Decorator that retries a function with exponential backoff upon specified exceptions.

    Args:
        max_retries: Maximum number of retry attempts.
        delay: Initial delay between retries in seconds.
        backoff: Multiplier applied to delay after each failure.
        allowed_exceptions: Tuple of exceptions to intercept and retry.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            current_delay = delay
            last_exception = None

            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except allowed_exceptions as exc:
                    last_exception = exc
                    if attempt == max_retries:
                        logger.error(
                            f"[Retry Failed] '{func.__name__}' failed after {max_retries} attempts: {exc}"
                        )
                        raise
                    logger.warning(
                        f"[Retry {attempt}/{max_retries}] '{func.__name__}' encountered {exc.__class__.__name__}: {exc}. "
                        f"Retrying in {current_delay:.2f}s..."
                    )
                    time.sleep(current_delay)
                    current_delay *= backoff

            raise last_exception  # Fallback

        return wrapper

    return decorator


def timing_profiler(
    threshold_seconds: float = 0.0,
    custom_logger: Optional[logging.Logger] = None,
) -> Callable:
    """
    Decorator measuring execution duration using high-precision `time.perf_counter`.
    Logs execution time or warns if the duration exceeds the defined threshold.
    """
    log_target = custom_logger or logger

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                elapsed = time.perf_counter() - start_time
                if elapsed >= threshold_seconds:
                    log_target.info(
                        f"[Profiler] '{func.__module__}.{func.__name__}' completed in {elapsed:.4f}s"
                    )

        return wrapper

    return decorator


def memoize(max_size: int = 128, ttl_seconds: Optional[float] = None) -> Callable:
    """
    Thread-safe Least-Recently-Used (LRU) memoization decorator with optional TTL.
    Exposes `.cache_info()` and `.cache_clear()` introspection methods.
    """
    def decorator(func: Callable) -> Callable:
        cache: OrderedDict[Tuple[Any, ...], Tuple[Any, float]] = OrderedDict()
        lock = Lock()
        hits = 0
        misses = 0

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            nonlocal hits, misses

            # Build hashable key from args and sorted kwargs items
            key_items = []
            for arg in args:
                if isinstance(arg, (list, dict, set)):
                    key_items.append(str(arg))
                else:
                    key_items.append(arg)
            for k in sorted(kwargs.keys()):
                v = kwargs[k]
                key_items.append((k, str(v) if isinstance(v, (list, dict, set)) else v))

            cache_key = tuple(key_items)
            now = time.time()

            with lock:
                if cache_key in cache:
                    val, timestamp = cache[cache_key]
                    if ttl_seconds is None or (now - timestamp) < ttl_seconds:
                        hits += 1
                        cache.move_to_end(cache_key)
                        return val
                    else:
                        del cache[cache_key]

                misses += 1

            result = func(*args, **kwargs)

            with lock:
                if len(cache) >= max_size:
                    cache.popitem(last=False)  # Evict oldest entry
                cache[cache_key] = (result, now)

            return result

        def cache_info() -> Dict[str, Any]:
            with lock:
                return {
                    "hits": hits,
                    "misses": misses,
                    "size": len(cache),
                    "max_size": max_size,
                }

        def cache_clear() -> None:
            nonlocal hits, misses
            with lock:
                cache.clear()
                hits = 0
                misses = 0

        wrapper.cache_info = cache_info  # type: ignore
        wrapper.cache_clear = cache_clear  # type: ignore
        return wrapper

    return decorator


def validate_non_empty(*arg_names: str) -> Callable:
    """
    Decorator that verifies specified string or collection arguments are not empty or None.
    Raises ValueError if any validated argument fails.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Map positional args to param names via code object
            arg_names_all = func.__code__.co_varnames[:func.__code__.co_argcount]
            combined_args = dict(zip(arg_names_all, args))
            combined_args.update(kwargs)

            for target in arg_names:
                if target in combined_args:
                    val = combined_args[target]
                    if val is None or (isinstance(val, (str, list, dict, set, tuple)) and len(val) == 0):
                        raise ValueError(
                            f"Argument '{target}' in '{func.__name__}' must not be None or empty."
                        )

            return func(*args, **kwargs)

        return wrapper

    return decorator
