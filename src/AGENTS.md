# Codomyrmex Agents — src

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Hosts core source code and agent-enabled services for the Codomyrmex platform.

## Active Components
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Project file
- `codomyrmex/` – Directory containing codomyrmex components
- `codomyrmex.llm/` – Directory containing codomyrmex.llm components

## Operating Contracts

1. **Code Quality**: Maintain alignment between code, documentation, and tests
2. **MCP Interfaces**: Ensure Model Context Protocol interfaces remain available
3. **Telemetry**: Record outcomes in shared telemetry
4. **Layered Architecture**: Respect Foundation → Core → Service → Specialized layer dependencies

## Signposting

### Document Hierarchy

- **Self**: [AGENTS.md](AGENTS.md)
- **Parent**: [../AGENTS.md](../AGENTS.md) - Project root agent coordination
- **Project Root**: [../README.md](../README.md)

### Sibling Directories

| Directory | AGENTS.md | Purpose |
| :--- | :--- | :--- |
| docs/ | [../docs/AGENTS.md](../docs/AGENTS.md) | Documentation |
| scripts/ | [../scripts/AGENTS.md](../scripts/AGENTS.md) | Automation scripts |
| config/ | [../config/AGENTS.md](../config/AGENTS.md) | Configuration |

### Child Directories

| Directory | AGENTS.md | Purpose |
| :--- | :--- | :--- |
| codomyrmex/ | [codomyrmex/AGENTS.md](codomyrmex/AGENTS.md) | Main module hub |

### Related Documentation

- [README.md](README.md) - Source overview
- [SPEC.md](SPEC.md) - Functional specification
- [codomyrmex/PAI.md](codomyrmex/PAI.md) - PAI documentation
