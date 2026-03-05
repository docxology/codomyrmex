# Codomyrmex — TODO

**Version**: v1.1.1 | **Date**: 2026-03-05 | **Modules**: 127 | **Sprint**: 25

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
| Ruff violations | **9,706** (triaged from 119k) | `uv run ruff check .` |
| Ruff auto-fixed | **10,946** applied | `uv run ruff check --fix .` |
| Ruff formatted | **3,420** files | `uv run ruff format --check .` |
| Script parse errors | **0** (46 fixed in v1.1.1) | `python3 -c "import ast"` |
| ty diagnostics | **1,772** (tightened config) | `uv run ty check src/` |
| Pass-only function stubs | **4** intentional no-ops | AST analysis |
| Coverage gate | `fail_under=31`; actual ~32% ✅ | Gate ratcheted |
| MCP `@mcp_tool` decorators | **545** | `grep -r '@mcp_tool'` |
| RASP documentation | 127/127 | Automated audit |
| `py.typed` markers | **572** | PEP 561 ✅ |
| Zero-Mock policy | Enforced via ruff | `pyproject.toml` |
| Build backend | **uv_build** | Migrated from hatchling |
| Linter | **ruff** (select=ALL) | Replaced flake8+black+isort |
| Type checker | **ty** (tightened) | Replaced mypy |
| Build artifacts | `codomyrmex-1.1.1.tar.gz` + `.whl` | `uv build` ✅ |

---

## 🟡 v1.1.1 — "Polish & Hardening"

Incremental release focused on quality ramp, ruff triage, and developer experience.

### Ruff Triage (118,922 → target: <80,000)

| Rule Category | Count | Action | Scope |
| :--- | :--- | :--- | :--- |
| `D` (pydocstyle) | ~40,000 est. | Ignore rules `D100–D107` (missing docstrings) in `pyproject.toml` | Repo-wide |
| `ANN` (annotations) | ~15,000 est. | Ignore `ANN001`, `ANN002`, `ANN003` (missing arg annotations) | Repo-wide |
| `ERA001` (commented-out code) | ~3,000 est. | `ruff check --select=ERA001 --fix .` — safe auto-removal | Repo-wide |
| `T201` (print statements) | ~2,000 est. | Triage: keep in scripts/, remove from library code | `src/codomyrmex/` |
| `F401` (unused imports) | ~500 est. | `ruff check --select=F401 --fix .` — safe auto-removal | Repo-wide |
| `UP` (pyupgrade) | ~2,000 est. | `ruff check --select=UP --fix .` — modernize syntax | Repo-wide |
| `I` (isort) | already fixed | Verify zero remaining after format pass | Repo-wide |

**Technical details**: Add rule ignores to `[tool.ruff.lint]` `ignore` list in `pyproject.toml`. Run `ruff check --select=<RULE> --fix .` for each auto-fixable category. Manual review for `T201` (print) in library code.

### ty Tightening (1,771 → target: <1,000)

| Rule | Current | Action |
| :--- | :--- | :--- |
| `unresolved-import` | `"ignore"` | Keep ignored — many optional deps |
| `possibly-unbound` | `"ignore"` | Tighten to `"warn"` after fixing top offenders |
| `invalid-return-type` | default (warn) | Fix the ~50 most common return type mismatches |
| `redundant-cast` | default | Fix — these are safe auto-fixes |

**Technical details**: Update `[tool.ty.rules]` in `pyproject.toml`. Fix return type annotations in `website/`, `agents/`, `orchestrator/` first (highest diagnostic density). Run `uv run ty check src/ 2>&1 | grep -c "invalid-return-type"` to measure progress.

### Codebase Quality

