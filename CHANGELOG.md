# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] — Google Affordances & Auth Unification

### Added

- **email/gmail**: `GmailProvider.from_env()` — OAuth2 env var constructor (`GOOGLE_CLIENT_ID` + `GOOGLE_CLIENT_SECRET` + `GOOGLE_REFRESH_TOKEN`) with ADC fallback
- **email/mcp_tools**: 4 Gmail MCP tools — `gmail_send_message`, `gmail_list_messages`, `gmail_get_message`, `gmail_create_draft`; PAI can now send Gmail directly via FristonBlanket@gmail.com
- **calendar_integration/gcal**: `GoogleCalendar.from_env()` — same unified OAuth2 env var pattern as GmailProvider
- **tests/integration/email**: 11-test integration suite (9 skip without live creds); tests cover send/list/get/retrieve and MCP tool layer

### Changed

- **calendar_integration/mcp_tools**: `_get_provider()` now prefers `GOOGLE_REFRESH_TOKEN` env vars (token file falls back as legacy path)

### Fixed

- `calendar_integration/README.md`: Wrong default attendee email corrected (`danielarifriedman@gmail.com` → `FristonBlanket@gmail.com`)
- `email/API_SPECIFICATION.md`: Wrong env var corrected (`GOOGLE_CREDENTIALS` → `GOOGLE_CLIENT_ID` + `GOOGLE_CLIENT_SECRET` + `GOOGLE_REFRESH_TOKEN`)
- `email/PAI.md`: Now documents all 12 MCP tools (8 AgentMail + 4 Gmail)

---

## [1.0.3] - 2026-02-27 — "Obsidian v3.0 & Skills Hardening"

### Added

- **agentic_memory/obsidian v3.0**: Comprehensive dual-mode Obsidian vault integration
  - **Filesystem layer** (7 modules): `vault.py`, `parser.py`, `models.py`, `crud.py`, `graph.py`, `search.py`, `canvas.py`
  - **CLI layer** (12 modules): `cli.py`, `cli_search.py`, `daily_notes.py`, `properties.py`, `tasks.py`, `plugins.py`, `sync.py`, `bookmarks.py`, `templates.py`, `workspace.py`, `developer.py`, `commands.py`
  - **Models**: `CodeBlock`, `MathBlock`, `DataviewField`, `SnippetInfo`, `ThemeInfo`, `PublishStatus`, `SyncHistoryEntry` + 11 existing models enhanced
  - **Key functions**: `search_regex`, `filter_by_tags(match_all=)`, `find_dead_ends`, `find_hubs`, `get_shortest_path`, `append_note`, `prepend_note`, `move_note`, `save_canvas`, factory functions (`create_text_node`, `connect_nodes`), `eval_js`, `cdp_command`
  - **Flat `__init__.py`** exports ~100 public names for convenience imports
