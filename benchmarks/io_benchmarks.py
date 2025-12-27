"""
I/O and serialization benchmarks to compare Python version performance.

These benchmarks stress:
- JSON serialization/deserialization
- CSV processing
- File read/write operations
- Pickle operations
- Text processing
"""

from __future__ import annotations

import csv
import io
import json
import pickle
import random
import tempfile
from pathlib import Path
from typing import Any

from benchmarks.utils import BenchmarkResult, benchmark

# Set seed for reproducibility
random.seed(42)


# =============================================================================
# JSON benchmarks
# =============================================================================


def generate_complex_json_data(n_records: int) -> list[dict[str, Any]]:
    """Generate complex nested JSON data."""
    return [
        {
            "id": i,
            "name": f"User_{i}",
            "email": f"user_{i}@example.com",
            "active": i % 2 == 0,
            "score": random.random() * 100,
            "tags": [f"tag_{j}" for j in range(random.randint(1, 5))],
            "metadata": {
                "created_at": f"2024-01-{(i % 28) + 1:02d}",
                "updated_at": f"2024-12-{(i % 28) + 1:02d}",
                "settings": {
                    "notifications": i % 3 == 0,
                    "theme": ["light", "dark", "auto"][i % 3],
                    "language": ["en", "es", "fr", "de"][i % 4],
                },
            },
            "scores": [random.random() * 100 for _ in range(10)],
        }
        for i in range(n_records)
    ]


def json_serialize(data: list[dict[str, Any]]) -> str:
    """Serialize data to JSON string."""
    return json.dumps(data)


def json_deserialize(json_str: str) -> list[dict[str, Any]]:
    """Deserialize JSON string to data."""
    result: list[dict[str, Any]] = json.loads(json_str)
    return result


def json_serialize_pretty(data: list[dict[str, Any]]) -> str:
    """Serialize data to pretty-printed JSON."""
    return json.dumps(data, indent=2, sort_keys=True)


def json_file_operations(data: list[dict[str, Any]], path: Path) -> list[dict[str, Any]]:
    """Write and read JSON file."""
    with open(path, "w") as f:
        json.dump(data, f)
    with open(path) as f:
        result: list[dict[str, Any]] = json.load(f)
    return result


# =============================================================================
# CSV benchmarks
# =============================================================================


def generate_csv_data(n_rows: int, n_cols: int) -> list[list[str]]:
    """Generate CSV data."""
    headers = [f"column_{i}" for i in range(n_cols)]
    rows = [[str(random.random()) for _ in range(n_cols)] for _ in range(n_rows)]
    return [headers] + rows


