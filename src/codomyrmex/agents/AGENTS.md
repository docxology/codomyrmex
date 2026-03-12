# Codomyrmex Agents — src/codomyrmex/agents

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
Contains components for the src system.

## Active Components
- `AGENT_COMPARISON.md` – Project file
- `API_SPECIFICATION.md` – Project file
- `MCP_TOOL_SPECIFICATION.md` – Project file
- `PAI.md` – Project file
- `README.md` – Project file
- `SPEC.md` – Project file
- `__init__.py` – Project file
- `agent_setup/` – Directory containing agent_setup components
- `agentic_seek/` – Directory containing agentic_seek components
- `ai_code_editing/` – Directory containing ai_code_editing components
- `autonomous.py` – Project file
- `benchmarks.py` – Project file
- `claude/` – Directory containing claude components
- `cli/` – Directory containing cli components
- `codex/` – Directory containing codex components
- `context/` – Directory containing context components
- `core/` – Directory containing core components
- `deepseek/` – Directory containing deepseek components
- `droid/` – Directory containing droid components
- `editing_loop.py` – Project file
- `education.py` – Project file
- `evaluation/` – Directory containing evaluation components
- `every_code/` – Directory containing every_code components
- `gemini/` – Directory containing gemini components
- `generic/` – Directory containing generic components
- `git_agent/` – Directory containing git_agent components
- `google_workspace/` – Directory containing google_workspace components
- `hermes/` – Directory containing hermes components
- `history/` – Directory containing history components
- `infrastructure/` – Directory containing infrastructure components
- `jules/` – Directory containing jules components
- `learning/` – Directory containing learning components
- `llm_client.py` – Project file
- `mcp_tools.py` – Project file
- `memory/` – Directory containing memory components
- `meta/` – Directory containing meta components
- `mission_control/` – Directory containing mission_control components (builderz-labs/mission-control dashboard)
- `pi/` – Directory containing pi coding agent components (pi.dev terminal agent)
- `mistral_vibe/` – Directory containing mistral_vibe components
- `o1/` – Directory containing o1 components
- `openclaw/` – Directory containing openclaw components
- `opencode/` – Directory containing opencode components
- `openfang/` – Directory containing openfang components
- `orchestrator.py` – Project file
- `pai/` – Directory containing pai components
- `perplexity/` – Directory containing perplexity components
- `planner/` – Directory containing planner components
- `pooling/` – Directory containing pooling components
- `py.typed` – Project file
- `qwen/` – Directory containing qwen components
- `specialized/` – Directory containing specialized components
- `theory/` – Directory containing theory components
- `transport/` – Directory containing transport components

## Operating Contracts
- Maintain alignment between code, documentation, and configured workflows.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.

## Key Files
- `AGENTS.md` - Agent coordination and navigation
- `README.md` - Directory overview
- `AGENT_COMPARISON.md`
- `API_SPECIFICATION.md`
- `MCP_TOOL_SPECIFICATION.md`
- `PAI.md`
- `README.md`
- `SPEC.md`
- `__init__.py`
- `autonomous.py`
- `benchmarks.py`
- `editing_loop.py`
- `education.py`
- `llm_client.py`
- `mcp_tools.py`
- `orchestrator.py`
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
