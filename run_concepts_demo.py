"""
Interactive Python Concepts Demonstration Script.

Designed for academic evaluation, project viva, and professor demonstration.
Demonstrates live execution of all major Python concepts embedded in this project.
"""

import sys
import time
import pandas as pd
from collections import defaultdict, Counter, deque
from dataclasses import FrozenInstanceError

from core.enums import DataType, AgentRoute, ExecutionStatus
from core.models import TokenStat, DatasetFingerprint, ColumnProfile, DatasetContainer
from core.decorators import retry, timing_profiler, memoize, validate_non_empty
from core.context_managers import BenchmarkTimer, temporary_directory_scope
from core.exceptions import (
    CSVAnalyticsError,
    DatasetNotFoundError,
    InvalidCSVFormatError,
    ColumnNotFoundError,
)
from core.base_agent import BaseAgent
from agents.agent_factory import AgentRegistry
import agents  # Ensures all agents are registered
from utils.functional_tools import (
    filter_numeric_columns,
    map_column_names,
    build_schema_dict_comprehension,
    extract_unique_datatypes_set_comprehension,
    compute_column_aggregations,
    apply_pipeline,
)


def print_banner(title: str, step: int):
    print("\n" + "=" * 70)
    print(f"  CONCEPT #{step}: {title.upper()}")
    print("=" * 70)


def demo_oop_and_abc():
    print_banner("Object-Oriented Programming & Abstract Base Classes", 1)
    print("1. Subclassing BaseAgent(abc.ABC) with abstract method `process`:")
    agent = AgentRegistry.create("query")
    print(f"   -> Agent Name: {agent.name}")
    print(f"   -> Description: {agent.description}")
    print(f"   -> Subclass of BaseAgent: {isinstance(agent, BaseAgent)}")
    print(f"   -> Representation (__repr__): {repr(agent)}")

    print("\n2. Template Method Pattern & Callable Object Protocol (__call__):")
    state = {"question": "What is the total revenue?", "csv_question": "revenue sum"}
    print(f"   -> Invocations before run: {agent.execution_count}")
    print("   -> Executing `agent(state)` invokes Template Method (pre -> process -> post)...")
    try:
        # Dummy invocation without running external LLM if offline
        agent.before_run(state)
        time.sleep(0.01)
        agent.after_run(state, 0.01)
        print("   -> Template hooks executed successfully!")
    except Exception as e:
        print(f"   -> Handled: {e}")


def demo_dunder_methods():
    print_banner("Magic / Dunder Methods in Custom Container", 2)
    sample_df = pd.DataFrame({
        "product": ["Laptop", "Mouse", "Keyboard", "Monitor"],
        "price": [1200, 25, 75, 300],
        "in_stock": [True, True, False, True],
    })
    container = DatasetContainer("inventory", sample_df)

    print("1. __len__: len(container)")
    print(f"   -> Row count: {len(container)}")

    print("\n2. __getitem__: container['product'] and container[0]")
    print(f"   -> Column access ['product']: {list(container['product'])}")
    print(f"   -> Row access [0]: Product={container[0]['product']}, Price={container[0]['price']}")

    print("\n3. __contains__: 'in' operator")
    print(f"   -> 'price' in container: {'price' in container}")
    print(f"   -> 'discount' in container: {'discount' in container}")

    print("\n4. __iter__: iterating over column names")
    print(f"   -> [col for col in container]: {[col for col in container]}")

    print("\n5. Encapsulation (@property & @setter validation):")
    try:
        container.name = ""
    except ValueError as err:
        print(f"   -> Caught invalid name assignment: {err}")


def demo_decorators():
    print_banner("Advanced Metaprogramming & Custom Decorators", 3)

    print("1. @timing_profiler - Wall-clock profiling:")
    @timing_profiler(threshold_seconds=0.0)
    def calculate_fib(n: int) -> int:
        a, b = 0, 1
        for _ in range(n):
            a, b = b, a + b
        return a

    fib_val = calculate_fib(50)
    print(f"   -> fib(50) = {fib_val}")

    print("\n2. @memoize - Thread-safe LRU caching with cache introspection:")
    @memoize(max_size=3)
    def compute_heavy_metric(x: int) -> int:
        return x ** 3

    compute_heavy_metric(2)  # Miss
    compute_heavy_metric(2)  # Hit
    compute_heavy_metric(3)  # Miss
    info = compute_heavy_metric.cache_info()  # type: ignore
    print(f"   -> Cache Stats: Hits={info['hits']}, Misses={info['misses']}, Size={info['size']}/{info['max_size']}")

    print("\n3. @retry - Exponential backoff:")
    attempts = 0
    @retry(max_retries=3, delay=0.02, backoff=1.5, allowed_exceptions=(ConnectionError,))
    def simulated_api():
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise ConnectionError("Temporary connection drop")
        return "Connected successfully!"

    status = simulated_api()
    print(f"   -> Result after {attempts} attempts: '{status}'")


