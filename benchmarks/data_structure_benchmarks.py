"""
Data structure benchmarks to compare Python version performance.

These benchmarks stress:
- Dictionary operations (3.11+ has optimized dicts)
- List operations
- Set operations
- Tuple operations
- Deque operations
- DefaultDict and Counter operations
"""

from __future__ import annotations

import random
from collections import Counter, defaultdict, deque
from typing import Any

from benchmarks.utils import BenchmarkResult, benchmark

# Set seed for reproducibility
random.seed(42)


# =============================================================================
# Dictionary benchmarks
# =============================================================================


def dict_creation_literal(n: int) -> dict[str, int]:
    """Create dictionaries using literal syntax."""
    result = {}
    for i in range(n):
        result[f"key_{i}"] = i
    return result


def dict_creation_comprehension(n: int) -> dict[str, int]:
    """Create dictionaries using comprehension."""
    return {f"key_{i}": i for i in range(n)}


def dict_lookup(d: dict[str, int], keys: list[str]) -> int:
    """Perform many dictionary lookups."""
    total = 0
    for key in keys:
        total += d.get(key, 0)
    return total


def dict_update(d: dict[str, int], updates: dict[str, int]) -> dict[str, int]:
    """Update dictionary with another dictionary."""
    result = d.copy()
    result.update(updates)
    return result


def dict_merge_operator(d1: dict[str, int], d2: dict[str, int]) -> dict[str, int]:
    """Merge dictionaries using | operator (3.9+)."""
    return d1 | d2


def dict_iteration(d: dict[str, int]) -> int:
    """Iterate over dictionary items."""
    total = 0
    for k, v in d.items():
        total += len(k) + v
    return total


def dict_keys_intersection(d1: dict[str, int], d2: dict[str, int]) -> set[str]:
    """Find common keys between two dictionaries."""
    return d1.keys() & d2.keys()


def nested_dict_access(n: int) -> int:
    """Access deeply nested dictionary values."""
    # Create nested structure
    nested: dict[str, Any] = {}
    current = nested
    for i in range(10):
        current[f"level_{i}"] = {"value": i}
        if i < 9:
            current[f"level_{i}"]["next"] = {}
            current = current[f"level_{i}"]["next"]

    # Access it many times
    total = 0
    for _ in range(n):
        try:
            current = nested
            for i in range(10):
                current = current[f"level_{i}"]
                total += current["value"]
                if "next" in current:
                    current = current["next"]
        except (KeyError, TypeError):
            pass
    return total


# =============================================================================
# List benchmarks
# =============================================================================


def list_append(n: int) -> list[int]:
    """Append items to a list."""
    result: list[int] = []
    for i in range(n):
        result.append(i)
    return result


def list_comprehension(n: int) -> list[int]:
    """Create list using comprehension."""
    return [i * 2 for i in range(n)]


