# Personal AI Infrastructure — FPF Module

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Overview

The FPF (Functional Programming Framework) module provides functional programming primitives and transformations — immutable data structures, monadic composition, currying, pipe/compose, and algebraic data types for building reliable, composable data pipelines.

## PAI Capabilities

### Functional Composition

- `pipe` / `compose` — function composition pipelines
- `curry` — automatic function currying
- `map` / `filter` / `reduce` — functional collection operations
- Immutable data structures for safe concurrent access
- Result/Option monads for error handling without exceptions

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| Functional primitives | Various | Compose, pipe, curry utilities |
| Algebraic types | Various | Result, Option, Either monads |

## PAI Algorithm Phase Mapping

| Phase | FPF Contribution |
|-------|-------------------|
| **THINK** | Compose reasoning pipelines with functional transformations |
| **BUILD** | Build data transformation pipelines |
| **EXECUTE** | Chain operations safely with monadic error handling |

## Architecture Role

**Specialized Layer** — Functional programming toolkit used by modules needing composable data transformations.

## MCP Tools

This module does not expose MCP tools directly. Access its capabilities via:
- Direct Python import: `from codomyrmex.fpf import ...`
- CLI: `codomyrmex fpf <command>`

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
