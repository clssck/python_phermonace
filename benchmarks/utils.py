"""Utility functions for benchmarking."""
import gc
import statistics
import sys
import time
from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class BenchmarkResult:
    """Result of a benchmark run."""
    name: str
    category: str
    python_version: str
    mean_time: float
    std_dev: float
    min_time: float
    max_time: float
    iterations: int
    memory_mb: float = 0.0


def get_python_version() -> str:
    """Get formatted Python version string."""
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"


def benchmark(
    func: Callable[[], Any],
    name: str,
    category: str,
    warmup: int = 3,
    iterations: int = 10,
) -> BenchmarkResult:
    """
    Run a benchmark function multiple times and collect statistics.

    Args:
        func: The function to benchmark (should take no arguments)
        name: Name of the benchmark
        category: Category of the benchmark
        warmup: Number of warmup iterations
        iterations: Number of timed iterations

    Returns:
        BenchmarkResult with timing statistics
    """
    # Warmup runs
    for _ in range(warmup):
        func()
        gc.collect()

    # Timed runs
    times = []
    for _ in range(iterations):
        gc.collect()
        gc.disable()

        start = time.perf_counter()
        func()
        end = time.perf_counter()

        gc.enable()
        times.append(end - start)

    return BenchmarkResult(
        name=name,
        category=category,
        python_version=get_python_version(),
        mean_time=statistics.mean(times),
        std_dev=statistics.stdev(times) if len(times) > 1 else 0.0,
        min_time=min(times),
        max_time=max(times),
        iterations=iterations,
    )


def format_time(seconds: float) -> str:
    """Format time in human-readable format."""
    if seconds < 1e-6:
        return f"{seconds * 1e9:.2f} ns"
    elif seconds < 1e-3:
        return f"{seconds * 1e6:.2f} µs"
    elif seconds < 1:
        return f"{seconds * 1e3:.2f} ms"
    else:
        return f"{seconds:.2f} s"
