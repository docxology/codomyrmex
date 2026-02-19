# Codomyrmex Project Roadmap & To-Do

**Status**: Active | **Last Updated**: February 19, 2026 | **Current**: v0.1.9 | **Next**: v0.2.0 | **Target**: v0.4.0

**Codebase Snapshot** (as of v0.1.9):

| Metric | Value |
| :--- | ---: |
| Top-level modules | 81 |
| `@mcp_tool` decorated functions | 102 (across 27 files) |
| Modules with `mcp_tools.py` | 7 of 81 |
| Tests collected | 9,054 |
| Tests passing | 8,805 |
| Pre-existing failures | 74 |
| Skipped | 162 |
| Code coverage | 28% |
| SPEC.md files | 337 |
| README.md files | 1,248 |
| AGENTS.md files | 353 |

---

## Completed Releases

| Version | Theme | Key Deliverables | New Tests |
| :--- | :--- | :--- | ---: |
| v0.1.3 | Foundation Hardening | RASP standardization, `uv` migration | 84 |
| v0.1.4 | Zero-Mock Certification | `EphemeralServer`, `pytest-benchmark` | +3 |
| v0.1.5 | Module Refactoring | 79/79 `__all__` exports, 0 cross-layer violations | +2 |
| v0.1.6 | Agent & Memory | `AgentProtocol`, `ToolRegistry.from_mcp()`, `VectorStoreMemory`, `EventBus.emit_typed()` | +71 |
| v0.1.7 | Docs & MCP Plumbing | `MCPClient` (355 lines), 6 `mcp_tools.py` registered | +137 |
| v0.1.8 | MCP Robustness | Schema validation, circuit breaker, rate limiter, async scheduler, observability pipeline, perf baselines (7 streams) | +211 |
| v0.1.9 | Bulletproof Workflows | PAI bridge, trust gateway, 11 workflow tests, CLI doctor, concurrency, honeytokens, infinite conversation orchestrator (7 streams) | +68 |

---

## 🤖 v0.2.0 — "Agents Я Us" (Infrastructure Certification)

**Theme**: Certify what exists — fix failures, wire plumbing, verify round-trips
**Effort**: ~2 focused sessions | **Priority**: High → Low within each section

### P0 — Test Suite Health (74 failures → 0)

These 74 pre-existing failures block every downstream confidence claim. Fix them first.

- [ ] Triage 74 failures: classify as {bug, stale fixture, missing dep, env-specific}
- [ ] Fix or skip-with-reason all 74 → **0 failures**, ≤100 skips
- [ ] MCP test count verify ≥300 (currently 386 by marker, confirm after triage)

### P1 — MCP Wiring Completion

Only 7/81 modules have `mcp_tools.py`. The realistic goal is wiring the **active** modules — not all 81.

- [ ] Identify which of the 81 modules have substantive public APIs (estimated: ~25)
- [ ] Add `mcp_tools.py` to the top-15 active modules (from 7 → 22)
- [ ] Verify `MCPClient` ↔ `MCPServer` full round-trip (stdio transport)
- [ ] Tool argument schemas: audit `Any` usage, type the top-20 most-called tools
- [x] ~~Tool category taxonomy~~: 63/63 tools classified → `taxonomy.py`
- [ ] Rate limiting + circuit breaker: verify operational on external-facing tools

### P2 — Observability Wiring

Core infrastructure exists but isn't wired end-to-end.

- [x] ~~Correlation ID module~~: `logging_monitoring/correlation.py` (15/15 tests)
- [ ] Wire `correlation.py` into `_call_tool()` (MCP bridge)
- [ ] Wire `correlation.py` into `EventBus.emit()` / `emit_typed()`
- [ ] Verify: tool call → log line → event → relay all carry same CID
- [ ] `codomyrmex doctor --all` runs clean in CI

### P3 — Documentation Audit (targeted)

Not all 81 modules need full docs. Focus on the 25 active modules.

- [ ] Identify 25 "active" modules (have real code, not stubs)
- [ ] Verify each has current README.md, SPEC.md, AGENTS.md
- [ ] CHANGELOG.md entries through v0.2.0
- [ ] `SKILL.md` tool table: auto-validate against registry
- [ ] Architecture diagram: actual module dependency graph (auto-generated)