def list_extend(n: int) -> list[int]:
    """Extend list multiple times."""
    result: list[int] = []
    chunk = list(range(1000))
    for _ in range(n // 1000):
        result.extend(chunk)
    return result


def list_insert_front(n: int) -> list[int]:
    """Insert items at the front of a list (inefficient operation)."""
    result: list[int] = []
    for i in range(n):
        result.insert(0, i)
    return result


def list_pop_front(lst: list[int]) -> int:
    """Pop items from the front of a list."""
    result = lst.copy()
    total = 0
    while result:
        total += result.pop(0)
    return total


def list_sort(lst: list[int]) -> list[int]:
    """Sort a list."""
    result = lst.copy()
    result.sort()
    return result


def list_sort_key(lst: list[tuple[int, str]]) -> list[tuple[int, str]]:
    """Sort a list with a key function."""
    result = lst.copy()
    result.sort(key=lambda x: x[1])
    return result


def list_filter_map(lst: list[int]) -> list[int]:
    """Filter and map operations on list."""
    return [x * 2 for x in lst if x % 2 == 0]


def list_reduce_sum(lst: list[int]) -> int:
    """Sum all elements in list."""
    return sum(lst)


def list_slice_operations(lst: list[int]) -> list[int]:
    """Various slice operations."""
    result = lst[::2]  # Every other element
    result = result[10:100]  # Slice
    result = result[::-1]  # Reverse
    return result


# =============================================================================
# Set benchmarks
# =============================================================================


def set_creation(n: int) -> set[int]:
    """Create a set from range."""
    return set(range(n))


def set_comprehension(n: int) -> set[int]:
    """Create set using comprehension."""
    return {i * 2 for i in range(n)}


def set_lookup(s: set[int], items: list[int]) -> int:
    """Check membership in set."""
    return sum(1 for item in items if item in s)


def set_operations(s1: set[int], s2: set[int]) -> tuple[set[int], set[int], set[int]]:
    """Set union, intersection, difference."""
    return s1 | s2, s1 & s2, s1 - s2


def set_add_remove(n: int) -> set[int]:
    """Add and remove items from set."""
    s: set[int] = set()
    for i in range(n):
        s.add(i)
    for i in range(0, n, 2):
        s.discard(i)
    return s


# =============================================================================
# Tuple benchmarks
# =============================================================================


def tuple_creation(n: int) -> list[tuple[int, int, int]]:
    """Create many tuples."""
    return [(i, i + 1, i + 2) for i in range(n)]


def tuple_unpacking(tuples: list[tuple[int, int, int]]) -> int:
    """Unpack tuples."""
    total = 0
    for a, b, c in tuples:
        total += a + b + c
    return total


def named_tuple_creation(n: int) -> list[Any]:
    """Create named tuples."""
    from collections import namedtuple

    Point = namedtuple("Point", ["x", "y", "z"])
    return [Point(i, i + 1, i + 2) for i in range(n)]


def named_tuple_access(points: list[Any]) -> int:
    """Access named tuple attributes."""
    return sum(p.x + p.y + p.z for p in points)


# =============================================================================
# Deque benchmarks
# =============================================================================


def deque_append_both_ends(n: int) -> deque[int]:
    """Append to both ends of deque."""
    d: deque[int] = deque()
    for i in range(n):
        if i % 2 == 0:
            d.append(i)
        else:
            d.appendleft(i)
    return d


def deque_rotate(d: deque[int], rotations: int) -> deque[int]:
    """Rotate deque."""
    result = d.copy()
    for i in range(rotations):
        result.rotate(i % 10 - 5)
    return result


def deque_vs_list_front_ops(n: int) -> tuple[int, int]:
    """Compare deque vs list for front operations."""
    # Deque
    d: deque[int] = deque()
    for i in range(n):
        d.appendleft(i)
    deque_sum = sum(d)

    # List (inefficient)
    lst: list[int] = []
    for i in range(n):
        lst.insert(0, i)
    list_sum = sum(lst)

    return deque_sum, list_sum


# =============================================================================
# DefaultDict and Counter benchmarks
# =============================================================================


def defaultdict_grouping(items: list[tuple[str, int]]) -> dict[str, list[int]]:
    """Group items using defaultdict."""
    groups: defaultdict[str, list[int]] = defaultdict(list)
    for key, value in items:
        groups[key].append(value)
    return dict(groups)


def counter_operations(items: list[str]) -> Counter[str]:
    """Count items and perform operations."""
    counter = Counter(items)
    counter.update(items)
    return counter


def counter_most_common(items: list[str], n: int) -> list[tuple[str, int]]:
    """Get most common items."""
    return Counter(items).most_common(n)


# =============================================================================
# Benchmark runners
# =============================================================================


def run_data_structure_benchmarks() -> list[BenchmarkResult]:
    """Run all data structure benchmarks and return results."""
    results: list[BenchmarkResult] = []

    # Prepare test data
    n = 100000
    large_dict = {f"key_{i}": i for i in range(n)}
    large_dict2 = {f"key_{i + n // 2}": i for i in range(n)}
    lookup_keys = [f"key_{random.randint(0, n - 1)}" for _ in range(n)]

    large_list = list(range(n))
    random_list = [random.randint(0, n) for _ in range(n)]
    tuple_list = [(i, i + 1, i + 2) for i in range(n)]
    keyed_list = [(random.randint(0, n), f"str_{i}") for i in range(n)]

    large_set = set(range(n))
    large_set2 = set(range(n // 2, n + n // 2))
    set_lookup_items = [random.randint(0, n * 2) for _ in range(n)]

    group_items = [(f"group_{i % 100}", i) for i in range(n)]
    count_items = [f"item_{random.randint(0, 1000)}" for _ in range(n)]

    # Dictionary benchmarks
    results.append(
        benchmark(
            lambda: dict_creation_literal(50000),
            name="Dict Creation Literal (50k)",
            category="Data Structures - Dict",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: dict_creation_comprehension(50000),
            name="Dict Creation Comprehension (50k)",
            category="Data Structures - Dict",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: dict_lookup(large_dict, lookup_keys),
            name="Dict Lookup (100k lookups)",
            category="Data Structures - Dict",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: dict_merge_operator(large_dict, large_dict2),
            name="Dict Merge | Operator (100k each)",
            category="Data Structures - Dict",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: dict_iteration(large_dict),
            name="Dict Iteration (100k items)",
            category="Data Structures - Dict",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: nested_dict_access(10000),
            name="Nested Dict Access (10k)",
            category="Data Structures - Dict",
            iterations=10,
        )
    )

    # List benchmarks
    results.append(
        benchmark(
            lambda: list_append(100000),
            name="List Append (100k)",
            category="Data Structures - List",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: list_comprehension(100000),
            name="List Comprehension (100k)",
            category="Data Structures - List",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: list_extend(100000),
            name="List Extend (100k)",
            category="Data Structures - List",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: list_sort(random_list),
            name="List Sort (100k random)",
            category="Data Structures - List",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: list_sort_key(keyed_list),
            name="List Sort with Key (100k)",
            category="Data Structures - List",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: list_filter_map(large_list),
            name="List Filter+Map (100k)",
            category="Data Structures - List",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: list_slice_operations(large_list),
            name="List Slice Operations (100k)",
            category="Data Structures - List",
            iterations=10,
        )
    )

    # Set benchmarks
    results.append(
        benchmark(
            lambda: set_creation(100000),
            name="Set Creation (100k)",
            category="Data Structures - Set",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: set_lookup(large_set, set_lookup_items),
            name="Set Lookup (100k lookups)",
            category="Data Structures - Set",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: set_operations(large_set, large_set2),
            name="Set Operations (100k each)",
            category="Data Structures - Set",
            iterations=10,
        )
    )

    # Tuple benchmarks
    results.append(
        benchmark(
            lambda: tuple_creation(100000),
            name="Tuple Creation (100k)",
            category="Data Structures - Tuple",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: tuple_unpacking(tuple_list),
            name="Tuple Unpacking (100k)",
            category="Data Structures - Tuple",
            iterations=10,
        )
    )

    # Deque benchmarks
    large_deque = deque(range(n))
    results.append(
        benchmark(
            lambda: deque_append_both_ends(50000),
            name="Deque Append Both Ends (50k)",
            category="Data Structures - Deque",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: deque_rotate(large_deque, 1000),
            name="Deque Rotate (1000 rotations)",
            category="Data Structures - Deque",
            iterations=10,
        )
    )

    # DefaultDict and Counter benchmarks
    results.append(
        benchmark(
            lambda: defaultdict_grouping(group_items),
            name="DefaultDict Grouping (100k)",
            category="Data Structures - Collections",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: counter_operations(count_items),
            name="Counter Operations (100k)",
            category="Data Structures - Collections",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: counter_most_common(count_items, 100),
            name="Counter Most Common (100k items)",
            category="Data Structures - Collections",
            iterations=10,
        )
    )

    return results


if __name__ == "__main__":
    from benchmarks.utils import format_time

    print("Running data structure benchmarks...")
    results = run_data_structure_benchmarks()
    for r in results:
        print(f"{r.name}: {format_time(r.mean_time)} ± {format_time(r.std_dev)}")
