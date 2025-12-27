"""
Version-specific benchmarks that test features unique to each Python version.

Tests features like:
- 3.10+: Pattern matching (match/case)
- 3.11+: Zero-cost exceptions, TaskGroup, ExceptionGroup, tomllib
- 3.12+: Comprehension inlining, f-string improvements
- 3.13+: Improved typing performance
"""

from __future__ import annotations

import asyncio
import sys
from typing import Any

from benchmarks.utils import BenchmarkResult, benchmark

PYTHON_VERSION = sys.version_info[:2]


# =============================================================================
# Exception handling (3.11+ has zero-cost try/except)
# =============================================================================


def exception_no_raise(iterations: int) -> int:
    """Try/except with NO exception raised - tests zero-cost in 3.11+."""
    total = 0
    for i in range(iterations):
        try:  # noqa: SIM105 - intentionally benchmarking try/except
            total += i
        except ValueError:
            pass
    return total


def exception_always_raise(iterations: int) -> int:
    """Try/except with exception ALWAYS raised."""
    caught = 0
    for i in range(iterations):
        try:
            raise ValueError(i)
        except ValueError:
            caught += 1
    return caught


def exception_conditional_raise(iterations: int) -> int:
    """Try/except with occasional exceptions (realistic pattern)."""
    caught = 0
    for i in range(iterations):
        try:
            if i % 100 == 0:
                raise ValueError(i)
        except ValueError:
            caught += 1
    return caught


def nested_exception_handling(iterations: int) -> int:
    """Deeply nested try/except blocks."""
    caught = 0
    for i in range(iterations):
        try:
            try:
                try:
                    if i % 50 == 0:
                        raise ValueError(i)
                except TypeError:
                    pass
            except KeyError:
                pass
        except ValueError:
            caught += 1
    return caught


# =============================================================================
# Pattern matching (3.10+ only, but we measure the if/elif equivalent)
# =============================================================================


def dispatch_if_elif(items: list[dict[str, Any]]) -> list[str]:
    """Traditional if/elif dispatch."""
    results = []
    for item in items:
        item_type = item.get("type")
        if item_type == "user":
            results.append(f"User: {item.get('name', 'unknown')}")
        elif item_type == "order":
            results.append(f"Order #{item.get('id', 0)}")
        elif item_type == "product":
            results.append(f"Product: {item.get('title', 'untitled')}")
        elif item_type == "event":
            results.append(f"Event at {item.get('timestamp', 'unknown')}")
        else:
            results.append("Unknown")
    return results


def dispatch_dict_lookup(items: list[dict[str, Any]]) -> list[str]:
    """Dictionary-based dispatch."""

    def handle_user(item: dict[str, Any]) -> str:
        return f"User: {item.get('name', 'unknown')}"

    def handle_order(item: dict[str, Any]) -> str:
        return f"Order #{item.get('id', 0)}"

    def handle_product(item: dict[str, Any]) -> str:
        return f"Product: {item.get('title', 'untitled')}"

    def handle_event(item: dict[str, Any]) -> str:
        return f"Event at {item.get('timestamp', 'unknown')}"

    def handle_unknown(item: dict[str, Any]) -> str:
        return "Unknown"

    handlers = {
        "user": handle_user,
        "order": handle_order,
        "product": handle_product,
        "event": handle_event,
    }

    results = []
    for item in items:
        handler = handlers.get(item.get("type"), handle_unknown)
        results.append(handler(item))
    return results


# Pattern matching version (only runs on 3.10+)
if PYTHON_VERSION >= (3, 10):
    exec(
        """
def dispatch_match_case(items):
    results = []
    for item in items:
        match item:
            case {"type": "user", "name": name}:
                results.append(f"User: {name}")
            case {"type": "user"}:
                results.append("User: unknown")
            case {"type": "order", "id": order_id}:
                results.append(f"Order #{order_id}")
            case {"type": "product", "title": title}:
                results.append(f"Product: {title}")
            case {"type": "event", "timestamp": ts}:
                results.append(f"Event at {ts}")
            case _:
                results.append("Unknown")
    return results
""",
        globals(),
    )


