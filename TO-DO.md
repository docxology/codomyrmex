# Codomyrmex Project Roadmap & To-Do

**Status**: Active | **Last Updated**: February 19, 2026 | **Current**: v0.1.9 | **Next**: v0.2.0 | **Target**: v0.4.0

---

## Completed Releases

| Version | Theme | Key Deliverables | Tests |
| :--- | :--- | :--- | ---: |
| **v0.1.3** | Foundation Hardening | RASP standardization, `uv` migration | 84 |
| **v0.1.4** | Zero-Mock Certification | `EphemeralServer`, `pytest-benchmark` | +3 |
| **v0.1.5** | Module Refactoring | 79/79 `__all__` exports, 0 cross-layer violations | +2 |
| **v0.1.6** | Agent & Memory | `AgentProtocol`, `AgentMessage`, `ToolRegistry.from_mcp()`, `VectorStoreMemory`, `EventBus.emit_typed()` | +71 |
| **v0.1.7** | Docs & MCP Plumbing | Version sync, module count →82, `MCPClient` (355 lines), 6 `mcp_tools.py` registered, 535 tools | +137 |
| **v0.1.8** | MCP Robustness | Schema validation, error envelope, circuit breaker, rate limiter, async runner/scheduler, observability pipeline, performance baselines | +211 |
| **v0.1.9** | Bulletproof Workflows | PAI bridge hardening, trust gateway audit, 11 workflow integration tests, CLI doctor, concurrency hardening, honeytokens, infinite conversation orchestrator | +68 |

**Cumulative**: 8805 passed, 74 pre-existing failures, 162 skipped, 9043 total collected (442s)

<details>
<summary><strong>v0.1.8 Stream Details</strong> (7 streams, all ✅)</summary>

| Stream | Commit | Key Files | New Tests |
| :--- | :--- | :--- | ---: |
| S1: Schema Validation | `bf23e0e5` | `errors.py`, `validation.py` | 47 |
| S2: Transport Robustness | `c1c7445b` | `circuit_breaker.py`, `rate_limiter.py` | 47 |
| S3: Discovery Hardening | `13a3a2de` | `MCPDiscoveryEngine`, TTL cache | 34 |
| S4: Stress Tests | `8b6aade1` | 4 test files, 36 concurrent/stress tests | 36 |
| S5: Async Orchestrator | `0eea747d` | `async_runner.py`, `async_scheduler.py`, `@with_retry` | 34 |
| S6: Observability | `8c92635a` | `ws_handler.py`, `event_bridge.py`, `MCPObservabilityHooks` | 39 |
| S7: Performance | `c53923b5` | `benchmark_startup.py`, lazy import tests | 21 |

</details>

<details>
<summary><strong>v0.1.9 Stream Details</strong> (7 streams, all ✅)</summary>

| Stream | Key Files | New Tests |
| :--- | :--- | ---: |
| S1: PAI Bridge Hardening | `mcp_bridge.py` (+161), `discovery.py` refactored | — |
| S2: Trust Gateway | `trust_gateway.py` (+279), audit log, escalation hooks | — |
| S3: Workflow Tests | 11 files in `tests/integration/workflows/` | 54 |
| S4: CLI Doctor | `cli/doctor.py` (5 checks, `--json`, exit codes) | — |
| S5: Concurrency | `pool.py` (AsyncWorkerPool), `dead_letter.py`, `stores.py` lock fix | — |
| S6: Security | Honeytokens in `defense/active.py` | 6 |
| S7: Infinite Conversation | `agents/orchestrator.py`, real Ollama LLM tests | 7 |

**Gate Criteria (ALL MET)**:

- [x] 54+ workflow integration tests pass
- [x] `codomyrmex doctor --all` exits 0
- [x] Trust audit log captures 100% of invocations
- [x] Dead-letter queue operational
- [x] MCP test count ≥250 (achieved: 386)
- [x] Infinite conversation: 3 agents, real Ollama, 7/7 tests

</details>

---

## 🤖 v0.2.0 — "Agents Я Us" (Certification Release)

**Theme**: "Everything Works, Everything Connects" | **Scope**: No new cognitive features — bulletproof plumbing

### MCP Coverage Certification

