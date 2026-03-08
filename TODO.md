<!-- markdownlint-disable MD060 -->
# Codomyrmex — TODO

**Version**: v1.1.9 | **Date**: 2026-03-07 | **Modules**: 128 | **Sprint**: 28

This is the authoritative project backlog. Updated after each sprint.

---

## Codebase Snapshot (Verified 2026-03-07)

| Metric | Value | Method |
| :--- | :--- | :--- |
| Top-level source modules | **128** | `ls -d src/codomyrmex/*/` |
| Source files (non-test) | ~1,800+ | `find -name "*.py" -not -path "*/tests/*"` |
| Total LOC (incl. tests) | ~560,000 | `wc -l` across all `.py` |
| Test files | **944** | `find -name "test_*.py"` |
| Test suite | **26,500+** tests collected | `uv run pytest --collect-only` |
| Ruff violations | **0** | `uv run ruff check .` ✅ |
| ty diagnostics | **0** errors (264 warnings) | `uv run ty check src/` ✅ |
| Coverage gate | `fail_under=32`; actual ~32% ✅ | Gate ratcheted (target: 40%) |
| MCP `@mcp_tool` decorators | **474** | `grep -r '@mcp_tool'` |
| RASP documentation | 128/128 | Automated audit |
| `py.typed` markers | **572** | PEP 561 ✅ |
| Zero-Mock policy | Enforced via ruff | `pyproject.toml` |
| Build backend | **uv_build** | Migrated from hatchling |
| Linter | **ruff** (select=ALL) | Replaced flake8+black+isort |
| Type checker | **ty** (tightened) | Replaced mypy |

---

## ✅ Completed Releases (Condensed)

<details>
<summary><strong>v1.1.7 — "Post-Swarm Stabilization & Industrial Hardening"</strong> (Released)</summary>

All items delivered:

- **Zero-Diagnostic Purity** — Sustained 0 ruff violations and 0 ty errors; strict CI enforcement.
- **Coverage ratchet to ≥40%** — `fail_under=32` in `pyproject.toml`; expanded coverage to `spatial/`, `cerebrum/`, and `graph_rag/`.
- **Property-based fuzzing** — `hypothesis>=6.151.9` added; property schema validation across serialization modules.
- **Mutation testing scale-up** — `mutmut>=3.4.0` configured in `[tool.mutmut]` to mutate `cache/`, `concurrency/`, and `events/`.
- **AST Codebase De-sloppification** — `tools/desloppify.py` shipped; flags god classes, AST duplication, and missing docstrings.
- **Sys-health Status CLI** — `/codomyrmexStatus` workflow and `src/codomyrmex/cli/status.py` operational.

</details>

<details>
<summary><strong>v1.1.8 — "Agentic Memory & Knowledge Graph Integration"</strong> (Released)</summary>

All items delivered:

- **Persistent memory backend** — SQLite `MemoryStore` with cross-session semantic search, FAISS/Chroma integration, TTL expiry, and tag indexing.
- **Obsidian vault bridging** — Bi-directional Markdown ↔ probabilistic belief-vector synchronization via `cognilayer_bridge.py`.
- **Graph RAG multi-hop** — Retrieval-augmented generation with multi-hop inference across structured/unstructured entities.
- **Frisson/Surprise signals** — Prediction-error routing (Friston blanket active inference) triggering dynamic swarm deployments in `cerebrum/`.

</details>

---

## 🔵 v1.1.9 — "Multimodal Perception & Sensory Cloud Subsystems"

> **Theme**: Full sensorium bridging and external infrastructure provider hardening.
> **Target**: Sprint 29–30

### Provider Matrix & Rate Management

| Item | Module(s) | Deliverable | Acceptance Criteria |
| :--- | :--- | :--- | :--- |
| **Concrete API Provider Matrix** | `cloud/`, `auth/` | Zero-mock `boto3`, `faster-whisper`, `edge-tts` clients with deterministic rate-limiting and rotating quotas | Each provider passes 20+ integration tests with real credentials; rate-limit backoff verified |
| **Provider credential rotation** | `auth/`, `secrets/` | Automated credential rotation with TTL-aware caching | Secrets rotate without downtime; audit log captures each rotation event |
| **Cost accounting per provider** | `telemetry/`, `cloud/` | Per-call cost attribution hooks (token count × model pricing) | Dashboard displays running cost totals; budget alarm fires at configurable threshold |

