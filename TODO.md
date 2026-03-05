# Codomyrmex — TODO

**Version**: v1.1.0 | **Date**: 2026-03-04 | **Modules**: 127 | **Sprint**: 24

This is the authoritative project backlog. Updated after each sprint.

---

## Codebase Snapshot (Verified 2026-03-04)

| Metric | Value | Method |
| :--- | :--- | :--- |
| Top-level source modules | **127** | `ls -d src/codomyrmex/*/` |
| Source files (non-test) | ~1,800+ | `find -name "*.py" -not -path "*/tests/*"` |
| Total LOC (incl. tests) | ~560,000 | `wc -l` across all `.py` |
| Test files | **886** | `find -name "test_*.py"` |
| Test suite | **21,000+** tests collected | `uv run pytest --collect-only` |
| Ruff violations | **0** ✅ | Sprint 22 re-zeroed |
| Pass-only function stubs | **4** intentional no-ops | AST analysis |
| Coverage gate | `fail_under=31`; actual ~32% ✅ | Gate ratcheted |
| MCP `@mcp_tool` decorators | **545** | `grep -r '@mcp_tool'` |
| RASP documentation | 127/127 | Automated audit |
| `py.typed` markers | **572** | PEP 561 ✅ |
| Zero-Mock policy | Enforced via ruff | `pyproject.toml` |
| Integration test markers | **35/35** | `pytestmark = pytest.mark.integration` |
| PAI Skills | **81** installed | Skill registry |

---

## 🟡 v1.1.1 — "Polish & Hardening"

Incremental release focused on quality ramp, documentation polish, and developer experience.

| Item | Scope | Detail |
| :--- | :--- | :--- |
| **Desloppify score 63→70+** | Repo-wide | Reduce code smells, facade issues; target top categories |
| **noqa/suppression audit** | Repo-wide | 233 noqa + 178 `type: ignore` lines — reduce stale suppressions, fix underlying issues (F401:159, E402:54, F403:50 are top noqa codes) |
| ~~**Property-based tests**~~ ✅ | `agentic_memory/rules/` | Done: `test_rule_loader_property.py` (161 lines, 6 property classes) |
| **Dashboard WebSocket** | `website/` | Replace 15s polling with real-time push |
| **Coverage ramp 31→35%** | `pyproject.toml` | Ratchet `fail_under`, add tests for uncovered modules |
| **Lighthouse CI** | `.github/workflows/` | Performance budget enforcement for documentation site |
| ~~**Rules CLI**~~ ✅ | `cli/` | Already implemented: `codomyrmex rules list` and `codomyrmex rules check <file>` |
| ~~**Rule-AGENTS cross-ref**~~ ✅ | `agentic_memory/rules/` | Done: all 46 modules with cursorrules have `## Rule Reference` in AGENTS.md |
| ~~**Gemini workflow health**~~ ✅ | `.github/workflows/` | Done: 5 workflows verified; prompt files in `.gemini/` match; dual auth (API key + WIF) consistent |

### Optional-Dep Implementation (when deps installed)

| Area | Scope | Key Items |
| :--- | :--- | :--- |
| **Cloud providers** | `cloud/` | Concrete provider implementations (boto3, gcloud, azure) |
| **Audio STT/TTS** | `audio/` | Provider implementations behind `faster-whisper`, `edge-tts` |
| **Cache backends** | `cache/` | `redis` and `memcached` backend implementations |
| **WASM runtime** | `containerization/` | `wasmtime` integration for `load_module()/execute()` |

---

## 🔵 v1.2.0 — "Ecosystem Maturation"

Larger features requiring cross-module coordination. No fixed timeline.

- **Infomaniak cloud provider**: Storage (Swift-compat), compute (Nova-compat), DNS management via Infomaniak API. *Depends on*: `cloud/common/` ABC layer

- **Graph RAG pipeline**: Connect `graph_rag` knowledge graph to `llm/rag/` for retrieval-augmented generation with structured entity relationships. *Depends on*: `agentic_memory/obsidian`, `llm/rag`, `llm/embeddings`

- **Agentic memory persistence**: SQLite backend for `MemoryStore` with TTL-based expiry, tag indexing, cross-session retrieval. Redis optional. *Depends on*: `database_management`, `serialization`

- **Dashboard v2**: WebSocket streaming, test-run history timeline, module health heatmap, per-module sparklines. *Depends on*: `telemetry`, `performance`, `data_visualization`

- **Formal verification**: Wire `z3-solver` into `coding/` for automated invariant checking. *Depends on*: `coding/static_analysis`

- **Multimodal agent pipeline**: Voice-in/voice-out agent interaction via Whisper STT + Edge TTS. *Depends on*: `agents`, `llm`, `audio`, `video`

- **Cost management**: Real API spend tracking using provider usage APIs with budget alerting. *Depends on*: `llm/providers`, `events/notification`

---

## 🔮 Longer-Term Vision

Architectural extensions and research directions.

- **Spatial reasoning & Synergetics** — Fuller-inspired geodesic transforms, 4D rotation matrices, icosahedral mesh generation
- **Embodiment & ROS2 bridge** — Full ROS2 bridge with `rclpy` bindings or archive deprecated `embodiment` module
- **Cerebrum cognitive architecture** — Real probabilistic inference with `scipy.stats`, belief revision, uncertainty-aware planning
- **Inference optimization** — INT8/INT4 quantization wrappers, knowledge distillation, speculative decoding
- **Plugin marketplace** — Plugin discovery (entry points + PyPI search), sandboxed installation, version management
- **Multi-agent swarm protocols** — Raft consensus, hierarchical task decomposition, emergent behavior monitoring
- **Self-improving pipelines** — `ImprovementPipeline` → CI/CD via GitHub Actions for agent-driven quality PRs
- **Secure cognitive agent hardening** — STRIDE threat modeling, penetration testing, key management audit
- **Cross-platform distribution** — Homebrew formula, Nix flake, multi-arch Docker image, `pipx` install

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
- **Lint**: `uv run ruff check src/`
- **Type check**: `uv run mypy src/`
- **Build**: `uv run hatch build && uv run twine check dist/*`
- **Architecture**: `CLAUDE.md` + `PAI.md` + `src/codomyrmex/PAI.md`
- **PAI Integration**: `docs/pai/README.md` + `docs/pai/architecture.md`

---

*Last updated: 2026-03-04 — Sprint 24. v1.1.0 complete. v1.1.1 "Polish & Hardening" scoped.*
