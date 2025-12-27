"""
Startup time and memory benchmarks to compare Python version performance.

These benchmarks measure:
- Python interpreter startup time
- Import time for various modules
- Memory consumption patterns
- Object creation memory overhead
"""

from __future__ import annotations

import gc
import subprocess
import sys
import time
from dataclasses import dataclass
from typing import Any

from benchmarks.utils import BenchmarkResult, get_python_version


@dataclass
class StartupResult:
    """Result of a startup time benchmark."""

    name: str
    mean_time: float
    min_time: float
    max_time: float
    iterations: int


def measure_startup_time(python_path: str, code: str, iterations: int = 10) -> StartupResult:
    """Measure Python startup time for executing code."""
    times = []

    for _ in range(iterations):
        start = time.perf_counter()
        result = subprocess.run(
            [python_path, "-c", code],
            capture_output=True,
            text=True,
        )
        end = time.perf_counter()

        if result.returncode == 0:
            times.append(end - start)

    if not times:
        return StartupResult(
            name=f"Startup: {code[:30]}...",
            mean_time=float("inf"),
            min_time=float("inf"),
            max_time=float("inf"),
            iterations=0,
        )

    return StartupResult(
        name=f"Startup: {code[:30]}...",
        mean_time=sum(times) / len(times),
        min_time=min(times),
        max_time=max(times),
        iterations=len(times),
    )


def measure_import_time(python_path: str, module: str, iterations: int = 10) -> StartupResult:
    """Measure time to import a module."""
    code = f"import {module}"
    result = measure_startup_time(python_path, code, iterations)
    result.name = f"Import: {module}"
    return result


# =============================================================================
# Memory benchmarks (run within the current interpreter)
# =============================================================================


def get_object_size(obj: Any) -> int:
    """Get deep size of object in bytes."""
    import sys
    from collections import deque

    seen = set()
    size = 0
    queue: deque[Any] = deque([obj])

    while queue:
        current = queue.popleft()
        obj_id = id(current)

        if obj_id in seen:
            continue
        seen.add(obj_id)

        size += sys.getsizeof(current)

        if isinstance(current, dict):
            queue.extend(current.keys())
            queue.extend(current.values())
        elif isinstance(current, (list, tuple, set, frozenset)):
            queue.extend(current)
        elif hasattr(current, "__dict__"):
            queue.append(current.__dict__)

    return size


def memory_dict_overhead() -> dict[str, int]:
    """Measure dictionary memory overhead."""
    gc.collect()

    sizes = {}

    # Empty dict
    d: dict[str, int] = {}
    sizes["empty_dict"] = sys.getsizeof(d)

    # Small dict
    d = {str(i): i for i in range(10)}
    sizes["dict_10_items"] = sys.getsizeof(d)

    # Medium dict
    d = {str(i): i for i in range(100)}
    sizes["dict_100_items"] = sys.getsizeof(d)

    # Large dict
    d = {str(i): i for i in range(10000)}
    sizes["dict_10000_items"] = sys.getsizeof(d)

    return sizes


def memory_list_overhead() -> dict[str, int]:
    """Measure list memory overhead."""
    gc.collect()

    sizes = {}

    # Empty list
    lst: list[int] = []
    sizes["empty_list"] = sys.getsizeof(lst)

    # Small list
    lst = list(range(10))
    sizes["list_10_items"] = sys.getsizeof(lst)

    # Medium list
    lst = list(range(100))
    sizes["list_100_items"] = sys.getsizeof(lst)

    # Large list
    lst = list(range(10000))
    sizes["list_10000_items"] = sys.getsizeof(lst)

    return sizes


