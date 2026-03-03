# Agents

**Version**: v1.0.8 | **Status**: Active | **Last Updated**: March 2026

## Overview

The Agents module is the core agentic framework for codomyrmex, providing integration with 13 AI agent providers across API-based, CLI-based, and local deployment models. It serves as the Core layer's primary capability for intelligent automation workflows, offering session management, response parsing, multi-agent orchestration, and theoretical architecture foundations. When used with PAI, this module maps to PAI's three-tier agent system: Task Subagents dispatch through `AgentOrchestrator`, Named Agents consume tools via MCP, and Custom Agents extend `BaseAgent`.

## Architecture Overview

The module follows a provider-plugin architecture. A shared core framework defines interfaces (`AgentInterface`, `BaseAgent`), configuration (`AgentConfig`), and session management (`SessionManager`). Provider-specific clients implement these interfaces for each supported AI service. The `generic/` package provides base classes (`APIAgentBase`, `CLIAgentBase`) that handle the common concerns of API-based and CLI-based agent communication.

```
agents/
├── __init__.py              # Public API (40+ exports, lazy-loaded providers)
├── core/                    # Core framework (base classes, config, sessions, parsers, exceptions)
├── generic/                 # Base classes: APIAgentBase, CLIAgentBase, AgentOrchestrator
├── agent_setup/             # Agent discovery, YAML config, AgentRegistry
├── ai_code_editing/         # CodeEditor for AI-powered code generation
├── claude/                  # Claude API client
├── codex/                   # OpenAI Codex client
├── deepseek/                # DeepSeek Coder client
├── droid/                   # Droid controller integration
├── every_code/              # Every Code multi-agent orchestration
├── gemini/                  # Gemini CLI client
├── git_agent/               # Git-specialized agent (GitAgent)
├── infrastructure/          # Infrastructure management agent
├── jules/                   # Jules CLI client
├── mistral_vibe/            # Mistral Vibe CLI client
├── o1/                      # OpenAI o1/o3 reasoning models
├── openclaw/                # OpenClaw CLI client
├── opencode/                # OpenCode CLI client
├── qwen/                    # Qwen-Coder client
├── agentic_seek/            # agenticSeek CLI client
├── pooling/                 # Multi-agent load balancing and failover
├── evaluation/              # Agent benchmarking and quality metrics
├── history/                 # Conversation and context persistence
├── theory/                  # Theoretical foundations (reactive, deliberative, hybrid)
├── pai/                     # PAI system bridge (MCP discovery, trust, status)
├── cli/                     # CLI subcommands and handlers
└── mcp_tools.py             # MCP tool definitions (execute_agent, list_agents, get_agent_memory)
```

## PAI Integration

### Algorithm Phase Mapping

| Algorithm Phase | Role | Key Operations |
|----------------|------|---------------|
| OBSERVE | Agent reads codebase, discovers capabilities | `list_agents`, `get_agent_memory` |
| THINK | Select optimal agent provider/model for the task | `list_agents` (inventory check) |
| BUILD | Engineer agent runs code editing, generation, refactoring | `execute_agent` via CodeEditor |
| EXECUTE | All 13 provider clients dispatch tasks | `execute_agent` with specific agent_name |
| VERIFY | QATester agent runs benchmarks, validates output quality | `execute_agent`, `list_agents` |
| LEARN | Session history captured, agent memory stored | `get_agent_memory` |

## Key Classes and Functions

### Core Framework

**`AgentInterface`** -- Abstract base class defining the contract for all agents.

**`BaseAgent`** -- Base implementation with common agent behavior (execute, session management).

**`AgentConfig`** -- Configuration management for all agent providers.

```python
from codomyrmex.agents import AgentConfig, get_config, set_config

config = get_config()
set_config(AgentConfig(timeout=30, max_retries=3))
```

**`AgentOrchestrator`** -- Multi-agent orchestration for task decomposition and delegation.

### Provider Clients

**API-based:** `ClaudeClient`, `CodexClient`, `O1Client`, `DeepSeekClient`, `QwenClient`

**CLI-based:** `JulesClient`, `OpenCodeClient`, `OpenClawClient`, `GeminiClient`, `MistralVibeClient`, `EveryCodeClient`, `AgenticSeekClient`

**Local:** Ollama (via `llm/ollama/`)

### Session and Parsing

**`SessionManager`** -- Manages agent session lifecycle with message history.

**`parse_code_blocks()`** / **`parse_json_response()`** -- Extract structured data from agent responses.

## MCP Tools Reference

| Tool | Description | Parameters | Trust Level |
|------|-------------|------------|-------------|
| `execute_agent` | Execute an agent conversation with a prompt | `agent_name: str`, `prompt: str` | Safe |
| `list_agents` | Return all available AI agents with status | (none) | Safe |
| `get_agent_memory` | Retrieve interaction logs for a session | `session_id: str` | Safe |

## Configuration

```bash
export ANTHROPIC_API_KEY="sk-..."     # For Claude provider
export OPENAI_API_KEY="sk-..."        # For Codex/O1 providers
export GEMINI_API_KEY="..."           # For Gemini provider
export DEEPSEEK_API_KEY="..."         # For DeepSeek provider
```

## Usage Examples

### Example 1: List Available Agents

```python
from codomyrmex.agents.agent_setup import AgentRegistry

registry = AgentRegistry()
for agent_info in registry.probe_all():
    print(f"{agent_info.name}: {agent_info.status}")
```

### Example 2: Execute an Agent Task

```python
from codomyrmex.agents import AgentRequest
from codomyrmex.agents.agent_setup import AgentRegistry

registry = AgentRegistry()
agent = registry.create_agent("claude")
request = AgentRequest(prompt="Explain the observer pattern")
response = agent.execute(request)
print(response.content)
```

## Error Handling

- `AgentError` -- Base exception for all agent-related errors
- `AgentTimeoutError` -- Raised when an agent does not respond within the configured timeout
- `AgentConfigurationError` -- Raised for invalid agent configuration
- `ExecutionError` -- Raised when agent execution fails
- `ToolError` -- Raised when a tool invocation within an agent fails
- `ContextError` -- Raised for context management failures
- `SessionError` -- Raised for session lifecycle failures

## Related Modules

- [`agentic_memory`](../agentic_memory/readme.md) -- Memory storage consumed by agents for context continuity
- [`llm`](../llm/readme.md) -- LLM infrastructure (Ollama, providers) that agents delegate to
- [`coding`](../coding/readme.md) -- Code execution sandbox used by code editing agents

## Navigation

- **Source**: [src/codomyrmex/agents/](../../../../src/codomyrmex/agents/)
- **API Spec**: [API_SPECIFICATION.md](../../../../src/codomyrmex/agents/API_SPECIFICATION.md)
- **Parent**: [All Modules](../README.md)
