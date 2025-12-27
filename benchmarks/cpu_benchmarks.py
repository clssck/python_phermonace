"""
CPU-intensive benchmarks to compare Python version performance.

These benchmarks stress:
- Arithmetic operations (3.11+ has faster math)
- Function call overhead (3.11+ adaptive interpreter)
- Loop performance
- Recursion
- Integer operations (3.11+ optimized)
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from benchmarks.utils import BenchmarkResult, benchmark

if TYPE_CHECKING:
    from collections.abc import Generator


# =============================================================================
# Fibonacci benchmarks (recursion + function call overhead)
# =============================================================================


def fib_recursive(n: int) -> int:
    """Classic recursive fibonacci - stresses function call overhead."""
    if n < 2:
        return n
    return fib_recursive(n - 1) + fib_recursive(n - 2)


def fib_iterative(n: int) -> int:
    """Iterative fibonacci - stresses loop performance."""
    if n < 2:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def fib_generator(n: int) -> int:
    """Generator-based fibonacci."""

    def gen() -> Generator[int, None, None]:
        a, b = 0, 1
        while True:
            yield a
            a, b = b, a + b

    g = gen()
    for _ in range(n + 1):
        result = next(g)
    return result


# =============================================================================
# Prime number benchmarks (arithmetic + loops)
# =============================================================================


def is_prime(n: int) -> bool:
    """Check if a number is prime."""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    # Using explicit loop for benchmark purposes (measuring loop overhead)
    for i in range(3, int(math.sqrt(n)) + 1, 2):  # noqa: SIM110
        if n % i == 0:
            return False
    return True


def sieve_of_eratosthenes(limit: int) -> list[int]:
    """Find all primes up to limit using Sieve of Eratosthenes."""
    if limit < 2:
        return []
    sieve = [True] * (limit + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(math.sqrt(limit)) + 1):
        if sieve[i]:
            for j in range(i * i, limit + 1, i):
                sieve[j] = False
    return [i for i, is_p in enumerate(sieve) if is_p]


def count_primes_naive(limit: int) -> int:
    """Count primes using naive method - stresses function calls."""
    return sum(1 for n in range(2, limit + 1) if is_prime(n))


# =============================================================================
# Numerical computation benchmarks
# =============================================================================


def pi_leibniz(iterations: int) -> float:
    """Calculate pi using Leibniz formula - stresses float operations."""
    pi = 0.0
    sign = 1.0
    for i in range(iterations):
        pi += sign / (2 * i + 1)
        sign = -sign
    return pi * 4


def factorial_iterative(n: int) -> int:
    """Calculate factorial iteratively - stresses big integer operations."""
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result


def factorial_recursive(n: int) -> int:
    """Calculate factorial recursively."""
    if n <= 1:
        return 1
    return n * factorial_recursive(n - 1)


def sum_of_squares(n: int) -> int:
    """Sum of squares from 1 to n."""
    total = 0
    for i in range(1, n + 1):
        total += i * i
    return total


def sum_of_squares_comprehension(n: int) -> int:
    """Sum of squares using comprehension."""
    return sum(i * i for i in range(1, n + 1))


# =============================================================================
# Matrix operations (pure Python, no numpy)
# =============================================================================


def matrix_multiply(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
    """Multiply two matrices - stresses nested loops and list access."""
    rows_a, cols_a = len(a), len(a[0])
    cols_b = len(b[0])
    result = [[0.0] * cols_b for _ in range(rows_a)]
    for i in range(rows_a):
        for j in range(cols_b):
            for k in range(cols_a):
                result[i][j] += a[i][k] * b[k][j]
    return result


def create_matrix(rows: int, cols: int) -> list[list[float]]:
    """Create a matrix with sequential values."""
    return [[float(i * cols + j) for j in range(cols)] for i in range(rows)]


# =============================================================================
# String processing benchmarks
# =============================================================================


def string_concatenation(iterations: int) -> str:
    """Stress test string concatenation."""
    result = ""
    for i in range(iterations):
        result += str(i)
    return result


def string_join(iterations: int) -> str:
    """String building using join - more efficient."""
    return "".join(str(i) for i in range(iterations))


def string_formatting(iterations: int) -> list[str]:
    """Stress test f-string formatting."""
    return [f"Value {i}: {i * 2}, squared: {i ** 2}" for i in range(iterations)]


# =============================================================================
# Float-heavy computations
# =============================================================================


def mandelbrot_point(c_real: float, c_imag: float, max_iter: int) -> int:
    """Check if a point is in the Mandelbrot set."""
    z_real, z_imag = 0.0, 0.0
    for i in range(max_iter):
        z_real_sq = z_real * z_real
        z_imag_sq = z_imag * z_imag
        if z_real_sq + z_imag_sq > 4.0:
            return i
        z_imag = 2.0 * z_real * z_imag + c_imag
        z_real = z_real_sq - z_imag_sq + c_real
    return max_iter


def mandelbrot_set(
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float,
    width: int,
    height: int,
    max_iter: int,
) -> list[list[int]]:
    """Generate a Mandelbrot set image."""
    result = []
    for py in range(height):
        row = []
        y = y_min + (y_max - y_min) * py / height
        for px in range(width):
            x = x_min + (x_max - x_min) * px / width
            row.append(mandelbrot_point(x, y, max_iter))
        result.append(row)
    return result


def nbody_step(
    positions: list[list[float]],
    velocities: list[list[float]],
    masses: list[float],
    dt: float,
) -> None:
    """N-body simulation step - stresses float operations."""
    n = len(positions)
    g = 6.67430e-11

    # Calculate accelerations
    for i in range(n):
        ax, ay, az = 0.0, 0.0, 0.0
        for j in range(n):
            if i != j:
                dx = positions[j][0] - positions[i][0]
                dy = positions[j][1] - positions[i][1]
                dz = positions[j][2] - positions[i][2]
                dist_sq = dx * dx + dy * dy + dz * dz + 1e-10
                dist = math.sqrt(dist_sq)
                force = g * masses[j] / dist_sq
                ax += force * dx / dist
                ay += force * dy / dist
                az += force * dz / dist

        velocities[i][0] += ax * dt
        velocities[i][1] += ay * dt
        velocities[i][2] += az * dt

    # Update positions
    for i in range(n):
        positions[i][0] += velocities[i][0] * dt
        positions[i][1] += velocities[i][1] * dt
        positions[i][2] += velocities[i][2] * dt


# =============================================================================
# Benchmark runners
# =============================================================================


def run_cpu_benchmarks() -> list[BenchmarkResult]:
    """Run all CPU benchmarks and return results."""
    results: list[BenchmarkResult] = []

    # Fibonacci benchmarks
    results.append(
        benchmark(
            lambda: fib_recursive(30),
            name="Fibonacci Recursive (n=30)",
            category="CPU - Recursion",
            iterations=5,
        )
    )

    results.append(
        benchmark(
            lambda: fib_iterative(100000),
            name="Fibonacci Iterative (n=100k)",
            category="CPU - Loops",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: fib_generator(100000),
            name="Fibonacci Generator (n=100k)",
            category="CPU - Generators",
            iterations=10,
        )
    )

    # Prime benchmarks
    results.append(
        benchmark(
            lambda: sieve_of_eratosthenes(1000000),
            name="Sieve of Eratosthenes (1M)",
            category="CPU - Sieve",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: count_primes_naive(50000),
            name="Count Primes Naive (50k)",
            category="CPU - Function Calls",
            iterations=5,
        )
    )

    # Numerical benchmarks
    results.append(
        benchmark(
            lambda: pi_leibniz(1000000),
            name="Pi Leibniz (1M iterations)",
            category="CPU - Float Math",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: factorial_iterative(5000),
            name="Factorial Iterative (5000)",
            category="CPU - Big Integers",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: sum_of_squares(1000000),
            name="Sum of Squares Loop (1M)",
            category="CPU - Loops",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: sum_of_squares_comprehension(1000000),
            name="Sum of Squares Comprehension (1M)",
            category="CPU - Comprehension",
            iterations=10,
        )
    )

    # Matrix benchmarks
    m1 = create_matrix(100, 100)
    m2 = create_matrix(100, 100)
    results.append(
        benchmark(
            lambda: matrix_multiply(m1, m2),
            name="Matrix Multiply 100x100",
            category="CPU - Matrix",
            iterations=5,
        )
    )

    # String benchmarks
    results.append(
        benchmark(
            lambda: string_concatenation(10000),
            name="String Concat (10k)",
            category="CPU - Strings",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: string_join(100000),
            name="String Join (100k)",
            category="CPU - Strings",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: string_formatting(50000),
            name="F-String Formatting (50k)",
            category="CPU - Strings",
            iterations=10,
        )
    )

    # Float-heavy benchmarks
    results.append(
        benchmark(
            lambda: mandelbrot_set(-2.0, 1.0, -1.5, 1.5, 200, 200, 100),
            name="Mandelbrot Set 200x200",
            category="CPU - Float Intensive",
            iterations=5,
        )
    )

    # N-body simulation
    def run_nbody() -> None:
        import random

        random.seed(42)
        n_bodies = 50
        positions = [[random.random() * 1e10 for _ in range(3)] for _ in range(n_bodies)]
        velocities = [[random.random() * 1e3 for _ in range(3)] for _ in range(n_bodies)]
        masses = [random.random() * 1e24 for _ in range(n_bodies)]
        for _ in range(100):
            nbody_step(positions, velocities, masses, 3600.0)

    results.append(
        benchmark(
            run_nbody,
            name="N-Body Simulation (50 bodies, 100 steps)",
            category="CPU - Physics Simulation",
            iterations=5,
        )
    )

    return results


if __name__ == "__main__":
    from benchmarks.utils import format_time

    print("Running CPU benchmarks...")
    results = run_cpu_benchmarks()
    for r in results:
        print(f"{r.name}: {format_time(r.mean_time)} ± {format_time(r.std_dev)}")