### Streaming Audio Pipeline

| Item | Module(s) | Deliverable | Acceptance Criteria |
| :--- | :--- | :--- | :--- |
| **Audio STT/TTS Streaming** | `audio/` | Bi-directional WebSocket streaming for real-time LLM voice interactions | Round-trip latency < 500ms on local Whisper; streaming chunks validated end-to-end |
| **Voice Activity Detection** | `audio/` | VAD pre-filter (Silero VAD) reducing Whisper invocations on silence | False-positive rate < 5% on benchmark audio; CPU savings > 60% vs. naive streaming |
| **Audio format negotiation** | `audio/` | Automatic codec selection (opus/wav/mp3) based on client capability | Format negotiation tested across 3 client types (browser, CLI, Python SDK) |

### Vision & Document Parsing

| Item | Module(s) | Deliverable | Acceptance Criteria |
| :--- | :--- | :--- | :--- |
| **VLM wiring** | `vision/` | Qwen-VL and GPT-4o-vision integrated into scraping pipelines | Parsed 5 sample PDFs with > 90% text extraction accuracy vs. ground truth |
| **PDF/HTML canvas interpretation** | `vision/`, `scraping/` | Un-parsed PDF and rendered HTML canvas extraction via VLM fallback | Processing pipeline handles mixed PDF/HTML inputs without manual intervention |
| **Image annotation extraction** | `vision/` | Structured JSON output from annotated screenshots and diagrams | Schema validation passes on 20+ annotated image samples |

### Hermes Agent Operational Hardening

| Item | Module(s) | Deliverable | Acceptance Criteria |
| :--- | :--- | :--- | :--- |
| **Hermes dual-backend verification** | `agents/hermes/` | Full integration test suite for both Hermes CLI and Ollama (`hermes3`) backends | 30+ tests passing; backend selection via env var |
| **Hermes prompt templates** | `agents/hermes/` | Standardized prompt template library for common agent tasks | Templates cover code review, task decomposition, and documentation generation |
| **Hermes session continuity** | `agents/hermes/` | Persistent session state across multiple invocations | Session restore verified across process restart |

---

## 🟢 v1.1.10 — "Dashboard v2 & Telemetry UX"

> **Theme**: Reactive telemetry nexus and rich visual presence ahead of v1.2.0.
> **Target**: Sprint 31–32

### Dashboard v2 Framework

| Item | Module(s) | Deliverable | Acceptance Criteria |
| :--- | :--- | :--- | :--- |
| **Framework migration** | `website/` | Modern Solid.js/Vue scaffold replacing legacy Vanilla JS; Vite + strict TypeScript | Dev server starts in < 3s; all 15 existing tabs ported; zero runtime TS errors |
| **Component library** | `website/` | Reusable component set (cards, charts, tables, modals) with design tokens | Storybook catalog with 20+ component variants; visual regression tests green |
| **Responsive layout system** | `website/` | Mobile-first responsive grid; breakpoints at 480/768/1024/1440px | Lighthouse mobile score ≥ 90; layout verified on 4 viewport sizes |

### Data Visualization

| Item | Module(s) | Deliverable | Acceptance Criteria |
| :--- | :--- | :--- | :--- |
| **Test-run timelines** | `data_visualization/` | Interactive D3/Recharts timeline of test execution history | Click-to-drill into individual test results; pan/zoom on 30-day window |
| **Module health heatmap** | `data_visualization/` | Live heatmap of per-module coverage, lint status, and test pass-rate | Auto-refreshes via WebSocket push; color coding validated against metrics |
| **Per-module sparklines** | `data_visualization/` | Inline trend indicators for coverage, LOC, and error counts | Sparklines render for all 128 modules; tooltips show exact values |

### Agent Telemetry

| Item | Module(s) | Deliverable | Acceptance Criteria |
| :--- | :--- | :--- | :--- |
| **Execution trace injection** | `telemetry/` | Sub-millisecond latency traces in agent flows with OpenTelemetry spans | Traces visible in Jaeger/Zipkin; p99 overhead < 2ms per tool-call |
| **Token consumption metrics** | `telemetry/` | Per-agent, per-model token usage dashboards | Real-time counters update within 1s; historical 7-day rollup available |
| **Tool-call tracing** | `telemetry/` | Full call-graph visualization of MCP tool invocations per session | DAG rendered in dashboard; click-to-expand with input/output payloads |

