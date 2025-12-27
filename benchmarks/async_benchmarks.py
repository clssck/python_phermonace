"""
Async and concurrency benchmarks to compare Python version performance.

These benchmarks stress:
- asyncio task creation and scheduling
- async/await overhead
- Concurrent execution patterns
- Threading vs async comparison
- Exception handling in async context (3.11+ improvements)
"""

from __future__ import annotations

import asyncio
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from benchmarks.utils import BenchmarkResult, benchmark

# Check Python version for feature availability
PY311_PLUS = sys.version_info >= (3, 11)


# =============================================================================
# Basic async benchmarks
# =============================================================================


async def async_noop() -> None:
    """Minimal async function."""
    pass


async def async_sleep_zero() -> None:
    """Async sleep with zero delay (yields control)."""
    await asyncio.sleep(0)


async def async_gather_tasks(n: int) -> list[int]:
    """Create and gather many tasks."""

    async def task(i: int) -> int:
        await asyncio.sleep(0)
        return i * 2

    tasks = [task(i) for i in range(n)]
    results: list[int] = await asyncio.gather(*tasks)
    return results


async def async_sequential(n: int) -> int:
    """Sequential async operations."""
    total = 0
    for i in range(n):
        await asyncio.sleep(0)
        total += i
    return total


async def async_create_tasks(n: int) -> list[int]:
    """Create tasks individually and await them."""
    tasks = []
    for i in range(n):
        task: asyncio.Task[int] = asyncio.create_task(async_work(i))
        tasks.append(task)

    results = []
    for task in tasks:
        results.append(await task)
    return results


async def async_work(value: int) -> int:
    """Simulated async work."""
    await asyncio.sleep(0)
    return value * 2


# =============================================================================
# TaskGroup benchmarks (Python 3.11+)
# =============================================================================


async def async_taskgroup(n: int) -> list[int]:
    """Use TaskGroup for concurrent tasks (3.11+ feature)."""
    results: list[int] = []

    if PY311_PLUS:
        async with asyncio.TaskGroup() as tg:
            tasks = [tg.create_task(async_work(i)) for i in range(n)]
        results = [t.result() for t in tasks]
    else:
        # Fallback for older versions
        tasks_list = [asyncio.create_task(async_work(i)) for i in range(n)]
        results = await asyncio.gather(*tasks_list)

    return results


# =============================================================================
# Queue benchmarks
# =============================================================================


async def async_queue_operations(n_producers: int, n_items: int) -> int:
    """Producer-consumer pattern with async queue."""
    queue: asyncio.Queue[int] = asyncio.Queue()
    total_produced = 0
    total_consumed = 0

    async def producer(producer_id: int) -> None:
        nonlocal total_produced
        for i in range(n_items):
            await queue.put(producer_id * 1000 + i)
            total_produced += 1

    async def consumer() -> None:
        nonlocal total_consumed
        while True:
            try:
                await asyncio.wait_for(queue.get(), timeout=0.01)
                total_consumed += 1
                queue.task_done()
            except asyncio.TimeoutError:
                if queue.empty():
                    break

    # Start producers
    producer_tasks = [asyncio.create_task(producer(i)) for i in range(n_producers)]
    await asyncio.gather(*producer_tasks)

    # Start consumers
    consumer_tasks = [asyncio.create_task(consumer()) for _ in range(n_producers)]
    await asyncio.gather(*consumer_tasks)

    return total_consumed


# =============================================================================
# Event and synchronization benchmarks
# =============================================================================


async def async_event_wait(n: int) -> int:
    """Test Event synchronization primitive."""
    event = asyncio.Event()
    count = 0

    async def waiter() -> None:
        nonlocal count
        await event.wait()
        count += 1

    async def setter() -> None:
        await asyncio.sleep(0)
        event.set()

    for _ in range(n):
        event.clear()
        waiters = [asyncio.create_task(waiter()) for _ in range(10)]
        await asyncio.create_task(setter())
        await asyncio.gather(*waiters)

    return count


async def async_lock_contention(n: int) -> int:
    """Test Lock contention."""
    lock = asyncio.Lock()
    counter = 0

    async def increment() -> None:
        nonlocal counter
        async with lock:
            temp = counter
            await asyncio.sleep(0)
            counter = temp + 1

    tasks = [asyncio.create_task(increment()) for _ in range(n)]
    await asyncio.gather(*tasks)
    return counter


async def async_semaphore(n: int, limit: int) -> int:
    """Test Semaphore for rate limiting."""
    semaphore = asyncio.Semaphore(limit)
    counter = 0

    async def limited_work() -> None:
        nonlocal counter
        async with semaphore:
            await asyncio.sleep(0)
            counter += 1

    tasks = [asyncio.create_task(limited_work()) for _ in range(n)]
    await asyncio.gather(*tasks)
    return counter


# =============================================================================
# Exception handling benchmarks
# =============================================================================


async def async_exception_handling(n: int) -> int:
    """Test exception handling in async context."""
    caught = 0

    async def may_fail(i: int) -> int:
        if i % 3 == 0:
            raise ValueError(f"Failed at {i}")
        return i

    for i in range(n):
        try:
            await may_fail(i)
        except ValueError:
            caught += 1

    return caught


