"""
Data science benchmarks to compare Python version performance.

These benchmarks are particularly relevant for Dataiku and data processing pipelines.
They stress:
- NumPy array operations
- Pandas DataFrame operations
- Data transformation pipelines
- Aggregations and grouping
- Memory-intensive operations
"""

from __future__ import annotations

import random
from typing import Any

import numpy as np
import pandas as pd

from benchmarks.utils import BenchmarkResult, benchmark

# Set seeds for reproducibility
random.seed(42)
np.random.seed(42)


# =============================================================================
# NumPy benchmarks
# =============================================================================


def numpy_array_creation(size: int) -> np.ndarray[Any, np.dtype[np.float64]]:
    """Create NumPy arrays."""
    return np.random.random((size, size))


def numpy_matrix_operations(
    a: np.ndarray[Any, np.dtype[np.float64]], b: np.ndarray[Any, np.dtype[np.float64]]
) -> np.ndarray[Any, np.dtype[np.float64]]:
    """Matrix multiplication and operations."""
    c = np.dot(a, b)
    d = np.linalg.inv(c + np.eye(c.shape[0]))
    return d @ c.T


def numpy_element_wise(a: np.ndarray[Any, np.dtype[np.float64]]) -> float:
    """Element-wise operations."""
    b = np.sin(a) + np.cos(a)
    c = np.exp(-b) * np.log1p(np.abs(a) + 1)
    d = np.sqrt(np.abs(c)) + np.power(a, 2)
    return float(np.sum(d))


def numpy_aggregations(a: np.ndarray[Any, np.dtype[np.float64]]) -> dict[str, float]:
    """Various aggregation operations."""
    return {
        "sum": float(np.sum(a)),
        "mean": float(np.mean(a)),
        "std": float(np.std(a)),
        "min": float(np.min(a)),
        "max": float(np.max(a)),
        "median": float(np.median(a)),
        "percentile_25": float(np.percentile(a, 25)),
        "percentile_75": float(np.percentile(a, 75)),
    }


def numpy_sorting(a: np.ndarray[Any, np.dtype[np.float64]]) -> np.ndarray[Any, np.dtype[np.float64]]:
    """Sorting operations."""
    sorted_arr = np.sort(a, axis=0)
    indices = np.argsort(sorted_arr, axis=1)
    return np.take_along_axis(sorted_arr, indices, axis=1)


def numpy_boolean_indexing(
    a: np.ndarray[Any, np.dtype[np.float64]],
) -> np.ndarray[Any, np.dtype[np.float64]]:
    """Boolean indexing operations."""
    mask = (a > 0.3) & (a < 0.7)
    result = a.copy()
    result[mask] = result[mask] * 2
    result[~mask] = 0
    return result


def numpy_broadcasting(size: int) -> np.ndarray[Any, np.dtype[np.float64]]:
    """Broadcasting operations."""
    a = np.random.random((size, 1))
    b = np.random.random((1, size))
    c = np.random.random((size, size))
    return a + b + c - np.mean(c, axis=1, keepdims=True)


def numpy_concatenation(n: int, size: int) -> np.ndarray[Any, np.dtype[np.float64]]:
    """Array concatenation operations."""
    arrays = [np.random.random((size, size)) for _ in range(n)]
    stacked = np.vstack(arrays)
    return np.hstack([stacked, stacked])


def numpy_reshape_operations(a: np.ndarray[Any, np.dtype[np.float64]]) -> np.ndarray[Any, np.dtype[np.float64]]:
    """Reshape and transpose operations."""
    flat = a.flatten()
    reshaped = flat.reshape(-1, 10)
    transposed = reshaped.T
    return transposed.reshape(a.shape)


# =============================================================================
# Pandas DataFrame benchmarks
# =============================================================================


