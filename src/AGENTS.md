# Codomyrmex Agents — src

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Core source code directory containing all Codomyrmex modules. This is the primary implementation surface with 93 specialized modules organized by architectural layer.

## Directory Structure

```text
src/
├── codomyrmex/           # Main package
│   ├── agents/           # AI agent framework
│   ├── cerebrum/         # Case-based reasoning
│   ├── coding/           # Code execution sandbox
│   ├── data_visualization/  # Charts and plots
│   ├── identity/         # Secure Cognitive - Identity
│   ├── wallet/           # Secure Cognitive - Self-custody
│   ├── defense/          # Secure Cognitive - Active defense
│   ├── market/           # Secure Cognitive - Anonymous markets
│   ├── privacy/          # Secure Cognitive - Mixnets
│   ├── llm/              # LLM integration
│   ├── meme/             # Memetics & Information Dynamics
│   ├── logging_monitoring/  # Centralized logging
│   ├── model_context_protocol/  # MCP implementation
│   ├── orchestrator/     # Workflow orchestration
│   ├── testing/          # Test utilities
│   ├── tests/            # Unit and integration tests
│   └── ... (70+ more)
```

## Active Components

| Component                | Type    | Description                                   |
| ------------------------ | ------- | --------------------------------------------- |
| `codomyrmex/`            | Package | Main module package (89 modules)              |
| `codomyrmex.llm/`        | Package | LLM integration subpackage                    |
| `__init__.py`            | Module  | Package initialization                        |
| [README.md](README.md)   | Doc     | Directory overview                            |
| [SPEC.md](SPEC.md)       | Doc     | Functional specification                      |
| [PAI.md](PAI.md)         | Doc     | Personal AI considerations                    |

## Agent Guidelines

### Module Quality Standards

1. **Testing**: Each module must have ≥80% test coverage
2. **Documentation**: All public APIs must be documented
3. **RASP Compliance**: Each module directory must have README, AGENTS, SPEC, PAI
4. **MCP Tools**: Register tools in `MCP_TOOL_SPECIFICATION.md`

### Key Entry Points

| Module                    | Purpose                     | Priority   |
| ------------------------- | --------------------------- | ---------- |
| `logging_monitoring/`     | Start here for logging      | Foundation |
| `environment_setup/`      | Environment validation      | Foundation |
| `model_context_protocol/` | AI tool interfaces          | Foundation |
| `agents/`                 | AI agent framework          | Core       |
| `orchestrator/`           | Workflow coordination       | Service    |

### Secure Cognitive Modules

| Module      | Purpose                            |
| ----------- | ---------------------------------- |
| `identity/` | 3-tier personas, bio-verification  |
| `wallet/`   | Self-custody, Natural Ritual...    |
| `defense/`  | Exploit detection, context poison  |
| `market/`   | Reverse auctions, demand agg       |
| `privacy/`  | Crumb scrubbing, mixnet routing    |

## Operating Contracts

- Maintain alignment between code, documentation, and configured workflows
- Ensure Model Context Protocol interfaces remain available for sibling agents
- Record outcomes in shared telemetry and update TODO queues when necessary
- Follow Python best practices (PEP 8, type hints, docstrings)

## Navigation Links

- **📁 Parent**: [../README.md](../README.md) - Project root
- **📦 Main Package**: [codomyrmex/AGENTS.md](codomyrmex/AGENTS.md) - Module hub
- **🧪 Tests**: [codomyrmex/tests/AGENTS.md](codomyrmex/tests/AGENTS.md) - Test coordination
- **📖 Docs**: [../docs/modules/](../docs/modules/) - Module documentation
