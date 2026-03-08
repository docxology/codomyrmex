<!-- markdownlint-disable MD060 MD033 -->
# Codomyrmex — TODO

**Version**: v1.1.9 | **Date**: 2026-03-07 | **Modules**: 130 | **Sprint**: 28

This is the authoritative project backlog. Updated after each sprint.

---

## Codebase Snapshot (Verified 2026-03-07 18:25)

| Metric | Value | Method |
| :--- | :--- | :--- |
| Top-level source modules | **130** | `ls -d src/codomyrmex/*/` |
| Source files (non-test) | **2,075** | `find -name "*.py" -not -path "*/tests/*"` |
| Test files | **1,023** | `find -name "test_*.py"` |
| Test unit dirs | **162** | Module-level test directories |
| Ruff violations | **0** | `uv run ruff check .` ✅ |
| ty diagnostics | **0** errors (264 warnings) | `uv run ty check src/` ✅ |
| Coverage gate | `fail_under=32`; actual ~32% ✅ | Gate ratcheted (target: 40%) |
| GitNexus index | **77,101** symbols, **178,276** relationships | `npx gitnexus analyze` |
| MCP `@mcp_tool` decorators | **474** | `grep -r '@mcp_tool'` |
| RASP documentation | 128/128 | Automated audit ✅ |
| `py.typed` markers | **572** | PEP 561 ✅ |
| Zero-Mock policy | Enforced via ruff | `pyproject.toml` |
| Build backend | **uv_build** | Migrated from hatchling |
| Linter | **ruff** (select=ALL) | Replaced flake8+black+isort |
| Type checker | **ty** (tightened) | Replaced mypy |

---

## 🔴 Active Debt (Sprint 28 — Immediate)

### Coverage Gap: 32% → 40%

Current coverage is ~32% (126,615 stmts). Need ~9,700 more statements covered.

**Sprint 28 coverage test campaign**: 13 dedicated coverage test files (this session) + 30+ module-level `test_*_core.py` / `test_*_mcp_tools.py` files (parallel session). Total 162 test unit dirs.

| Module Group | Coverage Tests | Status |
| :--- | :--- | :--- |
| **P1 — largest gaps** | | |
| `documentation` (14.1%, 3,716 missing) | ✅ `test_documentation_coverage.py` | Written |
| `cli` (16.5%, 1,513 missing) | ✅ `test_cli_coverage.py` | Written |
| `git_operations` (19.3%, 2,644 missing) | ✅ `test_git_operations_coverage.py` | Written |
| `physical_management` | ✅ `test_physical_management_coverage.py` (50 tests) | Written |
| `collaboration` | ✅ `test_collaboration_coverage.py` (84 tests) | Written |
| **P2 — mid-range** | | |
| `cerebrum` (26%, 2,190 missing) | ✅ `test_cerebrum_coverage.py` + `test_cerebrum_deep_coverage.py` | Written |
| `config_management` | ✅ `test_config_management_coverage.py` + `test_config_management_core.py` | Written |
| `data_visualization` | ✅ `test_data_visualization_coverage.py` | Written |
| `agentic_memory` | ✅ `test_agentic_memory_coverage.py` | Written |
| `cloud` | ✅ `test_cloud_coverage.py` + `test_cloud_deep_coverage.py` | Written |
| **P3+ — parallel session (30+ modules)** | | |
| `auth`, `cache`, `compression` | ✅ `test_*_core.py` / `test_*_mcp_tools.py` | Written |
| `concurrency`, `crypto`, `defense` | ✅ `test_*_core.py` | Written |
| `deployment`, `events`, `formal_verification` | ✅ `test_*_core.py` | Written |
| `logging_monitoring`, `maintenance`, `model_ops` | ✅ `test_*_core.py` | Written |
| `networking`, `plugin_system`, `relations` | ✅ `test_*_core.py` | Written |
| `scrape`, `search`, `serialization` | ✅ `test_*_core.py` | Written |
| `static_analysis`, `telemetry`, `utils` | ✅ `test_*_core.py` / `test_*_mcp_tools.py` | Written |
| `validation`, `vector_store`, `video` | ✅ `test_*_core.py` / `test_*_mcp_tools.py` | Written |

**Next step**: Run full suite with `--cov` to measure actual coverage delta from all new test files. Ratchet `fail_under` gate upward as coverage increases.

### ~~TODO/FIXME/HACK/XXX Triage~~ ✅ Done

Triaged: all 189 grep hits are test data strings (pattern_matching fixtures) or template generators (`coding/test_generator.py`). **Zero real actionable TODO/FIXME/HACK/XXX comments in production source.**