def memory_object_overhead() -> dict[str, int]:
    """Measure object creation overhead."""
    gc.collect()

    sizes = {}

    # Empty class
    class Empty:
        pass

    sizes["empty_class_instance"] = sys.getsizeof(Empty())

    # Class with __slots__
    class WithSlots:
        __slots__ = ["a", "b", "c"]

        def __init__(self) -> None:
            self.a = 1
            self.b = 2
            self.c = 3

    sizes["slots_class_instance"] = sys.getsizeof(WithSlots())

    # Regular class with attributes
    class Regular:
        def __init__(self) -> None:
            self.a = 1
            self.b = 2
            self.c = 3

    sizes["regular_class_instance"] = sys.getsizeof(Regular())

    # Dataclass
    @dataclass
    class DataClass:
        a: int
        b: int
        c: int

    sizes["dataclass_instance"] = sys.getsizeof(DataClass(1, 2, 3))

    return sizes


def memory_string_overhead() -> dict[str, int]:
    """Measure string memory overhead."""
    gc.collect()

    sizes = {}

    # Empty string
    sizes["empty_string"] = sys.getsizeof("")

    # ASCII string
    sizes["ascii_10"] = sys.getsizeof("a" * 10)
    sizes["ascii_100"] = sys.getsizeof("a" * 100)
    sizes["ascii_1000"] = sys.getsizeof("a" * 1000)

    # Unicode string
    sizes["unicode_10"] = sys.getsizeof("日" * 10)
    sizes["unicode_100"] = sys.getsizeof("日" * 100)

    return sizes


def memory_comprehension_overhead() -> dict[str, Any]:
    """Compare memory of different comprehension types."""
    import tracemalloc

    gc.collect()
    results: dict[str, Any] = {}

    # List comprehension
    tracemalloc.start()
    lst = [i * 2 for i in range(10000)]
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    results["list_comp_10k"] = {"current": current, "peak": peak, "len": len(lst)}

    gc.collect()

    # Generator (memory efficient)
    tracemalloc.start()
    gen = (i * 2 for i in range(10000))
    gen_list = list(gen)  # Force evaluation
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    results["generator_10k"] = {"current": current, "peak": peak, "len": len(gen_list)}

    return results


# =============================================================================
# Exception handling overhead (improved in Python 3.11+)
# =============================================================================


def exception_handling_overhead(iterations: int) -> dict[str, float]:
    """Measure exception handling overhead."""
    results = {}

    # Try-except with no exception - intentionally measuring try/except overhead
    start = time.perf_counter()
    for _ in range(iterations):
        try:  # noqa: SIM105
            _ = 1 + 1
        except ValueError:
            pass
    results["try_no_exception"] = time.perf_counter() - start

    # Try-except with exception
    start = time.perf_counter()
    for _ in range(iterations):
        try:
            raise ValueError("test")
        except ValueError:
            pass
    results["try_with_exception"] = time.perf_counter() - start

    # Nested try-except
    start = time.perf_counter()
    for _ in range(iterations):
        try:
            try:
                try:
                    raise ValueError("test")
                except TypeError:
                    pass
            except KeyError:
                pass
        except ValueError:
            pass
    results["nested_try_except"] = time.perf_counter() - start

    return results


# =============================================================================
# Function call overhead
# =============================================================================


def function_call_overhead(iterations: int) -> dict[str, float]:
    """Measure function call overhead."""
    results = {}

    def simple_func() -> int:
        return 42

    def func_with_args(a: int, b: int, c: int) -> int:
        return a + b + c

    def func_with_kwargs(a: int = 1, b: int = 2, c: int = 3) -> int:
        return a + b + c

    def recursive_func(n: int) -> int:
        if n <= 1:
            return n
        return recursive_func(n - 1) + recursive_func(n - 2)

    # Simple function call
    start = time.perf_counter()
    for _ in range(iterations):
        simple_func()
    results["simple_call"] = time.perf_counter() - start

    # Function with positional args
    start = time.perf_counter()
    for _ in range(iterations):
        func_with_args(1, 2, 3)
    results["positional_args"] = time.perf_counter() - start

    # Function with keyword args
    start = time.perf_counter()
    for _ in range(iterations):
        func_with_kwargs(a=1, b=2, c=3)
    results["keyword_args"] = time.perf_counter() - start

    return results


# =============================================================================
# Benchmark runner for startup benchmarks
# =============================================================================


