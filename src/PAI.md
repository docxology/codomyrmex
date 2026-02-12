# Personal AI Infrastructure Context: src/

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

This is the main source directory containing the `codomyrmex` Python package with 94 specialized modules organized across four architectural layers.

## AI Agent Guidance

### Context for Agents

- This directory contains `codomyrmex/` - the main Python package
- All module implementations live under `src/codomyrmex/<module_name>/`
- The `__init__.py` files define public APIs
- Each module has its own RASP documentation (README, AGENTS, SPEC, PAI)

### Architectural Layers

| Layer | Modules | Purpose |
|-------|---------|---------|
| Foundation | `logging_monitoring`, `environment_setup`, `model_context_protocol`, `terminal_interface`, `config_management`, `metrics` | Core infrastructure |
| Core | `coding`, `static_analysis`, `llm`, `git_operations`, `security`, `data_visualization` | Primary functionality |
| Service | `build_synthesis`, `documentation`, `api`, `ci_cd_automation`, `containerization`, `database_management` | Higher-level services |
| Specialized | `agents`, `cerebrum`, `meme`, `fpf`, `spatial`, `evolutionary_ai`, `quantum` | Advanced features |

### Key Patterns

- **Imports**: Always use `from codomyrmex.<module> import <class>`
- **Testing**: Tests are in `src/codomyrmex/tests/` or per-module `tests/` folders
- **Documentation**: Every module has README, AGENTS, SPEC, PAI

### MCP Integration

Modules expose functionality via Model Context Protocol:

- Tool specifications in `MCP_TOOL_SPECIFICATION.md`
- Resource endpoints for data access
- Prompt templates for LLM interaction

### Agentic Memory Considerations

- `agentic_memory/` module provides persistent memory for agents
- Memory contexts integrate with `model_context_protocol/`
- State persistence uses `serialization/` and `cache/` modules

### Navigation Hints

- Find module by functionality, not alphabetically
- **Core Modules**: `agents`, `cerebrum`, `llm`, `orchestrator`
- **Infrastructure**: `cache`, `serialization`, `networking`, `database_management`
- **Security Suite**: `identity`, `wallet`, `defense`, `market`, `privacy`

## Cross-References

- [README.md](README.md) - Directory overview
- [AGENTS.md](AGENTS.md) - Agent rules
- [SPEC.md](SPEC.md) - Technical specification
- [codomyrmex/PAI.md](codomyrmex/PAI.md) - Main package PAI context
