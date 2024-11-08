#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Remove .pyc files
echo "Cleaning up .pyc files..."
find . -name "*.pyc" -delete

# Remove pytest cache
echo "Removing pytest cache..."
rm -rf .pytest_cache

# Run pytest with coverage and verbosity
echo "Running tests with pytest..."
python -m pytest -v -rsx --cov-report term-missing --cov=. -k "test_"
