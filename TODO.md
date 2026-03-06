<!-- markdownlint-disable MD060 -->
# Codomyrmex — TODO

**Version**: v1.1.7 | **Date**: 2026-03-06 | **Modules**: 127 | **Sprint**: 27

This is the authoritative project backlog. Updated after each sprint.

---

## Codebase Snapshot (Verified 2026-03-06)

| Metric | Value | Method |
| :--- | :--- | :--- |
| Top-level source modules | **127** | `ls -d src/codomyrmex/*/` |
| Source files (non-test) | ~1,800+ | `find -name "*.py" -not -path "*/tests/*"` |
| Total LOC (incl. tests) | ~560,000 | `wc -l` across all `.py` |
| Test files | **944** | `find -name "test_*.py"` |
| Test suite | **21,000+** tests collected | `uv run pytest --collect-only` |
| Ruff violations | **332** | `uv run ruff check .` 🔴 |
| Ruff auto-fixed | **10,946+** applied | `uv run ruff check --fix .` |
| Ruff formatted | **3,420+** files | `uv run ruff format --check .` |
| Script parse errors | **0** (46 fixed in v1.1.1) | `python3 -c "import ast"` |
| ty diagnostics | **1,451** (target <1,000) | `uv run ty check src/` 🔴 |
| Pass-only function stubs | **4** intentional no-ops | AST analysis |
| Coverage gate | `fail_under=31`; actual ~32% ✅ | Gate ratcheted |
| MCP `@mcp_tool` decorators | **545** | `grep -r '@mcp_tool'` |
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

### Expanded Testing Methodologies & Stabilization

| Item | Scope | Technical Detail |
| :--- | :--- | :--- |
| **Lint & Type Burn-down** | Root | Burn down the 332 `ruff` violations and 1,451 `ty` diagnostics introduced by the swarm patches. |
| **Coverage gate ratchet** | `pyproject.toml` | Bump `fail_under` to 38. Expand coverage onto `spatial/`, `cerebrum/`, and `graph_rag/`. |
| **Property-based testing** | `serialization/` | Add `hypothesis` dev-dependency; write robust property tests (`@given`) for schema validators and data round-trips. |
| **Mutation testing scale-up** | `pyproject.toml` | Expand `[tool.mutmut]` from 6 to 12 targets (e.g., `cache/core.py`, `concurrency/core.py`, `events/core.py`). |
| **Flaky testing tracking** | `pyproject.toml` | Apply `@pytest.mark.flaky(reruns=2)` using `pytest-rerunfailures` to explicitly track and document CI flakes. |

---

## 🟣 v1.1.8 — "Agentic Memory & Knowledge Graph Foundation"

Maturing the knowledge graph and agentic memory models to persistent forms.

### Memory Systems

| Item | Scope | Technical Detail |
| :--- | :--- | :--- |
| **Agentic memory backend** | `agentic_memory/` | Deploy SQLite backend for the `MemoryStore` enabling cross-session retrieval, TTL expiry, and tag indexing. |
| **Obsidian integration** | `agentic_memory/` | Bi-directional synchronization mapping Obsidian vault states securely to `agentic_memory`. |
| **Graph RAG pipeline** | `graph_rag`, `llm/rag` | Connect the knowledge graph to `llm/rag/` for retrieval-augmented generation with structured entity relationships. |

---

## 🔵 v1.1.9 — "Multimodal STT & Concrete Cloud Providers"

Establishing concrete providers for sensory and external infrastructure bridging.

### Advanced AI Integrations

| Feature | Depends On | Technical Detail |
| :--- | :--- | :--- |
| **Concrete Provider Integrations** | `cloud/`, `audio/` | Implement standard provider models (`boto3`, `faster-whisper`, `edge-tts`) gated via extras. |
| **Multimodal STT base** | `audio/` | Establish the base structure for Whisper STT into generic standard LLM interactions. |
| **Cost management** | `llm/providers` | Introduce basic API spend tracking on per-call basis via custom telemetry. |

---

## 🟢 v1.1.10 — "Dashboard v2 & Telemetry UX"

Gearing towards a richer visual presence ahead of the major 1.2.0 milestone.

### Visual Evolution

| Feature | Depends On | Technical Detail |
| :--- | :--- | :--- |
| **Dashboard v2 Framework**| `website/` | Implement Vue/React scaffold to eventually replace the legacy Vanilla JS framework, providing better reactivity. |
| **Data visualization UX** | `data_visualization` | Add test-run history timeline, module health heatmap, and per-module sparklines logic. |
| **Agent telemetry** | `telemetry/` | Add granular performance tracking to `agent` execution flows for exact latency visibility. |

---

## 🟠 v1.1.11 — "Advanced Orchestration & System Verification"

Strengthening the system boundaries through verification paradigms and global availability hooks.

### Integration Features

| Feature | Depends On | Technical Detail |
| :--- | :--- | :--- |
| **Formal verification basis** | `coding/` | Initial spike to wire `z3-solver` into `coding/` for automated invariant checking. |
| **Cross-platform distribution** | Root | Setup initial steps for Homebrew formula and Nix flake, `pipx` compatibility. |
| **Memory scaling** | `database_management` | Alembic schema migrations and potential Redis integration. |

---

## 🔴 v1.1.12 — "Pre-1.2.0 Polish & Agentic CI"

Final ecosystem integration and aggressive swarm-based CI tuning before the 1.2.0 cut.

### Ecosystem Integration

| Feature | Depends On | Technical Detail |
| :--- | :--- | :--- |
| **Agentic CI pipeline** | `specialized/agents` | `AutoPR.create()` with safety limits (max 3 files changed, requires human review) for autonomous system tuning. |
| **Budget alerting** | `events/notification` | Active budget alerting threshold events mapped over the v1.1.9 provider usage tracking. |
| **Dashboard v2 Finalization**| `telemetry`, `website` | Wire D3.js and the new React/Vue scaffolding with full WebSocket streaming capability. |

---

## 🔵 v1.2.0 — "Ecosystem Integration"

The culmination of the 1.1.x architectural series bridging the PAI PM server, full zero-mock compliance, real-time sync, and agentic orchestration.

| Feature | Depends On | Technical Detail |
| :--- | :--- | :--- |
| **Infomaniak cloud provider** | `cloud/schema` | Storage (Swift-compat), compute (Nova-compat), DNS management via Infomaniak API v1. |
| **1.2.0 Cut & Freeze** | `core/` | Final validation of all module APIs, schema locks, and stable PM system integration. |

---

## 🔮 v1.3.0+ — Longer-Term Vision

Architectural extensions and research directions.

| Direction | Scope | Notes |
| :--- | :--- | :--- |
| **Spatial reasoning & Synergetics** | `spatial/` | Fuller-inspired geodesic transforms, 4D rotation matrices, icosahedral mesh generation |
| **Embodiment & ROS2 bridge** | `embodiment/` | Full ROS2 bridge with `rclpy` bindings or archive deprecated module |
| **Cerebrum cognitive architecture** | `cerebrum/` | Real probabilistic inference with `scipy.stats`, belief revision, uncertainty-aware planning |
| **Inference optimization** | `quantization/`, `distillation/` | INT8/INT4 quantization wrappers, knowledge distillation, speculative decoding |
| **Plugin marketplace** | `plugin_system/` | Plugin discovery (entry points + PyPI search), sandboxed installation, version management |
| **Multi-agent swarm protocols** | `collaboration/` | Raft consensus, hierarchical task decomposition, emergent behavior monitoring |
| **Secure cognitive agent hardening** | `security/`, `agents/` | STRIDE threat modeling, penetration testing, key management audit |

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
