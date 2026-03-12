<!-- markdownlint-disable MD060 MD033 -->
# Codomyrmex — TODO

**Version**: v1.1.9 | **Date**: 2026-03-12 | **Modules**: 129 | **Sprint**: 28

Authoritative project backlog. Completed items removed; see git history.

---

## Codebase Snapshot (2026-03-12)

| Metric | Value |
| :--- | :--- |
| Source modules | **129** |
| Source files | **2,075** |
| Test files | **1,023** |
| Ruff violations | **0** ✅ |
| ty diagnostics | **0** errors |
| Coverage | `fail_under=75`; actual **75.10%** ✅ |
| MCP tools | **474** `@mcp_tool` decorators |
| RASP docs | **129/129** ✅ |
| Oversized files | **0** (all 16 decomposed) ✅ |

---

## 🔵 v1.1.9 — "Multimodal Perception, Hermes Hardening & Sensory Cloud"

> **Theme**: Full sensorium bridging, Hermes v0.2.0 alignment, and infrastructure provider hardening.

### ✅ Hermes Agent — v0.2.0 (Fully Delivered Sprint 28)

All 19 Hermes v0.2.0 items delivered. See git history for details.

**New modules**: `_provider_router.py` (ProviderRouter, UserModel, ContextCompressor, MCPBridgeManager), `hermes_atropos.py` (HermesAtroposEnvironment RL interface).
**New MCP tools**: `hermes_sampling`, `hermes_mcp_reload`, `hermes_user_context`.
**Enhanced**: `dispatch_hermes.py` (filesystem checkpoints), `hermes_client.py` (fallback model, worktree isolation), `session.py` (lineage), `setup_hermes.py` (MCP bridge + skills checks), `hermes.yaml` (4 new config sections).

### Cloud & Auth Infrastructure

| Item | Module(s) | Deliverable | Acceptance |
| :--- | :--- | :--- | :--- |
| **API Provider Matrix** | `cloud/`, `auth/` | Zero-mock `boto3`, `faster-whisper`, `edge-tts` clients with rate-limiting | Each provider passes 20+ integration tests |
| **Credential rotation** | `auth/`, `secrets/` | Automated rotation with TTL-aware caching | Secrets rotate without downtime |
| **Cost accounting** | `telemetry/`, `cloud/` | Per-call cost attribution hooks | Dashboard displays running cost totals |
| **VLM pipeline** | `vision/`, `scraping/` | VLM fallback for scanned PDFs and HTML canvases | Mixed PDF/HTML inputs end-to-end |

---

## 🟢 v1.1.10 — "Dashboard v2 & Telemetry UX"

> **Target**: Sprint 31–32

| Area | Items |
| :--- | :--- |
| **Dashboard v2** | Solid.js/Vue scaffold; component library with design tokens; responsive layout (480→1440px) |
| **Data Visualization** | Test-run timelines; module health heatmap; per-module sparklines |
| **Agent Telemetry** | OpenTelemetry traces; token consumption dashboards; MCP call-graph DAG |
| **Swarm UI** | Real-time node-status grid (500+ agents); throughput & error-rate gauges |

---

## 🟠 v1.1.11 — "Advanced Orchestration & System Verification"

> **Target**: Sprint 33–34

| Area | Items |
| :--- | :--- |
| **Formal Verification** | Z3 invariant synthesis, schema boundary proofs |
| **Hermetic Distribution** | Homebrew tap, Nix flake, pipx deployment |
| **Horizontal Memory** | Alembic migrations, Redis pub/sub cache layer |
| **Containerization** | Multi-stage Dockerfile per agent, Helm + HPA |

---

## 🔴 v1.1.12 — "Pre-1.2.0 Polish & Agentic CI"

> **Target**: Sprint 35–36

| Area | Items |
| :--- | :--- |
| **Autonomous CI** | AutoPR bot, CI self-healing, flaky test quarantine |
| **Budget & Cost** | Dynamic budget subsystem, spend attribution dashboard |
| **Final Integration** | WebSocket finalization, 1.2.0 RC audit |

---

## 🔵 v1.2.0 — "Ecosystem Integration & Codomyrmex Prime"

> **Target**: Sprint 37–38

| Feature | Detail |
| :--- | :--- |
| **Infomaniak Sovereign Cloud** | Swift storage, Nova compute, DNS via API v1 |
| **Swarm CLI** | `codomyrmex agent start`, `memory index`, `dashboard serve` |
| **Zero-Mock Gate** | Hard block if coverage < 50%; 30,000+ passing tests |
| **1.2.0 Freeze** | All 129 APIs frozen; schemas locked; SBOM generated |

---

## 🔮 v1.3.0+ — "Autonomous Evolution & Physical Embodiment"

| Direction | Module | Notes |
| :--- | :--- | :--- |
| **Spatial Reasoning** | `spatial/` | Geodesic transforms, 4D rotations, icosahedral meshes |
| **Physical Embodiment** | `embodiment/` | ROS2 `rclpy` bindings for LLM↔robot interaction |
| **Cerebrum Architecture** | `cerebrum/` | Active inference, belief revision, hierarchical planning |
| **Edge Distillation** | `quantization/` | INT8/INT4 MLX wrappers for offline inference |
| **Decentralization** | `collaboration/` | Raft consensus, cryptographic task negotiations |
| **Plugin Marketplace** | `plugin_system/` | WASM sandbox, zero-trust capability vetting |
| **Self-Modification** | `security/` | Bounded self-rewrite with Z3 formal gates |

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

*Last updated: 2026-03-12 — Sprint 28.*
