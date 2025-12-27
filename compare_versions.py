#!/usr/bin/env python3
"""
Compare benchmark results across Python versions.

Reads results from envs/py*/results.json and generates comparison reports.
"""

from __future__ import annotations

import json
from pathlib import Path

from rich.console import Console
from rich.table import Table

console = Console()

SCRIPT_DIR = Path(__file__).parent
RESULTS_DIR = SCRIPT_DIR / "results"
VERSIONS = ["py39", "py311", "py312", "py313", "py314"]
VERSION_LABELS = {
    "py39": "3.9",
    "py311": "3.11",
    "py312": "3.12",
    "py313": "3.13",
    "py314": "3.14",
}


def load_results() -> dict[str, list[dict]]:
    """Load results from each version's result file."""
    results = {}
    for ver in VERSIONS:
        result_file = RESULTS_DIR / f"{ver}_results.json"
        if result_file.exists():
            with open(result_file) as f:
                results[ver] = json.load(f)
            console.print(f"[green]✓[/green] Loaded {ver}: {len(results[ver])} benchmarks")
        else:
            console.print(f"[yellow]⚠[/yellow] Missing: {result_file}")
    return results


def calculate_speedups(results: dict[str, list[dict]], baseline: str = "py39") -> dict[str, dict[str, float]]:
    """Calculate speedups relative to baseline."""
    if baseline not in results:
        console.print(f"[red]Baseline {baseline} not found[/red]")
        return {}

    baseline_times = {r["name"]: r["mean_time"] for r in results[baseline]}
    speedups = {}

    for ver, ver_results in results.items():
        if ver == baseline:
            continue
        speedups[ver] = {}
        for r in ver_results:
            name = r["name"]
            if name in baseline_times and baseline_times[name] > 0:
                speedups[ver][name] = baseline_times[name] / r["mean_time"]

    return speedups


def print_summary(results: dict[str, list[dict]], speedups: dict[str, dict[str, float]]) -> None:
    """Print summary comparison table."""
    console.print("\n[bold cyan]═══ OVERALL SUMMARY ═══[/bold cyan]\n")

    table = Table(title="Average Speedup vs Python 3.9")
    table.add_column("Version", style="cyan")
    table.add_column("Avg Speedup", justify="right")
    table.add_column("Min", justify="right")
    table.add_column("Max", justify="right")
    table.add_column("Benchmarks", justify="right")

    for ver in ["py311", "py312", "py313", "py314"]:
        if ver not in speedups:
            continue
        speeds = list(speedups[ver].values())
        if not speeds:
            continue

        avg = sum(speeds) / len(speeds)
        color = "green" if avg > 1.0 else "red"

        table.add_row(
            f"Python {VERSION_LABELS[ver]}",
            f"[{color}]{avg:.2f}x[/{color}]",
            f"{min(speeds):.2f}x",
            f"{max(speeds):.2f}x",
            str(len(speeds)),
        )

    console.print(table)


def print_top_improvements(speedups: dict[str, dict[str, float]], top_n: int = 10) -> None:
    """Print top improvements for each version."""
    console.print("\n[bold cyan]═══ TOP IMPROVEMENTS ═══[/bold cyan]\n")

    for ver in ["py311", "py312", "py313", "py314"]:
        if ver not in speedups:
            continue

        sorted_speeds = sorted(speedups[ver].items(), key=lambda x: x[1], reverse=True)[:top_n]

        if not sorted_speeds:
            continue

        table = Table(title=f"Python {VERSION_LABELS[ver]} vs 3.9 - Top {top_n}")
        table.add_column("Benchmark", style="white")
        table.add_column("Speedup", justify="right", style="green")

        for name, speedup in sorted_speeds:
            table.add_row(name, f"{speedup:.2f}x faster")

        console.print(table)
        console.print()


def print_category_summary(results: dict[str, list[dict]], speedups: dict[str, dict[str, float]]) -> None:
    """Print summary by category."""
    console.print("\n[bold cyan]═══ BY CATEGORY ═══[/bold cyan]\n")

    # Group by category
    categories: dict[str, dict[str, list[float]]] = {}

    for ver, ver_speedups in speedups.items():
        for r in results.get(ver, []):
            name = r["name"]
            if name not in ver_speedups:
                continue
            category = r["category"].split(" - ")[0]
            if category not in categories:
                categories[category] = {}
            if ver not in categories[category]:
                categories[category][ver] = []
            categories[category][ver].append(ver_speedups[name])

    table = Table(title="Average Speedup by Category")
    table.add_column("Category", style="white")
    for ver in ["py311", "py312", "py313", "py314"]:
        table.add_column(f"{VERSION_LABELS.get(ver, ver)}", justify="right")

    for category in sorted(categories.keys()):
        row = [category]
        for ver in ["py311", "py312", "py313", "py314"]:
            if ver in categories[category]:
                avg = sum(categories[category][ver]) / len(categories[category][ver])
                color = "green" if avg > 1.0 else "red"
                row.append(f"[{color}]{avg:.2f}x[/{color}]")
            else:
                row.append("-")
        table.add_row(*row)

    console.print(table)


def save_comparison_report(results: dict[str, list[dict]], speedups: dict[str, dict[str, float]]) -> None:
    """Save comparison as JSON."""
    report = {
        "versions_tested": [VERSION_LABELS[v] for v in results.keys()],
        "baseline": "3.9",
        "summary": {},
        "by_benchmark": {},
    }

    for ver, ver_speedups in speedups.items():
        speeds = list(ver_speedups.values())
        if speeds:
            report["summary"][VERSION_LABELS[ver]] = {
                "average_speedup": sum(speeds) / len(speeds),
                "min_speedup": min(speeds),
                "max_speedup": max(speeds),
                "benchmark_count": len(speeds),
            }

    # All benchmark speedups
    for ver, ver_speedups in speedups.items():
        for name, speedup in ver_speedups.items():
            if name not in report["by_benchmark"]:
                report["by_benchmark"][name] = {}
            report["by_benchmark"][name][VERSION_LABELS[ver]] = speedup

    output_file = RESULTS_DIR / "comparison.json"
    with open(output_file, "w") as f:
        json.dump(report, f, indent=2)
    console.print(f"\n[green]Saved comparison to {output_file}[/green]")


def main() -> None:
    """Main entry point."""
    console.print("[bold]Python Version Performance Comparison[/bold]\n")

    results = load_results()
    if len(results) < 2:
        console.print("[red]Need at least 2 versions to compare[/red]")
        return

    speedups = calculate_speedups(results)
    if not speedups:
        console.print("[red]Could not calculate speedups[/red]")
        return

    print_summary(results, speedups)
    print_category_summary(results, speedups)
    print_top_improvements(speedups)
    save_comparison_report(results, speedups)


if __name__ == "__main__":
    main()