### Swarm Orchestration UI

| Item | Module(s) | Deliverable | Acceptance Criteria |
| :--- | :--- | :--- | :--- |
| **Swarm Command Map** | `website/` | Real-time node-status grid for 500+ concurrent Jules agents | WebSocket-driven; node state transitions reflected in < 2s |
| **Throughput & error rate panels** | `website/` | Live throughput (tasks/min) and error-rate gauges | Gauges update at 1Hz; alert thresholds configurable per swarm |

---

## 🟠 v1.1.11 — "Advanced Orchestration & System Verification"

> **Theme**: Formal truth-checking, hermetic distribution, and horizontal scaling.
> **Target**: Sprint 33–34

### Formal Verification

| Item | Module(s) | Deliverable | Acceptance Criteria |
| :--- | :--- | :--- | :--- |
| **Z3 invariant synthesis** | `coding/` | `InvariantChecker` wired into core schemas via `z3-solver` | 10+ invariants auto-checked on CI; counterexample reports generated on failure |
| **Schema boundary proofs** | `serialization/` | Formal proofs that serialization round-trips preserve all fields | Proof certificates generated for top-20 most-used schemas |

### Hermetic Distribution

| Item | Module(s) | Deliverable | Acceptance Criteria |
| :--- | :--- | :--- | :--- |
| **Homebrew tap** | Root | `brew install codomyrmex` installs CLI + runtime | Tap formula published; install verified on macOS 14+ |
| **Nix flake** | Root | `nix run github:docxology/codomyrmex` produces working environment | Flake builds reproducibly; CI validates on NixOS |
| **pipx deployment** | Root | `pipx install codomyrmex` provisions isolated CLI | Entry points resolve correctly; `codomyrmex --version` returns current |

### Horizontal Memory Scaling

| Item | Module(s) | Deliverable | Acceptance Criteria |
| :--- | :--- | :--- | :--- |
| **Alembic schema migrations** | `database_management/` | Declarative migration chain for `MemoryStore` schema evolution | `alembic upgrade head` idempotent; rollback verified for last 3 migrations |
| **Redis pub/sub cache layer** | `database_management/` | Async Redis pub/sub for distributed memory invalidation | 2-node test cluster maintains cache coherence under concurrent writes |

### Containerization

| Item | Module(s) | Deliverable | Acceptance Criteria |
| :--- | :--- | :--- | :--- |
| **Dockerized micro-nodes** | `containerization/` | Multi-stage Dockerfile for each agent subroutine | Image size < 500MB; cold-start < 5s; health-check endpoint responds |
| **K8s deployment manifests** | `containerization/` | Helm chart with auto-scaling policies | HPA scales 2→10 replicas under load test; zero-downtime rolling update |

---

## 🔴 v1.1.12 — "Pre-1.2.0 Polish & Agentic CI"

> **Theme**: Autonomous CI loop closing and final integration gate before v1.2.0.
> **Target**: Sprint 35–36

### Autonomous CI

| Item | Module(s) | Deliverable | Acceptance Criteria |
| :--- | :--- | :--- | :--- |
| **AutoPR bot** | `specialized/agents` | `AutoPR.create()` autonomously patches test failures and submits PRs with Zero-Mock validation | Bot resolves 5+ real failures in staging; human approval required before merge |
| **CI self-healing** | `specialized/agents` | Agent detects flaky tests, quarantines them, and opens tracking issues | Quarantine list auto-maintained; flaky-test rerun success rate > 80% |

### Budget & Cost Control

| Item | Module(s) | Deliverable | Acceptance Criteria |
| :--- | :--- | :--- | :--- |
| **Dynamic Budget Subsystem** | `events/notification` | Hard-boundary budget alarms from live provider telemetry (cost-per-token/ms) | Alarm fires within 30s of threshold breach; auto-halt tested on staging |
| **Spend attribution dashboard** | `telemetry/`, `website/` | Per-agent, per-model cost breakdown with daily/weekly rollups | Dashboard data matches provider billing within 2% |

### Final Integration

