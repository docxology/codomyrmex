# PAI Operational Flows

Detailed Mermaid diagrams visualizing every major operational sequence in the PAI ↔ Codomyrmex integration.

**Upstream**: [Personal AI Infrastructure](https://github.com/danielmiessler/Personal_AI_Infrastructure) | **Codomyrmex Source**: [`mcp_bridge.py`](../../../src/codomyrmex/agents/pai/mcp_bridge.py), [`trust_gateway.py`](../../../src/codomyrmex/agents/pai/trust_gateway.py)

---

## 1. Complete Tool Execution Lifecycle

This is the full sequence when a PAI agent calls a Codomyrmex MCP tool, from Algorithm phase selection through trust enforcement to result delivery.

```mermaid
sequenceDiagram
    participant U as User
    participant P as PAI Agent (Claude)
    participant H as Hook System
    participant A as The Algorithm
    participant T as TrustGateway
    participant M as MCPBridge
    participant C as Codomyrmex Module
    participant MEM as Memory System

    U->>P: Natural language request
    H->>P: FormatReminder hook classifies depth
    
    rect rgb(230, 245, 255)
        Note over A: Phase 1: OBSERVE
        P->>A: Reverse-engineer intent → ISC
        A->>M: call_tool("codomyrmex.list_modules")
        M-->>A: Module inventory
    end

    rect rgb(255, 245, 230)
        Note over A: Phase 2: THINK
        A->>M: call_tool("codomyrmex.analyze_python", path=...)
        M-->>A: File structure + metrics
        A->>A: Two-pass capability selection
    end

    rect rgb(230, 255, 230)
        Note over A: Phase 3: PLAN
        A->>M: call_tool("codomyrmex.read_file", path=...)
        M-->>A: File contents
    end

    rect rgb(255, 230, 230)
        Note over A: Phase 5: EXECUTE
        A->>T: trusted_call_tool("codomyrmex.write_file", ...)
        T->>T: Check trust level
        alt TRUSTED
            T->>M: call_tool("codomyrmex.write_file", ...)
            M->>C: Execute write operation
            C-->>M: Result
            M-->>T: Success
            T-->>A: Result
        else NOT TRUSTED
            T-->>A: PermissionError
            A-->>P: Request /codomyrmexTrust
        end
    end

    rect rgb(245, 230, 255)
        Note over A: Phase 6: VERIFY
        A->>M: call_tool("codomyrmex.git_diff")
        M-->>A: Changes confirmed
        A->>M: call_tool("codomyrmex.checksum_file", path=...)
        M-->>A: Checksum verified
    end

    rect rgb(255, 255, 220)
        Note over A: Phase 7: LEARN
        A->>MEM: Write to MEMORY/LEARNING/
        A-->>P: Report to user
    end

    P-->>U: Verified result with evidence
```

## 2. Dynamic Tool Discovery Pipeline

How the MCPBridge discovers and registers tools from across the entire Codomyrmex ecosystem.

```mermaid
flowchart TD
    START([Server Startup]) --> STATIC["Register 15 Static Core Tools<br/>(File I/O, Git, PAI, Testing)"]
    STATIC --> PROXY["Register 3 Universal Proxy Tools<br/>(list_module_functions, call_module_function, get_module_readme)"]
    PROXY --> PHASE1["Phase 1: Scan @mcp_tool Decorators"]
    
    PHASE1 --> SCAN["Scan 13 target modules:<br/>visualization, llm, security,<br/>git_operations, static_analysis,<br/>coding.execution, documentation,<br/>data_visualization.*, terminal_interface"]
    
    SCAN --> DECORATED["Collect decorated functions<br/>with schemas from decorators"]
    DECORATED --> PHASE2["Phase 2: Auto-Discover ALL<br/>Public Functions"]
    
    PHASE2 --> INSPECT["For each codomyrmex.* module:<br/>1. importlib.import_module()<br/>2. inspect.getmembers(mod, isfunction)<br/>3. inspect.signature(func)<br/>4. Generate JSON Schema"]
    
    INSPECT --> DEDUP["Deduplicate<br/>(decorated tools take priority)"]
    DEDUP --> REGISTER["Register in MCPToolRegistry"]
    REGISTER --> COUNT["Total: 100+ registered tools"]
    
    COUNT --> RESOURCES["Register 2 Resources<br/>(codomyrmex://modules, codomyrmex://status)"]
    RESOURCES --> PROMPTS["Register 10 Prompt Templates<br/>(analyze, debug, test, workflows)"]
    PROMPTS --> READY([MCP Server Ready])
```

## 3. Memory System Integration

How Codomyrmex operations feed into PAI's three-tier memory architecture.

```mermaid
graph TD
    subgraph Operations["Codomyrmex Operations"]
        A["Code Analysis<br/>(analyze_python)"]
        B["Test Execution<br/>(run_tests)"]
        C["Repository Changes<br/>(git_diff, git_status)"]
        D["PAI Status Check<br/>(pai_status, pai_awareness)"]
    end

    subgraph Bridge["PAI Bridge Layer"]
        E["PAIBridge.list_memory_stores()"]
        F["MCPBridge → pai_awareness tool"]
    end

    subgraph Memory["PAI Memory (~/.claude/MEMORY/)"]
        G["STATE/<br/>(Hot: Current session context)<br/>• Active file list<br/>• Current task state<br/>• Open sessions"]
        H["LEARNING/<br/>(Warm: Post-task insights)<br/>• What worked/failed<br/>• User preferences<br/>• Capability discoveries"]
        I["HISTORY/<br/>(Cold: Long-term archive)<br/>• Session transcripts<br/>• Decision logs<br/>• Performance metrics"]
        J["AGENTS/<br/>(Agent-specific memories)"]
        K["SECURITY/<br/>(Security event logs)"]
        L["RESEARCH/<br/>(Research findings)"]
    end

    A -->|"Analysis results"| G
    B -->|"Test pass/fail signals"| H
    C -->|"Change patterns"| H
    D -->|"System health snapshots"| I
    
    E -->|"Enumerates stores"| Memory
    F -->|"Reads awareness data"| Memory
    
    H -->|"Consolidation<br/>(periodic)"| I
    G -->|"Session end<br/>capture"| H
```

## 4. Trust Promotion Workflow

The complete `/codomyrmexVerify` → `/codomyrmexTrust` workflow.

```mermaid
sequenceDiagram
    participant U as User
    participant V as /codomyrmexVerify
    participant TR as TrustRegistry
    participant T as /codomyrmexTrust

    Note over U,T: Initial state: All tools UNTRUSTED

    U->>V: Run /codomyrmexVerify
    V->>V: Import codomyrmex<br/>Count modules
    V->>TR: verify_all_safe()
    TR->>TR: Scan all registered tools
    TR->>TR: Identify safe tools<br/>(read_file, list_directory, etc.)
    TR->>TR: Promote safe → VERIFIED
    TR-->>V: Promoted list
    V->>V: Check MCP server health
    V->>V: Check PAI bridge status
    V->>V: Validate skill manifest
    V-->>U: Structured report<br/>✅ N safe tools VERIFIED<br/>⚠️ M destructive tools remain UNTRUSTED

    Note over U: User reviews report

    U->>T: Run /codomyrmexTrust
    T->>TR: trust_all()
    TR->>TR: Promote ALL → TRUSTED
    TR->>TR: Persist to ~/.codomyrmex/trust_ledger.json
    TR-->>T: Promoted list
    T-->>U: All tools now TRUSTED<br/>Full execution enabled
```

## 5. Agent Personality Coordination

How PAI's agent personality definitions interact with the Codomyrmex `ClaudeClient`.

```mermaid
sequenceDiagram
    participant U as User
    participant P as PAIBridge
    participant AP as Agent Personality<br/>(~/.claude/agents/*.md)
    participant CI as ClaudeIntegrationAdapter
    participant CC as ClaudeClient
    participant API as Anthropic API

    U->>P: Request specialized analysis
    P->>AP: Load personality<br/>(e.g., Engineer.md)
    AP-->>P: Instructions, voice, expertise

    P->>CI: adapt_for_code_execution(code, "security")
    CI->>CI: Build analysis-specific prompt<br/>+ inject personality context
    CI->>CC: execute(AgentRequest)
    CC->>CC: Build messages with system prompt
    CC->>CC: Add conversation history
    CC->>API: messages.create(model, messages, system)
    API-->>CC: Response with usage stats
    CC->>CC: Calculate cost ($USD)
    CC->>CC: Extract content + tool calls
    CC-->>CI: AgentResponse
    CI->>CI: Parse structured analysis output
    CI-->>P: Analysis result dict
    P-->>U: Personality-informed report
```

## 6. MCP Server Initialization

Complete sequence for standing up the Codomyrmex MCP server that PAI agents connect to.

```mermaid
flowchart LR
    subgraph Init["create_codomyrmex_mcp_server()"]
        A["Create MCPServerConfig<br/>(name, transport)"] --> B["Create MCPServer"]
        B --> C["get_tool_registry()"]
        C --> D["Register static tools (15)"]
        D --> E["_discover_dynamic_tools()"]
        E --> F["Register dynamic tools (85+)"]
        F --> G["Register resources (2)"]
        G --> H["Register prompts (10)"]
        H --> I["Log tool/resource/prompt counts"]
    end
    
    I --> J{Transport?}
    J -->|stdio| K["server.run()<br/>(stdin/stdout)"]
    J -->|HTTP| L["server.run()<br/>(HTTP endpoint)"]
    
    K --> M["PAI Agent connects<br/>via claude_desktop_config.json"]
    L --> M
```

---

## Related Documents

- [Algorithm: The Seven Phases](ALGORITHM.md#the-seven-phases)
- [Architecture: Three-Layer Architecture](ARCHITECTURE.md#three-layer-architecture)
- [Skills: Skill Priority Hierarchy](SKILLS.md#skill-priority-hierarchy)
- [Hooks: FormatReminder](HOOKS.md#formatreminder-the-critical-hook)
- [TELOS: How TELOS Flows Through Codomyrmex](TELOS.md#how-telos-flows-through-codomyrmex)
- [Workflows: Agent Dispatch System](WORKFLOWS.md#agent-dispatch-system)
- [Signposts: Line-Level Code Pointers](SIGNPOSTS.md)