| Item | Scope | Technical Detail |
| :--- | :--- | :--- |
| **Desloppify score 63→70+** | Repo-wide | Run `/desloppify` workflow; target top categories: facade issues, oversized `__init__.py` files, dead code |
| **noqa/suppression audit** | Repo-wide | 233 `noqa` + 178 `type: ignore` lines — audit with `grep -rn "# noqa" src/ \| wc -l`; remove stale suppressions, fix underlying issues (top: F401:159, E402:54, F403:50) |
| **Coverage ramp 31→35%** | `pyproject.toml` | Ratchet `fail_under` to 35; add tests for uncovered modules (`embodiment/`, `quantum/`, `dark/`, `spatial/`); measure with `uv run pytest --cov=codomyrmex --cov-report=term-missing` |
| **Dashboard WebSocket** | `website/` | Replace 15s polling in `pai_mixin.py` with WebSocket push via `websockets` library; update `PAI_DASHBOARD.md` |
| **Parse error cleanup** | `scripts/` | Fix 4 syntax errors in `scripts/utils/orchestrate.py`, `scripts/utils/scaffold_modules.py`, `scripts/validation/orchestrate.py`, `scripts/website/orchestrate.py` |
| **Broken symlink cleanup** | `src/*/.cursor/` | Remove or fix broken `.cursorrules` symlinks in 5+ module dirs; these cause `uv build` source-tree warnings |

### CI/CD Improvements

| Item | Scope | Technical Detail |
| :--- | :--- | :--- |
| **Lighthouse CI** | `.github/workflows/` | Add `treosh/lighthouse-ci-action` workflow for docs site performance budgets (LCP <2.5s, CLS <0.1) |
| **Ruff CI gate** | `ci.yml` | Change ruff check from `continue-on-error: true` to hard fail once violation count is triaged below threshold |
| **ty CI gate** | `ci.yml` | Change ty check from `continue-on-error: true` to hard fail once diagnostics are below 500 |
| **Build verification** | `ci.yml` | Add `uv build` step to CI to catch build regressions (broken symlinks, missing files) |

### Optional-Dep Implementation (when deps installed)

| Area | Scope | Key Items |
| :--- | :--- | :--- |
| **Cloud providers** | `cloud/` | Concrete provider implementations (boto3, gcloud, azure); wire `from_env()` pattern |
| **Audio STT/TTS** | `audio/` | Provider implementations behind `faster-whisper`, `edge-tts`; add integration tests |
| **Cache backends** | `cache/` | `redis` and `memcached` backend implementations; benchmark against in-memory |
| **WASM runtime** | `containerization/` | `wasmtime` integration for `load_module()/execute()`; add security sandbox tests |

---

## � v1.1.2 — "Developer Experience"

Focused on making the project easy to contribute to and operate.

### Tooling & DX

| Item | Scope | Technical Detail |
| :--- | :--- | :--- |
| **prek migration** | `.pre-commit-config.yaml` | Migrate from `pre-commit` to `prek` (Trail of Bits); update `Makefile`, remove `pre-commit` from dev deps |
| **justfile** | Root | Add `justfile` as modern Makefile alternative; keep Makefile for backward compat |
| **uv script shebangs** | `scripts/` | Add `# /// script` inline metadata to standalone scripts per PEP 723; enables `uv run script.py` without prior install |
| **Nox/tox replacement** | Root | Configure `uv run --python 3.11,3.12,3.13` matrix testing via CI; remove any tox references |
| **Dev container** | `.devcontainer/` | Add `devcontainer.json` with uv, ruff, ty pre-installed; GitHub Codespaces support |

### Documentation Site

| Item | Scope | Technical Detail |
| :--- | :--- | :--- |
| **MkDocs build verification** | `mkdocs.yml` | Fix any broken cross-references in 1,029+ docs; add `mkdocs build --strict` to CI |
| **API reference generation** | `docs/reference/` | Auto-generate from docstrings using `mkdocstrings[python]`; add to `mkdocs.yml` nav |
| **Search index** | `docs/` | Verify `mkdocs-material` search plugin indexes all pages; tune `search.boost` for key pages |

### Testing Infrastructure

| Item | Scope | Technical Detail |
| :--- | :--- | :--- |
| **Property-based testing expansion** | `validation/`, `serialization/`, `crypto/` | Add Hypothesis strategies for schema validators, round-trip serialization, crypto operations |
| **Mutation testing** | `pyproject.toml` | Expand `[tool.mutmut]` from 6→12 target files; focus on `cache/`, `concurrency/`, `events/` core logic |
| **Flaky test quarantine** | `pytest.ini_options` | Tag and track flaky tests with `@pytest.mark.flaky`; report in CI dashboard |

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

*Last updated: 2026-03-05 — Sprint 25. v1.1.1 complete. Ruff triaged (119k→9.9k). 46 parse errors fixed. CI hardened.*
