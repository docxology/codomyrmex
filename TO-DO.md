# TO-DO — Codomyrmex Development Roadmap

**Version**: v1.0.4-dev | **Date**: 2026-02-27 | **Modules**: 88

---

## Codebase Snapshot (Verified 2026-02-27)

| Metric | Value | Method |
| :--- | :--- | :--- |
| Top-level source modules | 88 | `len(codomyrmex._submodules)` |
| Source files (non-test) | 1,623 | `find -name "*.py" -not -path "*/tests/*"` |
| Source LOC (non-test) | 290,319 | `wc -l` across source files |
| Total LOC (incl. tests) | 490,240 | `wc -l` across all `.py` |
| Test files | 689 | `find -path "*/tests/*" -name "*.py"` |
| `NotImplementedError` sites | 12 across 10 source files | `grep -rn NotImplementedError` (excl. tests, comments, string literals, code generation) |
| Pass-only function stubs | **255** across 38 modules | AST analysis: functions whose only real body statement is `pass` |
| Missing `@abstractmethod` markers | **0** (was 26, all resolved in v1.0.4 cycle) | AST analysis: pass-only methods in classes missing `@abstractmethod` |
| Conditional skip markers (`skipif` / `importorskip`) | 49 test files | `grep -rc` |
| `xfail` markers | 4 test files | `grep -rc` |
| Unconditional `skip` markers | 1 test file | `grep -rc` |
| Coverage threshold (unified) | 68% | `pyproject.toml`, `pytest.ini`, `ci.yml` aligned |
| RASP documentation compliance | 100% (87/87) | Automated audit |
| Zero-Mock policy | Enforced via `ruff.lint.flake8-tidy-imports.banned-api` | `pyproject.toml` |
| Python compatibility | 3.10 – 3.14 | `pyproject.toml classifiers` + `conftest.py` namespace guard |

### Pass-Only Stub Distribution (Top 15 Modules)

| Module | Stub Count | Nature |
| :--- | :---: | :--- |
| `cloud` | 27 | ABC interfaces (`CloudProvider`, `StorageProvider`, `ComputeProvider`, `ServerlessProvider`) + Infomaniak |
| `llm` | 25 | ABC interfaces (`BaseLLMProvider`, `BaseEmbedding`, `BaseMemory`, `BaseChunker`, `BaseRetriever`) |
| `cache` | 17 | ABC interfaces (`BaseCacheBackend`) + backend implementations |
| `agents` | 16 | ABC/protocol methods + `AgentRegistry` |
| `audio` | 14 | ABC + STT/TTS provider stubs |
| `collaboration` | 12 | `CollaborationAgent`, `Channel`, `Protocol` ABCs |
| `coding` | 12 | Parser ABCs + refactoring/static analysis stubs |
| `telemetry` | 10 | `SpanExporter`, `MetricReader` ABC methods |
| `ide` | 8 | `IDEIntegration` base class — 8 methods all stubs |
| `model_ops` | 8 | `FeatureStore`, `ArtifactStore` interfaces |
| `security` | 7 | `AuditStore`, `ComplianceControl`, `SecurityCheck` ABCs |
| `api` | 7 | `APIEndpoint` interface methods |
| `orchestrator` | 7 | `ExecutionEngine`, `PipelineStage`, `Trigger` ABCs |
| `containerization` | 6 | WASM runtime + security scanner stubs |
| `vector_store` | 6 | `VectorStore` ABC — full interface |

> **Interpretation**: ~120 of the 255 stubs are intentional ABCs (abstract base class methods defining interfaces for subclass implementation). The remaining ~135 are **implementation gaps** — methods on concrete classes or modules that should contain real logic.

---

## v1.0.3 — "Obsidian Module v3.0" ✅ RELEASED (2026-02-27)

| # | Item | Status |
| :-- | :--- | :---: |
| 1 | Obsidian CI stability (413/413 tests) | ✅ |
| 2 | Coverage holds (`--cov-fail-under=68`) | ✅ |
| 3 | CHANGELOG consolidation (two `[1.0.3-dev]` → `[1.0.3]`) | ✅ |
| 4 | SECURITY.md version table (`0.1.x` → `1.0.x`) | ✅ |
| 5 | Root docs version sweep | ✅ |
| 6 | Pre-commit pin refresh (Black 26.1.0, ruff v0.15.4, mypy v1.19.1) | ✅ |
| 7 | `__init__.py` + `pyproject.toml` version bump → `1.0.3` | ✅ |