def create_dataframe(n_rows: int, n_cols: int) -> pd.DataFrame:
    """Create a DataFrame with mixed types."""
    data: dict[str, Any] = {}

    # Numeric columns
    for i in range(n_cols // 3):
        data[f"num_{i}"] = np.random.random(n_rows) * 100

    # Integer columns
    for i in range(n_cols // 3):
        data[f"int_{i}"] = np.random.randint(0, 1000, n_rows)

    # String/Category columns
    categories = ["A", "B", "C", "D", "E"]
    for i in range(n_cols // 3):
        data[f"cat_{i}"] = np.random.choice(categories, n_rows)

    # Date column
    data["date"] = pd.date_range("2020-01-01", periods=n_rows, freq="h")

    return pd.DataFrame(data)


def pandas_groupby_agg(df: pd.DataFrame) -> pd.DataFrame:
    """GroupBy with multiple aggregations."""
    return df.groupby("cat_0").agg(
        {
            "num_0": ["mean", "std", "min", "max"],
            "num_1": ["sum", "count"],
            "int_0": ["mean", "median"],
        }
    )


def pandas_multiple_groupby(df: pd.DataFrame) -> pd.DataFrame:
    """GroupBy with multiple columns."""
    return df.groupby(["cat_0", "cat_1", "cat_2"]).agg({"num_0": "mean", "num_1": "sum", "int_0": "count"})


def pandas_filter_operations(df: pd.DataFrame) -> pd.DataFrame:
    """Complex filtering operations."""
    mask = (df["num_0"] > 25) & (df["num_0"] < 75) & (df["cat_0"].isin(["A", "B", "C"])) & (df["int_0"] > 500)
    return df[mask]


def pandas_sort_operations(df: pd.DataFrame) -> pd.DataFrame:
    """Sorting by multiple columns."""
    return df.sort_values(by=["cat_0", "num_0", "date"], ascending=[True, False, True])


def pandas_merge_operations(df1: pd.DataFrame, df2: pd.DataFrame) -> pd.DataFrame:
    """Merge/Join operations."""
    # Add a key column
    df1 = df1.copy()
    df2 = df2.copy()
    df1["key"] = np.random.randint(0, 100, len(df1))
    df2["key"] = np.random.randint(0, 100, len(df2))
    return pd.merge(df1, df2, on="key", how="inner", suffixes=("_left", "_right"))


def pandas_pivot_operations(df: pd.DataFrame) -> pd.DataFrame:
    """Pivot table operations."""
    return pd.pivot_table(df, values="num_0", index="cat_0", columns="cat_1", aggfunc="mean", fill_value=0)


def pandas_rolling_operations(df: pd.DataFrame) -> pd.DataFrame:
    """Rolling window calculations."""
    df = df.sort_values("date")
    result = df.copy()
    result["rolling_mean"] = df["num_0"].rolling(window=100).mean()
    result["rolling_std"] = df["num_0"].rolling(window=100).std()
    result["rolling_sum"] = df["num_0"].rolling(window=50).sum()
    return result


def pandas_apply_operations(df: pd.DataFrame) -> pd.DataFrame:
    """Apply custom functions."""

    def custom_transform(x: float) -> float:
        return float(np.log1p(np.abs(x)) * np.sign(x))

    result = df.copy()
    result["transformed"] = df["num_0"].apply(custom_transform)
    return result


def pandas_string_operations(df: pd.DataFrame) -> pd.DataFrame:
    """String operations on categorical data."""
    result = df.copy()
    result["cat_upper"] = df["cat_0"].str.upper()
    result["cat_lower"] = df["cat_0"].str.lower()
    result["cat_combined"] = df["cat_0"] + "_" + df["cat_1"]
    return result


def pandas_datetime_operations(df: pd.DataFrame) -> pd.DataFrame:
    """DateTime operations."""
    result = df.copy()
    result["year"] = df["date"].dt.year
    result["month"] = df["date"].dt.month
    result["day"] = df["date"].dt.day
    result["hour"] = df["date"].dt.hour
    result["dayofweek"] = df["date"].dt.dayofweek
    result["is_weekend"] = df["date"].dt.dayofweek >= 5
    return result


def pandas_memory_operations(df: pd.DataFrame) -> pd.DataFrame:
    """Memory-optimized type conversions."""
    result = df.copy()
    for col in result.select_dtypes(include=["float64"]).columns:
        result[col] = result[col].astype("float32")
    for col in result.select_dtypes(include=["int64"]).columns:
        result[col] = result[col].astype("int32")
    for col in result.select_dtypes(include=["object"]).columns:
        result[col] = result[col].astype("category")
    return result


def pandas_concat_operations(dfs: list[pd.DataFrame]) -> pd.DataFrame:
    """Concatenation operations."""
    return pd.concat(dfs, ignore_index=True)


# =============================================================================
# Data pipeline benchmarks (realistic scenarios)
# =============================================================================


def etl_pipeline(df: pd.DataFrame) -> pd.DataFrame:
    """Simulate an ETL pipeline."""
    # Filter
    df = df[df["num_0"] > 10]

    # Transform
    df = df.copy()
    df["score"] = df["num_0"] * 0.5 + df["num_1"] * 0.3 + df["int_0"] * 0.001

    # Group and aggregate
    summary = df.groupby(["cat_0", "cat_1"]).agg(
        {"score": ["mean", "std", "count"], "num_0": "sum", "int_0": "max"}
    )

    # Flatten columns
    summary.columns = ["_".join(col).strip() for col in summary.columns]

    return summary.reset_index()


def feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    """Feature engineering pipeline."""
    result = df.copy()

    # Numerical features
    result["num_ratio"] = df["num_0"] / (df["num_1"] + 1)
    result["num_diff"] = df["num_0"] - df["num_1"]
    result["num_product"] = df["num_0"] * df["num_1"]

    # Statistical features
    result["num_zscore"] = (df["num_0"] - df["num_0"].mean()) / df["num_0"].std()

    # Category encoding (simple frequency encoding)
    freq = df["cat_0"].value_counts(normalize=True)
    result["cat_freq"] = df["cat_0"].map(freq)

    # Time features
    result["hour"] = df["date"].dt.hour
    result["is_business_hour"] = (df["date"].dt.hour >= 9) & (df["date"].dt.hour <= 17)

    return result


# =============================================================================
# Benchmark runners
# =============================================================================


def run_datascience_benchmarks() -> list[BenchmarkResult]:
    """Run all data science benchmarks and return results."""
    results: list[BenchmarkResult] = []

    # Prepare NumPy test data
    small_array = np.random.random((500, 500))
    medium_array = np.random.random((1000, 1000))

    # NumPy benchmarks
    results.append(
        benchmark(
            lambda: numpy_array_creation(500),
            name="NumPy Array Creation (500x500)",
            category="NumPy - Creation",
            iterations=20,
        )
    )

    results.append(
        benchmark(
            lambda: numpy_matrix_operations(small_array, small_array),
            name="NumPy Matrix Operations (500x500)",
            category="NumPy - Matrix",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: numpy_element_wise(medium_array),
            name="NumPy Element-wise (1000x1000)",
            category="NumPy - Element-wise",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: numpy_aggregations(medium_array),
            name="NumPy Aggregations (1000x1000)",
            category="NumPy - Aggregations",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: numpy_sorting(small_array),
            name="NumPy Sorting (500x500)",
            category="NumPy - Sorting",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: numpy_boolean_indexing(medium_array),
            name="NumPy Boolean Indexing (1000x1000)",
            category="NumPy - Indexing",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: numpy_broadcasting(500),
            name="NumPy Broadcasting (500x500)",
            category="NumPy - Broadcasting",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: numpy_concatenation(10, 100),
            name="NumPy Concatenation (10x 100x100)",
            category="NumPy - Concat",
            iterations=10,
        )
    )

    # Prepare Pandas test data
    small_df = create_dataframe(10000, 15)
    medium_df = create_dataframe(50000, 15)
    large_df = create_dataframe(100000, 15)

    # Pandas benchmarks
    results.append(
        benchmark(
            lambda: create_dataframe(50000, 15),
            name="Pandas DataFrame Creation (50k rows)",
            category="Pandas - Creation",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: pandas_groupby_agg(medium_df),
            name="Pandas GroupBy Agg (50k rows)",
            category="Pandas - GroupBy",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: pandas_multiple_groupby(large_df),
            name="Pandas Multi-Column GroupBy (100k rows)",
            category="Pandas - GroupBy",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: pandas_filter_operations(large_df),
            name="Pandas Complex Filter (100k rows)",
            category="Pandas - Filter",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: pandas_sort_operations(medium_df),
            name="Pandas Multi-Column Sort (50k rows)",
            category="Pandas - Sort",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: pandas_merge_operations(small_df, small_df),
            name="Pandas Merge (10k x 10k rows)",
            category="Pandas - Merge",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: pandas_pivot_operations(medium_df),
            name="Pandas Pivot Table (50k rows)",
            category="Pandas - Pivot",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: pandas_rolling_operations(medium_df),
            name="Pandas Rolling Window (50k rows)",
            category="Pandas - Rolling",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: pandas_apply_operations(small_df),
            name="Pandas Apply Function (10k rows)",
            category="Pandas - Apply",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: pandas_string_operations(medium_df),
            name="Pandas String Operations (50k rows)",
            category="Pandas - Strings",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: pandas_datetime_operations(medium_df),
            name="Pandas DateTime Operations (50k rows)",
            category="Pandas - DateTime",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: pandas_memory_operations(small_df),
            name="Pandas Type Optimization (10k rows)",
            category="Pandas - Memory",
            iterations=10,
        )
    )

    # Pipeline benchmarks
    results.append(
        benchmark(
            lambda: etl_pipeline(medium_df),
            name="ETL Pipeline (50k rows)",
            category="Pipeline - ETL",
            iterations=10,
        )
    )

    results.append(
        benchmark(
            lambda: feature_engineering(medium_df),
            name="Feature Engineering (50k rows)",
            category="Pipeline - Features",
            iterations=10,
        )
    )

    return results


if __name__ == "__main__":
    from benchmarks.utils import format_time

    print("Running data science benchmarks...")
    results = run_datascience_benchmarks()
    for r in results:
        print(f"{r.name}: {format_time(r.mean_time)} ± {format_time(r.std_dev)}")
