# Getting Started with Agents

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

A comprehensive guide to how agentic operations are deployed, orchestrated, and integrated within the Codomyrmex ecosystem — spanning **15+ agent providers**, **130 Python modules**, **~474 MCP tools**, **81 PAI skills**, and **15 Antigravity workflows**.

---

## Agent Architecture Overview

Codomyrmex hosts a multi-layer agent system. Users interact through **IDEs** (Cursor, Antigravity, Claude Code) or the **CLI**. Requests flow through the **Agent Orchestrator** to provider-specific agents, which consume Codomyrmex modules via the **MCP Bridge** and **Trust Gateway**.

```mermaid
graph TB
    subgraph IDE["🖥️ IDE & CLI Layer"]
        direction LR
        CURSOR["Cursor IDE<br/>.cursorrules"]
        ANTIGRAV["Antigravity IDE<br/>.agent/workflows/"]
        CLAUDE_CODE["Claude Code<br/>~/.claude/skills/"]
        CLI["CLI<br/>uv run codomyrmex"]
    end

    subgraph ORCH["🎯 Agent Orchestrator"]
        direction TB
        CORE["core.py<br/>Strategy: best_match | round_robin | parallel"]
        SCHED["Scheduler<br/>cron + event triggers"]
        RESILIENCE["Resilience<br/>retry + circuit breaker"]
    end

    subgraph AGENTS["🤖 Agent Providers (15+)"]
        direction LR
        subgraph API_AGENTS["API-based"]
            CLAUDE["Claude"]
            CODEX["Codex"]
            O1["O1/O3"]
            DEEPSEEK["DeepSeek"]
            QWEN["Qwen"]
        end
        subgraph CLI_AGENTS["CLI-based"]
            JULES["Jules"]
            GEMINI["Gemini"]
            MISTRAL["Mistral Vibe"]
            EVERYCODE["Every Code"]
            OPENCODE["OpenCode"]
        end
        subgraph LOCAL_AGENTS["Local"]
            OLLAMA["Ollama"]
        end
    end

    subgraph INFRA["⚙️ Infrastructure"]
        direction TB
        TRUST["Trust Gateway<br/>3-tier security"]
        MCP["MCP Bridge<br/>JSON-RPC + stdio/HTTP"]
        EVENTS["EventBus<br/>phase transitions"]
    end

    subgraph MODULES["🐜 Codomyrmex (130 modules)"]
        direction LR
        SKILLS_MOD["Skills<br/>81 installed"]
        MEMORY_MOD["Agentic Memory<br/>rules + obsidian"]
        LLM_MOD["LLM Providers"]
        SEC_MOD["Security"]
        TELEM_MOD["Telemetry"]
    end

    IDE --> ORCH
    ORCH --> AGENTS
    AGENTS --> INFRA
    INFRA --> MODULES

    style IDE fill:#1a1a2e,stroke:#e94560,color:#e8e8e8
    style ORCH fill:#533483,stroke:#e94560,color:#e8e8e8
    style AGENTS fill:#0f3460,stroke:#533483,color:#e8e8e8
    style INFRA fill:#16213e,stroke:#0f3460,color:#e8e8e8
    style MODULES fill:#1a1a2e,stroke:#16213e,color:#e8e8e8
```

---

## 1. IDE Integrations

Codomyrmex meets agents where developers work — inside their IDEs. Each IDE surface has a distinct integration pattern:

```mermaid
graph LR
    subgraph Cursor["🖱️ Cursor IDE"]
        CR_RULES[".cursorrules<br/>75 per-module rule files"]
        CR_AGENT["Cursor Agent Mode<br/>file edits, terminal, search"]
    end

    subgraph Antigravity["🚀 Antigravity IDE"]
        AG_WORKFLOWS[".agent/workflows/<br/>15 workflow files"]
        AG_BRIDGE["AntigravityAgent<br/>agent_bridge.py"]
        AG_CLIENT["AntigravityClient<br/>HTTP client"]
        AG_ROUTER["Tool Router<br/>prompt → tool routing"]
    end

    subgraph ClaudeCode["🧠 Claude Code"]
        CC_SKILLS["~/.claude/skills/<br/>SKILL.md plugins"]
        CC_COMMANDS["~/.claude/commands/<br/>slash commands"]
        CC_MCP["MCP Server<br/>stdio transport"]
    end

    CR_RULES --> CR_AGENT
    AG_WORKFLOWS --> AG_BRIDGE
    AG_BRIDGE --> AG_CLIENT
    AG_CLIENT --> AG_ROUTER
    CC_SKILLS --> CC_MCP
    CC_COMMANDS --> CC_MCP
    CC_MCP --> |"JSON-RPC"| CDM["Codomyrmex<br/>Modules"]
    AG_ROUTER --> CDM
    CR_AGENT --> |"direct file access"| CDM

    style Cursor fill:#1a1a2e,stroke:#e94560,color:#e8e8e8
    style Antigravity fill:#533483,stroke:#e94560,color:#e8e8e8
    style ClaudeCode fill:#0f3460,stroke:#533483,color:#e8e8e8
```