def run_startup_benchmarks(python_path: str) -> list[StartupResult]:
    """Run startup time benchmarks."""
    results = []

    # Basic startup
    results.append(measure_startup_time(python_path, "pass"))

    # Print hello world
    results.append(measure_startup_time(python_path, "print('Hello')"))

    # Import common standard library modules
    common_modules = [
        "sys",
        "os",
        "json",
        "csv",
        "pathlib",
        "collections",
        "itertools",
        "functools",
        "typing",
        "dataclasses",
        "asyncio",
        "re",
        "datetime",
        "math",
        "random",
        "hashlib",
        "urllib.request",
        "sqlite3",
    ]

    for module in common_modules:
        results.append(measure_import_time(python_path, module))

    # Heavy imports
    heavy_imports = [
        "numpy",
        "pandas",
    ]

    for module in heavy_imports:
        results.append(measure_import_time(python_path, module, iterations=5))

    return results


def run_memory_benchmarks() -> list[BenchmarkResult]:
    """Run memory overhead benchmarks."""
    from benchmarks.utils import benchmark

    results: list[BenchmarkResult] = []

    # Memory overhead measurements
    dict_sizes = memory_dict_overhead()
    list_sizes = memory_list_overhead()
    object_sizes = memory_object_overhead()
    string_sizes = memory_string_overhead()

    # Convert to benchmark results (using size as the "time" for comparison)
    for name, size in dict_sizes.items():
        results.append(
            BenchmarkResult(
                name=f"Memory: {name}",
                category="Memory - Dict",
                python_version=get_python_version(),
                mean_time=size,  # Using bytes as the metric
                std_dev=0,
                min_time=size,
                max_time=size,
                iterations=1,
                memory_mb=size / (1024 * 1024),
            )
        )

    for name, size in list_sizes.items():
        results.append(
            BenchmarkResult(
                name=f"Memory: {name}",
                category="Memory - List",
                python_version=get_python_version(),
                mean_time=size,
                std_dev=0,
                min_time=size,
                max_time=size,
                iterations=1,
                memory_mb=size / (1024 * 1024),
            )
        )

    for name, size in object_sizes.items():
        results.append(
            BenchmarkResult(
                name=f"Memory: {name}",
                category="Memory - Objects",
                python_version=get_python_version(),
                mean_time=size,
                std_dev=0,
                min_time=size,
                max_time=size,
                iterations=1,
                memory_mb=size / (1024 * 1024),
            )
        )

    for name, size in string_sizes.items():
        results.append(
            BenchmarkResult(
                name=f"Memory: {name}",
                category="Memory - Strings",
                python_version=get_python_version(),
                mean_time=size,
                std_dev=0,
                min_time=size,
                max_time=size,
                iterations=1,
                memory_mb=size / (1024 * 1024),
            )
        )

    # Exception handling overhead
    results.append(
        benchmark(
            lambda: exception_handling_overhead(100000),
            name="Exception: try with no exception (100k)",
            category="Overhead - Exceptions",
            iterations=5,
        )
    )

    results.append(
        benchmark(
            lambda: exception_handling_overhead(10000),
            name="Exception: try with exception (10k)",
            category="Overhead - Exceptions",
            iterations=5,
        )
    )

    # Function call overhead
    results.append(
        benchmark(
            lambda: function_call_overhead(1000000),
            name="Function Call Overhead (1M calls)",
            category="Overhead - Function Calls",
            iterations=5,
        )
    )

    return results


if __name__ == "__main__":
    from benchmarks.utils import format_time

    python_path = sys.executable

    print(f"Running startup benchmarks with {python_path}...")
    startup_results = run_startup_benchmarks(python_path)
    print("\nStartup Times:")
    for r in startup_results:
        print(f"  {r.name}: {r.mean_time * 1000:.2f} ms")

    print("\nRunning memory benchmarks...")
    memory_results = run_memory_benchmarks()
    print("\nMemory Results:")
    for r in memory_results:
        if "Memory:" in r.name:
            print(f"  {r.name}: {r.mean_time:.0f} bytes")
        else:
            print(f"  {r.name}: {format_time(r.mean_time)}")
