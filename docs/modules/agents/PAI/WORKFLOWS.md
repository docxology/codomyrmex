# PAI Workflows & Dispatch

Workflows are multi-step procedures that compose skills, tools, and prompts into reusable execution pipelines. The Dispatch system bridges the PAI web interface with AI agents for active execution.

**Upstream**: [Personal AI Infrastructure](https://github.com/danielmiessler/Personal_AI_Infrastructure) | **Dispatch Version**: v3.2.1

---

## Workflow System

### Codomyrmex-Defined Workflows

The `get_skill_manifest()` function ([L888-933](../../../src/codomyrmex/agents/pai/mcp_bridge.py)) defines 5 workflows that PAI agents can invoke:

```mermaid
graph TD
    subgraph W1["codomyrmexVerify"]
        V1["codomyrmex.pai_status"] --> V2["verify_capabilities()"]
    end

    subgraph W2["codomyrmexTrust"]
        T1["trust_all()"]
    end

    subgraph W3["analyze_and_test"]
        A1["list_modules"] --> A2["module_info"]
        A2 --> A3["analyze_python"]
        A3 --> A4["run_tests"]
    end

    subgraph W4["code_review"]
        C1["git_status"] --> C2["git_diff"]
        C2 --> C3["search_codebase"]
        C3 --> C4["analyze_python"]
    end

    subgraph W5["pai_health_check"]
        H1["pai_status"] --> H2["pai_awareness"]
        H2 --> H3["list_modules"]
    end
```

| Workflow | Steps | Purpose |
|:---|:---:|:---|
| `codomyrmexVerify` | 2 | Audit all capabilities, promote safe tools |
| `codomyrmexTrust` | 1 | Promote destructive tools to TRUSTED |
| `analyze_and_test` | 4 | Discover → Analyze → Test a module |
| `code_review` | 4 | Review changes via git + analysis |
| `pai_health_check` | 3 | Full PAI + Codomyrmex health assessment |

### Slash Command Workflows

Codomyrmex also defines slash-command workflows in `.agent/workflows/`:

| Slash Command | Backing Function | Purpose |
|:---|:---|:---|
| `/codomyrmexVerify` | `verify_capabilities()` | Full read-only audit with trust promotion |
| `/codomyrmexTrust` | `trust_all()` | Promote all tools to TRUSTED |
| `/codomyrmexStatus` | `PAIBridge.get_status()` | System health report |
| `/codomyrmexAnalyze` | Code analysis pipeline | Deep structural analysis |
| `/codomyrmexSearch` | Regex search | Pattern matching across codebase |
| `/codomyrmexDocs` | Module documentation | Retrieve README or SPEC |
| `/codomyrmexMemory` | Memory system | Add entry to agentic memory |

---

## Agent Dispatch System

The Dispatch system (v3.2.1) is PAI's active execution bridge, managed by `PMServer.ts`.

### Evolution Path

```mermaid
graph LR
    V2["v2.0: Clipboard<br/>(Passive)"]
    V3["v3.0: Active Execution<br/>(Semi-Autonomous)"]

    V2 -->|"Evolution"| V3

    style V2 fill:#6c757d,color:white
    style V3 fill:#2d6a4f,color:white
```

| Version | Mode | Mechanism | Features |
|:---|:---|:---|:---|
| **v2.0** | Passive | Clipboard copy | 14 prompt templates, manual review |
| **v3.0+** | Active | `Bun.spawn` subprocess | Real-time streaming, job tracking, multi-backend |

### Active Execution Architecture

```mermaid
sequenceDiagram
    participant U as User (SPA)
    participant PM as PMServer.ts
    participant B as Backend Selection
    participant C as Claude Code CLI
    participant O as Ollama

    U->>PM: POST /api/dispatch/execute<br/>{entity, action, backend}
    PM->>B: Route to selected backend

    alt Claude Code
        B->>C: claude -p --verbose --output-format stream-json "prompt"
        C-->>PM: NDJSON events (content_block_delta)
    else Ollama
        B->>O: ollama run llama3.2 "prompt"
        O-->>PM: Direct text chunks
    end

    PM-->>U: WebSocket streaming (300-500ms intervals)
    PM->>PM: Persist in job Map
```

### Dispatch API Reference

| Endpoint | Method | Purpose |
|:---|:---|:---|
| `/api/dispatch/execute` | POST | Trigger execution (returns `jobId`) |
| `/api/dispatch/status/:id` | GET | Job state + full output buffer |
| `/api/dispatch/jobs` | GET | Recent 20 dispatch operations |
| `/api/dispatch/queue` | POST | Add task to sequential queue |
| `/api/dispatch/queue/run` | POST | Trigger sequential executor |

### Execution Backends

| Backend | Binary Path | Streaming Format | Performance |
|:---|:---|:---|:---|
| **Claude Code CLI** | `~/.local/bin/claude` | NDJSON (`content_block_delta`) | Varies by model |
| **Ollama** | `/opt/homebrew/bin/ollama` | Raw text chunks | ~18-25 tok/s |

### Context Standard Pattern

All dispatch actions use a standardized entity context:

```json
{
  "title": "Entity Name",
  "id": "slug-identifier",
  "status": "Active",
  "priority": "HIGH",
  "goal": "Project objective",
  "criteria": ["Success criterion 1", "Success criterion 2"]
}
```

Technical details are stored in `dispatch_context` within YAML files:

- `links`: Reference URLs/paths
- `summary`: AI-generated rolling summary
- `notes`: Detailed implementation context

---

## Codomyrmex Workflow Integration

### How Codomyrmex Workflows Map to PAI Dispatch

```mermaid
graph TD
    subgraph PAI_Dispatch["PAI Dispatch Actions"]
        D1["Analyze"] 
        D2["Implement"]
        D3["Review"]
        D4["Test"]
        D5["Deploy"]
    end

    subgraph Codomyrmex_WF["Codomyrmex Workflows"]
        W1["analyze_and_test<br/>(list → info → analyze → test)"]
        W2["code_review<br/>(status → diff → search → analyze)"]
        W3["pai_health_check<br/>(status → awareness → modules)"]
        W4["codomyrmexVerify<br/>(status → verify_capabilities)"]
    end

    D1 -->|"Dispatches to"| W1
    D3 -->|"Dispatches to"| W2
    D4 -->|"Dispatches to"| W4
    D2 -->|"Uses"| W3
```

### Workflow Execution Through MCP

When a PAI agent invokes a Codomyrmex workflow, each step is a discrete MCP tool call:

```mermaid
sequenceDiagram
    participant A as PAI Agent
    participant M as MCPBridge
    participant T as TrustGateway
    
    Note over A,T: Workflow: analyze_and_test

    A->>M: call_tool("codomyrmex.list_modules")
    M-->>A: Module list
    
    A->>M: call_tool("codomyrmex.module_info", module="coding")
    M-->>A: Module details
    
    A->>M: call_tool("codomyrmex.analyze_python", path="...")
    M-->>A: Analysis results
    
    A->>T: trusted_call_tool("codomyrmex.run_tests", module="coding")
    T->>T: Check TRUSTED (destructive)
    T->>M: call_tool("codomyrmex.run_tests", module="coding")
    M-->>T: Test results
    T-->>A: Test results
```

---

## PMServer: The Orchestration Hub

The PMServer provides the web infrastructure for workflow management:

### Three-Layer Architecture

```mermaid
graph TD
    subgraph API["API Layer"]
        REST["REST Endpoints<br/>(GET/POST/PUT/DELETE)"]
        WS["WebSocket<br/>(Real-time events)"]
        SPA["SPA Delivery<br/>(Single Page App)"]
    end

    subgraph Logic["Logic Layer"]
        PM["Project Management<br/>(Missions → Projects → Tasks)"]
        DISPATCH["Agent Dispatch<br/>(Claude / Ollama)"]
        INTERVIEW["Interview System<br/>(LLM Q&A)"]
    end

    subgraph Storage["Storage Layer"]
        FS["Filesystem Registry<br/>(YAML / JSON)"]
        MEMORY["Memory Stores<br/>(~/.claude/MEMORY/)"]
    end

    API --> Logic --> Storage
```

### SPA Tabs

| Tab | Description | Status |
|:---|:---|:---|
| **Dashboard/Data** | Live overview, searchable mission/project lists | ✅ Verified |
| **Board (Kanban)** | Strategic mission overview + tactical task boards | ✅ Verified |
| **Projects** | Detailed project views with task lists | ✅ Verified |
| **Network** | D3 force-directed graph of relationships | ✅ Verified |
| **Dispatch** | Active execution hub (Claude/Ollama) | ✅ Verified |
| **Analytics/Timeline** | Progress metrics and temporal distribution | ✅ Verified |
| **Git** | Repository management | ✅ Verified |
| **Integration** | External tool connections | ✅ Verified |
| **Interview** | Human-in-the-loop intelligence gathering (v4.1.0) | ✅ Verified |

---

## Related Documents

- [Algorithm: Phase-to-Tool Mapping](ALGORITHM.md#the-seven-phases)
- [Skills: Codomyrmex as a Skill](SKILLS.md#codomyrmex-as-a-pai-skill)
- [Architecture: MCP Server Initialization](ARCHITECTURE.md#layer-2-mcpbridge-communication)
- [Flows: MCP Server Initialization](FLOWS.md#6-mcp-server-initialization)