### Cursor Integration

Cursor uses **`.cursorrules`** files (75 per-module rule files) to configure agent behavior per directory. Rules are resolved hierarchically — more specific rules override general ones.

```python
from codomyrmex.agentic_memory.rules import RuleEngine

engine = RuleEngine()
rules = engine.resolve("src/codomyrmex/agents/pai/trust_gateway.py")
print(f"{len(rules)} rules apply to this file")
```

### Antigravity Integration

Antigravity connects via HTTP through the `AntigravityAgent` adapter, which wraps the `AntigravityClient` for the `AgentOrchestrator`.

**15 installed workflows** (`.agent/workflows/`):

| Workflow | Purpose |
|----------|---------|
| `/codomyrmexAnalyze` | Deep project/file analysis |
| `/codomyrmexDocs` | Retrieve module documentation |
| `/codomyrmexMemory` | Add to agentic long-term memory |
| `/codomyrmexSearch` | Codebase regex search |
| `/codomyrmexStatus` | System health & PAI awareness |
| `/codomyrmexVerify` | Capability audit & trust promotion |
| `/codomyrmexTrust` | Destructive tool trust granting |
| `/codomyrmexWorktree` | Git worktree management |
| `/desloppify` | Codebase health & tech debt scan |
| `/gitnexus` | Repo analysis & knowledge graph |
| `/modernPython` | Modern Python best practices (uv, ruff, ty) |
| `/propertyBasedTesting` | Hypothesis-based property testing |
| `/securityAudit` | Trail of Bits-style security audit |
| `/systematicDebugging` | Root-cause investigation methodology |
| `/tdd` | Test-Driven Development workflow |

### Claude Code Integration

Claude Code consumes Codomyrmex through two mechanisms:

| Mechanism | Language | Discovery | Examples |
|-----------|----------|-----------|----------|
| **MCP Tools** | Python (`@mcp_tool`) | Auto-discovered via pkgutil | `data_visualization`, `git_analysis` |
| **External Skills** | Markdown (`SKILL.md`) | Loaded from `~/.claude/skills/` | `visual-explainer`, `Codomyrmex` |

**MCP server startup:**

```bash
uv run python scripts/model_context_protocol/run_mcp_server.py --transport stdio
```

---

## 2. Agent Providers

### Provider Taxonomy

```mermaid
graph TD
    ROOT["Agent Providers"] --> API["API-based<br/>(direct SDK)"]
    ROOT --> CLI_B["CLI-based<br/>(subprocess)"]
    ROOT --> LOCAL["Local<br/>(on-device)"]

    API --> CLAUDE_P["Claude<br/>Anthropic SDK"]
    API --> CODEX_P["Codex<br/>OpenAI SDK"]
    API --> O1_P["O1/O3<br/>OpenAI reasoning"]
    API --> DS_P["DeepSeek<br/>cost-effective"]
    API --> QW_P["Qwen<br/>multilingual"]

    CLI_B --> JULES_P["Jules<br/>simple & fast"]
    CLI_B --> GEMINI_P["Gemini<br/>Google · OAuth"]
    CLI_B --> MISTRAL_P["Mistral Vibe<br/>vibe CLI"]
    CLI_B --> EC_P["Every Code<br/>multi-agent"]
    CLI_B --> OC_P["OpenCode<br/>open-source"]
    CLI_B --> OW_P["OpenClaw<br/>open-source"]

    LOCAL --> OLLAMA_P["Ollama<br/>privacy-first<br/>zero cost"]

    style ROOT fill:#e94560,stroke:#1a1a2e,color:#fff
    style API fill:#533483,stroke:#1a1a2e,color:#fff
    style CLI_B fill:#0f3460,stroke:#1a1a2e,color:#fff
    style LOCAL fill:#16213e,stroke:#1a1a2e,color:#fff
```

### Core Agent Modules (`src/codomyrmex/agents/`)

