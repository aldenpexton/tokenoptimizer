#!/bin/bash
# Script to run tests for the TokenOptimizer SDK

# Exit on error
set -e

# Change to the script directory
cd "$(dirname "$0")"

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "pytest not found. Installing test dependencies..."
    pip install -r requirements-dev.txt
fi

# Run tests with coverage
echo "Running tests with coverage..."
pytest --cov=tokenoptimizer tests/ -v

# Print coverage report
echo "Coverage report:"
coverage report -m

echo "Tests completed successfully!" 