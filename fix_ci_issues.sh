#!/bin/bash
set -e

# Fix trailing whitespace in run_demo.py
sed -i -e 's/[[:space:]]*$//' projects/test_project/run_demo.py

# Fix blank lines containing whitespace in run_demo.py
sed -i -e 's/^[[:space:]]*$//' projects/test_project/run_demo.py

# Organize imports in run_demo.py using ruff
uv run ruff check --fix --select I projects/test_project/run_demo.py || true

# Run ruff check over scripts to fix linting errors
uv run ruff check --fix --select W291,W293,I,UP,F841,F541,E402,B007 scripts/ || true
uv run ruff format scripts/ || true

echo "Done fixing issues."
