# Code Audits -- Agent Coordination

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

Audit scripts for verifying codebase quality including documentation coverage, module exports, import analysis, and RASP documentation compliance.

## Scripts Available

- **audit_documentation.py**: Audits documentation coverage by scanning all module directories for README.md and docstrings
- **audit_exports.py**: Verifies that module __all__ exports match actual public API surface
- **audit_imports.py**: Analyzes import dependencies between modules to detect circular imports
- **audit_rasp.py**: Checks RASP documentation compliance (README, AGENTS, SPEC, PAI) across all modules


## Agent Instructions

1. Run scripts from the repository root directory using `uv run python scripts/audits/<script>`
2. Ensure prerequisites are installed: `uv sync`
3. Scripts are demonstration/utility tools and do not modify production state

## Navigation

- [README.md](README.md) | [SPEC.md](SPEC.md)
