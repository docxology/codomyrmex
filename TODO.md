<!-- markdownlint-disable MD060 MD033 -->
# Codomyrmex — TODO

**Version**: v1.2.7 | **Date**: 2026-03-19 | **Modules**: 129 | **Sprint**: 35

> **Current release**: v1.2.7 "Multi-Agent Swarm Orchestration" (2026-03-19).
> Sprint 35 work is scoped below as v1.2.8–v1.2.12, to be released incrementally.

Authoritative project backlog. Completed sprints summarised; upcoming work scoped fully.

---

## ✅ Released — v1.2.4 → v1.2.7

| Version | Date | Theme |
| :--- | :--- | :--- |
| v1.2.4 | 2026-03-18 | Google Affordances & Auth Unification |
| v1.2.5 | 2026-03-19 | Advanced Context Archival & Search |
| v1.2.6 | 2026-03-19 | Autonomous Knowledge Codification |
| v1.2.7 | 2026-03-19 | Multi-Agent Swarm Orchestration |

---

## 🔜 v1.2.8 — Automated Code Review Pipeline *(Sprint 35)*

> **Theme**: Surface `coding/review/` as a first-class MCP-accessible review pipeline. The underlying `ReviewAnalyzer`, `ReviewModels`, and code pattern matching already exist (750+ lines). This release wires them into MCP tools and integration tests.

| # | Deliverable | Module | Concrete Scope |
| :--- | :--- | :--- | :--- |
| D1 | `code_review_analyze` MCP tool | `coding/review/` | Wrap `ReviewAnalyzer.analyze(filepath)` → structured `ReviewReport` (issues, severity, suggestions). Accept `language`, `ruleset` params. |
| D2 | `code_review_batch` MCP tool | `coding/review/` | Batch-analyze a directory path; return aggregated findings sorted by severity. Use `ReviewAnalyzer` + `os.walk` with filter by extension. |
| D3 | `code_review_diff` MCP tool | `coding/review/` | Analyze only lines changed in a git diff; parse `git diff` output via `git_operations`, feed changed hunks to `ReviewAnalyzer`. |
| D4 | `StaticAnalysisReport` Pydantic model | `coding/review/models.py` | Add `overall_score: float`, `blocker_count: int`, `suggestion_count: int` aggregate fields to existing `ReviewReport`. |
| D5 | Integration tests | `tests/integration/coding/` | `test_review_analyze.py` (real Python files as targets, 8+ tests), `test_review_diff.py` (4+ tests against real git diffs). |

**Release criteria**: ruff clean, all tests pass, `pyproject.toml` → `1.2.8`, CHANGELOG entry.

---

## 🔜 v1.2.9 — Observability & Telemetry Hardening *(Sprint 35)*

> **Theme**: Make `telemetry/` production-grade — OpenTelemetry export, metric aggregation, agent-level tracing hooks, and a dashboard feed. `otel.py`, `pipeline.py`, and `metric_aggregator.py` exist (570+ lines); need MCP tools and integration.

| # | Deliverable | Module | Concrete Scope |
| :--- | :--- | :--- | :--- |
| D1 | `telemetry_record_event` MCP tool | `telemetry/` | Record a named event with `{name, attributes, timestamp}` via `TelemetryClient`; persist to `TelemetryPipeline`. |
| D2 | `telemetry_get_metrics` MCP tool | `telemetry/` | Query `MetricAggregator` for last-N-minutes aggregated metrics by label. Returns `{p50, p95, p99, count}`. |
| D3 | `telemetry_export_otel` MCP tool | `telemetry/otel.py` | Flush buffered spans/metrics to OTLP endpoint (configurable via `OTEL_EXPORTER_OTLP_ENDPOINT`). Silent no-op when endpoint unset. |
| D4 | Agent-level trace hooks | `telemetry/agent_hooks.py` | Wire `AgentOrchestrator.execute()` and `HermesClient.execute()` to emit spans automatically via `agent_hooks` decorators. |
| D5 | `telemetry_dashboard_feed` MCP tool | `telemetry/` | Return last 20 events as a time-sorted JSON feed for PAI dashboard integration. |
| D6 | Integration tests | `tests/integration/telemetry/` | `test_telemetry_pipeline.py` (6+ tests using real SQLite event store), `test_agent_hooks.py` (4+ tests on real `HermesClient` execution trace). |

**Release criteria**: ruff clean, all tests pass, `pyproject.toml` → `1.2.9`, CHANGELOG entry.

---

## 🔜 v1.2.10 — Graph RAG & Semantic Knowledge Retrieval *(Sprint 35)*

> **Theme**: `graph_rag/` has a `KnowledgeGraph` and multi-hop retrieval engine. `vector_store/` has `InMemoryVectorStore`. Together they enable graph-aware semantic search over codebases and knowledge items. Wire them with MCP tools and Ollama embedding.

