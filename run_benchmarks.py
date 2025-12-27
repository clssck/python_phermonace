#!/usr/bin/env python3
"""
Main benchmark runner for Python version performance comparison.

This script runs all benchmarks across multiple Python versions using uv
and collects results for comparison.

Usage:
    uv run python run_benchmarks.py
    uv run python run_benchmarks.py --versions 3.9 3.11 3.12
    uv run python run_benchmarks.py --quick  # Run quick subset
"""

from __future__ import annotations

import argparse
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.table import Table

console = Console()

# Python versions to test
DEFAULT_VERSIONS = ["3.9", "3.11", "3.12", "3.13", "3.14"]

# Project root
PROJECT_ROOT = Path(__file__).parent


def install_python_version(version: str) -> bool:
    """Install a Python version using uv."""
    console.print(f"[blue]Installing Python {version}...[/blue]")
    result = subprocess.run(
        ["uv", "python", "install", version],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        console.print(f"[red]Failed to install Python {version}: {result.stderr}[/red]")
        return False
    return True


def get_python_path(version: str) -> str | None:
    """Get the path to a Python version managed by uv."""
    result = subprocess.run(
        ["uv", "python", "find", version],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        return result.stdout.strip()
    return None


def run_benchmark_script(python_path: str, script: str) -> list[dict[str, Any]]:
    """Run a benchmark script and collect results."""
    # Create a temporary script that imports and runs the benchmark
    benchmark_code = f'''
import json
import sys
sys.path.insert(0, "{PROJECT_ROOT}")

from benchmarks.{script} import run_{script.replace("_benchmarks", "")}_benchmarks
from dataclasses import asdict

results = run_{script.replace("_benchmarks", "")}_benchmarks()
print(json.dumps([asdict(r) for r in results]))
'''

    result = subprocess.run(
        [python_path, "-c", benchmark_code],
        capture_output=True,
        text=True,
        timeout=600,  # 10 minute timeout
        cwd=PROJECT_ROOT,
    )

    if result.returncode != 0:
        console.print(f"[red]Benchmark failed: {result.stderr}[/red]")
        return []

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        console.print(f"[red]Failed to parse results: {result.stdout[:500]}[/red]")
        return []


def run_all_benchmarks_for_version(
    version: str, quick: bool = False
) -> list[dict[str, Any]]:
    """Run all benchmarks for a specific Python version."""
    python_path = get_python_path(version)
    if not python_path:
        console.print(f"[yellow]Python {version} not found, installing...[/yellow]")
        if not install_python_version(version):
            return []
        python_path = get_python_path(version)
        if not python_path:
            return []

    console.print(f"[green]Using Python at: {python_path}[/green]")

    # Install dependencies for this Python version
    console.print(f"[blue]Installing dependencies for Python {version}...[/blue]")
    subprocess.run(
        ["uv", "pip", "install", "-p", python_path, "-e", str(PROJECT_ROOT)],
        capture_output=True,
        cwd=PROJECT_ROOT,
    )

    all_results: list[dict[str, Any]] = []

    benchmark_scripts = [
        "cpu_benchmarks",
        "data_structure_benchmarks",
        "io_benchmarks",
        "async_benchmarks",
    ]

    if not quick:
        benchmark_scripts.append("datascience_benchmarks")

    for script in benchmark_scripts:
        console.print(f"  [cyan]Running {script}...[/cyan]")
        try:
            results = run_benchmark_script(python_path, script)
            all_results.extend(results)
        except subprocess.TimeoutExpired:
            console.print(f"  [red]Timeout running {script}[/red]")
        except Exception as e:
            console.print(f"  [red]Error running {script}: {e}[/red]")

    return all_results


def create_comparison_table(
    all_results: dict[str, list[dict[str, Any]]], benchmark_name: str
) -> Table:
    """Create a comparison table for a specific benchmark."""
    table = Table(title=benchmark_name)
    table.add_column("Python Version", style="cyan")
    table.add_column("Mean Time", style="green")
    table.add_column("Std Dev", style="yellow")
    table.add_column("vs 3.9", style="magenta")

    baseline_time = None

    for version in sorted(all_results.keys()):
        results = all_results[version]
        matching = [r for r in results if r["name"] == benchmark_name]
        if matching:
            result = matching[0]
            mean_time = result["mean_time"]
            std_dev = result["std_dev"]

            if baseline_time is None:
                baseline_time = mean_time
                speedup = "baseline"
            else:
                ratio = baseline_time / mean_time if mean_time > 0 else 0
                if ratio >= 1:
                    speedup = f"[green]{ratio:.2f}x faster[/green]"
                else:
                    speedup = f"[red]{1/ratio:.2f}x slower[/red]"

            # Format time
            if mean_time < 1e-3:
                time_str = f"{mean_time * 1e6:.2f} µs"
            elif mean_time < 1:
                time_str = f"{mean_time * 1e3:.2f} ms"
            else:
                time_str = f"{mean_time:.2f} s"

            if std_dev < 1e-3:
                std_str = f"± {std_dev * 1e6:.2f} µs"
            elif std_dev < 1:
                std_str = f"± {std_dev * 1e3:.2f} ms"
            else:
                std_str = f"± {std_dev:.2f} s"

            table.add_row(version, time_str, std_str, speedup)

    return table


def save_results(all_results: dict[str, list[dict[str, Any]]], output_path: Path) -> None:
    """Save results to JSON file."""
    output = {
        "timestamp": datetime.now().isoformat(),
        "results": all_results,
    }
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)
    console.print(f"[green]Results saved to {output_path}[/green]")


def generate_summary_report(
    all_results: dict[str, list[dict[str, Any]]]
) -> dict[str, Any]:
    """Generate a summary report comparing versions."""
    summary: dict[str, Any] = {
        "versions_tested": list(all_results.keys()),
        "total_benchmarks": 0,
        "improvements": [],
        "regressions": [],
        "categories": {},
    }

    if "3.9" not in all_results:
        console.print("[yellow]Warning: Python 3.9 results not available for comparison[/yellow]")
        return summary

    baseline_results = {r["name"]: r for r in all_results.get("3.9", [])}
    summary["total_benchmarks"] = len(baseline_results)

    for version, results in all_results.items():
        if version == "3.9":
            continue

        for result in results:
            name = result["name"]
            if name not in baseline_results:
                continue

            baseline_time = baseline_results[name]["mean_time"]
            current_time = result["mean_time"]

            if baseline_time > 0 and current_time > 0:
                speedup = baseline_time / current_time
                category = result["category"]

                if category not in summary["categories"]:
                    summary["categories"][category] = []

                summary["categories"][category].append(
                    {
                        "benchmark": name,
                        "version": version,
                        "speedup": speedup,
                        "baseline_time": baseline_time,
                        "current_time": current_time,
                    }
                )

                if speedup > 1.1:  # More than 10% faster
                    summary["improvements"].append(
                        {
                            "benchmark": name,
                            "version": version,
                            "speedup": speedup,
                        }
                    )
                elif speedup < 0.9:  # More than 10% slower
                    summary["regressions"].append(
                        {
                            "benchmark": name,
                            "version": version,
                            "slowdown": 1 / speedup,
                        }
                    )

    # Sort by speedup
    summary["improvements"].sort(key=lambda x: x["speedup"], reverse=True)
    summary["regressions"].sort(key=lambda x: x["slowdown"], reverse=True)

    return summary


def print_summary(summary: dict[str, Any]) -> None:
    """Print a summary of the benchmark results."""
    console.print("\n[bold]═══════════════════════════════════════════════════════════════[/bold]")
    console.print("[bold cyan]                    BENCHMARK SUMMARY                           [/bold cyan]")
    console.print("[bold]═══════════════════════════════════════════════════════════════[/bold]\n")

    console.print(f"[bold]Versions tested:[/bold] {', '.join(summary['versions_tested'])}")
    console.print(f"[bold]Total benchmarks:[/bold] {summary['total_benchmarks']}\n")

    if summary["improvements"]:
        console.print("[bold green]Top 10 Improvements (vs Python 3.9):[/bold green]")
        table = Table()
        table.add_column("Benchmark", style="cyan")
        table.add_column("Version", style="yellow")
        table.add_column("Speedup", style="green")

        for item in summary["improvements"][:10]:
            table.add_row(item["benchmark"], item["version"], f"{item['speedup']:.2f}x faster")

        console.print(table)
        console.print()

    if summary["regressions"]:
        console.print("[bold red]Regressions (vs Python 3.9):[/bold red]")
        table = Table()
        table.add_column("Benchmark", style="cyan")
        table.add_column("Version", style="yellow")
        table.add_column("Slowdown", style="red")

        for item in summary["regressions"][:10]:
            table.add_row(item["benchmark"], item["version"], f"{item['slowdown']:.2f}x slower")

        console.print(table)
        console.print()

    # Category summary
    console.print("[bold]Performance by Category:[/bold]")
    for category, benchmarks in summary.get("categories", {}).items():
        if not benchmarks:
            continue
        avg_speedup = sum(b["speedup"] for b in benchmarks) / len(benchmarks)
        if avg_speedup >= 1:
            color = "green"
            direction = "faster"
            ratio = avg_speedup
        else:
            color = "red"
            direction = "slower"
            ratio = 1 / avg_speedup
        console.print(f"  {category}: [{color}]{ratio:.2f}x {direction}[/{color}] (avg)")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Run Python version benchmarks")
    parser.add_argument(
        "--versions",
        nargs="+",
        default=DEFAULT_VERSIONS,
        help="Python versions to test",
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run quick subset of benchmarks",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "results" / "benchmark_results.json",
        help="Output file for results",
    )
    args = parser.parse_args()

    console.print("[bold cyan]Python Version Performance Benchmark Suite[/bold cyan]")
    console.print(f"Testing versions: {', '.join(args.versions)}\n")

    all_results: dict[str, list[dict[str, Any]]] = {}

    start_time = time.time()

    for version in args.versions:
        console.print(f"\n[bold]{'═' * 60}[/bold]")
        console.print(f"[bold yellow]Testing Python {version}[/bold yellow]")
        console.print(f"[bold]{'═' * 60}[/bold]")

        results = run_all_benchmarks_for_version(version, quick=args.quick)
        if results:
            all_results[version] = results
            console.print(f"[green]Completed {len(results)} benchmarks for Python {version}[/green]")

    elapsed = time.time() - start_time
    console.print(f"\n[bold]Total benchmark time: {elapsed:.1f} seconds[/bold]")

    # Save results
    args.output.parent.mkdir(parents=True, exist_ok=True)
    save_results(all_results, args.output)

    # Generate and print summary
    summary = generate_summary_report(all_results)
    print_summary(summary)

    # Save summary
    summary_path = args.output.parent / "benchmark_summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    console.print(f"[green]Summary saved to {summary_path}[/green]")


if __name__ == "__main__":
    main()