### Oversized Files (13 remaining >800 LOC)

✅ **Done**: `physical_management/object_manager.py` (951→645 LOC) → extracted `models.py` (330 LOC)

| File | LOC | Action |
| :--- | :--- | :--- |
| `cerebrum/fpf/orchestration.py` | 980 | Extract pipeline stages |
| `data_visualization/git/git_visualizer.py` | 970 | Split chart types |
| `cloud/coda_io/models.py` | 944 | Split data models |
| `ci_cd_automation/pipeline/manager.py` | 932 | Extract step handlers |
| `llm/ollama/model_runner.py` | 930 | Separate download/run |
| `cerebrum/fpf/combinatorics.py` | 915 | Extract solver classes |
| `config_management/core/config_loader.py` | 867 | Split file/env/merge |
| `agents/pai/trust_gateway.py` | 854 | Extract verification |
| `agents/droid/generators/physical_generators/doc_generators.py` | 854 | Template per doc type |
| `documentation/scripts/documentation_scan_report.py` | 850 | Extract reporters |
| `terminal_interface/shells/interactive_shell.py` | 848 | Separate REPL/completion |
| `agents/droid/generators/spatial.py` | 842 | Extract transform types |
| `agents/ai_code_editing/claude_task_master.py` | 827 | Separate task/exec |

---

## 🔵 v1.1.9 — "Multimodal Perception & Sensory Cloud Subsystems"

> **Theme**: Full sensorium bridging and external infrastructure provider hardening.
> **Target**: Sprint 29–30

### ✅ Delivered (v1.1.9)

- **Streaming Audio Pipeline** — `audio/streaming/` with `AudioStreamServer`, `AudioStreamClient`, `CodecNegotiator`, energy-based VAD
- **Vision Module** — `vision/` with `VLMClient`, `PDFExtractor`, `AnnotationExtractor` (Ollama local-first)
- **Hermes Agent** — Dual-backend (`hermes3` CLI + Ollama), session persistence, prompt template library
- **OpenFang Agent** — `agents/openfang/` with core, hands, update, config, exceptions, MCP tools (7 source files)
- **Version Sync** — 17,000+ files synchronized to v1.1.9; RASP 128/128; ruff 0 violations
- **RASP Completion** — `vision/PAI.md` and `languages/PAI.md` created; 128/128 modules documented
- **Modularization** — `physical_management/object_manager.py` (951→645 LOC) → `models.py` (330 LOC)
- **Zero-Mock Test Campaign** — 1,023 test files across 162 unit test directories; 30+ modules with new `_core.py`/`_mcp_tools.py` tests
- **GitNexus Re-Index** — 77,101 symbols, 178,276 relationships, 300 execution flows

### Remaining (v1.1.9)

| Item | Module(s) | Deliverable | Acceptance Criteria |
| :--- | :--- | :--- | :--- |
| **Concrete API Provider Matrix** | `cloud/`, `auth/` | Zero-mock `boto3`, `faster-whisper`, `edge-tts` clients with rate-limiting | Each provider passes 20+ integration tests |
| **Provider credential rotation** | `auth/`, `secrets/` | Automated credential rotation with TTL-aware caching | Secrets rotate without downtime |
| **Cost accounting per provider** | `telemetry/`, `cloud/` | Per-call cost attribution hooks | Dashboard displays running cost totals |
| **VLM pipeline integration** | `vision/`, `scraping/` | VLM fallback for scanned PDFs and HTML canvases | Mixed PDF/HTML inputs processed end-to-end |

---

## 🟢 v1.1.10 — "Dashboard v2 & Telemetry UX"

> **Theme**: Reactive telemetry nexus and rich visual presence ahead of v1.2.0.
> **Target**: Sprint 31–32

### Dashboard v2 Framework

| Item | Module(s) | Deliverable | Acceptance Criteria |
| :--- | :--- | :--- | :--- |
| **Framework migration** | `website/` | Modern Solid.js/Vue scaffold replacing legacy Vanilla JS; Vite + strict TypeScript | Dev server starts in < 3s; all 15 existing tabs ported; zero runtime TS errors |
| **Component library** | `website/` | Reusable component set (cards, charts, tables, modals) with design tokens | Storybook catalog with 20+ component variants |
| **Responsive layout system** | `website/` | Mobile-first responsive grid; breakpoints at 480/768/1024/1440px | Lighthouse mobile score ≥ 90 |

### Data Visualization

