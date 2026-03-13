<!-- markdownlint-disable MD060 MD033 -->
# Codomyrmex — TODO

**Version**: v1.5.0 | **Date**: 2026-03-13 | **Modules**: 129 | **Sprint**: 33

> v1.5.5 "Obsidian Vault Memory & Archival" delivered. Session context is natively dumped to local Obsidian Vaults; parsing and regex/history vault search RAG MCP capabilities added.

Authoritative project backlog. Upcoming work only; completed items removed.

---

## 🚀 v1.5.6 — Task Orchestration & Scheduling

> **Theme**: Internalizing step-by-step reasoning via explicit checklist states.

| # | Deliverable | Module | Concrete Scope |
| :--- | :--- | :--- | :--- |
| D1 | **Internal TaskScheduler** | `agents/hermes/` | Map agent execution logic directly to the `orchestrator.TaskScheduler`. Expose tools for agents to natively break down their own instructions into checkable tasks. |
| D2 | **Workflow Mapping** | `agents/hermes/` | Add `WorkflowEngine` bindings allowing the agent to submit its own multi-step task list to an internal executor loop instead of returning to the user immediately. |

---

## 🚀 v1.5.7 — Error-Correction Handoffs

> **Theme**: Subprocess self-healing and proactive error containment.

| # | Deliverable | Module | Concrete Scope |
| :--- | :--- | :--- | :--- |
| D1 | **Recursive Retry Loop** | `agents/hermes/` | If an executed subprocess (e.g. bash or python script) fails, intercept the stderr stack trace and automatically feed it back into an active retry block before alerting the user natively. |
| D2 | **Recovery Prompting** | `agents/hermes/` | Structure system prompts during failure domains specifically focusing on trace analysis rather than feature generation. |

---

## 🚀 v1.5.8 — Delegation Primitive

> **Theme**: Multi-agent Swarm routing.

| # | Deliverable | Module | Concrete Scope |
| :--- | :--- | :--- | :--- |
| D1 | **Sub-Agent Deferral** | `agents/hermes/` | Expose a `delegate_task` MCP wrapper that executes `CodexClient` or `ClaudeClient` instances for isolated logic operations. |
| D2 | **Context Filtering** | `agents/hermes/` | Pass only minimal context bounds to sub-agents (preventing context bloat when deferring single file functions). |

---

## 🚀 v1.5.9 — Context Summarization & Archival

> **Theme**: Infinite-length sessions & Token Optimization.

| # | Deliverable | Module | Concrete Scope |
| :--- | :--- | :--- | :--- |
| D1 | **Rolling Summary Pipeline** | `agents/hermes/` | As a session window nears 8k tokens, strip early conversational chat nodes and replace them with a background LLM-generated summary token. |
| D2 | **Fact Extraction** | `agents/hermes/` | Inject specific user preferences learned during the trimmed conversation directly back into the system `UserModel` preference map instead of losing them in summary nodes. |

---

## 🚀 v1.5.10 — Semantic Deduplication

> **Theme**: Optimizing repetitive text streams.

| # | Deliverable | Module | Concrete Scope |
| :--- | :--- | :--- | :--- |
| D1 | **Trace Compression** | `agents/hermes/` | Scan large incoming stack trace objects and use AST or semantic grouping to strip repetitive loop errors, shrinking payload overhead to OpenRouter. |
| D2 | **Log Referencing** | `agents/hermes/` | Redirect 10,000+ line logs into an ephemeral tmp file and prompt the agent to explicitly search the text payload dynamically, rather than dumping it natively. |

---

## 🚀 v1.5.11 — Resource Monitoring Integration

> **Theme**: Hardware-aware local scaling.

| # | Deliverable | Module | Concrete Scope |
| :--- | :--- | :--- | :--- |
| D1 | **HealthChecker Scaling** | `agents/hermes/` | Tie active session loads into `system_discovery.HealthChecker` dynamically surfacing VLM / Local STT RAM pressure. |
| D2 | **Dynamic Fallbacks** | `agents/hermes/` | Auto-failback to lighter Ollama models (`qwen2.5:0.5b`) or upstream providers if the system is thrashing heavily on swap memory natively. |

---

## 🔭 v1.6.0+ — Horizon & Integration

> **Theme**: Cryptographic persistence, spatial world modeling, and omnimodal processing.

| # | Direction | Builds On | Concrete Next Step |
| :--- | :--- | :--- | :--- |
| R1 | **Spatial World Models** | `spatial/` | Fully integrate 4D time-series scene generation to render persistent simulation environments natively for agent embodied trials. |
| R2 | **Self-Custody Wallet** | `wallet/` | Expose zero-knowledge decentralized self-custody frameworks to allow agents to control their operational resources and perform autonomous transactions securely. |
| R3 | **Identity & Persona** | `identity/` | Establish bio-verified and multi-persona cognitive masking for defensive agentic operations across public networks. |

---

## Release Criteria

> [!IMPORTANT]
> **Strict Delivery Requirements**:
>
> - **Zero-Mock Policy**: All tests must use 100% real dependencies and functional components. No mock methods.
> - **Full Test Pass**: All 33,000+ unit and integration tests passing natively (`uv run pytest`) before final branch integration.
> - **Code Health**: No backwards or legacy methods, no technical debt, and 100% lint compliance. Clean repository state.
> - **Documentation**: Complete API documentation and signposting (`AGENTS.md`) for all new capabilities. Consistency with README.md and SPEC.md.

---

## Reference

- **Coverage**: `pyproject.toml [tool.coverage.report] fail_under=75`
- **Test**: `uv run pytest` · **Lint**: `uv run ruff check .` · **Format**: `uv run ruff format .`
- **Type check**: `uv run ty check src/` · **Build**: `uv build`

---

*Last updated: 2026-03-13 — Sprint 33.*
