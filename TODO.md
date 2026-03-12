<!-- markdownlint-disable MD060 MD033 -->
# Codomyrmex — TODO

**Version**: v1.1.11 | **Date**: 2026-03-12 | **Modules**: 129 | **Sprint**: 29

> v1.1.10 released. Dashboard v2, Telemetry UX, and all Cloud & Auth items delivered.

Authoritative project backlog. Completed items removed; see git history.

---

## Codebase Snapshot (2026-03-12)

| Metric | Value |
| :--- | :--- |
| Source modules | **129** |
| Source files | **2,075** |
| Test files | **1,125** |
| Tests collected | **33,583** |
| Ruff violations | **0** ✅ |
| ty diagnostics | **0** errors |
| Coverage | `fail_under=75`; actual **75.10%** ✅ |
| MCP tools | **474** `@mcp_tool` decorators |
| RASP docs | **129/129** ✅ |
| Oversized files | **0** (all 18 decomposed) ✅ |

---

## ✅ v1.1.10 — "Dashboard v2 & Telemetry UX" (Fully Delivered)

> **Theme**: Production-grade observability, dashboard rebuild, real-time UX.

All deliverables complete. 41/41 targeted tests pass. 8 new files, ~2,100 LOC.

- **Design Tokens**: `website/static/design_tokens.css` — 250+ CSS custom properties (colors, typography, spacing, shadows, animations), dark mode support, responsive shell layout (sidebar + header + content, 480px–1440px breakpoints).
- **Component Library**: Card, Badge, StatusDot, Table, ProgressBar, NavItem, Grid — all using design tokens, responsive across breakpoints.
- **Sparkline Renderer**: `data_visualization/charts/sparkline.py` — inline SVG sparklines with `SparklineConfig`, fill areas, endpoint dots, HTML wrapper.
- **Module DAG Exporter**: `data_visualization/mermaid/dag_exporter.py` — scans source imports, builds `ModuleDAG`, renders layer-styled Mermaid flowcharts.
- **MCP Call-Graph Collector**: `telemetry/tracing/call_graph.py` — `MCPCallGraphCollector` with auto-timed `trace()` context manager, DAG builder, singleton registry.
- **Token Consumption Tracker**: `telemetry/metrics/token_tracker.py` — `TokenTracker` with per-model aggregates, StatsD emission, `get_stats()`/`get_recent()` API.
- **Module Health Provider**: `website/module_health.py` — `ModuleHealthProvider` scanning 129 modules for file count, LOC, test count, doc completeness.
- **Dashboard API**: `website/handlers/dashboard_api.py` — 5 JSON endpoints: `/api/modules`, `/api/costs/summary`, `/api/mcp-call-graph`, `/api/tokens`, `/api/agents/status`.

---

## ✅ v1.1.11 — "Hermetic Distribution & System Verification" (Fully Delivered)

> **Theme**: Package the system for distribution; formal verification foundations.

All deliverables complete. 24/24 targeted tests pass. 5 new files.

- **Multi-stage Dockerfile** — Python 3.13-slim base, uv sync, non-root user (`codo`), health check, <200MB image target.
- **Docker Compose stack** — 4 services: app, Redis 7 (Alpine), Ollama LLM, PM dashboard. Health checks, named volumes, GPU-ready Ollama.
- **CLI entry point** — `codomyrmex = "codomyrmex.cli:main"` in pyproject.toml (pre-existing, verified).
- **GitHub Actions CI** — Pre-existing `ci.yml` and `release.yml` verified functional.
- **MCP Schema Boundary Verifier** — `formal_verification/schema_verifier.py` scans @mcp_tool decorators via AST, verifies function signatures.
- **Config Invariant Checker** — `formal_verification/config_invariants.py` verifies env→yaml→default cascade determinism and precedence.
- **Property-Based Tests** — 5 Hypothesis properties: sparkline round-trip, JSON serialization, config determinism, call-graph consistency, token tracker aggregation.
- **SQLite Session Store** — Pre-existing `agentic_memory/sqlite_store.py` (144 LOC) verified with CRUD tests.
- **GitHub Actions CI** — `ci.yml` and `release.yml` verified present and functional.

---

## ✅ v1.1.12 — "Pre-1.2.0 Polish & Agentic CI" (Fully Delivered)

> **Theme**: Autonomous CI, budget controls, final integration sweep.

All deliverables complete. 34/34 targeted tests pass. 5 new files.

- **Flaky test quarantine** — `ci_cd_automation/flaky_quarantine.py`: sliding window detector, auto-quarantine, pytest marker generation.
- **Dynamic budget manager** — `cost_management/budget_manager.py`: real-time spending enforcement, warning at 80%, auto-pause at 90%, per-model breakdown, webhook registration.
- **WebSocket live feed** — `website/live_feed.py`: typed FeedEvent emissions, bounded deque buffer, timestamp+source+type filtering, system state snapshots.
- **Pre-release audit** — `scripts/maintenance/release_audit.py`: 6 automated quality gate checks (version consistency, Dockerfile, docs, module README coverage, release tests, FIXME markers).

