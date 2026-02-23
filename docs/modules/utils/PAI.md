# Personal AI Infrastructure — Utils Module

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The Utils module provides shared utility functions used across the codomyrmex ecosystem — string manipulation, path helpers, type coercion, hashing, and general-purpose Python utilities.

## PAI Capabilities

- Path normalization and resolution utilities
- String formatting and sanitization helpers
- Hash computation (MD5, SHA256) for integrity checks
- Type conversion and coercion utilities
- Common data structure helpers

## Key Exports

| Export | Type | Purpose |
|--------|------|---------|
| Path helpers | Various | File path manipulation |
| String utilities | Various | Formatting and sanitization |
| Hash functions | Various | Integrity computation |
| Type coercion | Various | Data type conversions |

## PAI Algorithm Phase Mapping

| Phase | Utils Contribution |
|-------|---------------------|
| **All Phases** | Cross-cutting utility functions used throughout the system |

## Architecture Role

**Foundation Layer** — Lowest-level utility module with zero codomyrmex dependencies. Consumed by virtually all other modules.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md) | [API_SPECIFICATION.md](API_SPECIFICATION.md)
