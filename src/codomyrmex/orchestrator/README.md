# orchestrator

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Script orchestration module for discovering, configuring, executing, and reporting on Python scripts. Provides a unified entry point for running script suites with structured logging, configurable timeouts, and automated report generation.

## Features

- **Script Discovery**: Traverse directory trees to find Python scripts with configurable depth and exclusion patterns
- **Configuration Management**: YAML-based per-script configuration for timeouts, arguments, and environment variables
- **Execution Engine**: Run scripts via subprocess with timeout control and exit code validation
- **Reporting**: Generate JSON logs and Markdown summary reports

## Directory Contents

- `__init__.py` – Public API exports
- `core.py` – Main orchestration entry point
- `config.py` – Configuration loading and parsing
- `discovery.py` – Script discovery logic
- `runner.py` – Script execution engine
- `reporting.py` – Log and report generation
- `AGENTS.md` – Technical documentation
- `SPEC.md` – Functional specification

## Quick Start

```python
from codomyrmex.orchestrator import run_orchestrator

# Run orchestration from command line entry point
exit_code = run_orchestrator()
```

## Navigation

- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [README](../../../README.md)