- [ ] Every module with public functions has auto-discovered MCP tools (target: 600+)
- [ ] `MCPClient` ↔ `MCPServer` full round-trip verified (stdio + HTTP)
- [ ] Tool count parity: `get_total_tool_count()` matches SKILL.md
- [ ] MCP tool argument schemas fully typed — eliminate `Any` in tool signatures
- [ ] `_discover_dynamic_tools()` cached and <100ms
- [x] ~~Tool category taxonomy~~: 63/63 tools classified into {analysis, generation, execution, query, mutation} → `model_context_protocol/taxonomy.py`
- [ ] Rate limiting operational for external-facing tools
- [ ] Circuit breaker operational for all tool categories
- [ ] Schema validation on 100% of tool invocations

### PAI Integration Certification

- [x] ~~All 10+ workflow integration tests pass~~ (54 passed, 6 skipped)
- [x] ~~`verify_capabilities()` normalized~~ (v0.1.9 S1)
- [x] ~~Full trust lifecycle e2e~~ (v0.1.9 S2)
- [ ] Skill manifest matches actual capabilities — automated CI check
- [ ] PAI version sync: all config files `0.2.0`
- [ ] `PAIAGENTSYSTEM.md` mapping validated
- [ ] PAI Algorithm phase coverage: all 8 phases have ≥2 mapped modules with MCP tools

### Logging & Observability

- [x] ~~Structured JSON logging~~ (v0.1.8 S6: `enable_structured_json()`)
- [x] ~~`WebSocketLogHandler`~~ (v0.1.8 S6)
- [x] ~~`codomyrmex doctor` CLI~~ (v0.1.9 S4)
- [x] ~~`EventBus` → logging bridge~~ (v0.1.8 S6: `EventLoggingBridge`)
- [x] ~~Correlation ID propagation~~ → `logging_monitoring/correlation.py` (15/15 tests)
- [x] ~~MCP metrics resource~~ (`codomyrmex://mcp/metrics` via `MCPObservabilityHooks`)
- [ ] Wire correlation into `_call_tool()` and `EventBus`

### Concurrency & Performance

- [x] ~~`AsyncParallelRunner`~~ (v0.1.8 S5)
- [x] ~~CLI startup <500ms, import <200ms~~ (v0.1.8 S7)
- [x] ~~Thread-safe shared state~~ (concurrent stress tests)
- [x] ~~Dead-letter queue~~ (v0.1.9 S5)
- [ ] Connection pooling on HTTP transport with DNS cache
- [ ] Memory profiling for long-running orchestrator workflows

### Test Suite Certification

- [ ] Full regression: **0 failures** (currently 74 pre-existing), ≤100 skips
- [ ] MCP test count ≥300 (current: 386 ✅)
- [ ] Coverage ≥80% on actively maintained modules
- [ ] Mutation testing on critical paths (MCP bridge, trust, retry)
- [ ] Load test: 100 concurrent tool invocations
- [x] ~~Test execution <600s~~ (current: 442s ✅)

### Documentation Freeze

- [ ] All 82 modules have current README.md, SPEC.md, AGENTS.md
- [ ] CHANGELOG.md complete through v0.2.0
- [ ] API reference auto-generated (Sphinx or mkdocstrings)
- [ ] `SKILL.md` tool table auto-validated against registry
- [ ] Architecture diagrams match actual dependencies

**Gate**: `codomyrmex doctor --all` exit 0 · 0 test failures · coverage ≥80% · MCP tools ≥600 · all workflows passing · PAI version sync

---

## 🧠 v0.3.0 — "Active Inference"

**Theme**: "Thinking Agents" | **Scope**: Cognitive architecture on the v0.2.0 base

### Chain-of-Thought Reasoning

| Deliverable | File | Description |
| :--- | :--- | :--- |
| CoT prompting wrapper | `llm/chain_of_thought.py` (NEW) | `think()` → `reason()` → `conclude()` pipeline. `ReasoningTrace` with confidence. |
| `ThinkingAgent` | `agents/core/thinking_agent.py` (NEW) | Extends `ReActAgent` with CoT. Traces stored in `AgentMemory`. |
| Sliding context window | `llm/context_manager.py` (NEW) | Token-aware: FIFO, importance-weighted, semantic similarity. |
| Reasoning MCP tools | `agents/core/mcp_tools.py` | `think`, `reason`, `get_reasoning_trace` tools. |

### Cerebrum + GraphRAG Integration