| Item | Module(s) | Deliverable | Acceptance Criteria |
| :--- | :--- | :--- | :--- |
| **Test-run timelines** | `data_visualization/` | Interactive D3/Recharts timeline of test execution history | Click-to-drill into individual test results |
| **Module health heatmap** | `data_visualization/` | Live heatmap of per-module coverage, lint status, and test pass-rate | Auto-refreshes via WebSocket push |
| **Per-module sparklines** | `data_visualization/` | Inline trend indicators for coverage, LOC, and error counts | Sparklines render for all 128 modules |

### Agent Telemetry

| Item | Module(s) | Deliverable | Acceptance Criteria |
| :--- | :--- | :--- | :--- |
| **Execution trace injection** | `telemetry/` | Sub-millisecond latency traces with OpenTelemetry spans | Traces visible in Jaeger/Zipkin; p99 overhead < 2ms |
| **Token consumption metrics** | `telemetry/` | Per-agent, per-model token usage dashboards | Real-time counters; historical 7-day rollup |
| **Tool-call tracing** | `telemetry/` | Full call-graph visualization of MCP tool invocations | DAG rendered in dashboard |

### Swarm Orchestration UI

| Item | Module(s) | Deliverable | Acceptance Criteria |
| :--- | :--- | :--- | :--- |
| **Swarm Command Map** | `website/` | Real-time node-status grid for 500+ concurrent Jules agents | WebSocket-driven; < 2s state transitions |
| **Throughput & error rate panels** | `website/` | Live throughput and error-rate gauges | Gauges update at 1Hz |

---

## 🟠 v1.1.11 — "Advanced Orchestration & System Verification"

> **Theme**: Formal truth-checking, hermetic distribution, and horizontal scaling.
> **Target**: Sprint 33–34

| Area | Items |
| :--- | :--- |
| **Formal Verification** | Z3 invariant synthesis (`coding/`), schema boundary proofs (`serialization/`) |
| **Hermetic Distribution** | Homebrew tap, Nix flake, pipx deployment |
| **Horizontal Memory** | Alembic migrations (`database_management/`), Redis pub/sub cache layer |
| **Containerization** | Multi-stage Dockerfile per agent, Helm chart with HPA auto-scaling |

---

## 🔴 v1.1.12 — "Pre-1.2.0 Polish & Agentic CI"

> **Theme**: Autonomous CI loop closing and final integration gate before v1.2.0.
> **Target**: Sprint 35–36

| Area | Items |
| :--- | :--- |
| **Autonomous CI** | AutoPR bot, CI self-healing + flaky test quarantine |
| **Budget & Cost Control** | Dynamic budget subsystem, spend attribution dashboard |
| **Final Integration** | WebSocket stream finalization, 1.2.0 Release Candidate Audit |

---

## 🔵 v1.2.0 — "Ecosystem Integration & Codomyrmex Prime"

> **Theme**: Convergence of the 1.1.x series into a unified, enterprise-grade platform.
> **Target**: Sprint 37–38

| Feature | Technical Detail |
| :--- | :--- |
| **Infomaniak Sovereign Cloud** | Storage (Swift), compute (Nova), DNS via Infomaniak API v1 |
| **Swarm CLI "Codomyrmex Prime"** | `codomyrmex agent start`, `codomyrmex memory index`, `codomyrmex dashboard serve` |
| **100% Zero-Mock Gate** | Hard block if coverage < 50%; gating on 30,000+ passing tests |
| **1.2.0 Cut & Freeze** | All 128 module APIs frozen; serialization schemas locked; SBOM generated |

---

## 🔮 v1.3.0+ — "Autonomous Evolution & Physical Embodiment"

| Direction | Module | Notes |
| :--- | :--- | :--- |
| **Spatial Reasoning & Synergetics** | `spatial/` | Fuller geodesic transforms, 4D rotations, icosahedral meshes |
| **Physical Embodiment & ROS2** | `embodiment/` | `rclpy` bindings for LLM↔robot chassis interaction |
| **Cerebrum Cognitive Architecture** | `cerebrum/` | Active inference, dynamic belief revision, hierarchical planning |
| **Local Inference & Edge Distillation** | `quantization/` | INT8/INT4 MLX wrappers for Qwen 1.5B/Llama 3 8B offline |
| **Secure Autonomous Decentralization** | `collaboration/` | Raft consensus, cryptographic task negotiations |
| **Open Plugin Marketplace** | `plugin_system/` | WebAssembly sandbox, zero-trust capability vetting |
| **Self-Modifying Architecture** | `security/` | Bounded self-rewrite with Z3 formal verification gates |

---

## Release Quality Gate Standard

> [!IMPORTANT]
> Every method **must** satisfy all four criteria before the release tag:
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
