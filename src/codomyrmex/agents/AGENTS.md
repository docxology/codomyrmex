# Codomyrmex Agents — src/codomyrmex/agents

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose
LLM provider integrations and agent implementations for Claude, Codex, Gemini, OpenAI, and other AI providers. Handles API communication, tool orchestration, and provider-specific features.

## Active Components
- `AGENT_COMPARISON.md` – Agent Comparison implementation
- `API_SPECIFICATION.md` – API reference — public functions, classes, parameters, and return types
- `MCP_TOOL_SPECIFICATION.md` – MCP tool definitions — schemas, parameters, and invocation patterns
- `PAI.md` – Public API Interface — integration patterns and usage guidelines
- `README.md` – Module overview — quick start, features, and usage examples
- `SPEC.md` – Module specification — design, purpose, interfaces, and architecture
- `__init__.py` – Python package entry point — exports and initialization
- `agent_setup/` – agent setup module implementation
- `agentic_seek/` – agentic seek module implementation
- `ai_code_editing/` – ai code editing module implementation
- `autonomous.py` – Autonomous implementation
- `benchmarks.py` – Benchmarks implementation
- `claude/` – claude module implementation
- `cli/` – Command-line interface handlers
- `codex/` – codex module implementation
- `context/` – context module implementation
- `core/` – Core abstractions and base classes
- `deepseek/` – deepseek module implementation
- `droid/` – droid module implementation
- `editing_loop.py` – Internal implementation module
- `education.py` – Education implementation
- `evaluation/` – evaluation module implementation
- `every_code/` – every code module implementation
- `gemini/` – gemini module implementation
- `generic/` – generic module implementation
- `git_agent/` – git agent module implementation
- `google_workspace/` – google workspace module implementation
- `ghost_architecture/` – ghost architecture framework submodule
- `hermes/` – hermes module implementation
- `open_gauss/` – [OpenGauss](https://github.com/math-inc/OpenGauss) submodule — Lean4 theorem proving & autoformalization workflows (SessionDB, GaussProject, swarm manager) | [docs](../../../../../docs/agents/open_gauss/README.md) | [tests](../../tests/agents/test_open_gauss.py) | 77 tests passing
- `history/` – history module implementation
- `infrastructure/` – infrastructure module implementation
- `jules/` – jules module implementation
- `learning/` – learning module implementation
- `llm_client.py` – Client implementation for external service integration
- `mcp_tools.py` – MCP tool implementations — tool handlers and schemas
- `memory/` – memory module implementation
- `meta/` – meta module implementation
- `mission_control/` – mission control module implementation (builderz-labs/mission-control dashboard)
- `pi/` – Directory containing pi coding agent components (pi.dev terminal agent)
- `mistral_vibe/` – mistral vibe module implementation
- `o1/` – o1 module implementation
- `openclaw/` – openclaw module implementation
- `opencode/` – opencode module implementation
- `openfang/` – openfang module implementation
- `orchestrator.py` – Orchestrator implementation
- `pai/` – pai module implementation
- `perplexity/` – perplexity module implementation
- `planner/` – planner module implementation
- `pooling/` – pooling module implementation
- `py.typed` – PEP 561 marker for typed package
- `qwen/` – qwen module implementation
- `specialized/` – specialized module implementation
- `theory/` – theory module implementation
- `transport/` – transport module implementation


## Key Interfaces

- `hermes_client.py — Hermes agent client for codomyrmex integration`
- `mcp_tools.py — MCP tool definitions for agent operations`
- `session.py — Agent session management and state persistence`
- `_provider_router.py — Dynamic provider selection and routing`

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
