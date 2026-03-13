<!-- markdownlint-disable MD060 MD033 -->
# Codomyrmex — TODO

**Version**: v1.3.3 | **Date**: 2026-03-13 | **Modules**: 129 | **Sprint**: 31

> v1.3.2 "Execution Capabilities & Distillation" delivered. All 33,000+ tests natively passing.

Authoritative project backlog. Upcoming work only; completed items removed.

---

## 🚀 v1.3.3 — "Resilience & Abstract Reasoning"

> **Theme**: Formal verifications, hierarchical planning, and robust consensus.

| # | Deliverable | Module | Concrete Scope |
| :--- | :--- | :--- | :--- |
| D1 | **Z3 Formal Verifier** | `formal_verification/` | Concrete Z3 solver integration for mathematically proving state invariants |
| D2 | **Hierarchical Planner** | `orchestrator/` | HTN (Hierarchical Task Network) multi-scale planner for temporal abstraction |
| D3 | **PBFT Consensus** | `collaboration/` | Practical Byzantine Fault Tolerance mechanism for robust multi-agent voting |

---

## 🔭 v1.4.0+ — Research Horizon

> **Theme**: Embedded operations & emergent swarms.

| # | Direction | Builds On | Concrete Next Step |
| :--- | :--- | :--- | :--- |
| R1 | **Physical Embodiment** | `embodiment/` | WebSocket-based physical abstraction bridge for drone/rover telemetry |
| R2 | **Evolutionary Synthesis** | `evolutionary_ai/` | Genetic algorithm for self-optimizing prompt templates and config tuning |
| R3 | **Information Dynamics** | `meme/` | Exposing meme transmission and narrative engines as an MCP toolset |

---

## Release Criteria

> [!IMPORTANT]
> **Strict Delivery Requirements**:
>
> - **Zero-Mock Policy**: All tests must use 100% real dependencies and functional components.
> - **Full Test Pass**: All 33,000+ unit and integration tests passing natively (`uv run pytest`).
> - **Code Health**: No backwards or legacy methods, no technical debt, and 100% lint compliance.
> - **Documentation**: Complete API documentation and signposting (`AGENTS.md`) for all new capabilities.

---

## Reference

- **Coverage**: `pyproject.toml [tool.coverage.report] fail_under=75`
- **Test**: `uv run pytest` · **Lint**: `uv run ruff check .` · **Format**: `uv run ruff format .`
- **Type check**: `uv run ty check src/` · **Build**: `uv build`

---

*Last updated: 2026-03-13 — Sprint 31.*