---

## v1.0.4 — "Stub Elimination & Concrete Modules"

### Release Quality Gate Standard

> [!IMPORTANT]
> Every method implemented in v1.0.4 **must** satisfy all four criteria before the release tag:
>
> 1. **Real** — Functional implementation, no mocks, no placeholder logic
> 2. **Tested** — Zero-mock test(s) in `src/codomyrmex/tests/unit/` validating real behaviour
> 3. **Validated** — `pytest` green, `py_compile` clean, lint-free
> 4. **Documented** — Docstring with Args/Returns/Example sections; module README/SPEC updated if public API
>
> Additionally, each *module area* touched must have a **thin orchestration example** in `scripts/examples/` — a runnable ~50-80 line script demonstrating real cross-module integration (no mocks, no stubs, real I/O).

### 1. `NotImplementedError` Elimination (12 remaining → 0)

7 sites were implemented in the v1.0.3 cycle. The remaining 12 are all correct architectural patterns:

| File | Sites | Classification | Action |
| :--- | :---: | :--- | :--- |
| `agents/core/base.py` | 2 | `@abstractmethod` ABC (`plan()`, `act()`) | ✅ Correct — add `# ABC: intentional` comment |
| `agents/generic/api_agent_base.py` | 2 | `@abstractmethod` ABC (`observe()`, `_build_prompt()`) | ✅ Correct — add `# ABC: intentional` comment |
| `collaboration/coordination/leader_election.py` | 1 | `@abstractmethod` ABC (`elect()`) — concrete impls exist | ✅ Correct |
| `collaboration/agents/base.py` | 1 | `@abstractmethod` ABC (`_execute_task()`) | ✅ Correct |
| `identity/identity.py` | 1 | `@abstractmethod` ABC (`authenticate()`) — concrete impls exist | ✅ Correct |
| `module_template/scaffold.py` | 1 | Intentional template sentinel (`process()`) | ✅ Correct — sentinel for consuming module |
| `cloud/infomaniak/base.py` | 1 | Design-by-contract (`from_env()` requires subclass override) | ✅ Correct |
| `model_context_protocol/transport/client.py` | 3 | `@abstractmethod` ABC (`send`, `send_notification`, `close`) — `_StdioTransport` + `_HTTPTransport` are concrete | ✅ Correct |

**Previously implemented in v1.0.3→v1.0.4 cycle** (7 sites, all tested):

| File | Function | Implementation |
| :--- | :--- | :--- |
| `documents/transformation/converter.py` | `_to_markdown` | HTML→MD via markdownify with fallback |
| `config_management/monitoring/config_monitor.py` | `_get_previous_hash` + `_persist_hashes` | JSON file-based hash persistence |
| `agents/llm_client.py` | `create_session` + `close_session` | In-memory session tracking |
| `llm/mcp.py` | `_handle_resource_read` | `file://` URI reads + metadata fallback |
| `coding/debugging/patch_generator.py` | `generate` + `_parse_patches` | LLM-driven diff generation and parsing |
| `ide/cursor/__init__.py` | `get_active_file` | MRU file heuristic |
| `ide/antigravity/__init__.py` | `get_active_file` | Artifact MRU + workspace fallback |

### 2. Missing `@abstractmethod` Marker Fix ✅ COMPLETE (26 → 0)

All 26 pass-only methods on concrete/ABC classes have been addressed in the v1.0.4 cycle:
- Optional-override hooks received `return None` + docstring (e.g., `on_success`, `shutdown`, `__exit__`)
- True abstract methods received `@abstractmethod` decoration (e.g., `WorldModel.update`)
- Initializers received real initialization logic (e.g., `SecurityScanner.__init__`, `ASTMatcher.__init__`)
- `synergetics_transform()` in `spatial/four_d` converted to `raise NotImplementedError`

