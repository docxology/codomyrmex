# Codomyrmex Agents — src/codomyrmex/llm

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Contains components for the src system.

## Active Components
- `API_SPECIFICATION.md` – Project file
- `MCP_TOOL_SPECIFICATION.md` – Project file
- `PAI.md` – Project file
- `README.md` – Project file
- `SECURITY.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Project file
- `chain_of_thought.py` – Project file
- `chains/` – Directory containing chains components
- `config.py` – Project file
- `context_manager.py` – Project file
- `cost_tracking/` – Directory containing cost_tracking components
- `embeddings/` – Directory containing embeddings components
- `exceptions.py` – Project file
- `fabric/` – Directory containing fabric components
- `guardrails/` – Directory containing guardrails components
- `mcp.py` – Project file
- `mcp_tools.py` – Project file
- `memory/` – Directory containing memory components
- `models/` – Directory containing models components
- `multimodal/` – Directory containing multimodal components
- `ollama/` – Directory containing ollama components
- `outputs/` – Directory containing outputs components
- `prompt_templates/` – Directory containing prompt_templates components
- `prompts/` – Directory containing prompts components
- `providers/` – Directory containing providers components
- `py.typed` – Project file
- `rag/` – Directory containing rag components
- `router.py` – Project file
- `safety.py` – Project file
- `streaming/` – Directory containing streaming components
- `tools/` – Directory containing tools components

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Key Files
- `AGENTS.md` - Agent coordination and navigation
- `README.md` - Directory overview
- `API_SPECIFICATION.md`
- `MCP_TOOL_SPECIFICATION.md`
- `PAI.md`
- `README.md`
- `SECURITY.md`
- `SPEC.md`
- `__init__.py`
- `chain_of_thought.py`
- `config.py`
- `context_manager.py`
- `exceptions.py`
- `mcp.py`
- `mcp_tools.py`
- `py.typed`
- `router.py`
- `safety.py`

## Dependencies
- Inherits dependencies from the parent module. See `pyproject.toml` or `package.json` for global dependencies.

## Development Guidelines
- Follow the universal agent protocols defined in the root `AGENTS.md`.
- Adhere to the Python PEP 8 style guide and project-specific linting rules.
- Ensure all new features are accompanied by corresponding tests (zero-mock policy).

## Navigation Links
- **📁 Parent Directory**: [codomyrmex](../README.md) - Parent directory documentation
- **🏠 Project Root**: ../../../README.md - Main project documentation
