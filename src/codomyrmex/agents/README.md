# Agents Module

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Agentic framework integrations providing AI code editing, task management, and multi-provider support. Core layer for intelligent automation workflows with 12 provider integrations, session management, response parsing, and theoretical architecture foundations.

When used with [PAI](../../../PAI.md) (`~/.claude/skills/PAI/`), this module maps to PAI's three-tier agent system: Task Subagents (Engineer, Architect, QATester) dispatch through `AgentOrchestrator`, Named Agents consume tools via MCP, and Custom Agents extend `BaseAgent`. See [PAI.md](PAI.md) for full integration details.

## Installation

```bash
uv add codomyrmex
```

Or for development:

```bash
uv sync
```

## Key Exports

### Core Framework

- **`AgentInterface`** — Abstract base class for all agents
- **`BaseAgent`** — Base implementation with common agent behavior
- **`AgentIntegrationAdapter`** — Adapter pattern for integrating external agent frameworks
- **`APIAgentBase`** / **`CLIAgentBase`** — Base classes for API-based and CLI-based agents
- **`AgentCapabilities`** — Enum of agent capabilities
- **`AgentRequest`** — Dataclass request structure for agent operations (prompt, context, parameters)
- **`AgentResponse`** — Dataclass response structure from agent operations (content, error, tokens)
- **`AgentConfig`** / `get_config` / `set_config` / `reset_config` — Configuration management

### Code Editing

- **`CodeEditor`** — Agent specialized in code editing, generation, and analysis (extends BaseAgent)

### Provider Clients

- **`ClaudeClient`** — Claude API integration
- **`CodexClient`** — OpenAI Codex integration
- **`GeminiClient`** — Gemini CLI integration
- **`JulesClient`** — Jules CLI integration
- **`MistralVibeClient`** — Mistral Vibe CLI integration
- **`EveryCodeClient`** — Every Code CLI (multi-agent orchestration)
- **`OpenCodeClient`** — OpenCode CLI integration
- **`OpenClawClient`** — OpenClaw CLI integration
- **`DroidController`** — Droid controller integration
- **`O1Client`** — OpenAI o1/o3 reasoning models (lazy-loaded)
- **`DeepSeekClient`** — DeepSeek Coder integration (lazy-loaded)
- **`QwenClient`** — Qwen-Coder integration (lazy-loaded)

### Session & Parsing

- **`AgentSession`** / **`SessionManager`** / **`Message`** — Session lifecycle management
- **`parse_json_response`** / **`parse_code_blocks`** / **`parse_first_code_block`** — Response parsing utilities
- **`parse_structured_output`** / **`CodeBlock`** / **`ParseResult`** / **`clean_response`**

### Architecture & Theory

- **`ReactiveArchitecture`** / **`DeliberativeArchitecture`** / **`HybridArchitecture`** — Agent architectures
- **`KnowledgeBase`** — Knowledge management for agents
- **`AgentOrchestrator`** — Multi-agent orchestration

### Additional Submodules (lazy-loaded)

- **`AgentPool`** — Multi-agent load balancing and failover (`pooling/`)
- **`AgentEvaluator`** — Agent benchmarking and quality metrics (`evaluation/`)
- **`ConversationHistory`** — Conversation and context persistence (`history/`)
- **`InfrastructureAgent`** — Infrastructure management agent (`infrastructure/`)
- **`AgentRegistry`** — Declarative agent catalog with live health probes (`agent_setup/`)

### Exceptions

- `AgentError`, `AgentTimeoutError`, `AgentConfigurationError`, `ExecutionError`, `ToolError`, `ContextError`, `SessionError`

## Directory Contents

- `AGENT_COMPARISON.md` - Provider comparison reference
- `API_SPECIFICATION.md` - Programmatic interface documentation
- `MCP_TOOL_SPECIFICATION.md` - Model Context Protocol tool definitions
- `PAI.md` - PAI integration details (three-tier agent mapping, Algorithm capability selection, composition patterns)
- `SPEC.md` - Functional specification
- `__init__.py` - Module exports (40+ items)
- `exceptions.py` - Agent exception hierarchy
- `ai_code_editing/` - AI-powered code editing integration
- `claude/` - Claude API client
- `cli/` - CLI subcommands and handlers
- `codex/` - OpenAI Codex client
- `core/` - Core agent framework (base classes, config, sessions, parsers)
- `deepseek/` - DeepSeek Coder integration
- `droid/` - Droid controller integration
- `evaluation/` - Agent benchmarking and quality metrics
- `every_code/` - Every Code multi-agent orchestration
- `gemini/` - Gemini CLI client
- `generic/` - Base agent classes (APIAgentBase, CLIAgentBase, AgentOrchestrator)
- `git_agent/` - Git-specialized agent (GitAgent)
- `history/` - Conversation and context persistence
- `infrastructure/` - Infrastructure management agent
- `jules/` - Jules CLI client
- `mistral_vibe/` - Mistral Vibe CLI client
- `o1/` - OpenAI o1/o3 reasoning model client
- `openclaw/` - OpenClaw CLI client
- `opencode/` - OpenCode CLI client
- `pai/` - PAI system bridge (discovery, validation, status)
- `pooling/` - Multi-agent load balancing and failover
- `qwen/` - Qwen-Coder integration
- `theory/` - Theoretical foundations (reactive, deliberative, hybrid architectures)

## Quick Start

```python
import codomyrmex.agents

# Check which agents are available
from codomyrmex.agents.agent_setup import AgentRegistry
registry = AgentRegistry()
for r in registry.probe_all():
    print(f"{r.name}: {r.status}")

# Run the orchestration demo
# uv run python src/codomyrmex/examples/agent_orchestration_demo.py
```

## Testing

Running the full Zero-Mock test suite:

```bash
# Run all agent tests (350+ tests, zero-mock)
uv run python -m pytest src/codomyrmex/tests/unit/agents/ -v

# Run specific component tests
uv run python -m pytest src/codomyrmex/tests/unit/agents/test_agents_core_config.py
uv run python -m pytest src/codomyrmex/tests/unit/agents/test_agents_core_session.py
uv run python -m pytest src/codomyrmex/tests/unit/agents/test_agents_core_tools.py
uv run python -m pytest src/codomyrmex/tests/unit/agents/test_agents_core_orchestration.py
```

### Zero-Mock Policy

Tests use `FakeLLMClient` and real `BaseAgent` implementations (`ConcreteAgent`, `FailingAgent`) instead of `unittest.mock.MagicMock`. This ensures robust integration testing of the agent framework's core logic.

## Navigation

- **Full Documentation**: [docs/modules/agents/](../../../docs/modules/agents/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
