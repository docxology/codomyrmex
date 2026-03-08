# Formal Verification Scripts

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

Orchestrator and example scripts for the `formal_verification` module, which provides Z3-based constraint solving, model checking, and ISC (Ideal State Criteria) consistency verification.

## Purpose

These scripts demonstrate the full formal verification lifecycle: basic constraint solving, incremental solving with push/pop, ISC consistency checks, conflict detection via unsat core extraction, and optimization using Z3's Optimize solver.

## Contents

| File | Description |
|------|-------------|
| `orchestrate.py` | Full lifecycle demo: constraints, incremental solving, ISC verification, optimization |
| `examples/` | Additional example scripts for specific verification scenarios |

## Usage

**Prerequisites:**
```bash
uv sync --extra formal_verification  # requires z3-solver
```

**Run:**
```bash
uv run python scripts/formal_verification/orchestrate.py
```

## Agent Usage

Agents performing formal verification should use the MCP tools (`clear_model`, `add_item`, `delete_item`, `replace_item`, `get_model`, `solve_model`) rather than calling Z3 directly. This orchestrator demonstrates the correct interaction pattern.

## Related Module

- Source: `src/codomyrmex/formal_verification/`
- MCP Tools: `clear_model`, `add_item`, `delete_item`, `replace_item`, `get_model`, `solve_model`

## Navigation

- [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [PAI.md](PAI.md)
- [Parent: scripts/](../README.md)