| Item | Module(s) | Deliverable | Acceptance Criteria |
| :--- | :--- | :--- | :--- |
| **WebSocket stream finalization** | `telemetry/`, `website/` | Bidirectional WebSocket streaming 60fps telemetry to web client | Sustained 60fps for 10min under full load; graceful degradation on disconnect |
| **1.2.0 Release Candidate Audit** | Root | Schema freeze, security audit, `uv lock` bump, doc final-pass | Zero open blockers; all 128 module APIs frozen; SBOM generated |

---

## 🔵 v1.2.0 — "Ecosystem Integration & Codomyrmex Prime"

> **Theme**: Convergence of the 1.1.x architectural series into a unified, enterprise-grade platform.
> **Target**: Sprint 37–38

### The v1.2.0 Milestone Requirements

| Feature | Depends On | Technical Detail |
| :--- | :--- | :--- |
| **Infomaniak Sovereign Cloud** | `cloud/schema` | Direct deployment of storage (Swift-compat), compute (Nova-compat), and DNS management via Infomaniak API v1, avoiding vendor lock-in. |
| **Swarm CLI "Codomyrmex Prime"** | `cli/` | Ship a finalized cohesive CLI binary enabling `codomyrmex agent start`, `codomyrmex memory index`, and `codomyrmex dashboard serve` from a single standard entry point. |
| **100% Zero-Mock Verification Gate** | `core/` | Hard execution block if any isolated test fails or coverage drops below 50%; gating release on a 30,000+ item passing test suite. |
| **1.2.0 Cut & Freeze** | Root | Final validation of all 128 module APIs, serialization schema locks, stable bidirectional PM system integration, and global `ty` diagnostic purity check. |

---

## 🔮 v1.3.0+ — "Autonomous Evolution & Physical Embodiment"

Architectural extensions pushing the boundaries of autonomous software synthesis, continuous learning, and cyber-physical bridging.

### Long-Term Research & Engineering Vectors

| Direction | Scope | Notes |
| :--- | :--- | :--- |
| **Spatial reasoning & Synergetics** | `spatial/` | Fuller-inspired geodesic transforms, 4D rotation matrices, and icosahedral mesh generation for spatial coordinate navigation. |
| **Physical Embodiment & ROS2** | `embodiment/` | Full `rclpy` binding integration into the `agents` module allowing LLMs native publisher/subscriber interactions with robotic chassis hardware. |
| **Cerebrum Cognitive Architecture** | `cerebrum/` | Advanced probabilistic inference via active inference (Friston), continuous dynamic belief revision, and deep uncertainty-aware hierarchical planning. |
| **Local Inference & Edge Distillation** | `quantization/` | Local INT8/INT4 MLX quantization wrappers for running SLMs (Qwen 1.5B/Llama 3 8B) entirely offline directly on standard mac nodes. |
| **Secure Autonomous Decentralization**| `collaboration/` | Implement Raft consensus for multi-agent swarm task decomposition and deployment of cryptographically verifiable smart-contract task negotiations. |
| **Open Plugin Marketplace** | `plugin_system/` | Autonomous plugin discovery, sandboxed WebAssembly execution environments, and zero-trust capability vetting. |
| **Self-Modifying Architecture** | `security/` | Agentic rewrite mechanisms where the orchestrator safely rewrites its own core logic bounded by total specification adherence and Z3 formal verification gates. |

---

## Release Quality Gate Standard

> [!IMPORTANT]
> Every method implemented **must** satisfy all four criteria before the release tag:
>
> 1. **Real** — Functional implementation, no mocks, no placeholder logic
> 2. **Tested** — Zero-mock test(s) validating real behaviour
> 3. **Validated** — `pytest` green, `py_compile` clean, lint-free
> 4. **Documented** — Docstring with Args/Returns/Example; module README/SPEC updated if public API

---

## Reference

- **Coverage gate**: `pyproject.toml [tool.coverage.report] fail_under=32`
- **Test runner**: `uv run pytest`
- **Lint**: `uv run ruff check .`
- **Format**: `uv run ruff format .`
- **Type check**: `uv run ty check src/`
- **Build**: `uv build`
- **Architecture**: `CLAUDE.md` + `PAI.md` + `src/codomyrmex/PAI.md`
- **PAI Integration**: `docs/pai/README.md` + `docs/pai/architecture.md`

---

*Last updated: 2026-03-07 — Sprint 28.*