| Module | Methods | Resolution |
| :--- | :--- | :--- |
| `orchestrator/pipelines` | `Stage.on_success`, `Stage.on_failure` | ✅ Optional-override no-ops with docstrings |
| `telemetry/tracing` | `ConsoleExporter.shutdown` | ✅ `return None  # Intentional no-op` |
| `telemetry/exporters` | `ConsoleExporter.shutdown`, `FileExporter.shutdown`, `OTLPExporter.shutdown` | ✅ `return None  # Intentional no-op` |
| `coding/pattern_matching` | `CodeSimilarity.__init__`, `ASTMatcher.__init__` | ✅ Real initialization logic added |
| `coding/static_analysis` | `performance_context.__init__/__exit__` | ✅ Legitimate context manager no-ops |
| `ci_cd_automation/build` | `BuildManager.__init__` | ✅ Config loading implemented |
| `cloud/infomaniak` | `InfomaniakS3Base.close` | ✅ Real `self._conn.close()` logic |
| `data_visualization` | `performance_context.__init__/__exit__` ×4 | ✅ Legitimate context manager no-ops |
| `utils/process` | `ScriptBase.add_arguments`, `LogContext.__exit__` | ✅ Optional-override no-ops |
| `agents/ai_code_editing` | `CodeEditor.setup` | ✅ `return None  # Optional setup hook` |
| `containerization/security` | `SecurityScanner.__init__`, `PerformanceOptimizer.__init__` | ✅ Registry initialization |
| `performance` | `performance_context.__exit__` | ✅ `return None  # Intentional no-op` |
| `performance/monitoring` | `performance_context.__init__/__exit__` | ✅ No-op stub with docstring |
| `spatial/world_models` | `WorldModel.update` | ✅ `@abstractmethod` marker added |
| `examples/` | `SimulatedAgent.setup` | ✅ `return None  # Demo agent` |

### 3. High-Priority Stub Backfill (~135 concrete stubs → working implementations)

Prioritized by module criticality and user-facing impact. Excludes ~120 intentional ABC methods which should instead receive `@abstractmethod` markers.

| Priority | Module | Stubs | Key Functions to Implement | Dependencies |
| :--- | :--- | :---: | :--- | :--- |
| **P0** | `ide` | 8 | `connect()`, `disconnect()`, `execute_command()`, `open_file()` | Cursor/Antigravity extension APIs |
| **P0** | `collaboration` | 12 | `CollaborationAgent.process_task()`, `Channel.send()/receive()`, `Protocol.execute()` | `events`, `agents` |
| **P1** | `coding` | 12 | `TreeSitterParser.parse()`, `RefactoringEngine.analyze()/execute()`, `StaticAnalyzer.__init__()` | `tree-sitter` optional dep |
| **P1** | `cloud` | 27 | `CloudProvider` CRUD, `StorageProvider` bucket/file ops, `ServerlessProvider` function mgmt | `boto3`, `google-cloud-storage`, `azure-*` optional deps |
| **P1** | `orchestrator` | 7 | `ExecutionEngine.execute()`, `PipelineStage.execute()`, `Trigger.get_next_run()` | `events`, `concurrency` |
| **P2** | `llm` | 25 | `BaseLLMProvider.complete()/complete_stream()`, `BaseEmbedding.embed()`, `BaseMemory.add_message()` | Mostly ABCs — add `@abstractmethod`; implement on concrete subclasses |
| **P2** | `telemetry` | 10 | `SpanExporter.export()/shutdown()`, `MetricReader.get_value()` | `opentelemetry-*` optional deps |
| **P2** | `security` | 7 | `AuditStore.store()/query()`, `ComplianceControl.check()`, `SecurityCheck.check()` | None |
| **P3** | `audio` | 14 | STT/TTS provider implementations | `faster-whisper`, `edge-tts` optional deps |
| **P3** | `cache` | 17 | `BaseCacheBackend` implementations | `redis` optional dep |
| **P3** | `containerization` | 6 | WASM runtime `load_module()/execute()` | `wasmtime` (new optional dep) |
| **P3** | `evolutionary_ai` | 3 | `mutate()`, `crossover()`, `select()` operators | `numpy` |
| **P3** | `feature_flags` | 3 | `Strategy.evaluate()`, serialization | None |

### 4. Structural Quality

