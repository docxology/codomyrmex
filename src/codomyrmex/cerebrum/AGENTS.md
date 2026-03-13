# Codomyrmex Agents — src/codomyrmex/cerebrum

**Version**: v1.3.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Cognitive modeling layer integrating case-based reasoning, Bayesian inference, and active inference with free-energy minimization.

## Active Components
- `API_SPECIFICATION.md` – Project file
- `CHANGELOG.md` – Project file
- `MCP_TOOL_SPECIFICATION.md` – Project file
- `PAI.md` – Project file
- `README.md` – Project file
- `SECURITY.md` – Project file
- `SPEC.md` – Project file
- `USAGE_EXAMPLES.md` – Project file
- `__init__.py` – Project file
- `agent_prompts.py` – Project file
- `anti_patterns.py` – Project file
- `code_reviewer.py` – Project file
- `core/` – Directory containing core components
- `distillation.py` – Project file
- `drift_tracker.py` – Project file
- `fpf/` – Directory containing fpf components
- `inference/` – Directory containing inference components
- `inference/free_energy_loop.py` – Closed-loop free-energy minimization runner (v1.3.0)
- `mcp_tools.py` – Project file
- `py.typed` – Project file
- `visualization/` – Directory containing visualization components

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Key Files
- `AGENTS.md` - Agent coordination and navigation
- `README.md` - Directory overview
- `API_SPECIFICATION.md`
- `CHANGELOG.md`
- `MCP_TOOL_SPECIFICATION.md`
- `PAI.md`
- `README.md`
- `SECURITY.md`
- `SPEC.md`
- `USAGE_EXAMPLES.md`
- `__init__.py`
- `agent_prompts.py`
- `anti_patterns.py`
- `code_reviewer.py`
- `distillation.py`
- `drift_tracker.py`
- `mcp_tools.py`
- `py.typed`

## Dependencies
- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../../README.md - Main project documentation
