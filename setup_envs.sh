#!/bin/bash
# Setup script to install Python versions and sync environments

set -e

echo "Installing Python versions..."
uv python install 3.9 3.11 3.12 3.13 3.14

echo ""
echo "Syncing environments..."

for ver in py39 py311 py312 py313 py314; do
    echo "Setting up envs/$ver..."
    cd "$(dirname "$0")/envs/$ver"
    uv sync
    cd ../..
done

echo ""
echo "Verifying Python versions:"
for ver in py39 py311 py312 py313 py314; do
    echo -n "$ver: "
    ./envs/$ver/.venv/bin/python --version
done

echo ""
echo "Setup complete! Run benchmarks with:"
echo "  ./run_version_benchmarks.sh"