| # | Deliverable | Module | Concrete Scope |
| :--- | :--- | :--- | :--- |
| D1 | `graph_rag_ingest` MCP tool | `graph_rag/` | Add a document (text + metadata) to the `KnowledgeGraph`; build entity→entity edges from co-occurrence and WikiLink parsing. |
| D2 | `graph_rag_query` MCP tool | `graph_rag/` | Multi-hop graph retrieval: embed query via Ollama `nomic-embed-text`, walk the KG, return `{nodes, edges, passages, score}`. |
| D3 | `graph_rag_prune` MCP tool | `graph_rag/` | Remove stale nodes by age (`max_age_days`) or low-connectivity threshold (`min_degree`). |
| D4 | `vector_store_upsert` / `vector_store_search` MCP tools | `vector_store/` | Expose `InMemoryVectorStore` via MCP: upsert `{id, text, metadata}`, cosine-similarity search with top-k. |
| D5 | Ollama embedding bridge | `graph_rag/embedding.py` | Real embedding via `llm/ollama/` — `nomic-embed-text` with 2 s timeout, fallback to TF-IDF bag-of-words. |
| D6 | Integration tests | `tests/integration/graph_rag/` | `test_graph_ingest_query.py` (8+ tests: round-trip ingest→query), `test_vector_search.py` (6+ tests). Ollama-guarded with `@pytest.mark.network`. |

**Release criteria**: ruff clean, all tests pass, `pyproject.toml` → `1.2.10`, CHANGELOG entry.

---

## 🔜 v1.2.11 — Prompt Engineering & LLM Evaluation Suite *(Sprint 36)*

> **Theme**: `prompt_engineering/` has `PromptOptimizer` (342 lines), `TemplateLibrary`, and `EvaluationEngine` (397 lines). This release turns them into first-class MCP-accessible tools for PAI prompt iteration and LLM output assessment.

| # | Deliverable | Module | Concrete Scope |
| :--- | :--- | :--- | :--- |
| D1 | `prompt_optimize` MCP tool | `prompt_engineering/optimization.py` | Run `PromptOptimizer.optimize(prompt, task_description)` — iterative rewrite using `HermesClient` + evaluation feedback loop (max 3 rounds). |
| D2 | `prompt_evaluate` MCP tool | `prompt_engineering/evaluation.py` | Score a `(prompt, response)` pair on `{coherence, relevance, completeness, safety}` via `EvaluationEngine`. Returns `{score: float, breakdown: dict}`. |
| D3 | `prompt_template_render` MCP tool | `prompt_engineering/templates.py` | Render a named `PromptTemplate` with `variables: dict`. Templates loaded from `~/.codomyrmex/prompt_templates/`. |
| D4 | `prompt_ab_compare` MCP tool | `prompt_engineering/` | Evaluate two prompt variants against the same task; return ranked comparison `{winner, margin, rationale}`. |
| D5 | LLM output schema validator | `prompt_engineering/evaluation.py` | Add `validate_schema(response, schema: dict)` — JSON schema enforcement for structured LLM outputs, real `jsonschema` validation. |
| D6 | Integration tests | `tests/integration/prompt_engineering/` | `test_prompt_evaluate.py` (6+ tests), `test_template_render.py` (5+ tests with real template files). |

**Release criteria**: ruff clean, all tests pass, `pyproject.toml` → `1.2.11`, CHANGELOG entry.

---

## 🔜 v1.2.12 — Security Hardening & Compliance Reporting *(Sprint 36)*

> **Theme**: `security/` has `ComplianceReport` (169 lines), `SecurityScanner`, `Permissions`, and a `dashboard.py`. Wire into actionable MCP tools — automated dependency CVE scanning, SBOM generation, and compliance gate for CI workflows.

| # | Deliverable | Module | Concrete Scope |
| :--- | :--- | :--- | :--- |
| D1 | `security_scan_dependencies` MCP tool | `security/` | Run `pip-audit` / `uv audit` on `pyproject.toml`; return `{vulnerable: [{package, cve, severity, fix_version}]}`. |
| D2 | `security_generate_sbom` MCP tool | `security/` | Generate a CycloneDX SBOM from `uv pip list --format json`; write to `sbom.json` in project root. |
| D3 | `security_compliance_report` MCP tool | `security/compliance_report.py` | Run `ComplianceReport.generate(policy)` for `{owasp_top10, cwe_sans_25, pci_dss_basic}`; return structured findings with remediation hints. |
| D4 | `security_check_permissions` MCP tool | `security/permissions.py` | Audit file permissions in `src/` for world-writable or executable Python files; return flagged paths. |
| D5 | CI gate script | `scripts/security/security_gate.py` | Call `security_scan_dependencies` + `security_compliance_report`; exit non-zero if any HIGH/CRITICAL findings. Makefile target `make security-gate`. |
| D6 | Integration tests | `tests/integration/security/` | `test_scan_dependencies.py` (5+ tests on real lock file), `test_compliance_report.py` (4+ tests). |

