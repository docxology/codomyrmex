# Codomyrmex — TODO

**Version**: v1.1.5 | **Date**: 2026-03-05 | **Modules**: 127 | **Sprint**: 25

This is the authoritative project backlog. Updated after each sprint.

---

## Codebase Snapshot (Verified 2026-03-05)

| Metric | Value | Method |
| :--- | :--- | :--- |
| Top-level source modules | **127** | `ls -d src/codomyrmex/*/` |
| Source files (non-test) | ~1,800+ | `find -name "*.py" -not -path "*/tests/*"` |
| Total LOC (incl. tests) | ~560,000 | `wc -l` across all `.py` |
| Test files | **905+** | `find -name "test_*.py"` |
| Test suite | **21,000+** tests collected | `uv run pytest --collect-only` |
| Ruff violations | **0** (triaged from 119k) | `uv run ruff check .` ✅ |
| Ruff auto-fixed | **10,946** applied | `uv run ruff check --fix .` |
| Ruff formatted | **3,420** files | `uv run ruff format --check .` |
| Script parse errors | **0** (46 fixed in v1.1.1) | `python3 -c "import ast"` |
| ty diagnostics | **971** (target <1,000 met) | `uv run ty check src/` |
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

## 🟡 v1.1.5 — "Type Safety & Coverage Ratchet"

Incremental release focused on eliminating remaining type errors and tightening the coverage gate.

### `ty` Diagnostic Reduction (1,446 → 971) ✅

| Rule | Est. Count | Action | Focus |
| :--- | :--- | :--- | :--- |
| `invalid-assignment` | **~600** | Fix return types in top offenders (`website/`, `agents/`, `orchestrator/`); add proper annotations | ✅ Core Modules |
| `invalid-return-type` | **~400** | Explicitly handle or type the return values of asynchronous functions and factory methods | ✅ Async/Factory |
| `invalid-parameter-default` | **~300** | Auto-fix via ruff `RUF013` applied previously; verify all instances of `def f(x: str = None)` are resolved | ✅ Verification |
| `possibly-unresolved-reference` | **~140** | Add `TYPE_CHECKING` guards around conditional imports to satisfy the type checker without circular dependencies | ✅ Manual Fix |

**Technical details**: Focus on the `src/codomyrmex/` library files. Run `uv run ty check src/ 2>&1 | grep -c "invalid-return-type"` to track diagnostic reductions. Add hard-fail on `ci.yml` when diagnostics drop below 1,000.

### Codebase Quality & Testing (Coverage 32% → 35%)

| Item | Scope | Technical Detail |
| :--- | :--- | :--- |
| **Coverage gate ratchet** | `pyproject.toml` | Bump `fail_under` to 35. Add tests for `embodiment/`, `quantum/`, and `dark/` to reach threshold |
| **`noqa` / `type: ignore` Audit** | Repo-wide | Audit existing 178 `type: ignore` and 233 `noqa` flags; remove state suppressions as `ty` and `ruff` accurately capture truth |
| **Broken symlink cleanup** | `.cursorrules` | Fix broken symlinks in module directories (`src/*/.cursor/`) causing warnings during `uv build` |
| **Dashboard WebSocket** | `website/` | Replace 15s polling in `pai_mixin.py` with WebSocket push via `websockets` library |

---

## 🟢 v1.1.6 — "Tooling & Developer Experience"

Focused on making the project easier to contribute to, operate, and extend efficiently.

### Infrastructure & Pipeline

| Item | Scope | Technical Detail |
| :--- | :--- | :--- |
| **Dependency audit** | `uv.lock` | Run `uv pip audit`; resolve any identified CVEs; pin dependencies for security |
| **SBOM generation** | `.github/workflows/`| Add CycloneDX SBOM generation to `sbom.yml`; attach output `sbom.json` to GitHub release assets |
| **PEP 723 script metadata** | `scripts/` | Add `# /// script` inline metadata to top 10 most-used scripts enabling standalone execution (e.g. `uv run script.py`) |
| **`justfile` Migration** | Root | Create a `justfile` mirroring the `Makefile` with targets (`just lint`, `just test`, `just build`); preserve `Makefile` |

### Documentation Site Tuning