async def async_exception_group(n: int) -> int:
    """Test exception handling with multiple concurrent failures."""
    caught = 0

    async def may_fail(i: int) -> int:
        await asyncio.sleep(0)
        if i % 5 == 0:
            raise ValueError(f"Failed at {i}")
        return i

    tasks = [may_fail(i) for i in range(n)]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    for result in results:
        if isinstance(result, Exception):
            caught += 1

    return caught


# =============================================================================
# Threading comparison benchmarks
# =============================================================================


def sync_work(value: int) -> int:
    """Synchronous work for comparison."""
    time.sleep(0.0001)
    return value * 2


def threaded_execution(n: int, workers: int) -> list[int]:
    """Execute work using thread pool."""
    with ThreadPoolExecutor(max_workers=workers) as executor:
        results = list(executor.map(sync_work, range(n)))
    return results


async def async_execution(n: int) -> list[int]:
    """Execute work using async."""

    async def work(i: int) -> int:
        await asyncio.sleep(0.0001)
        return i * 2

    return await asyncio.gather(*[work(i) for i in range(n)])


# =============================================================================
# Async comprehension benchmarks
# =============================================================================


async def async_generator(n: int) -> int:
    """Async generator benchmark."""

    async def gen() -> Any:
        for i in range(n):
            await asyncio.sleep(0)
            yield i

    total = 0
    async for value in gen():
        total += value
    return total


async def async_comprehension(n: int) -> list[int]:
    """Async comprehension benchmark."""

    async def get_value(i: int) -> int:
        await asyncio.sleep(0)
        return i * 2

    return [await get_value(i) for i in range(n)]


# =============================================================================
# Benchmark runners
# =============================================================================


def run_async_benchmark(coro: Any) -> None:
    """Helper to run async benchmark."""
    asyncio.run(coro)


def run_async_benchmarks() -> list[BenchmarkResult]:
    """Run all async benchmarks and return results."""
    results: list[BenchmarkResult] = []

    # Basic async overhead
    results.append(
        benchmark(
            lambda: asyncio.run(async_noop()),
            name="Async Noop (event loop overhead)",
            category="Async - Overhead",
            iterations=100,
        )
    )

    results.append(
        benchmark(
            lambda: asyncio.run(async_gather_tasks(1000)),
            name="Async Gather (1k tasks)",
            category="Async - Tasks",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: asyncio.run(async_create_tasks(1000)),
            name="Async Create Tasks (1k)",
            category="Async - Tasks",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: asyncio.run(async_sequential(1000)),
            name="Async Sequential (1k awaits)",
            category="Async - Sequential",
            iterations=10,
        )
    )

    # TaskGroup (3.11+ optimized)
    results.append(
        benchmark(
            lambda: asyncio.run(async_taskgroup(1000)),
            name="Async TaskGroup (1k tasks)",
            category="Async - TaskGroup",
            iterations=10,
        )
    )

    # Queue operations
    results.append(
        benchmark(
            lambda: asyncio.run(async_queue_operations(10, 100)),
            name="Async Queue (10 producers, 100 items each)",
            category="Async - Queue",
            iterations=10,
        )
    )

    # Synchronization primitives
    results.append(
        benchmark(
            lambda: asyncio.run(async_event_wait(100)),
            name="Async Event Wait (100 rounds)",
            category="Async - Sync",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: asyncio.run(async_lock_contention(500)),
            name="Async Lock Contention (500 tasks)",
            category="Async - Sync",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: asyncio.run(async_semaphore(500, 10)),
            name="Async Semaphore (500 tasks, limit 10)",
            category="Async - Sync",
            iterations=10,
        )
    )

    # Exception handling
    results.append(
        benchmark(
            lambda: asyncio.run(async_exception_handling(1000)),
            name="Async Exception Handling (1k)",
            category="Async - Exceptions",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: asyncio.run(async_exception_group(500)),
            name="Async Exception Group (500 tasks)",
            category="Async - Exceptions",
            iterations=10,
        )
    )

    # Async generators and comprehensions
    results.append(
        benchmark(
            lambda: asyncio.run(async_generator(1000)),
            name="Async Generator (1k yields)",
            category="Async - Generators",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: asyncio.run(async_comprehension(500)),
            name="Async Comprehension (500 items)",
            category="Async - Comprehension",
            iterations=10,
        )
    )

    # Threading comparison
    results.append(
        benchmark(
            lambda: threaded_execution(100, 10),
            name="ThreadPool Execution (100 tasks, 10 workers)",
            category="Concurrency - Threads",
            iterations=5,
        )
    )

    results.append(
        benchmark(
            lambda: asyncio.run(async_execution(100)),
            name="Async Execution (100 tasks)",
            category="Concurrency - Async",
            iterations=5,
        )
    )

    return results


if __name__ == "__main__":
    from benchmarks.utils import format_time

    print(f"Running async benchmarks (Python {sys.version_info.major}.{sys.version_info.minor})...")
    print(f"TaskGroup available: {PY311_PLUS}")
    results = run_async_benchmarks()
    for r in results:
        print(f"{r.name}: {format_time(r.mean_time)} ± {format_time(r.std_dev)}")
