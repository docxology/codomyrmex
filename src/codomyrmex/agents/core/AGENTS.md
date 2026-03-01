# agents/core -- Agent Capabilities

**Version**: v1.0.1 | **Status**: Active | **Last Updated**: February 2026

## Purpose

The `agents/core` submodule provides the ThinkingAgent -- a Chain-of-Thought reasoning engine that decomposes prompts into structured reasoning steps, scores confidence at each step, and synthesizes conclusions. Agents and orchestrators use these tools to perform deliberate, traceable reasoning with configurable depth (shallow, normal, deep).

## Active Components

| Component | Type | File | Status |
|-----------|------|------|--------|
| `ThinkingAgent` | Reasoning engine | `thinking_agent.py` | Active |
| `AgentRequest` | Request model | `base.py` | Active |
| `AgentConfig` | Configuration model | `config.py` | Active |
| `AgentRegistry` | Agent registration | `registry.py` | Active |
| `AgentSession` | Session management | `session.py` | Active |
| `ReactAgent` | ReAct loop agent | `react.py` | Active |
| `parsers` | Output parsing utilities | `parsers.py` | Active |
| `exceptions` | Exception hierarchy | `exceptions.py` | Active |
| `mcp_tools` | MCP tool definitions | `mcp_tools.py` | Active (4 tools) |

## MCP Tools Available

All tools are auto-discovered via `@mcp_tool` decorators and exposed through the MCP bridge.

| Tool | Description | Trust Level |
|------|-------------|-------------|
| `think` | Run Chain-of-Thought reasoning on a prompt with configurable depth (shallow/normal/deep) | Safe |
| `get_thinking_depth` | Return the current thinking depth of the ThinkingAgent | Safe |
| `set_thinking_depth` | Set the ThinkingAgent reasoning depth to shallow, normal, or deep | Safe |
| `get_last_trace` | Retrieve the most recent reasoning trace (steps, confidence, conclusion) | Safe |

## Operating Contracts

- **Singleton agent instance.** The MCP tools share a module-level `ThinkingAgent` singleton. Depth changes via `set_thinking_depth` persist across subsequent `think` calls within the same process.
- **Depth values.** Only `"shallow"`, `"normal"`, and `"deep"` are valid. Invalid values default to `normal` in `think` or return an error in `set_thinking_depth`.
- **Trace availability.** `get_last_trace` returns an error dict if no reasoning has been performed yet. Always call `think` before retrieving traces.
- **Zero-mock policy.** Tests must never mock the ThinkingAgent or its traces. Use `@pytest.mark.skipif` if LLM dependencies are unavailable.
- **Explicit failures.** All errors surface as `{"status": "error", "message": "..."}` dictionaries -- no silent fallbacks.

## Quick Verification

```bash
# Check module availability
uv run python -c "from codomyrmex.agents.core.mcp_tools import think; print(think.__name__)"

# Run agent core tests
uv run pytest src/codomyrmex/tests/unit/agents/ -k core -v
```

## Integration Points

| Module | Relationship |
|--------|-------------|
| `llm` | ThinkingAgent uses `llm.models.reasoning.ThinkingDepth` for depth control |
| `agents` | Parent module; core provides base classes consumed by all agent implementations |
| `cerebrum` | Reasoning traces feed into knowledge base for case-based retrieval |
| `model_context_protocol` | `@mcp_tool` decorators in `mcp_tools.py` enable auto-discovery |

## Navigation

- **Module**: `src/codomyrmex/agents/core/`
- **PAI integration**: [PAI.md](PAI.md)
- **Specification**: [SPEC.md](SPEC.md)
- **README**: [README.md](README.md)
- **Parent**: [../AGENTS.md](../AGENTS.md)
