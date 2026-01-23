# Personal AI Infrastructure Context: src/

## Purpose

This is the main source directory containing all Codomyrmex Python packages.

## AI Agent Guidance

### Context for Agents

- This directory contains `codomyrmex/` - the main Python package
- All module implementations live under `src/codomyrmex/<module_name>/`
- The `__init__.py` files define public APIs
- Each module has its own Quadruple Play documentation

### Key Patterns

- **Imports**: Always use `from codomyrmex.<module> import <class>`
- **Testing**: Tests are in `src/codomyrmex/tests/` or per-module `tests/` folders
- **Documentation**: Every module has README, AGENTS, SPEC, PAI

### Navigation Hints

- Find module by functionality, not alphabetically
- Core modules: `agents`, `cerebrum`, `llm`, `orchestrator`
- Infrastructure: `cache`, `serialization`, `networking`, `database_management`

## Cross-References

- [README.md](README.md) - Directory overview
- [AGENTS.md](AGENTS.md) - Agent rules
- [SPEC.md](SPEC.md) - Technical specification
