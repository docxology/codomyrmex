# Ghost Architecture — Agent Coordination

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Agent coordination document for `docs/agents/ghost_architecture/`. This covers the Ghost Architecture continual-learning transformer submodule located at `src/codomyrmex/agents/ghost_architecture/`.

## Key Documents in This Directory

| File | Purpose |
|------|---------|
| [`README.md`](README.md) | Primary documentation: architecture, API, training pipeline |
| [`AGENTS.md`](AGENTS.md) | This file: agent coordination |

## Operating Contracts

- **Upstream mirror**: All changes to the submodule upstream must be reflected here.
- **Zero-Mock Testing**: Tests in `src/codomyrmex/tests/agents/test_ghost_architecture.py` must use real PyTorch tensors.
- **Git Submodule**: The source code at `src/codomyrmex/agents/ghost_architecture/` is a git submodule. Documentation files (`AGENTS.md`, `SPEC.md`) are added directly to the submodule directory as Codomyrmex overlays.

## Navigation

- **Parent**: [docs/agents/AGENTS.md](../AGENTS.md)
- **Source**: [src/codomyrmex/agents/ghost_architecture/AGENTS.md](../../../src/codomyrmex/agents/ghost_architecture/AGENTS.md)
- **Tests**: [src/codomyrmex/tests/agents/test_ghost_architecture.py](../../../src/codomyrmex/tests/agents/test_ghost_architecture.py)
- **Upstream**: [https://github.com/B-Smith-92/ghost-architecture](https://github.com/B-Smith-92/ghost-architecture)
