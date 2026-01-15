# cli

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Command-line interface module for Codomyrmex. Provides the main entry point for interacting with all Codomyrmex modules via the `codomyrmex` command.

## Key Features

- **Environment commands**: `check`, `info`, `modules`, `status`, `shell`
- **Workflow management**: `workflow list/create/run`
- **Project management**: `project list/create`
- **Orchestration**: `orchestration status/health`
- **AI operations**: `ai generate/refactor`
- **Analysis**: `analyze code/git`
- **Build**: `build project`
- **FPF operations**: `fpf fetch/parse/export/search/visualize/context/analyze/report`
- **Skills management**: `skills sync/list/get/search`

## Quick Start

```bash
# Check environment
codomyrmex check

# Show available modules
codomyrmex modules

# Launch interactive shell
codomyrmex shell

# Generate code with AI
codomyrmex ai generate "create a factorial function" --language python
```

## Module Structure

- `core.py` – Main CLI entry point with argparse configuration
- `utils.py` – CLI utilities and formatters
- `handlers/` – Command handler implementations

## Navigation

- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [README](../../../README.md)