| Agent | Type | Module Path | Best For |
|-------|------|-------------|----------|
| **Claude** | API | `agents/claude/` | High-quality reasoning, production use |
| **Codex** | API | `agents/codex/` | Code-focused OpenAI tasks |
| **O1/O3** | API | `agents/o1/` | Complex reasoning, chain-of-thought |
| **DeepSeek** | API | `agents/deepseek/` | Cost-effective code generation |
| **Qwen** | API | `agents/qwen/` | Multilingual code tasks |
| **Jules** | CLI | `agents/jules/` | Simple, fast command-based tasks |
| **Gemini** | CLI | `agents/gemini/` | Google ecosystem, file ops |
| **Mistral Vibe** | CLI | `agents/mistral_vibe/` | Mistral models via `vibe` CLI |
| **Every Code** | CLI | `agents/every_code/` | Multi-agent orchestration |
| **OpenCode** | CLI | `agents/opencode/` | Open-source alternative |
| **OpenClaw** | CLI | `agents/openclaw/` | Open-source code agent |
| **Droid** | CLI | `agents/droid/` | General-purpose code agent |
| **Aider** | CLI | `agents/aider/` | Aider-style code editing |
| **AgenticSeek** | — | `agents/agentic_seek/` | Autonomous task-seeking |
| **Pooling** | — | `agents/pooling/` | Multi-agent load balancing & failover |

### Capability Matrix

| Capability | Claude | O1 | DeepSeek | Gemini | Every Code | Ollama |
|:-----------|:------:|:--:|:--------:|:------:|:----------:|:------:|
| Extended Reasoning | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Multi-agent | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
| Browser Integration | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ |
| File Operations | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ |
| Session Management | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ |
| Local / No API Cost | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |

### Discovery & Verification

```bash
# Check which agents are operative on this machine
uv run python -m codomyrmex.agents.agent_setup --status-only
```

---

## 3. Orchestration

### Agent Orchestrator (`src/codomyrmex/orchestrator/`)

The orchestrator manages multi-agent workflows with scheduling, resilience, and observability.

```mermaid
sequenceDiagram
    participant U as User / IDE
    participant O as AgentOrchestrator
    participant S as Scheduler
    participant A1 as Agent (Claude)
    participant A2 as Agent (Gemini)
    participant R as Resilience Layer
    participant T as Trust Gateway

    U->>O: execute(task, strategy="best_match")
    O->>S: check triggers / schedule
    S-->>O: ready

    alt best_match strategy
        O->>A1: dispatch(task)
        A1->>T: invoke MCP tool
        T-->>A1: result
        A1-->>O: response
    else parallel strategy
        par
            O->>A1: dispatch(task)
            A1-->>O: response_1
        and
            O->>A2: dispatch(task)
            A2-->>O: response_2
        end
        O->>O: merge responses
    end

    alt failure
        O->>R: retry / circuit_breaker
        R->>A1: retry with backoff
        A1-->>O: recovered response
    end

    O-->>U: final result
```

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

## 4. PAI Integration

### The Algorithm — 7-Phase Pipeline

PAI (Personal AI Infrastructure) executes a 7-phase pipeline on every Claude Code prompt. Each phase maps to specific Codomyrmex modules:

```mermaid
flowchart LR
    O["👁 OBSERVE"] --> T["🧠 THINK"]
    T --> P["📋 PLAN"]
    P --> B["🔨 BUILD"]
    B --> E["⚡ EXECUTE"]
    E --> V["✓ VERIFY"]
    V --> L["📚 LEARN"]

    O -..->|"list_modules<br/>list_directory"| CDM1["Codomyrmex"]
    T -..->|"analyze_python<br/>search_codebase"| CDM2["Codomyrmex"]
    P -..->|"read_file<br/>json_query"| CDM3["Codomyrmex"]
    B -..->|"write_file"| CDM4["Codomyrmex"]
    E -..->|"run_command<br/>run_tests"| CDM5["Codomyrmex"]
    V -..->|"git_status<br/>checksum_file"| CDM6["Codomyrmex"]
    L -..->|"pai_awareness<br/>agentic_memory"| CDM7["Codomyrmex"]

    style O fill:#e94560,stroke:#1a1a2e,color:#fff
    style T fill:#533483,stroke:#1a1a2e,color:#fff
    style P fill:#0f3460,stroke:#1a1a2e,color:#fff
    style B fill:#16213e,stroke:#1a1a2e,color:#fff
    style E fill:#0f3460,stroke:#1a1a2e,color:#fff
    style V fill:#533483,stroke:#1a1a2e,color:#fff
    style L fill:#e94560,stroke:#1a1a2e,color:#fff
```

