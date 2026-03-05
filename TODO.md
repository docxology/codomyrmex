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

## 🟢 v1.1.2 — "Developer Experience"

Focused on making the project easy to contribute to, operate, and extend. Every item has a concrete verification command.

### Ruff Triage Phase 2 (9,706 → target: <5,000)

| Rule | Count | Action | Fixable? |
| :--- | :--- | :--- | :--- |
| `T201` (print) | **2,464** | Move to per-file ignore for `scripts/`, suppress in `src/` library code; remove stale prints | ⚠️ Manual: review each `src/` occurrence |
| `DTZ005` (tz-naive datetime) | **470** | Bulk-fix: `datetime.now()` → `datetime.now(tz=UTC)` across all modules | ✅ Auto-fixable |
| `RUF013` (implicit `Optional`) | **421** | Bulk-fix: `x: str = None` → `x: str \| None = None` | ✅ Auto-fixable |
| `ARG005` (unused lambda arg) | **389** | Ignore in `pyproject.toml` — lambda convention | Ignore |
| `NPY002` (numpy legacy RNG) | **348** | Ignore — false positives on non-numpy code | Ignore |
| `F841` (unused variable) | **322** | `ruff check --select=F841 --fix .` — safe removal | ✅ Auto-fixable |
| `S607` (partial exec path) | **315** | Ignore in scripts/ per-file; audit in library code | ⚠️ Audit |
| `EXE001` (shebang) | **303** | `ruff check --select=EXE001 --fix .` — add missing shebangs | ✅ Auto-fixable |
| `PERF401` (manual list comp) | **302** | `ruff check --select=PERF401 --fix .` — convert to list comprehensions | ✅ Auto-fixable |
| `N806` (non-lowercase var) | **283** | Ignore — scientific/mathematical naming convention | Ignore |

**Technical details**: Run auto-fixes first (`DTZ005`, `RUF013`, `F841`, `EXE001`, `PERF401`), then add remaining ignores (`ARG005`, `NPY002`, `N806`). Manual audit `T201` in `src/codomyrmex/` only (not scripts). Expected reduction: ~2,500 auto-fixed + ~1,000 ignored = **~6,200 remaining**.

### noqa/Suppression Cleanup (179 → target: <100)

| Suppression | Count | Action |
| :--- | :--- | :--- |
| `# noqa: F401` (unused import) | ~100 est. | Audit each: if re-exported, add to `__all__`; else remove import |
| `# noqa: E402` (import order) | ~30 est. | Move path-setup code to `conftest.py` or use conditional imports |
| `# noqa: F403` (wildcard import) | ~25 est. | Replace `from x import *` with explicit imports; update `__all__` |
| Remaining noqa | ~24 | Case-by-case: fix or document reason |
| `# type: ignore` | ~50 est. | Cross-reference with ty diagnostics; remove stale ones |

**Technical details**: `grep -rn "# noqa: F401" src/ --include="*.py" | wc -l` to measure progress. For each `__init__.py` with `# noqa: F401`, check if the symbol is in `__all__`; if so, the noqa is stale. Remove `type: ignore` comments where ty's tightened rules now catch the issue.

### Tooling & DX

| Item | Scope | Technical Detail | Verification |
| :--- | :--- | :--- | :--- |
| **justfile** | Root | Create `justfile` with targets mirroring Makefile (40 targets); add `just lint`, `just test`, `just build`, `just release`; keep Makefile for CI backward compat | `just --list` shows all targets |
| **PEP 723 script metadata** | `scripts/` (top 10) | Add `# /// script` inline metadata to 10 most-used scripts; enables standalone `uv run script.py` without prior `uv sync` | `uv run scripts/utils/scaffold_modules.py --help` works without venv |
| **Dev container** | `.devcontainer/` | Create `devcontainer.json`: Python 3.11, uv pre-installed, ruff + ty extensions, port forwarding for docs (8000) and dashboard (8888) | `devcontainer build .` succeeds |
| **Nix flake** | `flake.nix` | Create flake with `devShells.default` providing Python 3.11, uv, just; `packages.default` for the wheel; `checks` for `ruff check` + `pytest` | `nix develop` drops into shell |
| **Pre-commit modernization** | `.pre-commit-config.yaml` | Update ruff hook to `0.15.x`; add `ty` hook via local hook; remove `bandit` (superseded by ruff S rules); add `uv lock --check` hook | `pre-commit run --all-files` passes |

### Documentation Site