---

## 🔵 v1.2.0 — "Ecosystem Integration & Codomyrmex Prime"

> **Target**: Sprint 36–38
> **Theme**: API freeze, sovereign cloud, CLI maturity, ecosystem lock.

### Sovereign Cloud

| # | Deliverable | Module(s) | Detail | Acceptance |
| :--- | :--- | :--- | :--- | :--- |
| SC1 | **Infomaniak Swift storage** | `cloud/infomaniak/` | Object storage via OpenStack Swift: upload, download, list, delete, presigned URLs | 20+ integration tests with real Swift endpoint |
| SC2 | **Infomaniak Nova compute** | `cloud/infomaniak/` | VM lifecycle: create, list, start/stop, delete, resize | VM boots Ubuntu 24.04 via API in <60s |
| SC3 | **DNS management** | `cloud/infomaniak/` | Zone CRUD, A/AAAA/CNAME record management via Infomaniak API v1 | DNS record propagation verified within 300s |

### CLI Maturity

| # | Deliverable | Module(s) | Detail | Acceptance |
| :--- | :--- | :--- | :--- | :--- |
| CL1 | **`codomyrmex agent start`** | `cli/`, `agents/` | Start named agent with config: `codomyrmex agent start hermes --model gemma3` | Agent responds to health ping within 5s |
| CL2 | **`codomyrmex memory index`** | `cli/`, `agentic_memory/` | Build/rebuild memory index: `codomyrmex memory index --vault ~/obsidian` | Index built from 1000+ notes in <30s |
| CL3 | **`codomyrmex dashboard`** | `cli/`, `website/` | Launch dashboard: `codomyrmex dashboard --port 8787` | Browser opens to running dashboard |
| CL4 | **`codomyrmex test`** | `cli/`, `tests/` | Run test suite: `codomyrmex test --module auth --coverage` | Tests run with per-module coverage report |

### Quality Gate Ratchet

| # | Deliverable | Detail | Acceptance |
| :--- | :--- | :--- | :--- |
| Q1 | **Coverage ≥ 40%** | Ratchet `fail_under` from 35→40% in pyproject.toml | Full test suite passes at 40%+ |
| Q2 | **35,000+ passing tests** | Add property-based + integration tests to reach 35k | `pytest --co -q` reports ≥35,000 collected |
| Q3 | **API freeze** | All 129 module public APIs locked; breaking changes require RFC | `API_SPECIFICATION.md` stamped with v1.2.0 |
| Q4 | **SBOM generation** | `cyclonedx-bom` or `syft` generates Software Bill of Materials | Valid CycloneDX JSON artifact in releases |

---

## 🔮 v1.3.0+ — "Autonomous Evolution & Physical Embodiment"

> **Theme**: Research-grade capabilities pushing toward autonomous systems.

| # | Direction | Module(s) | Concrete Deliverable | Readiness |
| :--- | :--- | :--- | :--- | :--- |
| R1 | **Spatial Reasoning** | `spatial/` (1.2k LOC, 26 classes) | Geodesic transforms, icosahedral mesh generation, 4D rotation quaternions | Foundation exists |
| R2 | **Physical Embodiment** | `embodiment/` (736 LOC, 12 classes) | ROS2 `rclpy` bridge: publish/subscribe topics, service calls, TF2 transforms | Bridge stubbed |
| R3 | **Cerebrum Active Inference** | `cerebrum/` (8.5k LOC, 69 classes) | Free-energy minimization loop, belief revision with Bayesian updates, hierarchical planning | Core engine exists |
| R4 | **Edge Distillation** | new: `quantization/` | INT8/INT4 MLX quantization wrappers; offline inference with <2GB models | Not started |
| R5 | **Decentralized Consensus** | `collaboration/` (6k LOC, 91 classes) | Raft consensus protocol, cryptographic task attestation, distributed agent voting | Collab framework exists |
| R6 | **Plugin Marketplace** | `plugin_system/` (2.3k LOC, 27 classes) | WASM sandbox for untrusted plugins, zero-trust capability vetting, marketplace API | Plugin loader exists |
| R7 | **Bounded Self-Modification** | `security/`, `formal_verification/` | Z3-gated self-rewrite: agent proposes code changes, formal verifier approves | Z3 solver exists |

---

## Quality Gate

> [!IMPORTANT]
> Every method must satisfy: **Real** (no mocks) · **Tested** (zero-mock) · **Validated** (pytest green, lint-free) · **Documented** (docstrings + README/SPEC)

---

## Reference

- **Coverage**: `pyproject.toml [tool.coverage.report] fail_under=75`
- **Test**: `uv run pytest` · **Lint**: `uv run ruff check .` · **Format**: `uv run ruff format .`
- **Type check**: `uv run ty check src/` · **Build**: `uv build`

---

*Last updated: 2026-03-12 — Sprint 29.*
