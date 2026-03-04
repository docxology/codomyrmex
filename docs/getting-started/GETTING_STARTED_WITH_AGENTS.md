# Getting Started with Agents

**Version**: v1.1.0 | **Status**: Active | **Last Updated**: March 2026

A comprehensive guide to how agentic operations are deployed, orchestrated, and integrated within the Codomyrmex ecosystem.

---

## Agent Architecture Overview

Codomyrmex hosts a multi-layer agent system spanning **13+ agent modules**, an **orchestration engine**, **81 PAI skills**, and **424 dynamically-discovered MCP tools**.

```text
┌─────────────────────────────────────────────────┐
│               User / IDE / CLI                  │
├─────────────────────────────────────────────────┤
│          Agent Orchestrator (core.py)           │
│   ┌──────┬──────┬─────┬──────┬──────┬────────┐  │
│   │Claude│Gemini│GPT  │Droid │Aider │Antigrav│  │
│   │Agent │Agent │Agent│Agent │Agent │Agent   │  │
│   └──┬───┴──┬───┴──┬──┴──┬───┴──┬───┴──┬─────┘  │
│      └──────┴──────┴─────┴──────┴──────┘         │
│         PAI Trust Gateway (299 tools)            │
│         MCP Bridge (JSON-RPC protocol)           │
│         EventBus (phase transitions)             │
├─────────────────────────────────────────────────┤
│  Skills │ Memory │ Telemetry │ Security │ LLM   │
└─────────────────────────────────────────────────┘
```

---

## 1. Agent Modules

### Core Agents (`src/codomyrmex/agents/`)

| Agent | Module Path | Description |
|-------|-------------|-------------|
| **Claude** | `agents/claude/` | Anthropic Claude integration via `anthropic` SDK |
| **Gemini** | `agents/gemini/` | Google Gemini integration via `google-generativeai` |
| **GPT** | `agents/gpt/` | OpenAI GPT integration via `openai` SDK |
| **Droid** | `agents/droid/` | General-purpose code agent |
| **Aider** | `agents/aider/` | Aider-style code editing agent |
| **AgenticSeek** | `agents/agentic_seek/` | Autonomous task-seeking agent |
| **EveryCode** | `agents/every_code/` | Code generation across languages |
| **MistralVibe** | `agents/mistral_vibe/` | Mistral model integration |
| **OpenClaw** | `agents/openclaw/` | Open-source code agent |
| **Pooling** | `agents/pooling/` | Multi-agent response pooling |
| **Cursor** | `agents/cursor/` | Cursor IDE integration |

### IDE Integration (`src/codomyrmex/ide/`)

| Component | File | Description |
|-----------|------|-------------|
| **AntigravityAgent** | `ide/antigravity/agent_bridge.py` | Adapts AntigravityClient for AgentOrchestrator |
| **AntigravityClient** | `ide/antigravity/client.py` | HTTP client for Antigravity IDE |
| **Tool Router** | `ide/antigravity/tool_router.py` | Routes prompts to specific Antigravity tools |

### PAI Bridge (`src/codomyrmex/agents/pai/`)

| Component | File | Purpose |
|-----------|------|---------|
| **Trust Gateway** | `trust_gateway.py` | 299 verified tools (295 safe, 4 destructive) |
| **MCP Bridge** | `mcp_bridge.py` | JSON-RPC protocol for tool invocation |
| **MCP Discovery** | `mcp/discovery.py` | Auto-discovers 126 modules with `mcp_tools.py` |
| **PAI Webhook** | `pai_webhook.py` | FastAPI router for bidirectional PAI ↔ Codomyrmex |
| **PAI Client** | `pai_client.py` | HTTP client to push events to PAI |

---

## 2. Orchestration

### Agent Orchestrator (`src/codomyrmex/orchestrator/`)

The orchestrator manages multi-agent workflows, scheduling, resilience, and observability.

```python
from codomyrmex.orchestrator.core import AgentOrchestrator

orchestrator = AgentOrchestrator()

# Register agents
orchestrator.register_agent("claude", claude_agent)
orchestrator.register_agent("gemini", gemini_agent)

# Execute a task with automatic agent selection
result = orchestrator.execute(
    task="Refactor the validation module",
    strategy="best_match",  # or "round_robin", "parallel"
)
```

**Key submodules:**

| Submodule | Purpose |
|-----------|---------|
| `execution/` | `async_runner.py`, `parallel_runner.py` — concurrent agent execution |
| `resilience/` | `retry_engine.py`, `agent_circuit_breaker.py` — fault tolerance |
| `scheduler/` | `scheduler.py`, `triggers.py` — cron/event-based scheduling |
| `workflows/` | `workflow_engine.py`, `workflow_journal.py` — multi-step pipelines |
| `observability/` | `orchestrator_events.py`, `reporting.py` — audit trail |

---

## 3. MCP Tool Integration

Every module exposes functionality through `mcp_tools.py` files. **127 modules** provide **424 dynamically-discovered tools**.

### Using MCP Tools

```python
from codomyrmex.agents.pai.mcp_bridge import get_tool_registry

registry = get_tool_registry()
tools = registry.list_tools()
print(f"{len(tools)} tools available")

# Invoke a tool
result = registry.invoke("analyze_code", {"file_path": "src/module.py"})
```