### P4 — PAI Integration

- [ ] Skill manifest matches actual capabilities — automated CI check
- [ ] PAI version sync: all config files bump to `0.2.0`
- [ ] `PAIAGENTSYSTEM.md` mapping validated against live tool list

### P5 — Infinite Conversation Hardening

- [x] ~~18/18 real-LLM tests pass~~ (orchestrator, file injection, TO-DO scaffolding)
- [ ] `dev_loop()` tested with real `TO-DO.md` from this repo (full round-trip)
- [ ] Conversation persistence: resume from exported JSONL
- [ ] Streaming output: print turns as they happen (for interactive use)

**v0.2.0 Gate**: 0 test failures · ≤100 skips · 22+ modules with MCP tools · CID wired end-to-end · `codomyrmex doctor` clean

---

## 🔧 v0.2.1 — "Coverage & Quality" (Hardening Release)

**Theme**: Raise coverage from 28% → 50%, mutation testing, load testing
**Depends on**: v0.2.0 (0 failures baseline)

### Coverage Push

- [ ] Coverage ≥50% on the 25 active modules (from 28% overall)
- [ ] Identify the 10 modules with lowest coverage → write targeted tests
- [ ] `pytest --cov-fail-under=50` in CI for active modules

### Mutation Testing

- [ ] `mutmut` on critical paths: MCP bridge, trust gateway, retry logic
- [ ] Fix mutations that survive (indicates missing test assertions)

### Load Testing

- [ ] 100 concurrent tool invocations → measure latency P50/P95/P99
- [ ] Connection pooling on HTTP transport with DNS cache
- [ ] Memory profiling for long-running orchestrator workflows

### Type Checking

- [ ] `mypy --strict` on top-10 active modules
- [ ] Fix type errors; add `py.typed` marker

**v0.2.1 Gate**: ≥50% coverage on active modules · 0 surviving critical mutations · P95 < 500ms at 100 concurrency

---

## 🧠 v0.3.0 — "Active Inference"

**Theme**: Cognitive architecture on the v0.2.x base
**Depends on**: v0.2.1 (coverage + quality baseline)

### Chain-of-Thought Reasoning

| Priority | Deliverable | File | Description |
| :---: | :--- | :--- | :--- |
| P0 | CoT prompting wrapper | `llm/chain_of_thought.py` [NEW] | `think()` → `reason()` → `conclude()` pipeline with `ReasoningTrace` |
| P0 | `ThinkingAgent` | `agents/core/thinking_agent.py` [NEW] | Extends `ReActAgent` with CoT; traces stored in `AgentMemory` |
| P1 | Sliding context window | `llm/context_manager.py` [NEW] | Token-aware FIFO with importance weighting |
| P2 | Reasoning MCP tools | `agents/core/mcp_tools.py` | `think`, `reason`, `get_reasoning_trace` tools |

### Cerebrum + GraphRAG Integration

| Priority | Deliverable | File | Description |
| :---: | :--- | :--- | :--- |
| P1 | Case retrieval | `cerebrum/case_retrieval.py` [NEW] | `CaseBase` + `VectorStoreMemory` similarity search |
| P1 | Graph-agent bridge | `graph_rag/agent_bridge.py` [NEW] | Graph retrieval → agent context; entity linking |
| P2 | Bayesian reasoning | `orchestrator/bayesian.py` [NEW] | Bayesian decision hooks for task selection |
| P2 | Knowledge distillation | `cerebrum/distillation.py` [NEW] | Extract patterns from agent traces → `CaseBase` |

### Memetic Analysis

| Priority | Deliverable | File | Description |
| :---: | :--- | :--- | :--- |
| P1 | Anti-pattern detector | `meme/anti_pattern_detector.py` [NEW] | Copy-paste drift, god objects, circular deps, dead code |
| P2 | Concept drift tracker | `meme/drift_tracker.py` [NEW] | Semantic drift between docs and code via LLM |

### Prompt Engineering