def csv_write_stringio(data: list[list[str]]) -> str:
    """Write CSV to StringIO."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerows(data)
    return output.getvalue()


def csv_read_stringio(csv_str: str) -> list[list[str]]:
    """Read CSV from StringIO."""
    reader = csv.reader(io.StringIO(csv_str))
    return list(reader)


def csv_dictwriter(data: list[dict[str, Any]]) -> str:
    """Write CSV using DictWriter."""
    if not data:
        return ""
    output = io.StringIO()
    fieldnames = list(data[0].keys())
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data)
    return output.getvalue()


def csv_dictreader(csv_str: str) -> list[dict[str, str]]:
    """Read CSV using DictReader."""
    reader = csv.DictReader(io.StringIO(csv_str))
    return list(reader)


# =============================================================================
# Pickle benchmarks
# =============================================================================


def pickle_serialize(data: Any) -> bytes:
    """Serialize data using pickle."""
    return pickle.dumps(data)


def pickle_deserialize(data: bytes) -> Any:
    """Deserialize pickle data."""
    return pickle.loads(data)


def pickle_file_operations(data: Any, path: Path) -> Any:
    """Write and read pickle file."""
    with open(path, "wb") as f:
        pickle.dump(data, f)
    with open(path, "rb") as f:
        return pickle.load(f)


# =============================================================================
# Text processing benchmarks
# =============================================================================


def generate_text_data(n_lines: int, line_length: int) -> str:
    """Generate random text data."""
    chars = "abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    lines = [
        "".join(random.choice(chars) for _ in range(line_length)) for _ in range(n_lines)
    ]
    return "\n".join(lines)


def text_line_processing(text: str) -> list[str]:
    """Process text line by line."""
    return [line.strip().upper() for line in text.splitlines() if line.strip()]


def text_split_join(text: str) -> str:
    """Split and rejoin text."""
    words = text.split()
    return " ".join(words)


def text_replace_multiple(text: str) -> str:
    """Multiple string replacements."""
    result = text
    for old, new in [("a", "X"), ("e", "Y"), ("i", "Z"), ("o", "W"), ("u", "V")]:
        result = result.replace(old, new)
    return result


def text_count_words(text: str) -> dict[str, int]:
    """Count word frequencies."""
    words = text.lower().split()
    counts: dict[str, int] = {}
    for word in words:
        counts[word] = counts.get(word, 0) + 1
    return counts


def text_find_all(text: str, pattern: str) -> list[int]:
    """Find all occurrences of pattern in text."""
    positions = []
    start = 0
    while True:
        pos = text.find(pattern, start)
        if pos == -1:
            break
        positions.append(pos)
        start = pos + 1
    return positions


# =============================================================================
# File I/O benchmarks
# =============================================================================


def file_write_lines(path: Path, n_lines: int) -> None:
    """Write many lines to file."""
    with open(path, "w") as f:
        for i in range(n_lines):
            f.write(f"Line number {i} with some content\n")


def file_read_lines(path: Path) -> list[str]:
    """Read all lines from file."""
    with open(path) as f:
        return f.readlines()


def file_read_iterate(path: Path) -> int:
    """Read file by iterating over lines."""
    count = 0
    with open(path) as f:
        for line in f:
            count += len(line)
    return count


def file_write_read_binary(path: Path, size_mb: float) -> int:
    """Write and read binary data."""
    data = bytes(random.randint(0, 255) for _ in range(int(size_mb * 1024 * 1024)))
    with open(path, "wb") as f:
        f.write(data)
    with open(path, "rb") as f:
        result = f.read()
    return len(result)


# =============================================================================
# Benchmark runners
# =============================================================================


def run_io_benchmarks() -> list[BenchmarkResult]:
    """Run all I/O benchmarks and return results."""
    results: list[BenchmarkResult] = []

    # Prepare test data
    json_data_small = generate_complex_json_data(1000)
    json_data_large = generate_complex_json_data(10000)
    json_str_small = json.dumps(json_data_small)
    json_str_large = json.dumps(json_data_large)

    csv_data = generate_csv_data(10000, 20)
    csv_str = csv_write_stringio(csv_data)

    dict_data = [{"col_" + str(i): str(random.random()) for i in range(20)} for _ in range(10000)]
    dict_csv_str = csv_dictwriter(dict_data)

    text_data = generate_text_data(10000, 100)
    large_text = generate_text_data(50000, 200)

    # Create temp directory for file operations
    temp_dir = Path(tempfile.mkdtemp())

    # JSON benchmarks
    results.append(
        benchmark(
            lambda: json_serialize(json_data_small),
            name="JSON Serialize (1k records)",
            category="I/O - JSON",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: json_serialize(json_data_large),
            name="JSON Serialize (10k records)",
            category="I/O - JSON",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: json_deserialize(json_str_small),
            name="JSON Deserialize (1k records)",
            category="I/O - JSON",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: json_deserialize(json_str_large),
            name="JSON Deserialize (10k records)",
            category="I/O - JSON",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: json_serialize_pretty(json_data_small),
            name="JSON Pretty Print (1k records)",
            category="I/O - JSON",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: json_file_operations(json_data_small, temp_dir / "test.json"),
            name="JSON File Read/Write (1k records)",
            category="I/O - JSON",
            iterations=10,
        )
    )

    # CSV benchmarks
    results.append(
        benchmark(
            lambda: csv_write_stringio(csv_data),
            name="CSV Write StringIO (10k rows)",
            category="I/O - CSV",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: csv_read_stringio(csv_str),
            name="CSV Read StringIO (10k rows)",
            category="I/O - CSV",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: csv_dictwriter(dict_data),
            name="CSV DictWriter (10k rows)",
            category="I/O - CSV",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: csv_dictreader(dict_csv_str),
            name="CSV DictReader (10k rows)",
            category="I/O - CSV",
            iterations=10,
        )
    )

    # Pickle benchmarks
    pickle_bytes = pickle_serialize(json_data_large)
    results.append(
        benchmark(
            lambda: pickle_serialize(json_data_large),
            name="Pickle Serialize (10k records)",
            category="I/O - Pickle",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: pickle_deserialize(pickle_bytes),
            name="Pickle Deserialize (10k records)",
            category="I/O - Pickle",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: pickle_file_operations(json_data_small, temp_dir / "test.pkl"),
            name="Pickle File Read/Write (1k records)",
            category="I/O - Pickle",
            iterations=10,
        )
    )

    # Text processing benchmarks
    results.append(
        benchmark(
            lambda: text_line_processing(text_data),
            name="Text Line Processing (10k lines)",
            category="I/O - Text",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: text_split_join(large_text),
            name="Text Split/Join (50k lines)",
            category="I/O - Text",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: text_replace_multiple(large_text),
            name="Text Multiple Replace (50k lines)",
            category="I/O - Text",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: text_count_words(large_text),
            name="Text Word Count (50k lines)",
            category="I/O - Text",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: text_find_all(large_text, "the"),
            name="Text Find All Pattern (50k lines)",
            category="I/O - Text",
            iterations=10,
        )
    )

    # File I/O benchmarks
    file_write_lines(temp_dir / "lines.txt", 50000)
    results.append(
        benchmark(
            lambda: file_write_lines(temp_dir / "write_test.txt", 10000),
            name="File Write Lines (10k)",
            category="I/O - File",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: file_read_lines(temp_dir / "lines.txt"),
            name="File Read Lines (50k)",
            category="I/O - File",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: file_read_iterate(temp_dir / "lines.txt"),
            name="File Iterate Lines (50k)",
            category="I/O - File",
            iterations=10,
        )
    )

    # Cleanup
    import shutil

    shutil.rmtree(temp_dir, ignore_errors=True)

    return results


if __name__ == "__main__":
    from benchmarks.utils import format_time

    print("Running I/O benchmarks...")
    results = run_io_benchmarks()
    for r in results:
        print(f"{r.name}: {format_time(r.mean_time)} ± {format_time(r.std_dev)}")
