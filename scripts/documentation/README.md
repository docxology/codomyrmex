# Documentation Scripts

This directory contains scripts for managing and maintaining project documentation.

## Scripts

- **`check_docs_status.py`** - Analyzes the entire repository to check documentation status across all directories
- **`documentation_status_summary.py`** - Generates comprehensive summaries of documentation improvements and status
- **`generate_missing_readmes.py`** - Automatically generates README.md files for directories that have AGENTS.md but missing README.md

## Usage

```bash
# Check documentation status across the entire repository
python scripts/documentation/check_docs_status.py

# Generate a summary of documentation improvements
python scripts/documentation/documentation_status_summary.py

# Generate missing README files for directories with AGENTS.md
python scripts/documentation/generate_missing_readmes.py
```
