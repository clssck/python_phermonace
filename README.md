# Python Version Performance Comparison

A comprehensive benchmark suite comparing Python 3.9, 3.11, 3.12, 3.13, and 3.14 performance. Designed to provide data-driven justification for upgrading from Python 3.9.

## Purpose

This project addresses the common scenario where development teams need concrete evidence to justify upgrading Python versions. It's particularly relevant for:

- **Dataiku users** running Python 3.9 who need performance metrics to justify upgrades
- **Data science teams** evaluating NumPy/Pandas performance across versions
- **Backend developers** comparing async and I/O performance

## Quick Start

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Run all benchmarks across all Python versions
uv run python run_benchmarks.py

# Run quick benchmarks (skip data science benchmarks)
uv run python run_benchmarks.py --quick

# Run specific versions only
uv run python run_benchmarks.py --versions 3.9 3.12 3.13

# Generate visualizations from results
uv run python visualize_results.py
```

## Benchmark Categories

### CPU Benchmarks
- Fibonacci (recursive/iterative/generator)
- Prime number calculations (sieve, naive)
- Matrix operations (pure Python)
- String operations (concat, join, formatting)
- Float-intensive (Mandelbrot, N-body simulation)
- Big integer operations (factorial)

### Data Structure Benchmarks
- Dictionary operations (creation, lookup, merge, iteration)
- List operations (append, sort, filter, slice)
- Set operations (creation, lookup, union/intersection)
- Tuple operations (creation, unpacking)
- Deque operations (append, rotate)
- Collections (Counter, defaultdict)

### I/O and Serialization
- JSON serialization/deserialization
- CSV read/write operations
- Pickle operations
- Text processing (split, join, replace)
- File I/O (read/write lines)

### Async Benchmarks
- asyncio task creation and scheduling
- TaskGroup (Python 3.11+)
- Queue operations
- Synchronization primitives (Lock, Event, Semaphore)
- Exception handling in async context
- Async generators and comprehensions

### Data Science Benchmarks
- NumPy array operations (creation, matrix ops, element-wise)
- NumPy aggregations and sorting
- Pandas DataFrame operations (creation, groupby, filter)
- Pandas merge/join operations
- Pandas rolling window calculations
- ETL pipeline simulations
- Feature engineering pipelines

### Startup and Memory
- Python interpreter startup time
- Module import times
- Memory overhead for data structures
- Exception handling overhead
- Function call overhead

## Key Python Version Improvements

### Python 3.11
- **10-60% faster** overall due to Faster CPython project
- Zero-cost exception handling (try blocks have no overhead)
- Specialized adaptive interpreter
- Optimized dict and list operations
- TaskGroup for structured concurrency

### Python 3.12
- Further interpreter optimizations
- Improved error messages
- Per-interpreter GIL (experimental)
- Better memory management

### Python 3.13
- Experimental JIT compiler
- Additional performance improvements
- Free-threaded mode (experimental)

### Python 3.14
- Latest optimizations and features
- Continued performance work

## Output

After running benchmarks, you'll find in the `results/` directory:

- `benchmark_results.json` - Raw benchmark data
- `benchmark_summary.json` - Summary with top improvements
- `benchmark_report.md` - Detailed Markdown report
- `overall_comparison.png` - Overall speedup chart
- `category_comparison.png` - Category-wise comparison
- `speedup_heatmap.png` - Heatmap of all benchmarks
- `top_improvements_*.png` - Top improvements per version
- `timing_distribution.png` - Timing distribution by category

## Development

```bash
# Lint code
uvx ruff check .

# Format code
uvx ruff format .

# Type check
uvx ty check

# Run single benchmark module
uv run python -m benchmarks.cpu_benchmarks
```

## Project Structure

```
python_phermonace/
├── benchmarks/
│   ├── __init__.py
│   ├── utils.py                    # Benchmark utilities
│   ├── cpu_benchmarks.py           # CPU-intensive benchmarks
│   ├── data_structure_benchmarks.py # Data structure operations
│   ├── io_benchmarks.py            # I/O and serialization
│   ├── async_benchmarks.py         # Async/concurrency benchmarks
│   ├── datascience_benchmarks.py   # NumPy/Pandas benchmarks
│   └── startup_memory_benchmarks.py # Startup/memory overhead
├── results/                        # Benchmark results (generated)
├── run_benchmarks.py              # Main benchmark runner
├── visualize_results.py           # Generate charts and reports
├── pyproject.toml                 # Project configuration
└── README.md
```

## Why This Matters for Dataiku

1. **Data Pipeline Performance**: NumPy and Pandas operations in newer Python versions show measurable improvements that directly impact data pipeline execution times.

2. **Exception Handling**: Python 3.11+ has zero-cost exception handling, which benefits code with try/except blocks (common in data validation).

3. **Memory Efficiency**: Reduced memory footprint allows processing larger datasets.

4. **Security**: Python 3.9 reaches end-of-life in October 2025. Continued use means no security patches.

5. **Ecosystem Support**: Major libraries are dropping Python 3.9 support.

## License

MIT
