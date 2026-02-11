# Codomyrmex Agents — src/codomyrmex/agents

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Multi-provider agent framework with 11 provider integrations (5 API, 5 CLI, 1 local), session management, response parsing, multi-agent pooling, evaluation, conversation history, and an interactive setup wizard. Core layer for intelligent automation workflows.

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

## Quick Verification

```bash
# Check which agents are operative on this machine
uv run python -m codomyrmex.agents.agent_setup --status-only

# Run the full agent test suite (129 tests, zero-mock)
uv run python -m pytest tests/unit/agents/ -v --no-cov
```

## Operating Contracts

- All agents implement `AgentInterface`: `execute()`, `stream()`, `setup()`, `test_connection()`
- All responses use `AgentResponse` with content, error, metadata, tokens, execution time
- Configuration through `AgentConfig` dataclass with environment variable fallbacks
- API keys masked in `to_dict()` output
- Zero-mock testing policy — all tests use real objects and functional verification

## Navigation Links

- **📁 Parent Directory**: [codomyrmex](../README.md)
- **🏠 Project Root**: [README.md](../../../README.md)