**Release criteria**: ruff clean, all tests pass, `pyproject.toml` → `1.2.12`, CHANGELOG entry.

---

## 🔭 v1.3.x Series — Cognitive & Multimodal Expansion *(Sprint 37+)*

> **Theme**: Unlock the AI-native modules — active inference, multimodal vision/audio pipelines, and the Cerebrum reasoning engine — as first-class PAI capabilities.

| Version | Theme | Key Deliverables |
| :--- | :--- | :--- |
| **v1.3.0** | **Cerebrum Reasoning Engine** | `CerebrumEngine.reason()` MCP tool; `BayesianNetwork` inference; `ActiveInferenceAgent` free-energy minimisation; `CaseBase.retrieve_similar()` for case-based reasoning. |
| **v1.3.1** | **Vision & PDF Intelligence** | `vision_analyze_image` / `vision_extract_pdf` MCP tools (Ollama VLM); `AnnotationExtractor` structured JSON from images; PAI can now visually inspect screenshots and PDFs. |
| **v1.3.2** | **Audio Pipeline & STT/TTS** | `audio_transcribe` (Whisper via `faster-whisper`), `audio_speak` (Edge TTS), `audio_stream_start/stop` WebSocket MCP tools; live voice interface for PAI. |
| **v1.3.3** | **Multimodal LLM Routing** | `multimodal_infer` MCP tool routing image+text to Ollama VLM or OpenAI GPT-4V; `SemanticRouter` dispatching via `semantic_router/` to best-fit LLM provider by modality+cost. |

---

## 🔭 v1.4.x Series — Platform Hardening *(Sprint 38+)*

> **Theme**: Production-grade infrastructure: type safety gate, mutation testing, containerised CI, and coverage push to 50%.

| Version | Theme | Key Deliverables |
| :--- | :--- | :--- |
| **v1.4.0** | **Type Safety Gate** | `ty` diagnostics to 0 across all 129 modules; `ty check` added to CI; `ANN*` rules progressively re-enabled in ruff. |
| **v1.4.1** | **Mutation Testing Integration** | `mutmut` expanded from 3 → 15 modules; mutation score ≥ 60% gated in CI; `make mutation-test` target. |
| **v1.4.2** | **Coverage Push → 50%** | Systematic coverage expansion for `cerebrum/`, `fpf/`, `relations/`, `orchestrator/`; `fail_under` ratcheted 40% → 50% in `pyproject.toml`. |
| **v1.4.3** | **Containerised CI & SBOM** | Docker-based test matrix (`python 3.11–3.14`); SBOM auto-generated on every release tag; `security-gate` in CI pipeline. |

---

## 🔭 v2.0.0 — Spatial & Identity *(Horizon)*

> **Theme**: Embodied agents, cryptographic self-custody, and 4D world modeling.

| # | Direction | Builds On | Concrete Next Step |
| :--- | :--- | :--- | :--- |
| R1 | **Spatial World Models** | `spatial/` | `spatial_render_agent_trial(scene_config)` MCP tool; 4D time-series scene generation via `spatial/four_d/` integrated into `spatial/world_models/`. |
| R2 | **Self-Custody Wallet** | `wallet/` | `WalletManager` ZK-proof interfaces; agent-controlled resource attestation; integration with `identity/` for signed capability proofs. |
| R3 | **Identity & Persona** | `identity/` | `BioCognitiveVerifier` real-bio hooks; multi-persona masking via `Persona` rotation on `IdentityManager`; gated via `security/` trust model. |
| R4 | **Anonymous Market** | `market/` | `ReverseAuction` + `DemandAggregator` for agent-to-agent capability trading; mixnet-proxied via `privacy/MixnetProxy`. |

---

## Release Criteria

> [!IMPORTANT]
> **Required before any version tag**:
>
> - **Zero-Mock Policy**: All tests use 100% real components. No `unittest.mock` behavioural mocking permitted.
> - **Full Test Pass**: `uv run pytest` exits 0.
> - **Lint Clean**: `uv run ruff check src/` exits 0.
> - **Version Sync**: `pyproject.toml`, `__init__.py`, `AGENTS.md`, `TODO.md`, `CHANGELOG.md` all agree.
> - **CHANGELOG Entry**: Written, dated, and in reverse-chronological order.
> - **Documentation Parity**: Any new MCP tools have entries in `MCP_TOOL_SPECIFICATION.md` for their module.

---

## Reference

- **Test**: `uv run pytest` · **Lint**: `uv run ruff check .` · **Format**: `uv run ruff format .`
- **Type**: `uv run ty check src/` · **Build**: `uv build` · **Coverage gate**: `fail_under=40`
- **Security**: `make security-gate` *(v1.2.12+)*

---

*Last updated: 2026-03-19 — Sprint 35.*