# =============================================================================
# Async TaskGroup (3.11+) vs gather
# =============================================================================


async def async_with_gather(n: int) -> list[int]:
    """Traditional asyncio.gather approach."""

    async def work(i: int) -> int:
        await asyncio.sleep(0)
        return i * 2

    return list(await asyncio.gather(*[work(i) for i in range(n)]))


async def async_with_taskgroup(n: int) -> list[int]:
    """TaskGroup approach (3.11+)."""
    results: list[int] = []

    if PYTHON_VERSION >= (3, 11):

        async def work(i: int) -> None:
            await asyncio.sleep(0)
            results.append(i * 2)

        async with asyncio.TaskGroup() as tg:
            for i in range(n):
                tg.create_task(work(i))
    else:
        # Fallback for older versions
        return await async_with_gather(n)

    return results


# =============================================================================
# Comprehension performance (3.12+ has inlined comprehensions)
# =============================================================================


def list_comprehension_simple(n: int) -> list[int]:
    """Simple list comprehension."""
    return [x * 2 for x in range(n)]


def list_comprehension_conditional(n: int) -> list[int]:
    """Conditional list comprehension."""
    return [x * 2 for x in range(n) if x % 2 == 0]


def list_comprehension_nested(n: int) -> list[tuple[int, int]]:
    """Nested list comprehension."""
    size = int(n**0.5)
    return [(x, y) for x in range(size) for y in range(size)]


def dict_comprehension(n: int) -> dict[str, int]:
    """Dictionary comprehension."""
    return {f"key_{x}": x * 2 for x in range(n)}


def set_comprehension(n: int) -> set[int]:
    """Set comprehension."""
    return {x % 1000 for x in range(n)}


def generator_expression_sum(n: int) -> int:
    """Generator expression consumed by sum."""
    return sum(x * 2 for x in range(n))


# =============================================================================
# String formatting (f-strings improved across versions)
# =============================================================================


def fstring_simple(n: int) -> list[str]:
    """Simple f-string formatting."""
    return [f"Value: {i}" for i in range(n)]


def fstring_complex(n: int) -> list[str]:
    """Complex f-string with expressions."""
    return [f"Val {i}: square={i**2}, half={i/2:.2f}" for i in range(n)]


def fstring_nested_quotes(n: int) -> list[str]:
    """F-strings with nested quotes (improved in 3.12)."""
    items = [{"name": f"item_{i}", "value": i} for i in range(n)]
    # 3.12+ allows f"{item['name']}" directly
    return [f"Item: {item['name']} = {item['value']}" for item in items]


def format_method(n: int) -> list[str]:
    """str.format() method for comparison."""
    return ["Value: {}".format(i) for i in range(n)]  # noqa: UP032 - intentional


def percent_formatting(n: int) -> list[str]:
    """Percent formatting for comparison."""
    return ["Value: %d" % i for i in range(n)]  # noqa: UP031 - intentional


# =============================================================================
# TOML parsing (3.11+ has tomllib built-in)
# =============================================================================


def parse_toml_content(content: str, iterations: int) -> int:
    """Parse TOML content multiple times."""
    count = 0
    if PYTHON_VERSION >= (3, 11):
        import tomllib

        for _ in range(iterations):
            data = tomllib.loads(content)
            count += len(data)
    else:
        # Use tomli package on older versions (needs to be installed)
        try:
            import tomli  # type: ignore[import-not-found]

            for _ in range(iterations):
                data = tomli.loads(content)
                count += len(data)
        except ImportError:
            pass
    return count


# =============================================================================
# Benchmark runners
# =============================================================================