| Item | Scope | Technical Detail | Verification |
| :--- | :--- | :--- | :--- |
| **`mkdocs build --strict`** | `mkdocs.yml` | Fix broken cross-refs (currently 1,029+ docs); add `--strict` to CI `docs-deploy.yml` workflow | `mkdocs build --strict` exits 0 |
| **API reference** | `docs/reference/` | Install `mkdocstrings[python]`; add `reference/` nav section in `mkdocs.yml`; auto-generate from `src/codomyrmex/` top-level `__init__.py` files | `mkdocs serve` → `/reference/` loads |
| **Module inventory page** | `docs/modules/` | Auto-generated markdown table of all 127 modules with status, test count, coverage %, and module-level dependency graph (Mermaid) | `docs/modules/index.md` renders correctly |
| **Search tuning** | `mkdocs.yml` | Set `search.boost` on key pages (README, ARCHITECTURE, module READMEs); verify Material search indexes all 1,029+ pages | Search "agents" returns top result |

### Testing Infrastructure

| Item | Scope | Technical Detail | Verification |
| :--- | :--- | :--- | :--- |
| **Coverage ramp 32→38%** | `pyproject.toml` | Ratchet `fail_under=38`; add tests for 5 lowest-coverage modules (identify via `--cov-report=term-missing`); focus on `embodiment/`, `quantum/`, `dark/`, `spatial/`, `cerebrum/` | `uv run pytest --cov=codomyrmex --cov-report=term-missing` ≥38% |
| **Property-based testing** | `validation/`, `serialization/` | Add `hypothesis` to dev deps; write 20+ property tests for schema validators (`@given(st.text())`), round-trip serialization, crypto hash determinism | `uv run pytest -k "hypothesis" --count` ≥20 |
| **Mutation testing expansion** | `pyproject.toml` | Expand `[tool.mutmut]` from 6→12 target files; add `cache/core.py`, `concurrency/core.py`, `events/core.py`, `validation/core.py`, `serialization/core.py`, `crypto/core.py` | `uv run mutmut run --paths-to-mutate=...` mutation score ≥50% |
| **Flaky test tracking** | `pyproject.toml` | Install `pytest-rerunfailures`; add `@pytest.mark.flaky(reruns=2)` to known flakey tests; add `--reruns 2` to CI `pytest` invocation | `grep -rn "@pytest.mark.flaky" src/ \| wc -l` documents all flaky tests |

---

## 🟣 v1.1.3 — "Quality Ratchet"

Focused on tightening every quality gate and reducing tech debt to near-zero in core modules.

### Ruff Phase 3 (target: <2,000)

| Action | Expected Reduction | Technical Detail | Verification |
| :--- | :--- | :--- | :--- |
| **Unsafe-fixes pass** | **−4,309** | Run `ruff check --unsafe-fixes --fix .` on 4,309 available unsafe fixes; review diff with `git diff --stat`; revert any that break tests | `uv run ruff check . \| tail -1` should show <2,000 |
| **PLW1510 audit** | **−264** | `subprocess.run()` calls missing `check=True`; add to each or explicitly handle returncode | `uv run ruff check --select=PLW1510 . \| wc -l` → 0 |
| **RET504 simplification** | **−128** | Unnecessary variable assignments before return; auto-fix available | `uv run ruff check --select=RET504 --fix .` |
| **SIM102 collapsible if** | **−103** | Nested ifs that can be collapsed; auto-fix available | `uv run ruff check --select=SIM102 --fix .` |
| **E402 import order** | **−111** | Imports not at top of file; refactor path-setup patterns to `conftest.py` | `uv run ruff check --select=E402 . \| wc -l` → 0 |
| **S110/S106 security** | **−244** | Suppress `S106` (hardcoded passwords — false positives on test fixtures) in per-file ignores for `tests/`; audit real `S110` (try/except/pass) occurrences | Manual audit |
| **Ruff CI hard-fail** | — | Change `ci.yml` ruff step from `continue-on-error: true` to hard fail once <2,000 | `ruff check .` exits 0 or CI fails |

### ty Phase 2 (1,772 → target: <500)

