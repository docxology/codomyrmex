# Codomyrmex Agents — scripts/fpf

## Signposting
- **Parent**: [scripts](../AGENTS.md)
- **Self**: [Agents](AGENTS.md)
- **Children**:
    - [examples](examples/AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Automation and utility scripts for First Principles Framework (FPF) integration with Codomyrmex. Provides CLI access to FPF functionality, specification processing, analysis, visualization, and export capabilities.

## Active Components
- `README.md` – Project file
- `SPEC.md` – Project file
- `AGENTS.md` – Project file
- `orchestrate.py` – Main orchestration script (FPF pipeline)
- `examples/` – Example implementations

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.
- Scripts delegate to core module in `src/codomyrmex/fpf/`.

## Navigation Links
- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **📁 Parent Directory**: [scripts](../README.md) - Parent directory documentation
- **🏠 Project Root**: [README](../../README.md) - Main project documentation
- **Core Module**: [src/codomyrmex/fpf](../../../src/codomyrmex/fpf/README.md)
