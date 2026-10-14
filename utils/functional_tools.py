"""
Functional programming utilities and streaming transformations.

Demonstrates:
- Higher-order functions: `map`, `filter`, `functools.reduce`
- Partial function application with `functools.partial`
- Lambda expressions
- List, Dict, and Set comprehensions
- Generator expressions
- `itertools` utilities (`islice`, `chain`, `groupby`)
- Type annotations with `Callable`, `Iterable`, `TypeVar`
"""

import itertools
from functools import reduce, partial
from typing import (
    Iterable,
    List,
    Dict,
    Set,
    Tuple,
    Callable,
    TypeVar,
    Any,
    Generator,
    Optional,
)

T = TypeVar("T")
R = TypeVar("R")


def apply_pipeline(data: Iterable[T], *transforms: Callable[[Iterable[T]], Iterable[Any]]) -> Iterable[Any]:
    """
    Applies a chain of transformations sequentially to an iterable using functools.reduce.
    Demonstrates higher-order function composition and `functools.reduce`.
    """
    return reduce(lambda acc, fn: fn(acc), transforms, data)


def filter_numeric_columns(columns_metadata: List[Dict[str, Any]]) -> List[str]:
    """
    Extracts names of numeric columns using `filter` and `lambda`.
    Demonstrates higher-order function `filter`.
    """
    numeric_items = filter(
        lambda col: col.get("datatype") in ("int", "float", "integer"),
        columns_metadata,
    )
    return list(map(lambda col: col["name"], numeric_items))


def map_column_names(df_columns: Iterable[str], formatter: Optional[Callable[[str], str]] = None) -> List[str]:
    """
    Transforms column names into sanitized snake_case format using `map`.
    Demonstrates `map`, `functools.partial`, and fallback lambdas.
    """
    sanitize_func = formatter or (lambda name: name.strip().lower().replace(" ", "_").replace("-", "_"))
    return list(map(sanitize_func, df_columns))


def build_schema_dict_comprehension(columns_metadata: List[Dict[str, Any]]) -> Dict[str, str]:
    """
    Builds a name -> datatype lookup dictionary.
    Demonstrates Dictionary Comprehension with conditional filtering.
    """
    return {
        col["name"]: col.get("datatype", "unknown")
        for col in columns_metadata
        if "name" in col
    }


def extract_unique_datatypes_set_comprehension(columns_metadata: List[Dict[str, Any]]) -> Set[str]:
    """
    Collects the set of unique data types present across columns.
    Demonstrates Set Comprehension.
    """
    return {
        col.get("datatype", "unknown")
        for col in columns_metadata
        if isinstance(col, dict)
    }


def chunk_iterable(iterable: Iterable[T], chunk_size: int) -> Generator[List[T], None, None]:
    """
    Yields batches of items from an iterable without loading the entire collection into memory.
    Demonstrates `itertools.islice`, custom generator function, and `yield`.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero.")

    iterator = iter(iterable)
    while True:
        chunk = list(itertools.islice(iterator, chunk_size))
        if not chunk:
            break
        yield chunk


def compute_column_aggregations(
    values: List[float],
) -> Dict[str, float]:
    """
    Computes summary metrics (sum, min, max, mean) using functional expressions.
    Demonstrates generator expressions and `reduce`.
    """
    if not values:
        return {"count": 0, "sum": 0.0, "mean": 0.0, "min": 0.0, "max": 0.0}

    total_sum = reduce(lambda a, b: a + b, values, 0.0)
    count = len(values)
    mean_val = total_sum / count

    # Using generator expression with min/max
    min_val = min(v for v in values)
    max_val = max(v for v in values)

    return {
        "count": count,
        "sum": round(total_sum, 4),
        "mean": round(mean_val, 4),
        "min": round(min_val, 4),
        "max": round(max_val, 4),
    }


def group_columns_by_type(columns_metadata: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """
    Groups column names by their data types using `itertools.groupby`.
    Demonstrates sorting and `itertools.groupby`.
    """
    sorted_cols = sorted(columns_metadata, key=lambda c: c.get("datatype", "unknown"))
    grouped: Dict[str, List[str]] = {}
    for dtype, group in itertools.groupby(sorted_cols, key=lambda c: c.get("datatype", "unknown")):
        grouped[dtype] = [col["name"] for col in group]
    return grouped
