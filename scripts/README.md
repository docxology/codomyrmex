# Codomyrmex Scripts

This directory contains orchestration, maintenance, and utility scripts for the Codomyrmex ecosystem.

## Main Entry Point

The primary script for executing tasks, running tests, and performing maintenance is:

```bash
python3 run_all_scripts.py [options]
```

Use `--help` for available options:

```bash
python3 run_all_scripts.py --help
```

## Directory Structure

- **`agents/`**: Agent orchestration
- **`api/`**: API management
- **`cerebrum/`**: Cerebrum module logic
- **`config/`**: Script configuration files
- **`docs/`**: Script documentation and specifications
- **`tools/`**: Repair and maintenance utilities
- **`utils/`**: Shared utilities
- **`...`**: (See `run_all_scripts.py --dry-run` for full list)

For detailed documentation, see `scripts/docs/README.md`.
