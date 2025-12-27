#!/bin/bash
# Run benchmarks using each Python version's isolated environment

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
RESULTS_DIR="$SCRIPT_DIR/results"
mkdir -p "$RESULTS_DIR"

# Versions to test (in order)
VERSIONS=("py39" "py311" "py312" "py313" "py314")

echo "========================================"
echo "Python Version Performance Benchmarks"
echo "========================================"
echo ""

for ver in "${VERSIONS[@]}"; do
    ENV_DIR="$SCRIPT_DIR/envs/$ver"
    PYTHON="$ENV_DIR/.venv/bin/python"

    if [ ! -f "$PYTHON" ]; then
        echo "⚠️  Skipping $ver - environment not set up"
        echo "   Run: cd envs/$ver && uv sync"
        continue
    fi

    VERSION=$($PYTHON --version 2>&1)
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Testing: $VERSION"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # Run benchmarks with this Python version
    PYTHONPATH="$SCRIPT_DIR" $PYTHON -c "
import json
import sys
sys.path.insert(0, '$SCRIPT_DIR')

from benchmarks.cpu_benchmarks import run_cpu_benchmarks
from benchmarks.data_structure_benchmarks import run_data_structure_benchmarks
from benchmarks.io_benchmarks import run_io_benchmarks
from benchmarks.async_benchmarks import run_async_benchmarks
from benchmarks.version_specific_benchmarks import run_version_specific_benchmarks
from dataclasses import asdict

print('  Running CPU benchmarks...')
cpu = run_cpu_benchmarks()

print('  Running data structure benchmarks...')
ds = run_data_structure_benchmarks()

print('  Running I/O benchmarks...')
io = run_io_benchmarks()

print('  Running async benchmarks...')
async_results = run_async_benchmarks()

print('  Running version-specific benchmarks...')
version_specific = run_version_specific_benchmarks()

all_results = cpu + ds + io + async_results + version_specific

# Save results
output_file = '$RESULTS_DIR/${ver}_results.json'
with open(output_file, 'w') as f:
    json.dump([asdict(r) for r in all_results], f, indent=2)

print(f'  ✓ Saved {len(all_results)} results to {output_file}')
"
    echo ""
done

echo "========================================"
echo "All benchmarks complete!"
echo "Results saved to: $RESULTS_DIR/"
echo ""
echo "To compare results, run:"
echo "  uv run python compare_versions.py"
echo "========================================"