### PAI Bridge Components (`src/codomyrmex/agents/pai/`)

| Component | File | Purpose |
|-----------|------|---------|
| **PAI Bridge** | `pai_bridge.py` | Discovery, validation — reads PAI's filesystem (read-only) |
| **Trust Gateway** | `trust_gateway.py` | 3-tier security gating for tool execution |
| **MCP Bridge** | `mcp_bridge.py` | JSON-RPC protocol for tool invocation |
| **MCP Discovery** | `mcp/discovery.py` | Auto-discovers 130 modules with `mcp_tools.py` |
| **PAI Webhook** | `pai_webhook.py` | FastAPI router for bidirectional PAI ↔ Codomyrmex |
| **PAI Client** | `pai_client.py` | HTTP client to push events to PAI |

### Trust Gateway

The 3-tier trust model gates destructive operations behind explicit approval:

```mermaid
stateDiagram-v2
    [*] --> UNTRUSTED: All tools start here
    UNTRUSTED --> VERIFIED: /codomyrmexVerify
    VERIFIED --> TRUSTED: /codomyrmexTrust

    state UNTRUSTED {
        [*] --> Blocked
        Blocked: Cannot execute anything
    }

    state VERIFIED {
        [*] --> SafeOps
        SafeOps: 18 safe tools promoted
        SafeOps: read_file, list_directory
        SafeOps: analyze_python, git_status
        SafeOps: search_codebase, json_query
    }

    state TRUSTED {
        [*] --> FullAccess
        FullAccess: 5 destructive tools enabled
        FullAccess: write_file
        FullAccess: run_command
        FullAccess: run_tests
        FullAccess: call_module_function
    }
```

### Deployment Sequence

```mermaid
sequenceDiagram
    participant U as User
    participant CC as Claude Code
    participant PAI as PAI Algorithm
    participant MCP as MCP Bridge
    participant CDM as Codomyrmex
    participant DB as Dashboard

    U->>CC: Prompt
    CC->>PAI: Invoke Algorithm
    PAI->>PAI: OBSERVE → THINK → PLAN
    PAI->>MCP: call_tool("codomyrmex.X")
    MCP->>MCP: Trust Gateway check
    MCP->>CDM: Execute tool
    CDM-->>MCP: Result
    MCP-->>PAI: Response
    PAI->>PAI: BUILD → EXECUTE → VERIFY → LEARN
    PAI-->>CC: Completed work
    CC-->>U: Response

    Note over DB: Dashboard runs at :8888
    U->>DB: Browse http://localhost:8888
    DB-->>U: 14-tab interface
```

---

## 5. MCP Tool Integration

Every module exposes functionality through `mcp_tools.py` files. **130 modules** provide **~474 dynamically-discovered tools** plus 20 static tools.

```mermaid
pie title MCP Tool Distribution (~447 Total)
    "Auto-Discovered (dynamic)" : 407
    "Core Static Tools" : 17
    "Universal Proxy Tools" : 3
    "Maintenance Tools" : 2
    "Email (AgentMail)" : 8
    "Calendar (Google)" : 5
    "Email (Gmail)" : 4
```

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

## 6. Skills System

### Two Extension Mechanisms

```mermaid
graph LR
    subgraph MCP_TOOLS["MCP Tools (Python)"]
        direction TB
        DECORATOR["@mcp_tool decorator"]
        DISCOVERY["pkgutil auto-discovery"]
        TRUST_CHECK["Trust Gateway enforced"]
    end

    subgraph EXT_SKILLS["External Skills (Markdown)"]
        direction TB
        SKILL_MD["SKILL.md files"]
        SKILLS_DIR["~/.claude/skills/"]
        NO_TRUST["No trust check needed"]
    end

    MCP_TOOLS -->|"runs Python in<br/>codomyrmex process"| CDM["Codomyrmex<br/>MCP Server"]
    EXT_SKILLS -->|"guides Claude's<br/>own generation"| CC["Claude Code<br/>Session"]

    style MCP_TOOLS fill:#0f3460,stroke:#533483,color:#e8e8e8
    style EXT_SKILLS fill:#533483,stroke:#e94560,color:#e8e8e8
```

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

### Installed External Skills

Skills are also accessible as **Claude Code plugins** via `~/.claude/skills/` and as **Antigravity workflows** via `.agent/workflows/`.

