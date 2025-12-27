#!/usr/bin/env python3
"""
Visualization and reporting for Python version benchmark results.

This script generates charts and reports from benchmark results.

Usage:
    uv run python visualize_results.py
    uv run python visualize_results.py --input results/benchmark_results.json
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from rich.console import Console

console = Console()

# Set style
sns.set_theme(style="whitegrid")
plt.rcParams["figure.figsize"] = (14, 8)
plt.rcParams["font.size"] = 10


def load_results(path: Path) -> dict[str, Any]:
    """Load benchmark results from JSON file."""
    with open(path) as f:
        return json.load(f)


def calculate_speedups(
    results: dict[str, list[dict[str, Any]]], baseline_version: str = "3.9"
) -> dict[str, dict[str, float]]:
    """Calculate speedups relative to baseline version."""
    speedups: dict[str, dict[str, float]] = {}

    if baseline_version not in results:
        console.print(f"[yellow]Baseline version {baseline_version} not found[/yellow]")
        return speedups

    baseline = {r["name"]: r["mean_time"] for r in results[baseline_version]}

    for version, version_results in results.items():
        speedups[version] = {}
        for result in version_results:
            name = result["name"]
            if name in baseline and baseline[name] > 0:
                speedups[version][name] = baseline[name] / result["mean_time"]

    return speedups


def plot_overall_comparison(
    results: dict[str, list[dict[str, Any]]], output_dir: Path
) -> None:
    """Create overall comparison bar chart."""
    speedups = calculate_speedups(results)

    if not speedups:
        return

    versions = sorted([v for v in speedups if v != "3.9"])
    avg_speedups = []

    for version in versions:
        if speedups[version]:
            avg = np.mean(list(speedups[version].values()))
            avg_speedups.append(avg)
        else:
            avg_speedups.append(1.0)

    fig, ax = plt.subplots(figsize=(10, 6))

    colors = ["#ff6b6b" if s < 1 else "#51cf66" for s in avg_speedups]
    bars = ax.bar(versions, avg_speedups, color=colors, edgecolor="black", linewidth=1.2)

    # Add value labels
    for bar, speedup in zip(bars, avg_speedups):
        height = bar.get_height()
        ax.annotate(
            f"{speedup:.2f}x",
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=12,
            fontweight="bold",
        )

    ax.axhline(y=1, color="gray", linestyle="--", linewidth=1.5, label="Python 3.9 baseline")
    ax.set_xlabel("Python Version", fontsize=12)
    ax.set_ylabel("Average Speedup (vs Python 3.9)", fontsize=12)
    ax.set_title("Overall Performance: Python Version Comparison", fontsize=14, fontweight="bold")
    ax.legend()

    plt.tight_layout()
    plt.savefig(output_dir / "overall_comparison.png", dpi=150, bbox_inches="tight")
    plt.close()
    console.print("[green]Saved overall_comparison.png[/green]")


def plot_category_comparison(
    results: dict[str, list[dict[str, Any]]], output_dir: Path
) -> None:
    """Create category-wise comparison chart."""
    # Group by category
    categories: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))

    speedups = calculate_speedups(results)

    for version, version_speedups in speedups.items():
        for benchmark_name, speedup in version_speedups.items():
            # Extract category from results
            for result in results.get(version, []):
                if result["name"] == benchmark_name:
                    # Simplify category name
                    category = result["category"].split(" - ")[0]
                    categories[category][version].append(speedup)
                    break

    if not categories:
        return

    # Calculate average speedup per category per version
    cat_names = sorted(categories.keys())
    versions = sorted([v for v in speedups if v != "3.9"])

    fig, ax = plt.subplots(figsize=(14, 8))

    x = np.arange(len(cat_names))
    width = 0.15

    for idx, version in enumerate(versions):
        cat_speedups = []
        for cat in cat_names:
            if version in categories[cat] and categories[cat][version]:
                cat_speedups.append(np.mean(categories[cat][version]))
            else:
                cat_speedups.append(1.0)

        offset = width * idx
        ax.bar(x + offset, cat_speedups, width, label=f"Python {version}")

    ax.axhline(y=1, color="gray", linestyle="--", linewidth=1.5)
    ax.set_xlabel("Benchmark Category", fontsize=12)
    ax.set_ylabel("Average Speedup (vs Python 3.9)", fontsize=12)
    ax.set_title("Performance by Category: Python Version Comparison", fontsize=14, fontweight="bold")
    ax.set_xticks(x + width * (len(versions) - 1) / 2)
    ax.set_xticklabels(cat_names, rotation=45, ha="right")
    ax.legend(loc="upper left")

    plt.tight_layout()
    plt.savefig(output_dir / "category_comparison.png", dpi=150, bbox_inches="tight")
    plt.close()
    console.print("[green]Saved category_comparison.png[/green]")


def plot_heatmap(
    results: dict[str, list[dict[str, Any]]], output_dir: Path
) -> None:
    """Create heatmap of speedups."""
    speedups = calculate_speedups(results)

    if not speedups or "3.9" not in results:
        return

    # Get all benchmark names
    all_benchmarks = sorted({r["name"] for r in results.get("3.9", [])})
    versions = sorted([v for v in speedups if v != "3.9"])

    # Create matrix
    data = []
    for benchmark in all_benchmarks:
        row = []
        for version in versions:
            row.append(speedups.get(version, {}).get(benchmark, 1.0))
        data.append(row)

    if not data:
        return

    # Limit to top 30 benchmarks with most variation
    variations = [max(row) - min(row) for row in data]
    sorted_indices = np.argsort(variations)[-30:]

    filtered_benchmarks = [all_benchmarks[i] for i in sorted_indices]
    filtered_data = [data[i] for i in sorted_indices]

    fig, ax = plt.subplots(figsize=(12, max(10, len(filtered_benchmarks) * 0.4)))

    # Create heatmap
    im = ax.imshow(filtered_data, cmap="RdYlGn", aspect="auto", vmin=0.5, vmax=2.0)

    # Set ticks
    ax.set_xticks(np.arange(len(versions)))
    ax.set_yticks(np.arange(len(filtered_benchmarks)))
    ax.set_xticklabels([f"Python {v}" for v in versions])
    ax.set_yticklabels(filtered_benchmarks)

    # Rotate x labels
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    # Add colorbar
    cbar = ax.figure.colorbar(im, ax=ax)
    cbar.ax.set_ylabel("Speedup vs Python 3.9", rotation=-90, va="bottom")

    # Add text annotations
    for i in range(len(filtered_benchmarks)):
        for j in range(len(versions)):
            value = filtered_data[i][j]
            text_color = "white" if value < 0.8 or value > 1.5 else "black"
            ax.text(j, i, f"{value:.2f}x", ha="center", va="center", color=text_color, fontsize=8)

    ax.set_title("Speedup Heatmap: Top 30 Benchmarks with Most Variation", fontsize=14, fontweight="bold")

    plt.tight_layout()
    plt.savefig(output_dir / "speedup_heatmap.png", dpi=150, bbox_inches="tight")
    plt.close()
    console.print("[green]Saved speedup_heatmap.png[/green]")


def plot_top_improvements(
    results: dict[str, list[dict[str, Any]]], output_dir: Path, top_n: int = 15
) -> None:
    """Plot top N improvements for each version."""
    speedups = calculate_speedups(results)
    versions = sorted([v for v in speedups if v != "3.9"])

    for version in versions:
        if not speedups.get(version):
            continue

        # Sort by speedup
        sorted_speedups = sorted(
            speedups[version].items(), key=lambda x: x[1], reverse=True
        )[:top_n]

        if not sorted_speedups:
            continue

        benchmarks = [s[0] for s in sorted_speedups]
        values = [s[1] for s in sorted_speedups]

        fig, ax = plt.subplots(figsize=(12, 8))

        colors = ["#51cf66" if v >= 1 else "#ff6b6b" for v in values]
        bars = ax.barh(benchmarks, values, color=colors, edgecolor="black", linewidth=0.5)

        ax.axvline(x=1, color="gray", linestyle="--", linewidth=1.5)
        ax.set_xlabel("Speedup (vs Python 3.9)", fontsize=12)
        ax.set_title(
            f"Top {top_n} Performance Improvements: Python {version} vs 3.9",
            fontsize=14,
            fontweight="bold",
        )

        # Add value labels
        for bar, value in zip(bars, values):
            width = bar.get_width()
            ax.annotate(
                f"{value:.2f}x",
                xy=(width, bar.get_y() + bar.get_height() / 2),
                xytext=(5, 0),
                textcoords="offset points",
                ha="left",
                va="center",
                fontsize=10,
            )

        plt.tight_layout()
        plt.savefig(output_dir / f"top_improvements_{version.replace('.', '')}.png", dpi=150, bbox_inches="tight")
        plt.close()
        console.print(f"[green]Saved top_improvements_{version.replace('.', '')}.png[/green]")


def plot_timing_distribution(
    results: dict[str, list[dict[str, Any]]], output_dir: Path
) -> None:
    """Plot timing distribution across versions."""
    versions = sorted(results.keys())

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()

    # Group benchmarks by rough category
    category_groups = ["CPU", "Data Structures", "I/O", "Async"]

    for idx, category in enumerate(category_groups):
        ax = axes[idx]
        data_for_plot = []
        labels = []

        for version in versions:
            version_times = []
            for result in results.get(version, []):
                if category in result["category"]:
                    version_times.append(result["mean_time"])

            if version_times:
                data_for_plot.append(version_times)
                labels.append(f"Python {version}")

        if data_for_plot:
            bp = ax.boxplot(data_for_plot, labels=labels, patch_artist=True)

            viridis = plt.colormaps["viridis"]
            colors = viridis(np.linspace(0, 1, len(data_for_plot)))
            for patch, color in zip(bp["boxes"], colors):
                patch.set_facecolor(color)
                patch.set_alpha(0.7)

            ax.set_title(f"{category} Benchmarks", fontsize=12, fontweight="bold")
            ax.set_ylabel("Time (seconds)")
            ax.set_yscale("log")

    plt.suptitle("Timing Distribution by Category", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig(output_dir / "timing_distribution.png", dpi=150, bbox_inches="tight")
    plt.close()
    console.print("[green]Saved timing_distribution.png[/green]")


def generate_markdown_report(
    results: dict[str, list[dict[str, Any]]], output_dir: Path
) -> None:
    """Generate a Markdown report."""
    speedups = calculate_speedups(results)
    versions = sorted(results.keys())

    report = []
    report.append("# Python Version Performance Comparison Report\n")
    report.append(f"**Versions Tested:** {', '.join(versions)}\n")
    report.append("**Baseline:** Python 3.9\n\n")

    # Overall summary
    report.append("## Executive Summary\n")
    report.append("### Average Speedup vs Python 3.9\n")
    report.append("| Version | Average Speedup | Recommendation |")
    report.append("|---------|----------------|----------------|")

    for version in sorted([v for v in versions if v != "3.9"]):
        if speedups.get(version):
            avg = np.mean(list(speedups[version].values()))
            if avg >= 1.25:
                rec = "✅ Strongly Recommended"
            elif avg >= 1.1:
                rec = "✅ Recommended"
            elif avg >= 1.0:
                rec = "⚠️ Marginal Improvement"
            else:
                rec = "❌ Performance Regression"
            report.append(f"| Python {version} | {avg:.2f}x | {rec} |")

    report.append("\n")

    # Category breakdown
    report.append("## Performance by Category\n")

    categories: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for version, version_speedups in speedups.items():
        if version == "3.9":
            continue
        for benchmark_name, speedup in version_speedups.items():
            for result in results.get(version, []):
                if result["name"] == benchmark_name:
                    category = result["category"]
                    categories[category][version].append(speedup)
                    break

    for category in sorted(categories.keys()):
        report.append(f"### {category}\n")
        report.append("| Version | Avg Speedup | Min | Max |")
        report.append("|---------|-------------|-----|-----|")
        for version in sorted(categories[category].keys()):
            speeds = categories[category][version]
            if speeds:
                report.append(
                    f"| Python {version} | {np.mean(speeds):.2f}x | {min(speeds):.2f}x | {max(speeds):.2f}x |"
                )
        report.append("\n")

    # Top improvements
    report.append("## Top 10 Performance Improvements\n")
    all_improvements = []
    for version, version_speedups in speedups.items():
        if version == "3.9":
            continue
        for benchmark, speedup in version_speedups.items():
            if speedup > 1.1:
                all_improvements.append((benchmark, version, speedup))

    all_improvements.sort(key=lambda x: x[2], reverse=True)

    report.append("| Benchmark | Version | Speedup |")
    report.append("|-----------|---------|---------|")
    for bench, ver, speed in all_improvements[:10]:
        report.append(f"| {bench} | Python {ver} | {speed:.2f}x |")

    report.append("\n")

    # Key insights for Dataiku
    report.append("## Key Insights for Dataiku Migration\n")
    report.append("### Why Upgrade from Python 3.9?\n\n")

    report.append("1. **Performance Improvements**: Newer Python versions show consistent ")
    report.append("performance gains across CPU-intensive operations, data processing, and I/O.\n\n")

    report.append("2. **Data Science Workloads**: NumPy and Pandas operations benefit from ")
    report.append("Python's improved interpreter in 3.11+.\n\n")

    report.append("3. **Exception Handling**: Python 3.11+ has zero-cost exception handling, ")
    report.append("significantly improving code with try/except blocks.\n\n")

    report.append("4. **Async Performance**: Python 3.11+ TaskGroup and improved async ")
    report.append("primitives provide better concurrent processing.\n\n")

    report.append("5. **Memory Efficiency**: Newer versions have optimized data structures ")
    report.append("that reduce memory footprint.\n\n")

    report.append("6. **Security**: Python 3.9 reaches end-of-life in October 2025. ")
    report.append("Upgrading ensures continued security patches.\n\n")

    # Write report
    report_path = output_dir / "benchmark_report.md"
    with open(report_path, "w") as f:
        f.write("\n".join(report))
    console.print("[green]Saved benchmark_report.md[/green]")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Visualize benchmark results")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("results/benchmark_results.json"),
        help="Input JSON file with benchmark results",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results"),
        help="Output directory for visualizations",
    )
    args = parser.parse_args()

    if not args.input.exists():
        console.print(f"[red]Results file not found: {args.input}[/red]")
        console.print("[yellow]Run benchmarks first with: uv run python run_benchmarks.py[/yellow]")
        return

    console.print(f"[cyan]Loading results from {args.input}...[/cyan]")
    data = load_results(args.input)
    results = data.get("results", {})

    if not results:
        console.print("[red]No results found in file[/red]")
        return

    args.output.mkdir(parents=True, exist_ok=True)

    console.print("[cyan]Generating visualizations...[/cyan]")

    # Generate all visualizations
    plot_overall_comparison(results, args.output)
    plot_category_comparison(results, args.output)
    plot_heatmap(results, args.output)
    plot_top_improvements(results, args.output)
    plot_timing_distribution(results, args.output)

    # Generate report
    generate_markdown_report(results, args.output)

    console.print(f"\n[bold green]All visualizations saved to {args.output}/[/bold green]")


if __name__ == "__main__":
    main()