| Priority | Deliverable | File | Description |
| :---: | :--- | :--- | :--- |
| P1 | Template→agent wiring | `prompt_engineering/agent_prompts.py` [NEW] | Dynamic prompt selection by task type |
| P2 | Context-aware prompts | `prompt_engineering/context.py` [NEW] | Enrich prompts with file history, similar code |

### Security Hardening

- [ ] `wallet/key_rotation.py`: automated key rotation
- [ ] `wallet/encrypted_storage.py`: AES-256-GCM credential storage
- [ ] Dependency scanning in CI/CD

**v0.3.0 Gate**: ThinkingAgent produces valid traces · case retrieval relevant results · anti-pattern detector flags ≥3 patterns · coverage ≥60%

---

## 🐜 v0.4.0 — "Ant Colony"

**Theme**: Autonomous multi-agent swarm orchestration
**Depends on**: v0.3.0 (cognitive architecture)

### Swarm Protocol

| Priority | Deliverable | File | Description |
| :---: | :--- | :--- | :--- |
| P0 | `SwarmProtocol` | `collaboration/swarm/protocol.py` [NEW] | Roles: Coder, Reviewer, DevOps, Architect, Tester. Consensus: majority, weighted, veto |
| P0 | `AgentPool` | `collaboration/swarm/pool.py` [NEW] | Capability-based routing, load balancing |
| P1 | `SwarmMessage` | `collaboration/swarm/message.py` [NEW] | Inter-agent format. Intent: REQUEST/RESPONSE/BROADCAST |
| P1 | Agent identity | `identity/capability.py` [NEW] | Capability advertisement + matching |
| P2 | Swarm MCP tools | `collaboration/swarm/mcp_tools.py` [NEW] | `create_swarm`, `assign_task`, `get_consensus`, `swarm_status` |

### Self-Healing Workflows

| Priority | Deliverable | File | Description |
| :---: | :--- | :--- | :--- |
| P0 | Auto-diagnosis | `orchestrator/self_healing.py` [NEW] | On failure: `ThinkingAgent` root cause analysis |
| P1 | Config-aware retry | `orchestrator/self_healing.py` | Detect config failures → auto-adjust → retry |
| P1 | Diagnostics dead-letter | `orchestrator/self_healing.py` | Structured reports with `related_cases` |

### Project-Level Context

| Priority | Deliverable | File | Description |
| :---: | :--- | :--- | :--- |
| P0 | `ProjectContext` | `agents/context/project.py` [NEW] | Full repo structure awareness |
| P1 | Repo indexer | `agents/context/indexer.py` [NEW] | Auto-index via `git_operations` + `coding.parsers` |
| P2 | Context-aware tool select | `agents/context/tool_selector.py` [NEW] | File type + task type → optimal MCP tools |

### Meta-Agent

| Priority | Deliverable | File | Description |
| :---: | :--- | :--- | :--- |
| P0 | `MetaAgent` | `agents/meta/meta_agent.py` [NEW] | Self-improving: rewrites prompts based on outcomes |
| P1 | Strategy library | `agents/meta/strategies.py` [NEW] | Persisted via `agentic_memory`; A/B testing |
| P2 | Outcome scoring | `agents/meta/scoring.py` [NEW] | Multi-dimensional: correctness, efficiency, quality |

**v0.4.0 Gate**: Swarm 3-agent code review working · self-healing fixes ≥3 failure patterns · MetaAgent improves over 10 iterations · MCP >200 typed tools

---

## 🔄 Ongoing Technical Debt

Ordered by impact:

| Priority | Item | Metric |
| :---: | :--- | :--- |
| P0 | Fix 74 pre-existing test failures | 0 failures |
| P0 | Coverage: 28% → 50% (active modules) | `--cov-fail-under=50` |
| P1 | Keep SPEC/AGENTS/CHANGELOG synchronized | CI check |
| P1 | PAI bridge version sync at each release | automated |
| P1 | MCP tool count parity: SKILL.md ↔ registry | CI check |
| P2 | Enforce `mypy --strict` progressively (10 → 25 → all) | 0 errors |
| P2 | Remove magic numbers and hardcoded paths | grep audit |
| P3 | Module RAS completeness in CI | automated |
| P3 | Deprecation tracking with removal target versions | CHANGELOG |
