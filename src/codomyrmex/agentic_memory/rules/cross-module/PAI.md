# Personal AI Infrastructure - Cross-Module Rules Context

**Directory**: `cursorrules/cross-module/`
**Status**: Active | **Last Updated**: February 2026

## Overview

Cross-module cursor rules for multi-module interactions and shared patterns. Contains **8 rules** for cross-cutting concerns like logging, MCP, static analysis, and build synthesis.

## Statistics

| Category | Count |
|----------|-------|
| Cross-module rules | 8 |

## AI Context

When working with cross-module rules:

1. **Scope**: These rules apply when working across module boundaries
2. **Priority**: Lower than file-specific and module-specific rules, higher than general
3. **Patterns**: Logging, MCP, static analysis, build, output, visualization, pattern matching, templates
4. **Mandatory Policies**: Zero-Mock, UV-Only, RASP, Python ≥ 3.10 apply unconditionally

## Key Policies

- **Zero-Mock**: Cross-module integration tests use real implementations
- **UV**: Dependencies via `uv add` → `pyproject.toml` — no `requirements.txt`
- **RASP**: All directories need README.md, AGENTS.md, SPEC.md, PAI.md

## Key Files

- 8 `.cursorrules` files covering cross-cutting concerns
- Each follows the standard 8-section template

## Navigation

- **Parent**: [../README.md](../README.md)
- **Agent Guidelines**: [AGENTS.md](AGENTS.md)
- **Specification**: [SPEC.md](SPEC.md)