| Skill | Source | Version | Slash Commands |
|-------|--------|---------|---------------|
| **visual-explainer** | [nicobailon/visual-explainer](https://github.com/nicobailon/visual-explainer) | v0.4.4 | `/generate-web-diagram`, `/generate-visual-plan`, `/generate-slides`, `/diff-review`, `/plan-review`, `/project-recap`, `/fact-check` |
| **Codomyrmex** | This repo | v1.1.9 | `/codomyrmexVerify`, `/codomyrmexTrust`, `/codomyrmexAnalyze`, `/codomyrmexSearch`, `/codomyrmexDocs`, `/codomyrmexStatus`, `/codomyrmexMemory` |

---

## 7. Agentic Memory

### Memory Architecture

```mermaid
graph TB
    subgraph MEMORY["🧠 Agentic Memory"]
        direction TB
        RULES["Rule Engine<br/>75 .cursorrules files"]
        OBSIDIAN["Obsidian Vault<br/>persistent knowledge"]
        LT["Long-Term Memory<br/>TTL · tagging · cross-session"]
        METHODS["Retrieval Methods<br/>recency · relevance · importance"]
    end

    RULES -->|"per-module<br/>behavior rules"| AGENT["Agent"]
    OBSIDIAN -->|"knowledge<br/>retrieval"| AGENT
    LT -->|"cross-session<br/>context"| AGENT
    METHODS --> LT

    AGENT -->|"writes"| LT
    AGENT -->|"writes"| OBSIDIAN

    style MEMORY fill:#1a1a2e,stroke:#e94560,color:#e8e8e8
```

```python
from codomyrmex.agentic_memory.rules import RuleEngine

engine = RuleEngine()
rules = engine.resolve("src/codomyrmex/agents/pai/trust_gateway.py")
print(f"{len(rules)} rules apply to this file")
```

| Component | Purpose |
|-----------|---------|
| `rules/` | 75 `.cursorrules` files governing agent behavior per module |
| `obsidian/` | Obsidian vault integration for persistent knowledge |
| `long_term/` | Long-term memory with TTL, tagging, cross-session retrieval |
| `methods/` | Memory retrieval strategies (recency, relevance, importance) |

---

## 8. Event-Driven Agent Communication

### EventBus (`src/codomyrmex/events/core/event_bus.py`)

Agents communicate through the EventBus for phase transitions, tool results, and status updates.

```mermaid
flowchart LR
    subgraph Publishers["Publishers"]
        AGENT_PUB["Agent"]
        PAI_PUB["PAI Bridge"]
        ORCH_PUB["Orchestrator"]
    end

    BUS["EventBus<br/>(singleton)"]

    subgraph Subscribers["Subscribers"]
        TELEM_SUB["Telemetry"]
        MEMORY_SUB["Memory"]
        DASH_SUB["Dashboard"]
    end

    AGENT_PUB -->|"agent.task_complete"| BUS
    PAI_PUB -->|"pai.phase_transition"| BUS
    ORCH_PUB -->|"orchestrator.dispatch"| BUS

    BUS -->|"on()"| TELEM_SUB
    BUS -->|"on()"| MEMORY_SUB
    BUS -->|"on()"| DASH_SUB

    style Publishers fill:#0f3460,stroke:#533483,color:#e8e8e8
    style BUS fill:#e94560,stroke:#1a1a2e,color:#fff
    style Subscribers fill:#533483,stroke:#e94560,color:#e8e8e8
```

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

## 9. Secret Management for Agents

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

## 10. Agent Diagnostics

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
| Discover agents | `uv run python -m codomyrmex.agents.agent_setup --status-only` |
| Start MCP server | `uv run python scripts/model_context_protocol/run_mcp_server.py --transport stdio` |

---

## See Also

- [Tutorials](tutorials/README.md) — Step-by-step guides including MCP tools and testing
- [setup.md](setup.md) — Installation and environment configuration
- [quickstart.md](quickstart.md) — 5-minute quick start
- [Agent Comparison](../../docs/modules/agents/AGENT_COMPARISON.md) — Detailed provider comparison with decision matrix
- [PAI docs](../../docs/pai/README.md) — Full PAI-Codomyrmex integration docs (architecture, tools, workflows)
- [Agent Module docs](../../docs/modules/agents/README.md) — Agent module exports, testing, and directory structure
- [PAI.md](PAI.md) — Personal AI context for this directory
- [AGENTS.md](AGENTS.md) — Agent guidelines for this directory