| Item | Current State | Target | Files |
| :--- | :--- | :--- | :--- |
| **Oversized files** | `website/server.py` = 1,052 LOC | ≤500 LOC per file | Extract route handlers into `website/routes/` |
| **ABC marker audit** | 26 pass-only stubs missing `@abstractmethod` | 0 missing markers | See §2 above |
| **Circular imports** | ~35 pairs estimated (from SPEC.md) | 0 pairs | Run `scripts/audit_imports.py`; break cycles with lazy imports or protocol classes |
| **Deprecated modules** | `embodiment`, `defense` emit `DeprecationWarning` | Add `DEPRECATED.md` migration guides in each module | `embodiment/`, `defense/` |
| **Skip marker hygiene** | 49 files with conditional skips, 4 with xfail, 1 unconditional | All unconditional skips removed; xfail items have linked issue numbers | Test files across modules |

---

## v1.1.0 — "Production Readiness"

First feature release targeting external consumption.

| Item | Scope | Detail |
| :--- | :--- | :--- |
| **PyPI publication** | `pyproject.toml`, `release/` | Validate: `hatch build` → `twine check` → TestPyPI dry-run → production publish. Requires: clean `__all__` exports, no broken imports on fresh install |
| **MCP deprecation timeline UI** | `model_context_protocol/`, `website/` | Surface `deprecated_in` metadata from `@mcp_tool` decorator in `/api/tools` JSON response and dashboard UI |
| **Bidirectional PAI ↔ Codomyrmex** | `agents/pai/` | Implement callback channel so Codomyrmex can initiate calls to PAI. Currently: filesystem back-channel only. Target: HTTP webhook or Unix socket |
| **CLI doctor v2** | `cli/doctor.py` | Add `--fix` mode: auto-create `.env` from template, install missing optional deps, fix `pythonpath`, validate RASP docs |
| **API key rotation workflow** | `config_management/secrets/` | Automated key rotation: detect stale keys → generate new → update `.env` → notify. Integrate with `pre-commit` secret scanner |
| **Mutation testing expansion** | `pyproject.toml [tool.mutmut]` | Extend from 3 files (`validation.py`, `trust_gateway.py`, `mcp_schemas.py`) to cover `security/secrets/`, `orchestrator/core.py`, `events/core/event_bus.py` |
| **mypy strict ramp** | `pyproject.toml [[tool.mypy.overrides]]` | Promote `agents` from `disallow_untyped_defs = false` to `true` incrementally. Current strict error count: ~612. Target: ≤300 |
| **Integration test formalization** | `tests/integration/` | Formalize existing 11 workflow integration test files into CI pipeline with `pytest -m integration` marker |
| **Documentation site deployment** | `docs_gen/site_generator.py`, `mkdocs.yml` (new) | Generate `mkdocs-material` site from 88 module RASP docs. Deploy to GitHub Pages or ReadTheDocs |

---

## Medium-Term Development

Functional deepening and ecosystem maturation. No fixed release target; items are ordered by estimated impact.

- **Collaboration module — Tier 2 promotion**: 12 pass-only stubs in `collaboration/agents/`, `communication/`, `coordination/`, `protocols/`. Implement `AgentRegistry` with in-memory store, `Channel.send()/receive()` over `EventBus`, and Bully leader election. Test with multi-agent task delegation scenario. *Depends on*: `events`, `agents`

- **Feature flags engine**: 3 stubs in `strategies/`. Implement `PercentageStrategy`, `UserListStrategy`, `TimeWindowStrategy`. Add JSON file persistence for flag state. Wire into `config_management` for runtime flag loading. *Depends on*: `serialization`, `config_management`

- **Infomaniak cloud provider**: 27 cloud stubs overall — Infomaniak is the concrete provider with the most gaps (`base.py` + 1 `NotImplementedError`). Implement storage API (Swift-compatible), compute API (Nova-compatible), and DNS management against Infomaniak's public API. *Depends on*: `cloud/common/` ABC layer

- **Graph RAG pipeline**: Connect `graph_rag` knowledge graph to `llm/rag/` for retrieval-augmented generation with structured entity relationships. Implement: graph construction from Obsidian vaults, entity-aware retrieval, and context window assembly. *Depends on*: `agentic_memory/obsidian`, `llm/rag`, `llm/embeddings`

- **Agentic memory persistence**: Currently in-memory only beyond Obsidian. Add SQLite backend for `MemoryStore` with TTL-based expiry, tag indexing, and cross-session retrieval. Redis backend as optional high-performance alternative. *Depends on*: `database_management`, `serialization`

- **Dashboard v2**: Current `website/server.py` (1,052 LOC) serves telemetry and test metrics. Add: WebSocket real-time streaming, test-run history timeline, module health heatmap, per-module stub/coverage sparklines. Requires route extraction (see v1.0.4 structural items). *Depends on*: `telemetry`, `performance`, `data_visualization`

