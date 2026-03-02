# Codomyrmex Agents — src/codomyrmex/agents

**Version**: v1.0.5 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Multi-provider agent framework with 12 provider integrations (5 API, 6 CLI, 1 local), session management, response parsing, multi-agent pooling, evaluation, conversation history, and an interactive setup wizard. Core layer for intelligent automation workflows.

## Active Components

### Provider Clients

| Agent | Type | Base Class | Binary / Env Var | Status |
| :--- | :--- | :--- | :--- | :--- |
| `claude/` | API | `APIAgentBase` | `ANTHROPIC_API_KEY` | Functional |
| `codex/` | API | `APIAgentBase` | `OPENAI_API_KEY` | Functional |
| `o1/` | API | `APIAgentBase` | `OPENAI_API_KEY` | Functional |
| `deepseek/` | API | `APIAgentBase` | `DEEPSEEK_API_KEY` | Functional |
| `qwen/` | API | `APIAgentBase` | `DASHSCOPE_API_KEY` | Functional |
| `jules/` | CLI | `CLIAgentBase` | `jules` | Functional |
| `opencode/` | CLI | `CLIAgentBase` | `opencode` | Functional |
| `gemini/` | CLI | `CLIAgentBase` | `gemini` | Functional |
| `mistral_vibe/` | CLI | `CLIAgentBase` | `vibe` | Functional |
| `every_code/` | CLI | `CLIAgentBase` | `code` | Functional |
| Ollama (local) | Local | via `llm/ollama/` | `OLLAMA_BASE_URL` | Functional |

### Core & Infrastructure

| Component | Path | Description |
| :--- | :--- | :--- |
| Core framework | `core/` | `BaseAgent`, `AgentInterface`, `AgentConfig`, parsers, sessions, `ReActAgent` |
| Generic bases | `generic/` | `APIAgentBase`, `CLIAgentBase`, `AgentOrchestrator`, `MessageBus`, `TaskPlanner` |
| Pooling | `pooling/` | `AgentPool`, `CircuitBreaker`, `AgentHealth` — load balancing and failover |
| Evaluation | `evaluation/` | `AgentBenchmark`, scorers (`ExactMatch`, `Contains`, `Length`, `Composite`) |
| History | `history/` | `ConversationManager`, `InMemoryHistoryStore`, `FileHistoryStore`, `SQLiteHistoryStore` |
| Agent Setup | `agent_setup/` | `AgentRegistry`, YAML config persistence, interactive setup wizard |
| Exceptions | `exceptions.py` | Full exception hierarchy: `AgentError` → provider-specific errors |

### Supplementary

| Component | Path | Description |
| :--- | :--- | :--- |
| AI code editing | `ai_code_editing/` | `CodeEditor` for refactoring, review, generation |
| Git agent | `git_agent/` | `GitAgent` for Git operations |
| Droid | `droid/` | Task management and automation |
| Infrastructure | `infrastructure/` | Infrastructure management agent |
| Theory | `theory/` | `ReactiveArchitecture`, `DeliberativeArchitecture`, `HybridArchitecture` |
| CLI | `cli/` | CLI subcommands and handlers |
| PAI Bridge | `pai/` | PAI system discovery and validation |

## Quick Verification

```bash
# Check which agents are operative on this machine
uv run python -m codomyrmex.agents.agent_setup --status-only

# Run the full agent test suite (350+ tests, zero-mock)
uv run python -m pytest src/codomyrmex/tests/unit/agents/ -v

# Run specific component tests
uv run python -m pytest src/codomyrmex/tests/unit/agents/test_agents_core_config.py
uv run python -m pytest src/codomyrmex/tests/unit/agents/test_agents_core_session.py
uv run python -m pytest src/codomyrmex/tests/unit/agents/test_agents_core_tools.py
uv run python -m pytest src/codomyrmex/tests/unit/agents/test_agents_core_orchestration.py

# Run the orchestration demo
uv run python src/codomyrmex/examples/agent_orchestration_demo.py
```

## Operating Contracts

- All agents implement `AgentInterface`: `execute()`, `stream()`, `setup()`, `test_connection()`
- All responses use `AgentResponse` with content, error, metadata, tokens, execution time
- Configuration through `AgentConfig` dataclass with environment variable fallbacks
- API keys masked in `to_dict()` output
- Zero-mock testing policy — all tests use real objects and functional verification

## PAI Agent Role Access Matrix

This section defines which PAI v4.0.1 agent types can access which agents submodules and at what trust level.

| PAI Agent | Access Level | Primary Capabilities | Trust Level |
|-----------|-------------|---------------------|-------------|
| **Engineer** | Full | `execute_agent`, `list_agents`, `get_agent_memory`; `CodeEditor`, `AgentOrchestrator`, all 12 provider clients | TRUSTED |
| **Architect** | Read + Design | `list_agents`, `get_agent_memory`; architecture analysis, provider selection, pool strategy design | OBSERVED |
| **QATester** | Validation | `list_agents`, `execute_agent` (test runs only); `AgentBenchmark`, all scorers (`ExactMatch`, `Contains`, `Composite`) | OBSERVED |
| **Researcher** | Read-only | `list_agents`, `get_agent_memory`; session history retrieval, conversation context inspection | OBSERVED |

### Engineer Agent
**Access**: Full — all provider clients, orchestration, code editing, session management
**Use Cases**: Implementing new provider integrations, building multi-agent workflows, AI-assisted code editing automation, parallel agent pool configuration.

### Architect Agent
**Access**: Read + Design — provider inventory, capability analysis, pool/circuit-breaker design
**Use Cases**: Agent architecture design, provider comparison and selection, pool sizing strategy, evaluation framework design, theoretical architecture review (reactive/deliberative/hybrid).

### QATester Agent
**Access**: Validation — benchmark runs, response validation, session persistence tests
**Use Cases**: Agent benchmark execution, provider integration verification, response format validation, conversation history round-trip tests.

### Researcher Agent
**Access**: Read-only — session history, agent capability discovery
**Use Cases**: Querying agent memory for prior work context, listing available providers for capability awareness, inspecting conversation history for research continuity.

## Navigation Links

- **📁 Parent Directory**: [codomyrmex](../README.md)
- **🏠 Project Root**: [README.md](../../../README.md)
