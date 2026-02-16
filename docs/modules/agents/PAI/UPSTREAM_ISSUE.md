# Codomyrmex × PAI: Bidirectional Integration Showcase

> **This is an ideation / sharing issue, not a bug report.** Codomyrmex has built a comprehensive integration with PAI and we wanted to share how the two systems complement each other, in the spirit of PAI's open community.

---

## What is Codomyrmex?

[**Codomyrmex**](https://github.com/docxology/codomyrmex) is an open-source, modular Python workspace for AI-assisted development. It exposes **100+ modules** spanning code analysis, testing, documentation, security, LLM orchestration, and infrastructure — all accessible via the **Model Context Protocol (MCP)**.

Repository: [`github.com/docxology/codomyrmex`](https://github.com/docxology/codomyrmex)

---

## How Codomyrmex Uses PAI

Codomyrmex implements a **bidirectional bridge** with PAI through three integration layers:

### 1. PAIBridge — Discovery Layer

[`src/codomyrmex/agents/pai/pai_bridge.py`](https://github.com/docxology/codomyrmex/blob/main/src/codomyrmex/agents/pai/pai_bridge.py)

- **Filesystem-based discovery** of every PAI subsystem — Skills, Tools, Hooks, Agents, Memory, TELOS, Security
- Encodes all **16 PAI Principles** as constants
- Embeds **The Algorithm v0.2.25** phases (Observe → Think → Plan → Build → Execute → Verify → Learn)
- Maps all **3 Response Depth Levels** (FULL, ITERATION, MINIMAL)

```python
from codomyrmex.agents.pai import PAIBridge

bridge = PAIBridge()
bridge.get_status()           # Full PAI inventory
bridge.list_skills()          # Skill packs (CORE, Agents, Art, Browser, ...)
bridge.get_telos_files()      # 10 TELOS identity files
bridge.list_hooks()           # Active & archived hooks
bridge.list_memory_stores()   # Three-tier memory (STATE/LEARNING/HISTORY)
bridge.get_security_config()  # Security policies
```

### 2. MCPBridge — Communication Layer

[`src/codomyrmex/agents/pai/mcp_bridge.py`](https://github.com/docxology/codomyrmex/blob/main/src/codomyrmex/agents/pai/mcp_bridge.py)

- Exposes **all Codomyrmex modules as MCP tools** that PAI agents can call
- 15 static core tools + 85+ dynamically discovered tools
- Generates a **PAI-compatible skill manifest** with Algorithm phase mapping:

```
OBSERVE → list_modules, module_info, list_directory
THINK   → analyze_python, search_codebase
PLAN    → read_file, json_query
BUILD   → write_file
EXECUTE → run_command, run_tests
VERIFY  → git_status, git_diff, checksum_file
LEARN   → pai_awareness, pai_status
```

### 3. TrustGateway — Security Layer

[`src/codomyrmex/agents/pai/trust_gateway.py`](https://github.com/docxology/codomyrmex/blob/main/src/codomyrmex/agents/pai/trust_gateway.py)

- Three-tier trust model: **UNTRUSTED → VERIFIED → TRUSTED**
- Integrates with PAI's Security System principle
- Destructive tools (write, execute, delete) require explicit user promotion
- Persistent trust ledger at `~/.codomyrmex/trust_ledger.json`

---

## How They Complement Each Other

```
┌─────────────────────────────────┐     ┌─────────────────────────────────┐
│           PAI                   │     │        Codomyrmex               │
│                                 │     │                                 │
│  TELOS  ──────────────────────────────▶ PAIBridge (discovers purpose)   │
│  Algorithm ───────────────────────────▶ ClaudeClient (execution engine) │
│  Skill System ────────────────────────▶ MCPBridge (capability routing)  │
│  Hook System ─────────────────────────▶ Lifecycle integration           │
│  Security ────────────────────────────▶ TrustGateway (enforcement)      │
│                                 │     │                                 │
│  Skill Catalog ◀──────────────────────── get_skill_manifest()           │
│  Memory System ◀──────────────────────── Session observations           │
│  Agent Personalities ◀────────────────── Specialized adapters           │
│                                 │     │                                 │
└─────────────────────────────────┘     └─────────────────────────────────┘
```

| PAI Provides | Codomyrmex Provides |
|:---|:---|
| Goal-oriented execution (TELOS + Algorithm) | Industrial module ecosystem (100+ capabilities) |
| Identity and personality system | MCP-based tool server |
| Three-tier memory (hot/warm/cold) | Code analysis, testing, documentation |
| Hook-driven lifecycle management | Trust-gated, secure tool execution |
| Skill routing and management | Algorithm-mapped capability catalog |

---

## PAI Principles We Align With

| # | PAI Principle | How Codomyrmex Implements It |
|:---:|:---|:---|
| 1 | User Centricity | TELOS integration — all operations are goal-informed |
| 5 | Deterministic Infrastructure | Zero-Mock testing policy — all tests use real functions |
| 6 | Code Before Prompts | Direct `call_tool()` Python API bypasses prompts/MCP |
| 7 | Spec / Test / Evals First | SPEC.md + pytest at every module level |
| 8 | UNIX Philosophy | Each of 100+ modules does one thing well |
| 12 | Skill Management | Full PAI skill manifest with Algorithm phase mapping |

---

## Documentation Suite

We've created a **10-document guide** for the integration:

| Document | Content |
|:---|:---|
| [README](https://github.com/docxology/codomyrmex/blob/main/docs/modules/agents/PAI/README.md) | Bidirectional architecture, principle mapping |
| [ARCHITECTURE](https://github.com/docxology/codomyrmex/blob/main/docs/modules/agents/PAI/ARCHITECTURE.md) | Three-layer technical deep dive |
| [ALGORITHM](https://github.com/docxology/codomyrmex/blob/main/docs/modules/agents/PAI/ALGORITHM.md) | The Algorithm v0.2.25 integration |
| [SKILLS](https://github.com/docxology/codomyrmex/blob/main/docs/modules/agents/PAI/SKILLS.md) | Skill System architecture |
| [TELOS](https://github.com/docxology/codomyrmex/blob/main/docs/modules/agents/PAI/TELOS.md) | Deep Goal Understanding |
| [HOOKS](https://github.com/docxology/codomyrmex/blob/main/docs/modules/agents/PAI/HOOKS.md) | Hook System integration |
| [WORKFLOWS](https://github.com/docxology/codomyrmex/blob/main/docs/modules/agents/PAI/WORKFLOWS.md) | Workflows & Dispatch |
| [FLOWS](https://github.com/docxology/codomyrmex/blob/main/docs/modules/agents/PAI/FLOWS.md) | Mermaid sequence diagrams |
| [SIGNPOSTS](https://github.com/docxology/codomyrmex/blob/main/docs/modules/agents/PAI/SIGNPOSTS.md) | Line-level code pointers |
| [AGENTS](https://github.com/docxology/codomyrmex/blob/main/docs/modules/agents/PAI/AGENTS.md) | Agent coordination guide |

---

## Why We're Sharing This

PAI's vision — **"AI should magnify everyone, not just the top 1%"** — resonates deeply with Codomyrmex's goal of making industrial-strength development tools accessible to AI agents. We see PAI as the **purpose layer** (who you are, what you want) and Codomyrmex as the **capability layer** (what you can do, how you do it).

Together, they create a system where:

1. **TELOS defines the goal** → Algorithm sequences the work → Codomyrmex provides the tools → Memory captures the learning
2. Every tool call is **trust-gated** — destructive operations require explicit user approval
3. The integration is **bidirectional** — PAI routes to Codomyrmex skills, Codomyrmex discovers PAI state

We'd love to hear thoughts from the PAI community on:

- Tighter integration opportunities (e.g., native PAI skill pack for Codomyrmex)
- Memory system interoperability patterns
- Algorithm phase extensions for domain-specific workflows

---

**Codomyrmex v0.1.1** | [Repository](https://github.com/docxology/codomyrmex) | [PAI Integration Docs](https://github.com/docxology/codomyrmex/tree/main/docs/modules/agents/PAI)
