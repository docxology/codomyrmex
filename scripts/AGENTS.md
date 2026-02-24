# AGENTS.md — Scripts Directory

## Purpose

This directory contains utility scripts, module-specific examples, and development tooling for the Codomyrmex project. Scripts are organized into category-based subdirectories.

## Agent Guidelines

### Directory Categories

- **`audits/`** — Code quality and compliance audits (documentation, exports, imports, RASP)
- **`demos/`** — Interactive module demonstrations (defense, identity, market, privacy, wallet)
- **`docs/`** — Documentation generation and remediation tools
- **`pai/`** — PAI integration validation and skill updates
- **`performance/`** — Startup benchmarks and mutation testing
- **`verification/`** — Phase-gated verification scripts for release readiness
- **`website/`** — Dashboard launcher and web utilities
- **`<module>/`** — Per-module example scripts mirroring `src/codomyrmex/` structure

### Running Scripts

All scripts should be run from the project root using `uv run`:

```bash
uv run python scripts/<category>/<script>.py
```

### Adding New Scripts

1. Place module-specific scripts in the matching module subdirectory
2. Place cross-cutting scripts in the appropriate category (`audits/`, `docs/`, etc.)
3. Never place generated artifacts (output, reports, metrics) in this directory — use project root `output/` or temp dirs
