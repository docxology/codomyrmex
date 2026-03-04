# Maintenance Scripts

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Maintenance and housekeeping utilities for the Codomyrmex codebase, including stub auditing, dependency health checks, RASP documentation fixers, documentation synchronization, and index verification.

## Purpose

These scripts automate routine maintenance tasks: auditing stub implementations for completeness, checking dependency health, fixing RASP documentation inconsistencies, synchronizing module docs with source, and verifying the module index.

## Contents

| File | Description |
|------|-------------|
| `audit_stubs.py` | Scans source tree for stub methods (pass, ..., bare NotImplementedError) and generates a Markdown report |
| `check_dependencies.py` | Checks dependency health: outdated packages, security advisories, dependency tree depth |
| `fix_llm_rasp.py` | Fixes RASP docs that still say "Codomyrmex Root" -- replaces with correct module titles |
| `fix_nested_rasp.py` | Fixes RASP docs in nested subdirectories with correct module names and version strings |
| `generate_configs.py` | Ensures every source module has a corresponding `/config/` directory with default `config.yaml` |
| `sync_docs.py` | Synchronizes `docs/modules/` directory structure with actual `src/codomyrmex/` modules |
| `update_overview.py` | Updates overview tables in `docs/modules/` documentation with new module entries |
| `verify_index.py` | Verifies `src/codomyrmex/INDEX.md` entries match actual module directories |

## Usage

**Prerequisites:**
```bash
uv sync
```

**Run:**
```bash
# Audit stubs across the codebase
uv run python scripts/maintenance/audit_stubs.py --src src/codomyrmex --output reports/stub_audit.md

# Check dependency health
uv run python scripts/maintenance/check_dependencies.py

# Fix RASP documentation titles
uv run python scripts/maintenance/fix_llm_rasp.py

# Sync docs structure with source modules
uv run python scripts/maintenance/sync_docs.py

# Generate missing config directories
uv run python scripts/maintenance/generate_configs.py
```

## Agent Usage

Agents performing codebase maintenance should use `audit_stubs.py` to identify incomplete implementations and `check_dependencies.py` for dependency health. The `fix_*` scripts are for batch RASP documentation remediation.

## Related Module

- Source: `src/codomyrmex/maintenance/`
- MCP Tools: `maintenance_health_check`, `maintenance_list_tasks`

## Navigation

- [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [PAI.md](PAI.md)
- [Parent: scripts/](../README.md)
