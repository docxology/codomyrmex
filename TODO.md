<!-- markdownlint-disable MD060 -->
# Codomyrmex — TODO

**Version**: v1.1.8 | **Date**: 2026-03-06 | **Modules**: 127 | **Sprint**: 28

This is the authoritative project backlog. Updated after each sprint.

---

## Codebase Snapshot (Verified 2026-03-06)

| Metric | Value | Method |
| :--- | :--- | :--- |
| Top-level source modules | **127** | `ls -d src/codomyrmex/*/` |
| Source files (non-test) | ~1,800+ | `find -name "*.py" -not -path "*/tests/*"` |
| Total LOC (incl. tests) | ~560,000 | `wc -l` across all `.py` |
| Test files | **944** | `find -name "test_*.py"` |
| Test suite | **26,500+** tests collected | `uv run pytest --collect-only` |
| Ruff violations | **0** | `uv run ruff check .` ✅ |
| Ruff auto-fixed | **10,946+** applied | `uv run ruff check --fix .` |
| Ruff formatted | **3,420+** files | `uv run ruff format --check .` |
| Script parse errors | **0** (46 fixed in v1.1.1) | `python3 -c "import ast"` |
| ty diagnostics | **0** errors (264 warnings) | `uv run ty check src/` ✅ |
| Pass-only function stubs | **4** intentional no-ops | AST analysis |
| Coverage gate | `fail_under=31`; actual ~32% ✅ | Gate ratcheted |
| MCP `@mcp_tool` decorators | **474** | `grep -r '@mcp_tool'` |
| RASP documentation | 127/127 | Automated audit |
| `py.typed` markers | **572** | PEP 561 ✅ |
| Zero-Mock policy | Enforced via ruff | `pyproject.toml` |
| Build backend | **uv_build** | Migrated from hatchling |
| Linter | **ruff** (select=ALL) | Replaced flake8+black+isort |
| Type checker | **ty** (tightened) | Replaced mypy |
| Build artifacts | `codomyrmex-1.1.4.tar.gz` + `.whl` | `uv build` ✅ |

---

## 🟡 v1.1.7 — "Post-Swarm Stabilization & Industrial Hardening"

Addressing the immediate tech debt introduced by the massive Jules Mega-Swarm and locking down ecosystem stability.

### Comprehensive Testing & Security Hardening

| Item | Scope | Technical Detail |
| :--- | :--- | :--- |
| **Zero-Diagnostic Purity** | Root | Sustain 0 `ruff` violations and 0 `ty` type checking errors. Enforce strict type checking in CI. |
| **Coverage ratchet to >40%** | `pyproject.toml` | Aggressively increase `fail_under` to 40. Expand coverage onto `spatial/`, `cerebrum/`, and `graph_rag/` with Zero-Mock purity. |
| **Property-based fuzzing** | `serialization/` | Add `hypothesis` dev-dependency; automate property schema validation across 128 modules. |
| **Mutation testing scale-up** | `pyproject.toml` | Expand `[tool.mutmut]` suite to dynamically mutate core `cache/`, `concurrency/`, and `events/` modules. |
| **AST Codebase De-sloppification** | `tools/` | Create a comprehensive `desloppify` technical debt analyzer that flags god classes, duplicated AST patterns, and missing docstrings. |
| **Sys-health Status CLI**| `cli/` | Construct a `/codomyrmexStatus` tool enabling deep visual diagnostics of the multi-agent graph, active worktrees, and memory buffers. |

---

## 🟣 v1.1.8 — "Agentic Memory & Knowledge Graph Integration"

Maturing the probabilistic knowledge graph and unifying agentic short/long-term memory.

### Next-Gen Cognitive Memory Systems

| Item | Scope | Technical Detail |
| :--- | :--- | :--- |
| **Persistent memory backend** | `agentic_memory/` | Deploy SQLite backend for the `MemoryStore` enabling rich cross-session semantic search with FAISS/Chroma integration. |
| **Obsidian vault bridging** | `agentic_memory/` | Bi-directional seamless synchronization mapping standard Markdown Obsidian states to probabilistic belief vectors. |
| **Graph RAG multi-hop** | `graph_rag` | Implement retrieval-augmented generation capable of multi-hop inference across structured/unstructured entities. |
| **Frisson/Surprise signals** | `cerebrum/` | Develop prediction-error "surprise" (Friston blanket active inference) routing to trigger dynamic swarm deployments. |

---

## 🔵 v1.1.9 — "Multimodal Perception & Sensory Cloud Subsystems"

Establishing full sensorium bridging and external infrastructure provider integration.

