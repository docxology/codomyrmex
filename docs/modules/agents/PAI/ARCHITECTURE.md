# PAI Architecture Deep Dive

This document provides a rigorous technical exploration of how Codomyrmex implements the bidirectional bridge with [Daniel Miessler's PAI](https://github.com/danielmiessler/Personal_AI_Infrastructure).

---

## Three-Layer Architecture

The integration is composed of three distinct layers, each with a clear responsibility:

```mermaid
graph TD
    subgraph L1["Layer 1: Discovery (PAIBridge)"]
        direction LR
        A1["PAIConfig<br/>(Path layout)"]
        A2["PAIBridge<br/>(Filesystem inspection)"]
        A3["Data Classes<br/>(PAISkillInfo · PAIToolInfo · etc.)"]
        A1 --> A2
        A2 --> A3
    end

    subgraph L2["Layer 2: Communication (MCPBridge)"]
        direction LR
        B1["Static Tool Registry<br/>(15 core tools)"]
        B2["Dynamic Discovery<br/>(@mcp_tool + auto-scan)"]
        B3["MCP Server<br/>(stdio / HTTP)"]
        B1 --> B3
        B2 --> B3
    end

    subgraph L3["Layer 3: Security (TrustGateway)"]
        direction LR
        C1["TrustLevel Enum<br/>(UNTRUSTED · VERIFIED · TRUSTED)"]
        C2["TrustRegistry<br/>(Persistent ledger)"]
        C3["trusted_call_tool<br/>(Gated execution)"]
        C1 --> C2
        C2 --> C3
    end

    L1 ==>|"Discovers PAI state"| L2
    L2 ==>|"Registers tools"| L3
    L3 ==>|"Gates execution"| L2
```

---

## Layer 1: PAIBridge (Discovery)

**Source**: [pai_bridge.py](../../../src/codomyrmex/agents/pai/pai_bridge.py)

The PAIBridge treats the **filesystem as the single source of truth**. It performs zero network calls — every discovery operation is a real `Path.is_file()` / `Path.iterdir()` call against the user's local `~/.claude/` directory.

### PAIConfig: The Path Layout

The `PAIConfig` dataclass ([L49-127](../../../src/codomyrmex/agents/pai/pai_bridge.py)) defines the entire PAI filesystem topology:

```mermaid
graph TD
    ROOT["~/.claude/"]
    ROOT --> SKILLS["skills/<br/>(Skill packs: CORE, Agents, Art, Browser)"]
    ROOT --> AGENTS_DIR["agents/<br/>(Personality .md files)"]
    ROOT --> MEMORY["MEMORY/<br/>(Three-tier: STATE, LEARNING, HISTORY)"]
    ROOT --> HOOKS["hooks/<br/>(Lifecycle event handlers)"]
    ROOT --> USER["USER/<br/>(TELOS: 10 identity files)"]
    ROOT --> SETTINGS["settings.json"]
    ROOT --> DESKTOP["claude_desktop_config.json<br/>(MCP server registrations)"]

    SKILLS --> PAI["PAI/<br/>(The core PAI skill)"]
    PAI --> SKILL_MD["SKILL.md<br/>(The Algorithm v0.2.25)"]
    PAI --> TOOLS["Tools/<br/>(Bun/TS CLI tools)"]
    PAI --> COMPONENTS["Components/<br/>(Algorithm sub-components)"]
    PAI --> SECURITY_DIR["PAISECURITYSYSTEM/<br/>(Security policies)"]
```

### What PAIBridge Discovers

| Method | PAI Upstream Concept | What It Returns |
|:---|:---|:---|
| `is_installed()` | PAI presence check | `bool` — does `SKILL.md` exist? |
| `get_status()` | Full system inventory | Dict with all components and settings |
| `get_algorithm_version()` | The Algorithm version | Parses version from `SKILL.md` (e.g., `"v0.2.25"`) |
| `get_algorithm_phases()` | 7-phase protocol | `OBSERVE → THINK → PLAN → BUILD → EXECUTE → VERIFY → LEARN` |
| `get_principles()` | 16 PAI Principles | From User Centricity to Permission to Fail |
| `list_skills()` | Skill System | All subdirectories of `~/.claude/skills/` with `SKILL.md` |
| `list_tools()` | PAI Tools | All `.ts` files in `PAI/Tools/` |
| `list_hooks()` | Hook System | All `.hook.*` files, with archived flag |
| `list_agents()` | Agent Personalities | All `.md` files in `~/.claude/agents/` |
| `list_memory_stores()` | Memory System | All subdirectories of `MEMORY/` with item counts |
| `get_telos_files()` | TELOS (Deep Goal Understanding) | 10 identity files: MISSION, GOALS, BELIEFS, etc. |
| `get_security_config()` | Security System | Policy files and patterns from `PAISECURITYSYSTEM/` |
| `get_pai_env()` | Environment variables | `PAI_DIR`, `PAI_CONFIG_DIR`, etc. |
| `has_codomyrmex_mcp()` | MCP registration | Checks if Codomyrmex is registered in Desktop config |

---

## Layer 2: MCPBridge (Communication)

**Source**: [mcp_bridge.py](../../../src/codomyrmex/agents/pai/mcp_bridge.py)

This layer transforms Codomyrmex from a Python library into a **remotely-callable service** that any PAI agent can use.

### Static Core Tools (15)

These are hardcoded in `_TOOL_DEFINITIONS` ([L275-512](../../../src/codomyrmex/agents/pai/mcp_bridge.py)):

| Tool Name | Category | Description |
|:---|:---|:---|
| `codomyrmex.read_file` | File I/O | Read file contents with metadata |
| `codomyrmex.write_file` | File I/O | Write content to a file |
| `codomyrmex.list_directory` | File I/O | List directory contents with filtering |
| `codomyrmex.analyze_python` | Code Analysis | Analyze Python file structure and metrics |
| `codomyrmex.search_codebase` | Code Analysis | Regex search across code files |
| `codomyrmex.git_status` | Git | Repository status |
| `codomyrmex.git_diff` | Git | Staged/unstaged diff |
| `codomyrmex.run_command` | Shell | Safe shell command execution |
| `codomyrmex.json_query` | Data | JSON file query via dot-notation |
| `codomyrmex.checksum_file` | Data | File checksum (md5/sha1/sha256) |
| `codomyrmex.list_modules` | Discovery | All available Codomyrmex modules |
| `codomyrmex.module_info` | Discovery | Module docstring, exports, path |
| `codomyrmex.pai_status` | PAI | PAI installation status and components |
| `codomyrmex.pai_awareness` | PAI | Missions, projects, tasks, TELOS, memory |
| `codomyrmex.run_tests` | Testing | Run pytest for a module or whole project |

### Universal Module Proxy (3 meta-tools)

These three tools give PAI agents **unlimited access** to every public function in every Codomyrmex module:

| Tool | Purpose |
|:---|:---|
| `codomyrmex.list_module_functions` | Introspect any module's public API |
| `codomyrmex.call_module_function` | Call any public function by path |
| `codomyrmex.get_module_readme` | Read any module's README/SPEC |

### Dynamic Discovery Engine

The `_discover_dynamic_tools()` function ([L637-684](../../../src/codomyrmex/agents/pai/mcp_bridge.py)) performs two-phase scanning:

```mermaid
flowchart TD
    START([Dynamic Discovery]) --> PHASE1["Phase 1: Scan @mcp_tool decorators"]
    PHASE1 --> TARGETS["13 targeted modules<br/>(visualization, llm, security, etc.)"]
    TARGETS --> MERGE["Merge into tool catalog"]
    MERGE --> PHASE2["Phase 2: Auto-discover ALL<br/>public functions"]
    PHASE2 --> DEDUP["Deduplicate<br/>(decorated tools take priority)"]
    DEDUP --> REGISTER["Register in MCPToolRegistry"]
    REGISTER --> COUNT["Total: 100+ tools"]
```

### Algorithm Mapping

The `get_skill_manifest()` function ([L836-993](../../../src/codomyrmex/agents/pai/mcp_bridge.py)) maps Codomyrmex tools to PAI Algorithm phases:

```mermaid
graph LR
    subgraph Algorithm["The Algorithm (v0.2.25)"]
        O["1. OBSERVE"]
        T["2. THINK"]
        P["3. PLAN"]
        B["4. BUILD"]
        E["5. EXECUTE"]
        V["6. VERIFY"]
        L["7. LEARN"]
    end

    subgraph Tools["Codomyrmex Tools"]
        O1["list_modules<br/>module_info<br/>list_directory"]
        T1["analyze_python<br/>search_codebase"]
        P1["read_file<br/>json_query"]
        B1["write_file"]
        E1["run_command<br/>run_tests"]
        V1["git_status<br/>git_diff<br/>checksum_file"]
        L1["pai_awareness<br/>pai_status"]
    end

    O --> O1
    T --> T1
    P --> P1
    B --> B1
    E --> E1
    V --> V1
    L --> L1
```

### MCP Resources and Prompts

**Resources** (2): `codomyrmex://modules` and `codomyrmex://status` — live data feeds for agent context.

**Prompts** (10): Pre-built prompt templates including `codomyrmex.analyze_module`, `codomyrmex.debug_issue`, `codomyrmex.create_test`, and all 7 `/codomyrmex*` workflow prompts.

---

## Layer 3: TrustGateway (Security)

**Source**: [trust_gateway.py](../../../src/codomyrmex/agents/pai/trust_gateway.py)

This layer implements PAI's **Security System** principle: commands are validated before execution.

### Three-Tier Trust Model

```mermaid
stateDiagram-v2
    [*] --> UNTRUSTED : Tool registered
    UNTRUSTED --> VERIFIED : /codomyrmexVerify<br/>(safe tools auto-promoted)
    VERIFIED --> TRUSTED : /codomyrmexTrust<br/>(explicit user approval)
    TRUSTED --> UNTRUSTED : reset_trust()

    note right of UNTRUSTED : Cannot execute
    note right of VERIFIED : Read-only execution
    note right of TRUSTED : Full execution (writes, commands)
```

### How Trust Enforcement Works

```mermaid
sequenceDiagram
    participant A as PAI Agent
    participant T as TrustGateway
    participant R as TrustRegistry
    participant M as MCPBridge

    A->>T: trusted_call_tool("codomyrmex.write_file", ...)
    T->>R: Check trust level
    R-->>T: UNTRUSTED ❌
    T-->>A: PermissionError: "Run /codomyrmexTrust first"

    Note over A: User runs /codomyrmexVerify then /codomyrmexTrust

    A->>T: trusted_call_tool("codomyrmex.write_file", ...)
    T->>R: Check trust level
    R-->>T: TRUSTED ✅
    T->>M: call_tool("codomyrmex.write_file", ...)
    M-->>T: Result
    T-->>A: Result
```

### Destructive Tool Detection

The gateway uses **two strategies** to identify destructive tools:

1. **Explicit set**: `DESTRUCTIVE_TOOLS` frozenset (write_file, run_command, run_tests, call_module_function)
2. **Pattern matching**: For auto-discovered tools, function names containing `write`, `delete`, `execute`, `kill`, `destroy`, etc. are flagged

### Persistent Trust Ledger

Trust state is persisted to `~/.codomyrmex/trust_ledger.json`, surviving process restarts. The `TrustRegistry` singleton reloads state on every query to support multi-process coordination.

---

## Claude Integration Layer

**Source**: [claude_client.py](../../../src/codomyrmex/agents/claude/claude_client.py) + [claude_integration.py](../../../src/codomyrmex/agents/claude/claude_integration.py)

The Claude layer is **not part of PAI itself** but is PAI's primary **execution engine** within Codomyrmex. It implements PAI's Algorithm phases in code:

```mermaid
graph TD
    subgraph Client["ClaudeClient (claude_client.py)"]
        API["Anthropic API"]
        RETRY["Exponential Backoff<br/>(3 retries, jitter)"]
        TOOLS_REG["Tool Registration"]
        SESSIONS["Session Management"]
        STREAM["Streaming Support"]
        COST["Cost Estimation"]
    end

    subgraph Adapter["ClaudeIntegrationAdapter (claude_integration.py)"]
        CODE_GEN["adapt_for_ai_code_editing()"]
        LLM_ADAPT["adapt_for_llm()"]
        CODE_EXEC["adapt_for_code_execution()"]
        REFACTOR["adapt_for_code_refactoring()"]
    end

    Client --> Adapter
    CODE_GEN -->|"PAI BUILD phase"| API
    LLM_ADAPT -->|"PAI THINK phase"| API
    CODE_EXEC -->|"PAI VERIFY phase"| API
    REFACTOR -->|"PAI EXECUTE phase"| API
```

### Key Methods

| Method | PAI Phase | Purpose |
|:---|:---|:---|
| `execute()` | All | Core API call with retry logic |
| `execute_with_session()` | THINK/PLAN | Multi-turn conversations with history |
| `execute_with_tools()` | EXECUTE | Automatic tool execution loop (max 10 rounds) |
| `register_tool()` | PLAN | Register function calling tools |
| `edit_file()` | BUILD | AI-guided file editing |
| `adapt_for_ai_code_editing()` | BUILD | Code generation with language-specific prompting |
| `adapt_for_llm()` | THINK | OpenAI-compatible message format |
| `adapt_for_code_execution()` | VERIFY | Security/bug/performance analysis |

---

## Knowledge Scope

The `get_skill_manifest()` function categorizes all 100+ Codomyrmex modules into knowledge domains that PAI agents can navigate:

| Domain | Module Count | Examples |
|:---|:---:|:---|
| Core Infrastructure | 11 | logging, config, events, exceptions, utils |
| AI & Agents | 12 | agents, llm, MCP, orchestrator, prompt engineering |
| Code & Analysis | 10 | coding, static analysis, tree-sitter, git, testing |
| Data & Processing | 12 | database, vector store, cache, graph RAG, search |
| Security & Identity | 8 | security, auth, encryption, privacy, defense |
| Infrastructure & Ops | 15 | cloud, containerization, CI/CD, telemetry, metrics |
| UI & Interface | 11 | CLI, website, terminal, IDE, visualization, audio |
| Domain & Simulation | 14 | bio_simulation, finance, logistics, spatial, quantum |
| System & Meta | 10 | system discovery, plugin system, skills, tools, API |

---

## Related Documents

- [Algorithm: Phase-to-Tool Mapping](ALGORITHM.md#the-seven-phases)
- [Skills: Codomyrmex as a PAI Skill](SKILLS.md#codomyrmex-as-a-pai-skill)
- [TELOS: Granular Customization Layers](TELOS.md#the-granular-customization-layers)
- [Hooks: Security Hooks and Trust](HOOKS.md#security-hooks-and-the-trust-bridge)
- [Workflows: Workflow Execution Through MCP](WORKFLOWS.md#codomyrmex-workflow-integration)
- [Flows: Operational Sequence Diagrams](FLOWS.md)
- [Signposts: Line-Level Code Pointers](SIGNPOSTS.md)