| Item | Scope | Technical Detail |
| :--- | :--- | :--- |
| **Strict MkDocs CI** | `mkdocs.yml` | Run `mkdocs build --strict` to fix broken cross-references (1,029+ docs); enforce in `docs-deploy.yml` |
| **API reference generation** | `docs/reference/` | Install `mkdocstrings[python]` and auto-generate from `src/codomyrmex/` top-level `__init__.py` files |
| **Lighthouse CI** | `.github/workflows/`| Enforce performance budgets (LCP < 2.5s, CLS < 0.1) for the documentation site on PR merges |

---

## 🟣 v1.1.7 — "Advanced Verification & Ecosystem Integration"

Targeted feature additions and aggressive testing protocols to guarantee industrial-grade stability.

### Expanded Testing Methodologies

| Item | Scope | Technical Detail |
| :--- | :--- | :--- |
| **Coverage gate ratchet** | `pyproject.toml` | Bump `fail_under` to 38. Expand coverage onto `spatial/`, `cerebrum/`, and `graph_rag/` |
| **Property-based testing** | `serialization/` | Add `hypothesis` dev-dependency; write robust property tests (`@given`) for schema validators and data round-trips |
| **Mutation testing scale-up** | `pyproject.toml` | Expand `[tool.mutmut]` from 6 to 12 targets (e.g., `cache/core.py`, `concurrency/core.py`, `events/core.py`) |
| **Flaky testing tracking** | `pyproject.toml` | Apply `@pytest.mark.flaky(reruns=2)` using `pytest-rerunfailures` to explicitly track and document CI flakes |

### Ecosystem Features

| Item | Scope | Technical Detail |
| :--- | :--- | :--- |
| **Graph RAG pipeline** | `graph_rag`, `llm/rag` | Connect the knowledge graph to `llm/rag/` for retrieval-augmented generation with structured entity relationships |
| **Agentic memory backend** | `agentic_memory/` | Deploy SQLite backend for the `MemoryStore` enabling cross-session retrieval, TTL expiry, and tag indexing |
| **Optional integrations** | `cloud/`, `audio/` | Implement concrete provider implementations (`boto3`, `faster-whisper`, `edge-tts`) gated via optional dependencies |

---

## 🔵 v1.2.0 — "Ecosystem Maturation"

Larger features requiring cross-module coordination.

### Core Features

| Feature | Depends On | Technical Detail |
| :--- | :--- | :--- |
| **Graph RAG pipeline** | `graph_rag`, `llm/rag`, `agentic_memory/obsidian` | Connect knowledge graph to `llm/rag/` for retrieval-augmented generation with structured entity relationships; implement `GraphRetriever.query()` → LLM context injection |
| **Agentic memory persistence** | `database_management`, `serialization` | SQLite backend for `MemoryStore` with TTL-based expiry, tag indexing, cross-session retrieval; Redis optional via `cache/` integration; migration: `alembic` schema |
| **Dashboard v2** | `telemetry`, `performance`, `data_visualization` | WebSocket streaming, test-run history timeline, module health heatmap, per-module sparklines; frontend: vanilla JS + D3.js |
| **Cost management** | `llm/providers`, `events/notification` | Real API spend tracking using provider usage APIs (OpenRouter `/api/v1/usage`, Gemini quota API); budget alerting via `events/notification` |

### Infrastructure

| Feature | Depends On | Technical Detail |
| :--- | :--- | :--- |
| **Infomaniak cloud provider** | `cloud/common/` ABC layer | Storage (Swift-compat), compute (Nova-compat), DNS management via Infomaniak API v1; implement `InfomaniakProvider(CloudProvider)` |
| **Formal verification** | `coding/static_analysis` | Wire `z3-solver` into `coding/` for automated invariant checking; implement `InvariantChecker.verify(ast_node)` → SAT/UNSAT |
| **Multimodal agent pipeline** | `agents`, `llm`, `audio`, `video` | Voice-in/voice-out agent interaction: Whisper STT → LLM reasoning → Edge TTS response; implement `MultimodalAgent(BaseAgent)` |
| **Self-improving CI** | `agents/specialized/improvement_pipeline` | `ImprovementPipeline` → GitHub Actions for agent-driven quality PRs; implement `AutoPR.create()` with safety limits (max 3 files changed, requires human review) |

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
| **Cross-platform distribution** | Root | Homebrew formula, Nix flake, multi-arch Docker image, `pipx install codomyrmex` |

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

*Last updated: 2026-03-05 — Sprint 25. v1.1.1 released. v1.1.2 & v1.1.3 deeply scoped with data-driven targets (ruff 9.7k→<5k→<2k, ty 1.8k→<500, coverage 32%→38%→42%).*