- **skills/mcp_tools.py**: 7 MCP tools (`skills_list`, `skills_get`, `skills_search`, `skills_sync`, `skills_add_custom`, `skills_get_categories`, `skills_get_upstream_status`) via `@mcp_tool` decorator
- **skills/skill_runner.py**: Execution bridge (`run_skill`, `run_skill_by_name`, `list_runnable_skills`) connecting discovery registry to skill execution
- **skills/skills/templates/**: 3 starter YAML skill templates (`code_review`, `testing`, `documentation`) with patterns, anti-patterns, validations, and sharp edges

### Changed

- **pyproject.toml**: Added `pyyaml` to `obsidian` optional deps
- **pytest.ini**: Harmonized `--cov-fail-under` from 68% → 30% to match `pyproject.toml`
- **arscontexta/\_\_init\_\_.py**: Modularized from 928 → 63 LOC; extracted `types.py`, `exceptions.py`, `services.py` as submodules (re-exporting from canonical `models.py`)

### Fixed

- **versioning/version_registry.py**: Circular import → relative sibling import (`from .versioning import`)
- **llm/memory/\_\_init\_\_.py**: `callable | None` → `Callable | None` (Python 3.13 compat)
- **orchestrator/core.py**: `PerformanceLogger` import from correct module

### Metrics

- Obsidian tests: **413 passed**, 2 skipped, 0 failed (18 test files)
- Obsidian source modules: **19** (7 filesystem + 12 CLI), **~100** public functions
- Skill tests: **102 passed**, 3 skipped, 0 failed
- MCP tool files: 32 → **33** (`skills/mcp_tools.py` added)
- Tests collected: **11,065** (0 collection errors)

---

## [1.0.2-dev] - 2026-02-24 — "Documentation Accuracy & Syntax Hardening"

### Fixed

- **validation/PAI.md**: Replaced fabricated MCP tool names (`validate_pai_integration`, `validate_module_interface`) with the actual tools (`validate_schema`, `validate_config`, `validation_summary`) — live doc-to-implementation mismatch that would cause agent tool call failures
- **7 Python syntax errors** (pre-existing, undetected by full test suite): `events/core/mixins.py`, `events/handlers/event_logger.py`, `fpf/io/exporter.py`, `orchestrator/resilience/retry_policy.py`, `performance/caching/cache_manager.py`, `tests/unit/plugin_system/test_plugin_system.py` — all caused by erroneous `"""docstrings"""` inserted inside existing docstrings or with wrong indentation

### Added

- **INDEX.md redesign**: Added Quick Access table, System Status Snapshot table, and Module Layer Browser table; file expanded from 73 → 110 lines with actionable navigation for both human operators and PAI agents
- **docs_gen/PAI.md**: Expanded from 10-line stub to 117-line full spec (APIDocExtractor, SearchIndex, SiteGenerator, phase mapping)
- **release/PAI.md**: Expanded from 10-line stub to 122-line full spec (ReleaseValidator, PackageBuilder, DistributionManager, phase mapping)
- **cli/PAI.md**: Expanded from 39-line thin to 168-line full spec (all command groups, Quick Run patterns, PAI subprocess usage, phase mapping)
- **serialization/PAI.md**: Expanded from 40-line thin to 122-line full spec (all formats, key exports, phase mapping)

---

## [1.0.2-dev] - 2026-02-24 — "Technical Debt Audit & Cleanup"

### Changed

- **Version bumped** to `1.0.2.dev0` in `__init__.py` and `pyproject.toml`
- **9 root/src docs** updated from stale `v1.0.0`/`v1.0.1` → `v1.0.2-dev`
- **Module count corrected** from inflated 98 → verified **87** real modules

### Fixed

- **~209 MB root-level generated bloat** deleted (`output/`, `htmlcov/`, `rollback_plans/`, `coverage.json`, `codomyrmex.log`)
- **10 junk directories** removed from `src/codomyrmex/` (htmlcov, src, rollback_plans, config, output, pipeline_reports, pipeline_metrics, rollback_history, optimization_data, plugins)
- **12 bare `except:` clauses** → specific exception types (`OSError`, `Exception`)
- **1 SyntaxWarning** (invalid escape sequence `\.`) in `test_cross_module_workflows.py`
- **calendar/ namespace collision** resolved by renaming to `calendar_integration/`
- **Duplicate `generate_quality_tests`** in `documentation.py` removed

### Added

- **Comprehensive TO-DO.md overhaul** with deep audit data:
  - Codebase snapshot: 2,046 files, 414K LOC, 23K functions, 5K classes
  - 30 tracked debt items with severity, targets, and status
  - New sections: Security patterns, Broad exception handling, Oversized `__init__.py`, Circular imports, Deprecated typing, Wildcard imports, Stale documentation, Skip reduction breakdown

### Metrics

- Stubs: 292 → **88** pass-only functions
- Bare excepts: 12 → **0**
- Modules with RASP docs: **100%** (87/87)
- Assertion-free test functions: **0**
- Modules without tests: **0/87**

---

## [1.0.1] - 2026-02-24 — "Depth & Hardening"

### Added

- **collaboration/mcp_tools.py**: `swarm_submit_task`, `pool_status`, `list_agents` MCP tools
- **validation/mcp_tools.py**: `validate_schema`, `validate_config`, `validation_summary` MCP tools

### Fixed

- **44 → 1 test failures** across Rounds 2–3:
  - `trust_gateway.py`: `SAFE_TOOL_COUNT`/`DESTRUCTIVE_TOOL_COUNT` changed from lambdas to eagerly-evaluated `int` constants; `SAFE_TOOLS` from function ref to `frozenset`
  - `auth.py`: Added missing `from .exceptions import InfomaniakAuthError` import
  - Stale `logging_monitoring.logger_config` → `logging_monitoring.core.logger_config` paths in `test_improvements.py` and `demo_defense.py`
  - `audit_documentation.py`: `documentation.audit` → `documentation.quality.audit` module path
  - `security/secrets/__init__.py`: `generate_secret()` stdlib `secrets` namespace collision resolved via `sys.modules` pop/restore (4 xfail tests now pass)
  - `infomaniak/security.py`: Updated deprecated `codomyrmex.defense` → `codomyrmex.security.ai_safety` import
  - `test_github_functionality_demo.py`: Fixed `return True` → `return` (PytestReturnNotNoneWarning)
- Added `filterwarnings` for `google.generativeai` FutureWarning and PytestCollectionWarning

### Metrics

- MCP tool files: 27 → **31**
- Tests passing: 9,628 → **9,675** (+47)
- Tests failing: 44 → **1** (flaky `test_save_plot_pdf_format` — passes in isolation)
- Warnings: 189 → **187**
- xfail tests: 4 → **0** (secrets namespace collision fixed)

---

## [1.0.0] - 2026-02-21 — "General Availability"

### Added

- **APIContract** (`api/api_contract.py`): Frozen API contracts with SHA-256 checksums and backward-compatibility validation
- **ContractValidator** (`api/api_contract.py`): Detects breaking changes (removals, signature changes, return type changes)
- **MigrationEngine** (`api/migration_engine.py`): Records renames, removals, deprecations; generates migration plans with markdown
- **APISurface** (`api/api_surface.py`): Analyzes public API endpoints, modules, coverage, and frozen percentage
- **BenchmarkRunner** (`performance/benchmark_runner.py`): Timed benchmarks with threshold validation and ops/sec
- **LoadTester** (`performance/load_tester.py`): Concurrent load simulation with latency percentiles and error rates
- **MemoryProfiler** (`performance/memory_profiler.py`): GC-based memory snapshots with configurable leak detection
- **ReleaseValidator** (`release/release_validator.py`): Multi-faceted certification (tests, coverage, security, docs)
- **PackageBuilder** (`release/package_builder.py`): Builds sdist/wheel with SHA-256 checksums
- **DistributionManager** (`release/distribution.py`): Pre-flight checks and publishing to PyPI/TestPyPI/GitHub
- **38 new tests** across 3 test files — all passing

### Metrics

- New tests: 38 (14 + 12 + 12)
- Test failures: 0

---

## [Unreleased] — v0.9.0 "Production Hardening"

### Added

- **APIVersion** (`model_context_protocol/versioning.py`): Semantic versioning with `@versioned` and `@deprecated` decorators
- **VersionRegistry** (`model_context_protocol/version_registry.py`): Tool version registry with migration guides
- **CompatShimGenerator** (`model_context_protocol/compat.py`): Backward-compatibility shim generation with param renaming
- **ObservabilityPipeline** (`telemetry/pipeline.py`): Unified correlation of spans, metrics, logs, and audit events
- **MetricAggregator** (`telemetry/metric_aggregator.py`): Counters, gauges, and histograms with percentile stats
- **AlertEvaluator** (`telemetry/alert_evaluator.py`): Rule-based alerting with severity levels and auto-resolution
- **DashboardBuilder** (`data_visualization/dashboard_builder.py`): Grafana-compatible dashboard construction
- **PermissionModel** (`security/permissions.py`): RBAC with admin/operator/viewer hierarchy
- **ComplianceGenerator** (`security/compliance_report.py`): OWASP Top 10 compliance reporting
- **SecretScanner** (`security/secret_scanner.py`): Regex + entropy-based secret detection
- **SecurityDashboard** (`security/dashboard.py`): Aggregate security posture with risk scoring
- **APIDocExtractor** (`docs_gen/api_doc_extractor.py`): AST-based Python docstring extraction
- **SearchIndex** (`docs_gen/search_index.py`): Inverted index with title-boosted relevance
- **SiteGenerator** (`docs_gen/site_generator.py`): Documentation site orchestrator with mkdocs config
- **55 new tests** across 4 test files — all passing

### Metrics

- New tests: 55 (14 + 14 + 13 + 14)
- Test failures: 0

---

## [Unreleased] — v0.8.0 "Distributed Intelligence"

### Added

- **AgentSerializer/Deserializer** (`agents/transport/`): JSON-based agent state serialization with HMAC-SHA256 integrity verification
- **TransportMessage** (`agents/transport/protocol.py`): Wire format with header, payload, and HMAC signing/verification
- **Checkpoint** (`agents/transport/checkpoint.py`): Durable JSON save/load with StateDelta diff computation
- **TaskQueue** (`concurrency/task_queue.py`): Priority heap with deduplication, deadline expiry, dead-letter queue, at-least-once delivery
- **TaskWorker** (`concurrency/task_worker.py`): Error-isolated task processing with timeout and lifecycle management
- **TaskScheduler** (`concurrency/task_scheduler.py`): Round-robin, least-loaded, and affinity-based task routing with capability filtering
- **ResultAggregator** (`concurrency/result_aggregator.py`): Per-worker statistics and aggregate result collection
- **EventStore** (`events/event_store.py`): Append-only event stream with sequence numbers, topic indexing, range/time queries, compaction
- **EventReplayer** (`events/replayer.py`): Deterministic replay with handler output capture and diff-based verification
- **StreamProjection** (`events/projections.py`): Counter, latest-per-key, generic fold, group-by, and running aggregate
- **HeartbeatMonitor** (`orchestrator/heartbeat.py`): Agent liveness detection with healthy/suspect/dead status
- **AgentSupervisor** (`orchestrator/agent_supervisor.py`): OTP-style supervision (one-for-one/one-for-all/rest-for-one) with escalation
- **ProcessOrchestrator** (`orchestrator/process_orchestrator.py`): Agent lifecycle management with spawn, shutdown, and crash recovery
- **53 new tests** across 4 test files — all passing

### Metrics

- New tests: 53 (14 + 14 + 13 + 12)
- Test failures: 0

---

## [Unreleased] — v0.7.0 "Advanced Agent Capabilities"

### Added

- **FeedbackLoop** (`agents/planner/feedback_loop.py`): Convergent planning-execution cycle wiring PlanEngine → WorkflowRunner → MemoryStore with quality-floor re-planning
- **PlanEvaluator** (`agents/planner/plan_evaluator.py`): Weighted composite scoring (success×0.4 + time×0.3 + retry×0.2 + memory×0.1) with convergence detection
- **FeedbackConfig** (`agents/planner/feedback_config.py`): Dataclass for iteration limits, quality floor, scoring weights, memory TTL
- **SharedMemoryPool** (`collaboration/knowledge/shared_pool.py`): Namespace-isolated multi-agent knowledge store with ACL, cross-namespace search, conflict resolution
- **KnowledgeRouter** (`collaboration/knowledge/knowledge_router.py`): Expertise-based query routing with tag overlap + domain match + recency weighting
- **Knowledge Models** (`collaboration/knowledge/models.py`): KnowledgeEntry, ExpertiseProfile, NamespaceACL, QueryResult
- **WorkflowJournal** (`orchestrator/workflow_journal.py`): Lifecycle event recorder (start/step/complete) with optional MemoryStore persistence
- **WorkflowAnalytics** (`orchestrator/workflow_analytics.py`): Failure hotspots, duration trends, per-step success rates, insight generation
- **ImprovementPipeline** (`agents/specialized/improvement_pipeline.py`): Full detect → fix → test → review cycle with safety limits
- **AntiPatternDetector**: Regex-based detection of bare_except, mutable defaults, star imports, print debug, TODO/FIXME
- **ImprovementReport** (`agents/specialized/improvement_report.py`): Markdown-renderable report with ProposedChange, TestSuiteResult, ReviewVerdict
- **ImprovementConfig** (`agents/specialized/improvement_config.py`): Safety limits (max_changes, min_confidence, scope_constraints)
- **53 new tests** across 4 test files — all passing

### Metrics

- Total tests collected: 9,567
- New tests: 53 (15 + 13 + 11 + 14)
- Collection errors: 9 (pre-existing — `agentic_memory` module not yet implemented)

---

## [Unreleased] — v0.6.1 "Stability & Polish"

### Added

- **Thinking MCP Tools**: 4 new `@mcp_tool` functions in `agents/core/mcp_tools.py` — `think`, `get_thinking_depth`, `set_thinking_depth`, `get_last_trace`
- **Knowledge Wiring**: `ThinkingAgent` now optionally accepts a `GraphRetriever` and auto-retrieves relevant knowledge context before Chain-of-Thought reasoning
- **Relation Strength Scoring** (`relations/strength_scoring.py`): `RelationStrengthScorer` with exponential/linear/step temporal decay and interaction-type weighting
- **Performance Regression Detector** (`performance/regression_detector.py`): `RegressionDetector` with configurable warning/critical thresholds
- **Benchmark Comparison** (`performance/benchmark_comparison.py`): `compute_delta`, `mean`, `stddev`, `coefficient_of_variation` utilities
- **Web Crawler** (`scrape/crawler.py`): `Crawler` with frontier management, rate limiting, domain scoping, robots.txt, and content dedup
- **Content Extractor** (`scrape/content_extractor.py`): `ContentExtractor` — regex-based HTML parsing for titles, headings, links, images, meta tags
- **Plugin Discovery** (`plugin_system/discovery.py`): `PluginDiscovery` — entry point and directory scanning with lifecycle state tracking
- **Dependency Resolver** (`plugin_system/dependency_resolver.py`): `DependencyResolver` — topological sort with cycle detection and missing dependency reporting
- **Maintenance Scheduler** (`maintenance/scheduler.py`): `MaintenanceScheduler` with task registration, due-task detection, and retry logic
- **Health Check Framework** (`maintenance/health_check.py`): `HealthChecker` with registry, batch execution, and aggregate reporting
- **Structured Log Formatter** (`logging_monitoring/structured_formatter.py`): `StructuredFormatter` — JSON-lines output with correlation ID, configurable fields, stacktrace capture
- **Log Aggregator** (`logging_monitoring/log_aggregator.py`): `LogAggregator` — in-memory search, filtering, and analytics (rate, error ratio, top modules)
- **6 new `mcp_tools.py` files**: `performance`, `maintenance`, `relations`, `logging_monitoring`, `plugin_system`, `scrape` (21 → 27 modules with MCP exposure)
- **37 new tests**: `test_tier3_promotions.py` (19 tests), `test_tier3_promotions_pass2.py` (18 tests)

### Changed

- Synchronized `__version__` in `__init__.py` from `0.1.9` → `0.6.0`
- Synced `pyproject.toml` version from stale `0.2.1` → `0.6.0`

### Fixed

- **249 collection errors → 0**: Added `pythonpath = src` to `pytest.ini` — tests now resolve `import codomyrmex` without requiring `pip install -e .`

### Metrics

- Modules with `mcp_tools.py`: 21 → **27**
- `@mcp_tool` decorators: 150 → **162**
- Tests collected: 9,400 → **9,661**
- Collection errors: 249 → **0**
- Tier-3 modules: 43 → **37** (6 promoted to Tier-2)

## [0.6.0] - 2026-02-20

### Added

- **Workflow Engine**: `orchestrator/workflow_engine.py` — `WorkflowStep`, `WorkflowRunner` with DAG-based topological execution (Kahn's algorithm)
- **Workflow Templates**: `orchestrator/workflow_templates.py` — pre-built CI/CD, code review, and data pipeline templates
- **Agent Memory Store**: `agents/memory/store.py` — `MemoryStore` with TTL-based expiry, tag search, and access counting
- **Conversation History**: `agents/memory/conversation.py` — `ConversationHistory` with summary generation
- **Learning Journal**: `agents/memory/journal.py` — `LearningJournal` with pattern detection
- **Integration Bus**: `events/integration_bus.py` — cross-module event routing with topic subscriptions and wildcard support
- **Module Connector**: `orchestrator/module_connector.py` — dependency injection container with singleton caching
- **Plan Engine**: `agents/planner/plan_engine.py` — hierarchical goal decomposition with keyword-driven task generation
- **Plan Executor**: `agents/planner/executor.py` — plan execution with progress tracking
- 45 new tests across workflow, memory, integration, and planning modules

## [0.2.0-rc1] - 2026-02-19

### Added

- **MCP Tool Expansion**: 15 full modules now expose over 150 MCP tools across the framework (e.g. `agents`, `security`, `documentation`, `data_visualization`, `cerebrum`, `cloud`, `llm`, `orchestrator`).
- **End-to-End Tracing**: Wired Correlation ID into EventBus and MCP transports (`X-Correlation-ID`) for distributed request tracing.
- **RASP Documentation Auto-Generation**: Backfilled `AGENTS.md`, `SPEC.md`, `PAI.md` and `README.md` specs across 15 newly promoted sub-modules.
- **Infinite Conversation Mode Support**: Real-LLM integrations tested successfully for infinite dialogue contexts.

### Fixed

- **100% Zero-Mock Compliance**: Remediated 74 remaining test suite failures spanning PAI Trust Gateway mocks, CORS origin strictness, validation module schema drift, missing Cloud credential bindings, and I18N instantiation leaks. The test suite of >8,800 tests now runs completely clean without ANY mocked system boundaries.

## [0.1.9] - 2026-02-19

### Added

- **Stream 3**: 11 workflow integration test files (`tests/integration/workflows/`) — ~54 tests covering all 7 Claude Code workflows (analyze, docs, status, trust, verify, search, memory, roundtrip, concurrent, CLI doctor)
- **Stream 4**: `cli/doctor.py` — 5 diagnostic checks (module imports, PAI bridge, MCP registry, RASP completeness, workflow validation), `--json` output, exit codes 0/1/2
- **Stream 5**: `concurrency/pool.py` (AsyncWorkerPool with semaphore bounds), `concurrency/dead_letter.py` (JSONL-backed DeadLetterQueue with replay)
- **Stream 6**: Honeytoken subsystem in `defense/active.py` — create/check/list canary tokens, thread-safe trigger tracking, 6 unit tests
- **Stream 7**: `agents/orchestrator.py` — ConversationOrchestrator for infinite multi-agent conversations over AgentRelay, using real Ollama LLM inference (zero mocks), 7 real-LLM integration tests

### Fixed

- `InMemoryStore.list_all()` and `JSONFileStore.list_all()` now acquire lock during iteration (concurrent modification bug)

### Changed

- `concurrency/__init__.py` exports: added AsyncWorkerPool, PoolStats, TaskResult, DeadLetterQueue
- `defense/active.py`: get_threat_report() now includes honeytoken metrics
- Bumped version to 0.1.9

## [0.1.8] - 2026-02-19

### Added

- **Stream 1**: MCP schema validation (`validation.py`) and error envelope (`errors.py` — MCPToolError, MCPErrorCode enum)
- **Stream 2**: MCP transport robustness — `circuit_breaker.py`, `rate_limiter.py`, client retry + health checks + connection pooling
- **Stream 3**: MCP discovery hardening — `MCPDiscoveryEngine` with error isolation, incremental scanning, TTL cache
- **Stream 4**: MCP stress/concurrency tests — 36 tests for concurrent execution, memory stability, malformed input handling
- **Stream 5**: Async-first orchestrator — `AsyncParallelRunner`, `AsyncScheduler`, `@with_retry` decorator
- **Stream 6**: Observability pipeline — `WebSocketLogHandler`, `EventLoggingBridge`, `MCPObservabilityHooks`
- **Stream 7**: Performance baselines — `pytest-benchmark` tests, import time analysis, lazy loading verification

## [0.1.7] - 2026-02-18

### Changed

- Corrected module count from various stale values (78, 80, 82+, 83) to verified 82 across all root documentation
- Updated `__init__.py` version from 0.1.6 to 0.1.7
- Synchronized version across `README.md`, `AGENTS.md`, `PAI.md`, `SPEC.md`, `CLAUDE.md`, `TO-DO.md`
- Added 21 previously unlisted modules to `AGENTS.md` Module Discovery section
- Removed duplicate Surface table accidentally inserted in `PAI.md`
- Updated `AGENTS.md` version history with v0.1.6 and v0.1.7 entries
- Refactored `scripts/` to thin orchestrator pattern delegating to `maintenance` library
- Added configuration/CLI args to audit and update scripts

### Fixed

- `SPEC.md` version was stale at v0.1.1 (now v0.1.7)
- `CHANGELOG.md` line 83 referenced "78 modules" (historical, preserved as-is)
- `AGENTS.md` version history was missing v0.1.2–v0.1.6 entries

## [0.1.6] - 2026-02-17

### Added

- `AgentProtocol` with `plan()`, `act()`, `observe()` methods in `agents/core/base.py`
- `AgentMessage` dataclass with typed role, tool calls, serialization in `agents/core/messages.py`
- `ToolRegistry.from_mcp()` bridge for MCP→agent tool bridging in `agents/core/registry.py`
- `VectorStoreMemory.from_chromadb()` optional factory in `agentic_memory/memory.py`
- `AgentMemory.add()` alias for MCP tool compatibility
- `UserProfile` dataclass with JSON persistence in `agentic_memory/user_profile.py`
- `EventBus.emit_typed()` and `subscribe_typed()` convenience methods in `events/core/event_bus.py`
- `orchestrator_events.py` with 7 typed event factory functions (workflow/task lifecycle)
- `Workflow.run()` now emits lifecycle events via optional `event_bus` parameter
- `JSONFileStore.list_all()` method with thread-safe file writes
- `BasePlot` enhanced with `__str__`, `__repr__`, `save()`, `to_dict()` methods
- `BarChart` and `LinePlot` upgraded from stubs to real matplotlib renderers
- Full submodule exports: plots (19 classes), components (14 classes), reports (5 classes)
- `test_agent_protocol.py`: 20 tests for AgentMessage, plan/act/observe, ToolRegistry.from_mcp
- `test_memory_integration.py`: 12 tests for stores, AgentMemory, VectorStoreMemory, UserProfile
- `test_event_orchestrator.py`: 17 tests for emit_typed, subscribe_typed, Workflow events
- `test_enhanced_methods.py`: 22 tests for visualization enhancements

### Changed

- `ReActAgent._execute_impl` refactored into discrete `plan→act→observe` calls
- `ReActAgent.llm_client` type-hinted as `BaseLLMClient | Any` (TYPE_CHECKING import)
- `RadarChart` now inherits from `BasePlot` (was standalone dataclass)
- All 19 plot subclasses call `super().__init__()` for proper `BasePlot` method inheritance
- Main `data_visualization/__init__.py` cleaned: removed dead `BarPlot`, expanded `__all__` to 30+ items
- Bumped version to 0.1.6

### Added

- `scripts/audit_exports.py` — validates every module has `__all__` (supports annotated assignments)
- `scripts/audit_imports.py` — AST-based cross-module import audit with architecture layer rules
- `__all__` to `module_template/__init__.py` and `tests/__init__.py`

### Changed

- 79/79 modules now have `__all__` defined (was 77/79)
- 0 cross-layer violations across 291 import edges
- Bumped version to 0.1.5

## [0.1.4] - 2026-02-17

### Added

- `EphemeralServer` utility for local HTTP testing (`tests/utils/ephemeral_server.py`)
- `pytest-benchmark` baselines for import time and AST parsing
- Benchmarks test suite (`tests/benchmarks/test_benchmarks.py`)

### Changed

- Networking tests now use local `EphemeralServer` instead of external `httpbin.org`
- Bumped version to 0.1.4 in `pyproject.toml` and `__init__.py`
- Updated roadmap: v0.1.5–7 focus on modularity/testing/orchestration, v0.1.8–9 cognitive, v0.2.0 stable swarm

## [0.1.2] - 2026-02-17

### Added

- MCP HTTP transport with FastAPI server and 33 registered tools
- Web UI for interactive MCP tool testing (`http://localhost:8080/`)
- Health, tools, resources, and prompts HTTP endpoints
- 30 unit tests for MCP HTTP server
- Website live dashboard with auto-refresh and MCP integration card
- `scripts/update_pai_docs.py` — batch PAI.md updater for all modules
- `scripts/update_root_docs.py`, `scripts/update_spec_md.py` — root doc automation
- `scripts/finalize_root_docs.py` — documentation finalization tooling
- Comprehensive GitHub workflow suite for CI/CD
- Documentation validation and remediation scripts
- Pre-commit hook configuration
- Security scanning workflows
- RASP documentation pattern (README, AGENTS, SPEC, PAI) defined across all 78 modules
- PAI integration documentation suite (`docs/pai/`)
- Skills documentation suite (`docs/skills/`)
- UOR (Universal Object Reference) module with PrismEngine, EntityManager, UORGraph
- Model evaluation metrics module (`model_ops/evaluation/metrics.py`)
- Data visualization modules: bar charts, line plots, components, reports
- Claude integration tests (`test_claude_integration.py`)
- UOR comprehensive test suite (`test_uor.py`)
- Backward-compatibility shims for cerebrum visualization and agents education

### Changed

- Migrated dependency management to UV
- Standardized test paths to `src/codomyrmex/tests/`
- Unified tests: migrated root `/tests/` to `src/codomyrmex/tests/unit/`
- PAI.md files for all 78 modules now include accurate exports from `__init__.py`, algorithm phase mapping, and navigation
- Root PAI.md rewritten as actual PAI system bridge documentation (v0.2.0)
- Agent system documentation expanded with provider comparison and three-tier agent architecture
- Standardized module count to 78 across all root documentation
- Test coverage target standardized to ≥80% across all documentation
- PAI bridge, trust gateway, and MCP bridge improved
- Rate limiter enhanced with `consume()` method and `initial_tokens` parameter
- Skills, security governance, and telemetry module exports refined

### Fixed

- Resolved all ruff linting errors across test files and analyzer modules
- Workflow test paths now correctly reference `src/codomyrmex/tests/unit/`
- Workflow-status filename mapping now correctly maps workflow names to filenames
- Module count inconsistencies resolved (was 94/95/105/106 in different docs, now consistently 104)
- Fixed `test_curriculum` calling convention (keyword-only args)
- Fixed `test_documentation_accuracy` to use actual API signatures for `create_line_plot`, `pyrefly_runner`, MCP schemas, visualization charts, and build orchestrator
- Fixed `test_analysis_security_cicd` to handle dataclass return types from `analyze_file` and `scan_vulnerabilities`
- Fixed `test_real_github_repos` helper function incorrectly collected as pytest test
- Version string in `src/__init__.py` updated from stale `0.1.0` to `0.1.2`
- Removed stale `deep_audit.py` and `polish_exports.py`

## [0.1.0] - 2026-02-05

### Added

- Initial project structure
- Core module framework
- Basic documentation with README.md and AGENTS.md patterns
- GitHub workflow templates
