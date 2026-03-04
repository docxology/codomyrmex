# Code Audits Specification

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Audit scripts for verifying codebase quality including documentation coverage, module exports, import analysis, and RASP documentation compliance.

## Functional Requirements

- **audit_documentation.py**: Audits documentation coverage by scanning all module directories for README.md and docstrings
- **audit_exports.py**: Verifies that module __all__ exports match actual public API surface
- **audit_imports.py**: Analyzes import dependencies between modules to detect circular imports
- **audit_rasp.py**: Checks RASP documentation compliance (README, AGENTS, SPEC, PAI) across all modules


## Execution

**Prerequisites:**
```bash
uv sync
```

**Run:**
```bash
uv run python scripts/audits/audit_documentation.py --root src/codomyrmex
```

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md)