### Creating MCP Tools

```python
from codomyrmex.model_context_protocol import mcp_tool

@mcp_tool(
    name="my_analyzer",
    description="Analyze code quality",
    deprecated_in=None,  # Set to version string to mark deprecated
)
def my_analyzer(file_path: str) -> dict:
    """Analyze code quality for the given file."""
    return {"file": file_path, "score": 95}
```

### Deprecation Timeline

```python
from codomyrmex.model_context_protocol.mcp_deprecation import get_deprecation_summary

summary = get_deprecation_summary()
print(f"{summary['total_deprecated']} tools deprecated")
for version, count in summary['by_version'].items():
    print(f"  v{version}: {count} tools")
```

---

## 4. Skills System

### PAI Skills (`src/codomyrmex/skills/`)

**81 installed skills** provide reusable, versioned capabilities.

```python
from codomyrmex.skills.skills_manager import SkillsManager

manager = SkillsManager()
skills = manager.list_skills()

# Execute a skill
result = manager.execute_skill("code_review", {
    "file_path": "src/codomyrmex/agents/pai/trust_gateway.py",
    "review_depth": "thorough",
})
```

Skills are also accessible as **Claude Code plugins** via `.claude/skills/` and as **Antigravity workflows** via `.agent/workflows/`.

---

## 5. Agentic Memory

### Memory Architecture (`src/codomyrmex/agentic_memory/`)

| Component | Purpose |
|-----------|---------|
| `rules/` | 75 `.cursorrules` files governing agent behavior per module |
| `obsidian/` | Obsidian vault integration for persistent knowledge |
| `long_term/` | Long-term memory with TTL, tagging, cross-session retrieval |
| `methods/` | Memory retrieval strategies (recency, relevance, importance) |

### Rule Engine

```python
from codomyrmex.agentic_memory.rules import RuleEngine

engine = RuleEngine()
rules = engine.resolve("src/codomyrmex/agents/pai/trust_gateway.py")
print(f"{len(rules)} rules apply to this file")
```

---

## 6. Agent Diagnostics

### CLI Doctor

```bash
# Quick check
uv run codomyrmex doctor

# Full diagnostic
uv run codomyrmex doctor --all

# Auto-fix issues
uv run codomyrmex doctor --fix

# JSON output for CI
uv run codomyrmex doctor --all --json
```

### PAI Health

```python
from codomyrmex.agents.pai.pai_client import PAIClient

client = PAIClient(base_url="http://localhost:8080")
health = client.check_health()
print(health)  # {"status": "ok", "events_received": 42, ...}
```

---

## 7. Event-Driven Agent Communication

### EventBus (`src/codomyrmex/events/core/event_bus.py`)

Agents communicate through the EventBus for phase transitions, tool results, and status updates.

```python
from codomyrmex.events.core.event_bus import EventBus

bus = EventBus.get_default()

# Listen for PAI events
bus.on("pai.phase_transition", lambda event: print(f"Phase: {event}"))

# Emit agent events
bus.emit("agent.task_complete", {"agent": "claude", "task_id": "abc123"})
```

### PAI Webhook Integration

```python
from codomyrmex.agents.pai.pai_client import PAIClient

client = PAIClient()

# Notify PAI of phase transition
client.send_phase_transition("Assessment", "Action")

# Report tool execution result
client.send_tool_result("analyze_code", {"files": 42, "issues": 3})
```

---

## 8. Secret Management for Agents

API keys, tokens, and credentials used by agents are managed through `SecretManager`:

```python
from codomyrmex.config_management.secrets.secret_manager import SecretManager

sm = SecretManager()

# Store an API key
key_id = sm.store_secret("OPENAI_API_KEY", "sk-...")

# Rotate a key
event = sm.rotate_secret("OPENAI_API_KEY", "sk-new-...")
print(f"Rotated: {event['previous_id']} → {event['new_id']}")

# Check staleness
age = sm.check_key_age("OPENAI_API_KEY", max_age_days=90)
if age["stale"]:
    print(f"⚠️ Key is {age['age_days']} days old — rotate!")
```

---

## Quick Reference

| What | Command / Import |
|------|-----------------|
| Run diagnostics | `uv run codomyrmex doctor --all` |
| List MCP tools | `from codomyrmex.agents.pai.mcp_bridge import get_tool_registry` |
| Execute orchestrated task | `from codomyrmex.orchestrator.core import AgentOrchestrator` |
| PAI health check | `from codomyrmex.agents.pai.pai_client import PAIClient` |
| Resolve rules for file | `from codomyrmex.agentic_memory.rules import RuleEngine` |
| Manage secrets | `from codomyrmex.config_management.secrets.secret_manager import SecretManager` |
| List skills | `from codomyrmex.skills.skills_manager import SkillsManager` |
| Deprecation timeline | `from codomyrmex.model_context_protocol.mcp_deprecation import get_deprecation_summary` |

---

## See Also

- [Tutorials](tutorials/README.md) — Step-by-step guides including MCP tools and testing
- [setup.md](setup.md) — Installation and environment configuration
- [quickstart.md](quickstart.md) — 5-minute quick start
- [PAI.md](PAI.md) — Personal AI context for this directory
- [AGENTS.md](AGENTS.md) — Agent guidelines for this directory