| Diagnostic | Count | Action | Focus |
| :--- | :--- | :--- | :--- |
| `invalid-assignment` | **661** | Fix top 50 modules: typically `x: str = some_func()` where return type isn't str; add proper annotations | Fix in: `website/`, `agents/`, `orchestrator/` (highest density) |
| `str`/`int`/`bool`/`float` literals | **1,026** combined | These are informational (type narrowing hints); suppress as category if ty supports it, else ignore | Check ty docs for suppression |
| `invalid-parameter-default` | **348** | Fix: `def f(x: str = None)` → `def f(x: str \| None = None)`; overlaps with `RUF013` fixes | Auto-fix via ruff RUF013 first |
| `possibly-unresolved-reference` | **148** | Fix conditional imports: add `TYPE_CHECKING` guards or re-export in `__init__.py` | `uv run ty check src/ 2>&1 \| grep -c possibly-unresolved` |
| `unused-type-ignore-comment` | **95** | Remove stale `# type: ignore` comments → now redundant after ty migration | `uv run ruff check --select=PGH003 --fix .` |
| `call-non-callable` / `no-matching-overload` | **143** | Fix overload signatures in `agents/`, `llm/` provider ABCs | Manual fixes |
| **ty CI hard-fail** | — | Change `ci.yml` ty step from `continue-on-error: true` to hard fail once <500 | `ty check src/` exits 0 or CI fails |

### Security Hardening

| Item | Scope | Technical Detail | Verification |
| :--- | :--- | :--- | :--- |
| **Dependency audit** | `uv.lock` | Run `uv pip audit` (or `pip-audit`); resolve any known CVEs; pin affected deps | `pip-audit --strict` exits 0 |
| **SBOM generation** | CI | Add CycloneDX SBOM generation to `sbom.yml` workflow; output to `sbom.json` in release assets | SBOM attached to GitHub release |
| **Secret scanning** | `.pre-commit-config.yaml` | Verify `detect-secrets` hook catches test credential patterns; add `.secrets.baseline` file | `detect-secrets scan --list-all-plugins` |
| **CSP headers** | `website/` | Add Content-Security-Policy headers to dashboard responses; implement `SecurityMiddleware` | Browser DevTools shows CSP header |
| **STRIDE threat model** | `docs/security/` | Create `THREAT_MODEL.md` covering: spoofing (MCP auth), tampering (agent code injection), repudiation (audit logging), info disclosure (LLM prompt leakage), DoS (rate limiting), elevation (skill permissions) | `docs/security/THREAT_MODEL.md` exists with all 6 STRIDE categories |

### CI/CD Improvements

| Item | Scope | Technical Detail | Verification |
| :--- | :--- | :--- | :--- |
| **Workflow consolidation** | `.github/workflows/` | 36 workflow files → consolidate to ~15 by merging related workflows (3 gemini-*→ 1, 5 pr-* → 1, 2 docs-* → 1) | `ls .github/workflows/*.yml \| wc -l` ≤ 20 |
| **Lighthouse CI** | `.github/workflows/` | Add `treosh/lighthouse-ci-action` for docs site; budgets: LCP <2.5s, CLS <0.1, Performance ≥90 | Lighthouse CI check passes on PR |
| **Matrix testing** | `ci.yml` | Add `strategy.matrix.python-version: ["3.11", "3.12", "3.13"]`; verify all 3 versions pass | CI matrix shows 3 green checks |
| **Release automation** | `release.yml` | Auto-generate release notes from CHANGELOG.md; attach `uv build` artifacts; update version badge | `gh release create` auto-generates notes |
| **Dependabot grouping** | `.github/dependabot.yml` | Group minor/patch updates by ecosystem; schedule weekly; auto-merge patch updates | Dependabot PRs are grouped |

### Coverage Ratchet (38% → target: 42%)

| Module | Current | Target | Key Functions to Test |
| :--- | :--- | :--- | :--- |
| `embodiment/` | ~0% | 30% | `RobotController.connect()`, `SensorFusion.merge()`, or archive module |
| `quantum/` | ~5% | 25% | `QuantumCircuit.execute()`, `QubitRegister.measure()` |
| `dark/` | ~5% | 25% | Core entropy functions, randomness generation |
| `spatial/` | ~10% | 30% | `GeodesicTransform.apply()`, rotation matrices |
| `cerebrum/` | ~10% | 30% | `BeliefNetwork.update()`, probabilistic inference |
| `graph_rag/` | ~15% | 35% | `GraphRetriever.query()`, entity extraction |
| `agentic_memory/` | ~15% | 35% | `MemoryStore.retrieve()`, TTL expiry, tag search |

**Technical details**: `uv run pytest --cov=codomyrmex --cov-report=term-missing --cov-report=html` → review `htmlcov/index.html`. Ratchet `fail_under` to 42 in `pyproject.toml`. Each module needs ≥5 real-logic tests (zero-mock policy).

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
