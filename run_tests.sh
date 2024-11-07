#!/bin/bash
find . -name \*.pyc | xargs rm 2>/dev/null
rm -rf .pytest_cache

python -m pytest -v -rsx --cov-report term-missing --cov=. -k "test_"