def run_version_specific_benchmarks() -> list[BenchmarkResult]:
    """Run version-specific benchmarks."""
    results: list[BenchmarkResult] = []

    # Exception handling benchmarks (key 3.11+ improvement)
    results.append(
        benchmark(
            lambda: exception_no_raise(100000),
            name="Try/Except No Raise (100k)",
            category="Exceptions - Zero Cost",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: exception_always_raise(10000),
            name="Try/Except Always Raise (10k)",
            category="Exceptions - Raise",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: exception_conditional_raise(100000),
            name="Try/Except Conditional (100k, 1% raise)",
            category="Exceptions - Conditional",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: nested_exception_handling(50000),
            name="Nested Try/Except (50k)",
            category="Exceptions - Nested",
            iterations=10,
        )
    )

    # Pattern matching / dispatch benchmarks
    dispatch_items = [
        {"type": t, "name": f"n{i}", "id": i, "title": f"t{i}", "timestamp": f"ts{i}"}
        for i, t in enumerate(["user", "order", "product", "event", "unknown"] * 10000)
    ]

    results.append(
        benchmark(
            lambda: dispatch_if_elif(dispatch_items),
            name="Dispatch If/Elif (50k items)",
            category="Dispatch - If/Elif",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: dispatch_dict_lookup(dispatch_items),
            name="Dispatch Dict Lookup (50k items)",
            category="Dispatch - Dict",
            iterations=10,
        )
    )

    if PYTHON_VERSION >= (3, 10):
        results.append(
            benchmark(
                lambda: dispatch_match_case(dispatch_items),  # noqa: F821
                name="Dispatch Match/Case (50k items)",
                category="Dispatch - Pattern Match",
                iterations=10,
            )
        )

    # Async benchmarks
    results.append(
        benchmark(
            lambda: asyncio.run(async_with_gather(1000)),
            name="Async Gather (1k tasks)",
            category="Async - Gather",
            iterations=10,
        )
    )

    if PYTHON_VERSION >= (3, 11):
        results.append(
            benchmark(
                lambda: asyncio.run(async_with_taskgroup(1000)),
                name="Async TaskGroup (1k tasks)",
                category="Async - TaskGroup",
                iterations=10,
            )
        )

    # Comprehension benchmarks
    results.append(
        benchmark(
            lambda: list_comprehension_simple(100000),
            name="List Comprehension Simple (100k)",
            category="Comprehension - List",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: list_comprehension_conditional(100000),
            name="List Comprehension Conditional (100k)",
            category="Comprehension - List",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: list_comprehension_nested(10000),
            name="List Comprehension Nested (100x100)",
            category="Comprehension - List",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: dict_comprehension(50000),
            name="Dict Comprehension (50k)",
            category="Comprehension - Dict",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: set_comprehension(100000),
            name="Set Comprehension (100k)",
            category="Comprehension - Set",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: generator_expression_sum(1000000),
            name="Generator Expression Sum (1M)",
            category="Comprehension - Generator",
            iterations=10,
        )
    )

    # String formatting benchmarks
    results.append(
        benchmark(
            lambda: fstring_simple(50000),
            name="F-String Simple (50k)",
            category="Strings - F-String",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: fstring_complex(50000),
            name="F-String Complex (50k)",
            category="Strings - F-String",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: fstring_nested_quotes(50000),
            name="F-String Nested Quotes (50k)",
            category="Strings - F-String",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: format_method(50000),
            name="str.format() (50k)",
            category="Strings - Format",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: percent_formatting(50000),
            name="Percent Formatting (50k)",
            category="Strings - Percent",
            iterations=10,
        )
    )

    # TOML parsing (3.11+ has tomllib)
    sample_toml = """
[project]
name = "test-project"
version = "1.0.0"
description = "A test project"

[project.dependencies]
numpy = ">=1.20.0"
pandas = ">=1.3.0"

[tool.ruff]
line-length = 100

[[items]]
name = "item1"
value = 42

[[items]]
name = "item2"
value = 84
"""

    if PYTHON_VERSION >= (3, 11):
        results.append(
            benchmark(
                lambda: parse_toml_content(sample_toml, 1000),
                name="TOML Parse tomllib (1k)",
                category="Parsing - TOML",
                iterations=10,
            )
        )

    return results


if __name__ == "__main__":
    from benchmarks.utils import format_time

    print(f"Running version-specific benchmarks (Python {PYTHON_VERSION[0]}.{PYTHON_VERSION[1]})...")
    results = run_version_specific_benchmarks()
    for r in results:
        print(f"{r.name}: {format_time(r.mean_time)} ± {format_time(r.std_dev)}")