| Deliverable | File | Description |
| :--- | :--- | :--- |
| Case retrieval | `cerebrum/case_retrieval.py` (NEW) | `CaseBase` + `VectorStoreMemory` similarity search. |
| Graph-agent bridge | `graph_rag/agent_bridge.py` (NEW) | Graph retrieval → agent context. Entity linking. |
| Bayesian reasoning | `orchestrator/bayesian.py` (NEW) | Bayesian decision hooks for task selection. |
| Knowledge distillation | `cerebrum/distillation.py` (NEW) | Extract patterns from agent traces → `CaseBase`. |

### Memetic Analysis

| Deliverable | File | Description |
| :--- | :--- | :--- |
| Anti-pattern detector | `meme/anti_pattern_detector.py` (NEW) | Copy-paste drift, god objects, circular deps, dead code. |
| Concept drift tracker | `meme/drift_tracker.py` (NEW) | Semantic drift between docs and code via LLM. |

### Prompt Engineering Integration

| Deliverable | File | Description |
| :--- | :--- | :--- |
| Template→agent wiring | `prompt_engineering/agent_prompts.py` (NEW) | Dynamic prompt selection by task type, A/B testing. |
| Context-aware prompts | `prompt_engineering/context.py` (NEW) | Enrich prompts with file history, similar code. |

### Security Hardening

- [ ] `wallet/key_rotation.py`: automated key rotation
- [ ] `wallet/encrypted_storage.py`: AES-256-GCM credential storage
- [ ] Dependency scanning in CI/CD

**Gate**: ThinkingAgent valid traces · case retrieval relevant · anti-pattern detector flags ≥3 · coverage ≥80%

---

## 🐜 v0.4.0 — "Ant Colony"

**Theme**: "Swarm Orchestration" | **Scope**: Autonomous multi-agent collaboration

### Swarm Protocol

| Deliverable | File | Description |
| :--- | :--- | :--- |
| `SwarmProtocol` | `collaboration/swarm/protocol.py` (NEW) | Roles: Coder, Reviewer, DevOps, Architect, Tester. Consensus: majority, weighted, veto. |
| `AgentPool` | `collaboration/swarm/pool.py` (NEW) | Capability-based routing, load balancing. |
| `SwarmMessage` | `collaboration/swarm/message.py` (NEW) | Inter-agent format. Intent: REQUEST/RESPONSE/BROADCAST. |
| Agent identity | `identity/capability.py` (NEW) | Capability advertisement + matching. |
| Swarm MCP tools | `collaboration/swarm/mcp_tools.py` (NEW) | `create_swarm`, `assign_task`, `get_consensus`, `swarm_status`. |

### Self-Healing Workflows

| Deliverable | File | Description |
| :--- | :--- | :--- |
| Auto-diagnosis | `orchestrator/self_healing.py` (NEW) | On failure: `ThinkingAgent` root cause analysis. |
| Config-aware retry | `orchestrator/self_healing.py` | Detect config failures → auto-adjust → retry. |
| Diagnostics dead-letter | `orchestrator/self_healing.py` | Structured reports with `related_cases`. |

### Project-Level Context

| Deliverable | File | Description |
| :--- | :--- | :--- |
| `ProjectContext` | `agents/context/project.py` (NEW) | Full repo structure awareness. |
| Repo indexer | `agents/context/indexer.py` (NEW) | Auto-index via `git_operations` + `coding.parsers`. |
| Context-aware tool select | `agents/context/tool_selector.py` (NEW) | File type + task type → optimal MCP tools. |

### Meta-Agent

| Deliverable | File | Description |
| :--- | :--- | :--- |
| `MetaAgent` | `agents/meta/meta_agent.py` (NEW) | Self-improving: rewrites prompts based on outcomes. |
| Strategy library | `agents/meta/strategies.py` (NEW) | Persisted via `agentic_memory`. A/B testing. |
| Outcome scoring | `agents/meta/scoring.py` (NEW) | Multi-dimensional: correctness, efficiency, quality. |

**Gate**: Swarm 3-agent code review · self-healing fixes ≥3 patterns · MetaAgent improves over 10 iterations · MCP >700

---

## 🔄 Ongoing Technical Debt

- [ ] Remove magic numbers and hardcoded paths
- [ ] Keep SPEC/AGENTS/CHANGELOG synchronized
- [ ] Enforce `mypy --strict` progressively
- [ ] PAI bridge version sync at each release
- [ ] Maintain MCP tool count parity: SKILL.md ↔ registry
- [ ] Module RAS completeness in CI
- [ ] Deprecation tracking with removal target versions