### Modality Expansion

| Feature | Depends On | Technical Detail |
| :--- | :--- | :--- |
| **Concrete API Provider Matrix** | `cloud/`, `auth/` | Fully implement zero-mock `boto3`, `faster-whisper`, `edge-tts` with deterministic rate-limiting and rotating quotas. |
| **Audio STT/TTS Streaming** | `audio/` | Implement streaming bi-directional WebSockets for ultra-low latency LLM voice interactions. |
| **Vision/Image Parsing** | `vision/` | Wire VLMs (Qwen-VL, GPT-4o-vision) directly into the scraping pipelines for un-parsed PDF/HTML canvas interpretation. |

---

## 🟢 v1.1.10 — "Dashboard v2 & Telemetry UX"

Gearing towards a richer visual presence ahead of the major 1.2.0 milestone, establishing a reactive telemetry nexus.

### Visual & Telemetry Nexus

| Feature | Depends On | Technical Detail |
| :--- | :--- | :--- |
| **Dashboard v2 Framework**| `website/` | Implement a modern solid-js/Vue scaffold replacing legacy Vanilla JS, utilizing Vite and strict-typing for maximum reactivity. |
| **Data visualization UX** | `data_visualization` | Embed dynamic test-run timelines, live module-health heatmaps, and interactive per-module sparklines powered by D3/Recharts. |
| **Granular Agent Telemetry** | `telemetry/` | Inject deep execution traces into `agent` flows for sub-millisecond latency visibility, token consumption metrics, and tool-call tracing. |
| **Swarm Orchestration UI** | `website/` | Introduce a real-time 'Swarm Command Map' to track active node status, throughput, and error rates of 500+ concurrent Jules agents. |

---

## 🟠 v1.1.11 — "Advanced Orchestration & System Verification"

Strengthening system boundaries and formalizing truth through advanced verification syntax and zero-trust orchestration.

### Formalization & Advanced Distros

| Feature | Depends On | Technical Detail |
| :--- | :--- | :--- |
| **Formal verification synthesis** | `coding/` | Wire `z3-solver` into core schemas for automated invariant checking, guaranteeing boundary logic across the type graph. |
| **Cross-platform hermetic builds** | Root | Establish Homebrew taps, Nix flakes, and `pipx` deployment structures for totally hermetic binary-like distributions. |
| **Distributed Memory scaling** | `database_management` | Implement Alembic declarative schema migrations and hook in an async Redis pub/sub layer for horizontal memory cache scaling. |
| **Containerized Micro-nodes** | `containerization/` | Dockerize all active agent subroutines for K8s deployment, scaling the zero-mock inference graph dynamically across physical clusters. |

---

## 🔴 v1.1.12 — "Pre-1.2.0 Polish & Agentic CI"

Final ecosystem integration and aggressive autonomous CI loop closing before the major 1.2.0 release window.

### Autonomous Continuous Integration

| Feature | Depends On | Technical Detail |
| :--- | :--- | :--- |
| **Agentic CI pipeline (AutoPR)** | `specialized/agents` | Deploy `AutoPR.create()` bots that autonomously patch test failures, resolve tech debt, and submit PRs with 100% Zero-Mock validation. |
| **Dynamic Budget Subsystem** | `events/notification` | Activate hard boundary budget-alarms using live provider telemetry (cost-per-token/millisecond), automatically halting runaway swarms. |
| **Dashboard WebSocket Stream**| `telemetry`, `website` | Finalize bidirectional WebSocket integration, streaming live 60fps telemetry graph updates directly to the web client without manual polling. |
| **1.2.0 Release Candidate Audit** | Root | Comprehensive freeze of schemas, rigorous security audit, trailing dependency bump (uv lock), and documentation final-pass standard verification. |

---

## 🔵 v1.2.0 — "Ecosystem Integration & Codomyrmex Prime"

The culmination of the 1.1.x architectural series bridging the PAI PM server, full zero-mock compliance, real-time sync, and autonomous agentic orchestration into a unified enterprise-grade operating system.

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

- **Coverage gate**: `pyproject.toml [tool.coverage.report] fail_under=31`
- **Test runner**: `uv run pytest`
- **Lint**: `uv run ruff check .`
- **Format**: `uv run ruff format .`
- **Type check**: `uv run ty check src/`
- **Build**: `uv build`
- **Architecture**: `CLAUDE.md` + `PAI.md` + `src/codomyrmex/PAI.md`
- **PAI Integration**: `docs/pai/README.md` + `docs/pai/architecture.md`

---

*Last updated: 2026-03-06 — Sprint 27. Swarm Wave Completion.*