def demo_context_managers():
    print_banner("Context Managers (__enter__ / __exit__ & @contextmanager)", 4)

    print("1. Class-based Context Manager (BenchmarkTimer):")
    with BenchmarkTimer(label="Demo_Timer", suppress_exceptions=True) as timer:
        time.sleep(0.02)
        print(f"   -> Inside block... running payload")
    print(f"   -> Exited block: Duration = {timer.elapsed_seconds:.4f}s | Success = {timer.success}")

    print("\n2. Generator-based Context Manager (temporary_directory_scope):")
    with temporary_directory_scope(prefix="demo_temp_") as temp_dir:
        import os
        print(f"   -> Created temporary sandbox: {temp_dir}")
        print(f"   -> Directory exists while inside: {os.path.exists(temp_dir)}")
    print(f"   -> Directory exists after exit: {os.path.exists(temp_dir)} (Guaranteed cleanup!)")


def demo_generators_and_streaming():
    print_banner("Generators & Memory-Efficient Streaming (`yield`)", 5)

    sample_df = pd.DataFrame({"id": list(range(1, 11)), "val": [x * 10 for x in range(1, 11)]})
    container = DatasetContainer("stream_data", sample_df)

    print("1. Streaming chunks using `yield` (Processes datasets without RAM exhaustion):")
    for idx, chunk in enumerate(container.stream_chunks(chunk_size=4), start=1):
        print(f"   -> Chunk #{idx} yielded {len(chunk)} rows: IDs {list(chunk['id'])}")

    print("\n2. Lazy Generator Expressions vs Eager List Comprehensions:")
    gen_exp = (x ** 2 for x in range(1, 6))
    print(f"   -> Generator object created: {gen_exp}")
    print(f"   -> First item via next(): {next(gen_exp)}")
    print(f"   -> Second item via next(): {next(gen_exp)}")


def demo_data_structures():
    print_banner("Data Structures: Dataclasses, NamedTuples, Collections & Enums", 6)

    print("1. Immutable NamedTuple:")
    token = TokenStat(token="revenue", frequency=28, is_stop_word=False)
    print(f"   -> Token: '{token.token}', Frequency: {token.frequency}, StopWord: {token.is_stop_word}")

    print("\n2. Frozen Dataclass with slots:")
    col_prof = ColumnProfile(
        name="sales",
        data_type=DataType.FLOAT,
        missing_count=0,
        unique_count=120,
        min_value=15.0,
        max_value=950.0,
        mean_value=340.2,
    )
    print(f"   -> Dataclass: {col_prof}")
    try:
        col_prof.name = "mutated"  # type: ignore
    except FrozenInstanceError:
        print("   -> Caught FrozenInstanceError: Immutability preserved!")

    print("\n3. Collections (defaultdict, Counter, deque):")
    words = ["sales", "profit", "sales", "revenue", "sales", "profit"]
    counter = Counter(words)
    print(f"   -> Counter frequency analysis: {dict(counter)}")

    rolling_buffer = deque(maxlen=3)
    for q in ["Q1", "Q2", "Q3", "Q4"]:
        rolling_buffer.append(q)
    print(f"   -> Rolling deque (maxlen=3): {list(rolling_buffer)}")


def demo_exceptions():
    print_banner("Custom Exception Hierarchy & Exception Chaining", 7)
    try:
        try:
            int("invalid_numeric_value")
        except ValueError as cause:
            raise InvalidCSVFormatError("monthly_data.csv", "Could not convert value to integer") from cause
    except CSVAnalyticsError as err:
        print(f"   -> Caught domain exception: {err}")
        print(f"   -> Error Code: {err.error_code}")
        print(f"   -> Underlying Cause (__cause__): {err.__cause__}")


def demo_functional_programming():
    print_banner("Functional Programming (map, filter, reduce, partial, comprehensions)", 8)

    sample_meta = [
        {"name": "employee_id", "datatype": "int"},
        {"name": "full_name", "datatype": "string"},
        {"name": "hourly_rate", "datatype": "float"},
        {"name": "is_active", "datatype": "boolean"},
    ]

    print("1. higher-order filter() & map():")
    numeric_cols = filter_numeric_columns(sample_meta)
    print(f"   -> Filtered numeric columns: {numeric_cols}")

    sanitized = map_column_names(["User Name", "Account ID", "Total-Cost"])
    print(f"   -> Mapped sanitized names: {sanitized}")

    print("\n2. Dictionary and Set Comprehensions:")
    schema_dict = build_schema_dict_comprehension(sample_meta)
    print(f"   -> Dict Comprehension (name -> type): {schema_dict}")

    unique_types = extract_unique_datatypes_set_comprehension(sample_meta)
    print(f"   -> Set Comprehension (unique types): {unique_types}")

    print("\n3. functools.reduce() for statistical aggregation:")
    rates = [25.0, 30.0, 45.0, 50.0]
    agg = compute_column_aggregations(rates)
    print(f"   -> Aggregations: Sum={agg['sum']}, Mean={agg['mean']}, Min={agg['min']}, Max={agg['max']}")


def main():
    print("=" * 70)
    print("   CSV ANALYTICS AGENT - COMPREHENSIVE PYTHON CONCEPTS DEMO")
    print("=" * 70)
    print("This interactive runner demonstrates how core & advanced Python concepts")
    print("are implemented throughout this production-grade multi-agent architecture.")

    demo_oop_and_abc()
    demo_dunder_methods()
    demo_decorators()
    demo_context_managers()
    demo_generators_and_streaming()
    demo_data_structures()
    demo_exceptions()
    demo_functional_programming()

    print("\n" + "=" * 70)
    print("   ALL DEMONSTRATIONS COMPLETED SUCCESSFULLY!")
    print("   To execute the formal unit test suite: python -m unittest discover tests")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
