# Personal AI Infrastructure — Agents/Core Module (ThinkingAgent)

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The `agents/core` module provides the **ThinkingAgent** — a Chain-of-Thought reasoning
engine that decomposes complex prompts into structured reasoning steps and synthesizes
a conclusion with confidence scoring.

It is the primary reasoning capability available to PAI agents during the **THINK**
phase. Four MCP tools expose the ThinkingAgent to all PAI agents via the MCP bridge.

## PAI Capabilities

### Chain-of-Thought Reasoning

```python
from codomyrmex.agents.core.mcp_tools import think, get_last_trace

# Run structured reasoning
result = think(
    prompt="Should we use Redis or in-memory caching for session state?",
    depth="deep",
)
# Returns: {"status": "success", "content": "...", "confidence": 0.87, "steps": 5, "depth": "deep"}

# Retrieve the full trace from the last reasoning run
trace = get_last_trace()
# Returns: trace_id, depth, step_count, confidence, conclusion
```

### Depth Control

```python
from codomyrmex.agents.core.mcp_tools import get_thinking_depth, set_thinking_depth

# Check current depth setting
current = get_thinking_depth()
# Returns: {"status": "success", "depth": "normal"}

# Adjust depth for the current session
set_thinking_depth("deep")    # thorough reasoning for complex ISC
set_thinking_depth("normal")  # default — good balance
set_thinking_depth("shallow") # fast scan for trivial decisions
```

## MCP Tools

The following four tools are auto-discovered via `@mcp_tool` and available through
the PAI MCP bridge without any Trust Gateway elevation:

| Tool | Description | Trust Level | Category |
|------|-------------|-------------|----------|
| `codomyrmex.think` | Run Chain-of-Thought reasoning on a prompt; returns conclusion + confidence | Safe | agents.core |
| `codomyrmex.get_thinking_depth` | Return the current reasoning depth of the ThinkingAgent | Safe | agents.core |
| `codomyrmex.set_thinking_depth` | Set ThinkingAgent depth to `shallow`, `normal`, or `deep` | Safe | agents.core |
| `codomyrmex.get_last_trace` | Retrieve the most recent reasoning trace (steps, confidence, conclusion) | Safe | agents.core |

### Tool Signatures

**`think(prompt, depth="normal")`**
- `prompt`: str — the question or problem to reason about
- `depth`: str — `"shallow"`, `"normal"`, or `"deep"`
- Returns: `{"status": "success", "content": str, "confidence": float, "steps": int, "depth": str}`

**`get_thinking_depth()`**
- No arguments
- Returns: `{"status": "success", "depth": str}`

**`set_thinking_depth(depth)`**
- `depth`: str — `"shallow"`, `"normal"`, or `"deep"`
- Returns: `{"status": "success", "depth": str}` or `{"status": "error", "message": str}`

**`get_last_trace()`**
- No arguments
- Returns: `{"status": "success", "trace_id": str, "depth": str, "steps": int, "confidence": float, "is_complete": bool, "conclusion": {...}}`
  or `{"status": "error", "message": "No reasoning traces available."}`

## PAI Algorithm Phase Mapping

| Phase | ThinkingAgent Contribution | MCP Tools |
|-------|---------------------------|-----------|
| **OBSERVE** (1/7) | Quickly assess request structure before deep analysis | `think` at `shallow` depth |
| **THINK** (2/7) | Pressure-test ISC criteria, identify risky assumptions, pre-mortem analysis | `think` at `normal` or `deep` depth; `get_last_trace` |
| **PLAN** (3/7) | Evaluate feasibility of proposed execution approaches | `think`, `set_thinking_depth` |
| **VERIFY** (6/7) | Re-examine evidence before claiming criteria pass | `think`, `get_last_trace` |

### Concrete PAI Usage Pattern

During the THINK phase, PAI uses the ThinkingAgent to pressure-test assumptions:

```python
# PAI THINK phase — run deep reasoning to catch ISC gaps
result = mcp_call("codomyrmex.think", {
    "prompt": "Given these ISC criteria: [list], what is the riskiest assumption?",
    "depth": "deep",
})
# Extract reasoning conclusion for ISC refinement
```

## Architecture Role

**Core Layer** — Foundation of the agent reasoning stack. The `ThinkingAgent` uses
`ThinkingDepth` from `llm/models/reasoning.py` and `AgentRequest`/`AgentResponse` base
classes. Consumed by the PAI THINK phase capability selection.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Agent module PAI capabilities
- **Root Bridge**: [../../../../PAI.md](../../../../PAI.md) — Authoritative PAI system bridge doc
- **MCP Tools**: [mcp_tools.py](mcp_tools.py)
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