- **Formal verification integration**: Wire `z3-solver` (already in optional deps) into `coding/` for automated invariant checking. Target: generate Z3 constraints from function signatures + docstring contracts, verify simple properties (bounds, null safety). *Depends on*: `coding/static_analysis`, `z3-solver`

- **Multimodal agent pipeline**: Connect `audio` extras (Whisper STT via `faster-whisper`, Edge TTS via `edge-tts`) and `video` extras (MoviePy, OpenCV) to agent conversation loop. Target: voice-in/voice-out agent interaction and image analysis in agent context. *Depends on*: `agents`, `llm`, `audio`, `video` optional deps

- **Cost management activation**: Implement real API spend tracking using provider usage APIs (OpenRouter `/api/v1/credits`, OpenAI `/v1/usage`, Anthropic `/v1/usage`). Add budget alerting with configurable thresholds and Slack/email notification via `events/notification/`. *Depends on*: `llm/providers`, `events/notification`, `networking`

---

## Longer-Term Vision

Architectural extensions and research directions. These are aspirational and may require significant design work before implementation.

- **Spatial reasoning & Synergetics** — Deepen the `spatial` module beyond current 2 stub functions (`synergetics_transform`, `update`). Implement Fuller-inspired geodesic coordinate transforms, 4D rotation matrices (quaternion-based), and icosahedral mesh generation. Integrate with `data_visualization` for 3D rendering via Matplotlib or ModernGL

- **Embodiment & ROS2 bridge** — The `embodiment` module is currently deprecated with `DeprecationWarning`. Decide: either archive and remove, or invest in full ROS2 bridge implementation with `rclpy` bindings, sensor data topic subscriptions, actuator command publishing, and safety interlock state machines

- **Evolutionary AI operators** — 3 stubs in `evolutionary_ai/operators/` (`mutate()`, `crossover()`, `select()`). Implement tournament selection, single-point/uniform crossover, Gaussian mutation. Add `Population` class for generation management and fitness tracking. Target: usable for neural architecture search in `inference_optimization`

- **Cerebrum cognitive architecture** — Extend Bayesian reasoning engine with real probabilistic inference using `scipy.stats`. Implement belief revision (Jeffrey conditionalization), multi-hypothesis planning (particle filtering), and integrate with `agents/planner/` for uncertainty-aware goal decomposition

- **Inference optimization** — Implement INT8/INT4 quantization wrappers (using `ctransformers` or `llama.cpp` bindings), knowledge distillation training loops, and speculative decoding for local model acceleration. Wire into `llm/providers/` as a transparent optimization layer

- **Plugin marketplace** — Build plugin discovery (scan entry points + PyPI search), installation (`pip install` with sandboxed dependency resolution), version management, and compatibility checking. Surface via `plugin_system/discovery.py` and `skills/` registry. Requires security review for arbitrary code execution

- **Multi-agent swarm protocols** — Production-grade swarm coordination beyond current `collaboration/` stubs. Target: fault-tolerant consensus (Raft implementation in `coordination/`), hierarchical task decomposition, emergent behavior monitoring via `telemetry`, and configurable communication topologies (mesh, star, ring)

- **Self-improving pipelines** — Connect existing `ImprovementPipeline` (detect → fix → test → review) to CI/CD via GitHub Actions workflow trigger. Target: agent-driven code quality PRs with `AntiPatternDetector` findings, automated test generation, and human-in-the-loop review gates

- **Secure cognitive agent hardening** — The 5 Secure Cognitive modules (`identity`, `wallet`, `defense`, `market`, `privacy`) are at demo-level maturity. Production deployment requires: formal threat modeling (STRIDE), penetration testing of bio-cognitive verification, key management audit, and mixnet routing validation with real network conditions

- **Cross-platform distribution** — Package `codomyrmex` CLI for broad adoption: Homebrew formula (macOS), Nix flake (NixOS/cross-platform), multi-arch Docker image (amd64/arm64), and `pipx` install pathway. Requires: clean entry point (`codomyrmex.cli:main`), minimal core deps, optional feature detection at runtime

---

*Last updated: 2026-02-28 — §2 complete (all 26 @abstractmethod markers resolved). v1.0.3 released.*
