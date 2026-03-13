# Codomyrmex Agents — src/codomyrmex/coding

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Code generation, review, debugging, refactoring, pattern matching, and sandbox execution. Static analysis integration and security scanning capabilities.

## Active Components
- `API_SPECIFICATION.md` – Project file
- `MCP_TOOL_SPECIFICATION.md` – Project file
- `MIGRATION_COMPLETE.md` – Project file
- `PAI.md` – Project file
- `README.md` – Project file
- `SECURITY.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Project file
- `_lang_utils.py` – Project file
- `analysis/` – Directory containing analysis components
- `debugging/` – Directory containing debugging components
- `exceptions.py` – Project file
- `execution/` – Directory containing execution components
- `generation/` – Directory containing generation components
- `generator.py` – Project file
- `mcp_tools.py` – Project file
- `monitoring/` – Directory containing monitoring components
- `parsers/` – Directory containing parsers components
- `pattern_matching/` – Directory containing pattern_matching components
- `py.typed` – Project file
- `refactoring/` – Directory containing refactoring components
- `review/` – Directory containing review components
- `sandbox/` – Directory containing sandbox components
- `static_analysis/` – Directory containing static_analysis components
- `test_generator.py` – Project file
- `testing/` – Directory containing testing components

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Key Files
- `AGENTS.md` - Agent coordination and navigation
- `README.md` - Directory overview
- `API_SPECIFICATION.md`
- `MCP_TOOL_SPECIFICATION.md`
- `MIGRATION_COMPLETE.md`
- `PAI.md`
- `README.md`
- `SECURITY.md`
- `SPEC.md`
- `__init__.py`
- `_lang_utils.py`
- `exceptions.py`
- `generator.py`
- `mcp_tools.py`
- `py.typed`
- `test_generator.py`

## Dependencies
- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../../README.md - Main project documentation
