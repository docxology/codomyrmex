# Codomyrmex Project Roadmap & To-Do

**Status**: Active | **Last Updated**: February 18, 2026 | **Current**: v0.1.7 | **Target**: v0.4.0

v0.1.8–0.1.9 harden foundations (MCP robustness, async orchestration, observability, PAI workflows, CLI diagnostics).
v0.2.0 certifies production-grade agent infrastructure.
v0.3.0 layers cognitive architecture. v0.4.0 delivers swarm orchestration.

---

## ✅ Completed Releases (v0.1.3 – v0.1.7)

| Version | Theme | Highlights |
|---------|-------|------------|
| **v0.1.3** | Foundation Hardening | RASP standardization, `uv` migration, 84 pass / 2 skip |
| **v0.1.4** | Zero-Mock Certification | `EphemeralServer` replaces httpbin, real LLM tests, `pytest-benchmark` |
| **v0.1.5** | Module Refactoring | 79/79 `__all__` exports, 0 cross-layer violations / 291 edges |
| **v0.1.6** | Agent & Memory Foundations | `AgentProtocol`, `AgentMessage`, `ToolRegistry.from_mcp()`, `VectorStoreMemory`, `EventBus.emit_typed()`, `OrchestratorEvents`, 71 new tests |
| **v0.1.7** | Documentation Audit & MCP Plumbing | Version sync to 0.1.7, module count →82, 62 dead scripts deleted, 6 `mcp_tools.py` registered, `MCPClient` (355 lines), 29 MCP tests, `ToolRegistry` thread-safe, 7 test failures→0, deprecated `get_event_loop` fixed |

<details>
<summary><strong>v0.1.7 — Detailed Record</strong></summary>

**Test Baseline**: 8205 passed, 245 skipped, 7 xfailed, 0 failures (497s).

**MCP Sprint**: 6 `mcp_tools.py` files (git_operations, containerization, coding, search, formal_verification, logistics). Auto-discovery in `discovery.py`. `MCPClient` with stdio + HTTP transports. 535 total tools. Full zero-mock test suite: `test_mcp_smoke.py` (13), `test_mcp_client.py` (9), `test_mcp_discovery.py` (7), `test_mcp_server.py` (30), `test_mcp_tools.py` (23), `test_mcp_bridge.py` (40), `test_mcp_http_and_errors.py` (15). Total: 137 MCP tests.

**Thread Safety**: `ToolRegistry._lock` added at `registry.py:40` with acquire/release in `register()`, `get_tool()`, `list_tools()`, `get_schemas()`, `execute()`.

**Script Refactoring**: 7 audit/update scripts refactored to thin orchestrators → `maintenance` library. 62 dead documentation scripts deleted.

**Doc Sync**: Version 0.1.7 synchronized across 12 files. Module count corrected (78/80/82+/83 → 82) in 15+ files. 21 missing modules added to AGENTS.md.
</details>

---

## 🔧 v0.1.8 — MCP Robustness & Async Orchestration

**Theme**: "Defend the Protocol, Wire the Backbone" | **Scope**: 6 work streams, ~30 deliverables

> **Codebase Baseline (Feb 2026)**:
>
> **MCP Infrastructure** (2,068 lines across 4 core files):
>
> - `MCPServer` (526 lines): 15 handlers, JSON-RPC dispatch, stdio + HTTP (FastAPI). `_call_tool()` returns success/error but **no input schema pre-validation** — `_tool_registry.execute()` is called directly on unvalidated args. **No per-tool timeout** — entire transport shares a 30s ceiling. **No rate limiting**. Error handling: bare `isError: true` with untyped string message (no error category, no tool context, no suggestion).
> - `MCPClient` (354 lines): 3 transports (`_StdioTransport`, `_HTTPTransport`, `_InMemoryTransport`). Timeout: configurable per-config but uniform across all calls. **No health check** — can't verify server liveness before sending requests. **No retry** on transient failures (network blips, 502s). HTTP transport: **no connection pooling** (creates new `aiohttp.ClientSession` per client instance, but never reuses across invocations). **No circuit breaker**.
> - `mcp_bridge.py` (1,042 lines): 18 static tools + auto-discovery. `_discover_dynamic_tools()` has cache with `threading.Lock` but **no TTL** — stale indefinitely. `call_tool()` does **no schema validation** before dispatch. `create_codomyrmex_mcp_server()` copies tools from registry to server one-by-one (no batch registration). **No tool versioning**. **No deprecation mechanism**.
> - `discovery.py` (146 lines): `MCPDiscovery` class with `scan_package()` + `_scan_module()`. Auto-discovers `@mcp_tool` decorated functions. `discover_all_public_tools()` imports every module — **heavy** (~2s first run). **No incremental scanning**. **No error isolation** — one broken module import kills entire discovery.
>
> **MCP Tests** (137 tests across 8 files):
>
> - `test_mcp_smoke.py` (13): import checks, safe tool execution, metadata validation.
> - `test_mcp_client.py` (9): `MCPClient` ↔ `MCPServer` loopback via `_InMemoryTransport`.
> - `test_mcp_discovery.py` (7): importability, tool counts, duplicate detection.
> - `test_mcp_http_and_errors.py` (15): HTTP tests via aiohttp TestServer, errors, timeouts.
> - `test_mcp_server.py` (30): server lifecycle, tool/resource/prompt registration.
> - `test_mcp_tools.py` (23): tool execution, schema validation assertions.
> - `test_mcp_bridge.py` (40): bridge tools, discovery, registry construction.
> - **Gaps**: No stress tests. No concurrent tool invocation tests. No schema validation fuzz. No transport failover testing. No tool timeout isolation tests. No tool deprecation workflow tests.
>
> **Orchestration** (26 files in `orchestrator/`):
>
> - `ParallelRunner` (328 lines): thread-pool based (`ThreadPoolExecutor`). `run_scripts_async` wraps sync via `asyncio.to_thread()`. No native async.
> - `Workflow.run()` (645 lines): async topological sort, `RetryPolicy`, semaphore, EventBus, conditional execution. Uses `asyncio.gather()` per level, not `TaskGroup`.
> - `scheduler/` (4 files): `Scheduler` with heapq, cron/interval/once triggers, thread-pool executor. Thread-safe.
> - `retry_policy.py` (163 lines): `RetryPolicy`, `PipelineRetryExecutor` (sync + async), exponential backoff, jitter, dead-letter routing.
>
> **Logging** (13 files in `logging_monitoring/`):
>
> - `json_formatter.py`, `logger_config.py`, `rotation.py`, `audit_logger.py`, `performance.py`. No WebSocket handler. No `enable_structured_json()`. No EventBus→logging bridge.

### Stream 1: MCP Schema Validation & Error Envelope

**Goal**: Every MCP tool invocation validates inputs before dispatch, returns structured errors, and logs context for debugging.

| Deliverable | File | Description |
|-------------|------|-------------|
| **Schema validation middleware** | `model_context_protocol/validation.py` (NEW, ~120 lines) | `validate_tool_arguments(tool_name: str, arguments: dict, schema: dict) → ValidationResult`. Uses `jsonschema.validate()` (dep: `jsonschema>=4.23.0` confirmed in `pyproject.toml:51`). Returns `ValidationResult(valid=bool, errors=list[str], coerced_args=dict)`. Supports type coercion for common cases (str→int, str→bool). |
| **Server-side pre-validation** | `model_context_protocol/server.py` `_call_tool()` at line 286 | Before `self._tool_registry.execute(tool_call)`: retrieve tool schema via `_tool_registry.get(tool_name)`, call `validate_tool_arguments()`. On failure: return `MCPToolError(code="VALIDATION_ERROR", message=str, field_errors=[{field, constraint, value}])`. Never reach the handler. |
| **Structured error envelope** | `model_context_protocol/errors.py` (NEW, ~80 lines) | `MCPToolError` dataclass: `code: str` (VALIDATION_ERROR, EXECUTION_ERROR, TIMEOUT, NOT_FOUND, RATE_LIMITED, INTERNAL), `message: str`, `tool_name: str`, `field_errors: list[dict]`, `suggestion: str | None`,`correlation_id: str`. Serializes to MCP`isError: true` with structured JSON in content text. |
| **Client-side error parsing** | `model_context_protocol/client.py` `_send()` at line 100 | Parse `isError: true` responses into typed `MCPToolError` objects. Expose `MCPToolCallResult.error: MCPToolError | None` for programmatic inspection. Preserve backward compat: `MCPClientError` still raised for RPC-level errors; tool-level errors are surfaced in result. |
| **Bridge error wrapping** | `agents/pai/mcp_bridge.py` `call_tool()` at line 820 | Wrap every tool handler in `try/except (ImportError, TimeoutError, jsonschema.ValidationError, Exception)`. Build `MCPToolError` with `tool_name`, `error_type` (from exception class), `module` (from tool name prefix), and `suggestion` (e.g., "Module 'X' is not installed. Run: uv sync --extra X"). Log via `logging.getLogger('codomyrmex.mcp')`. |

**Test Plan** (all zero-mock, in `tests/unit/mcp/`):

| Test | File | What it validates |
|------|------|-------------------|
| `test_mcp_validation.py` | NEW, ~15 tests | Valid args pass, invalid type rejected, missing required field rejected, extra field ignored (additionalProperties), coercion str→int, deeply nested schema, array items schema, enum validation, pattern validation, min/max constraints |
| `test_mcp_error_envelope.py` | NEW, ~10 tests | `MCPToolError` serialization/deserialization round-trip, all 6 error codes, field_errors present on validation failure, correlation_id uniqueness, backward compat with old `isError` clients |
| `test_mcp_bridge_errors.py` | NEW, ~8 tests | ImportError→`EXECUTION_ERROR` with suggestion, TimeoutError→`TIMEOUT`, generic Exception→`INTERNAL`, ValidationError→`VALIDATION_ERROR` with field details, missing tool→`NOT_FOUND`, all errors include tool_name and module |

### Stream 2: MCP Transport Robustness

**Goal**: MCP client handles transient failures, detects unhealthy servers, and provides per-tool timeout control.

| Deliverable | File | Description |
|-------------|------|-------------|
| **Health check** | `model_context_protocol/client.py` | `async def health_check(self) → HealthStatus`. Sends `initialize` if not yet initialized, else `tools/list`. Returns `HealthStatus(healthy=bool, latency_ms=float, server_info=dict, tools_count=int, error=str|None)`. Timeout: 5s (not configurable, fast-fail). |
| **Transport retry** | `model_context_protocol/client.py` `_HTTPTransport.send()` | On `aiohttp.ClientResponseError` (5xx) or `asyncio.TimeoutError`: retry up to 3 times with exponential backoff (0.5s, 1s, 2s). On `aiohttp.ClientConnectionError`: retry once, then raise `MCPClientError("Server unreachable")`. Log each retry via `codomyrmex.mcp.transport` logger. |
| **Connection pooling** | `model_context_protocol/client.py` `_HTTPTransport` | Share `aiohttp.ClientSession` across multiple `send()` calls (already done per instance). Add `TCPConnector(limit=20, ttl_dns_cache=300)` to control connection pool size and DNS cache. Add `keepalive_timeout=30`. |
| **Per-tool timeout** | `model_context_protocol/server.py` `_call_tool()` | Tool schema may include `"x-timeout": <seconds>` field. If present, wrap `_tool_registry.execute()` in `asyncio.wait_for(coro, timeout=tool_timeout)`. Default: `MCPServerConfig.default_tool_timeout` (30s). On timeout: return `MCPToolError(code="TIMEOUT", tool_name=..., message=f"Tool {name} timed out after {t}s")`. |
| **Circuit breaker** | `model_context_protocol/circuit_breaker.py` (NEW, ~100 lines) | `CircuitBreaker(failure_threshold=5, reset_timeout=60, half_open_max=2)`. States: CLOSED→OPEN→HALF_OPEN→CLOSED. Tracks failures per tool name. When OPEN: immediately return `MCPToolError(code="CIRCUIT_OPEN")` without calling handler. Integrates with server `_call_tool()`. Thread-safe with `threading.Lock`. |
| **Rate limiter** | `model_context_protocol/server.py` | Wire existing `concurrency/rate_limiter.py` `RateLimiter` into `_call_tool()`. Config: `MCPServerConfig.rate_limit_per_second: int = 0` (0=disabled). When rate-limited: return `MCPToolError(code="RATE_LIMITED", message="...", suggestion="Retry after {delay}s")`. Per-tool overrides via `"x-rate-limit"` in tool schema. |

**Test Plan**:

| Test | File | What it validates |
|------|------|-------------------|
| `test_mcp_health_check.py` | NEW, ~6 tests | Healthy server returns latency + tool count, unhealthy server returns error, timeout on unresponsive server, health check before/after initialization |
| `test_mcp_transport_retry.py` | NEW, ~8 tests | 503 retried and succeeds on 2nd attempt, 500 retried 3 times then fails, connection error retried once, non-retriable 400 not retried, retry delays follow exponential backoff (verify with time assertion ±100ms) |
| `test_mcp_timeout_isolation.py` | NEW, ~6 tests | Slow tool (3s sleep) times out at 2s, fast tool succeeds at same 2s limit, default timeout applies when no `x-timeout`, `x-timeout` overrides default, timeout error includes tool name |
| `test_mcp_circuit_breaker.py` | NEW, ~8 tests | 5 failures opens circuit, 6th call returns immediately without handler, circuit resets after timeout, half-open allows 2 probes, success in half-open closes circuit, failure in half-open re-opens, per-tool isolation (tool A open doesn't affect tool B) |
| `test_mcp_rate_limiter.py` | NEW, ~5 tests | Under limit succeeds, over limit returns RATE_LIMITED, per-tool override, disabled by default, rate limit resets after window |

### Stream 3: MCP Discovery Hardening

**Goal**: Tool discovery is fast, resilient to module failures, and supports incremental refresh.

| Deliverable | File | Description |
|-------------|------|-------------|
| **Error-isolated scanning** | `model_context_protocol/discovery.py` `scan_package()` | Wrap each module import in `try/except (ImportError, SyntaxError, Exception)`. Log failure via `codomyrmex.mcp.discovery` logger. Continue scanning remaining modules. Return `DiscoveryReport(tools=list, failed_modules=list[{module, error}], scan_duration_ms=float)`. |
| **Cache with TTL** | `agents/pai/mcp_bridge.py` `_discover_dynamic_tools()` | Add `_CACHE_EXPIRY: float | None = None` alongside `_DYNAMIC_TOOLS_CACHE`. Default TTL: 300s (5 min). On cache hit: check`time.monotonic() <_CACHE_EXPIRY`. On miss/expired: rescan and update both`_DYNAMIC_TOOLS_CACHE` and `_CACHE_EXPIRY`. Configurable via`CODOMYRMEX_MCP_CACHE_TTL` env var. |
| **Warm-up at server start** | `agents/pai/mcp_bridge.py` `create_codomyrmex_mcp_server()` | Before returning server: call `_discover_dynamic_tools()` eagerly. Log warm-up duration. Add `MCPServerConfig.warm_up: bool = True`. When `False`: lazy discovery on first tool call. |
| **Incremental scan** | `model_context_protocol/discovery.py` | `MCPDiscovery.scan_module(module_name: str) → list[DiscoveredTool]`. Scans single module, merges results into existing registry. Used by `_tool_invalidate_cache()` to refresh one module without full rescan. |
| **Discovery metrics** | `model_context_protocol/discovery.py` | `MCPDiscovery.get_metrics() → DiscoveryMetrics` dataclass: `total_tools: int`, `scan_duration_ms: float`, `failed_modules: list[str]`, `modules_scanned: int`, `cache_hits: int`, `last_scan_time: datetime`. Exposed as MCP resource `codomyrmex://discovery/metrics`. |

**Test Plan**:

| Test | File | What it validates |
|------|------|-------------------|
| `test_mcp_discovery_resilience.py` | NEW, ~8 tests | Broken module import doesn't kill discovery, `DiscoveryReport.failed_modules` populated, all other modules still registered, SyntaxError handled, recursive import loop handled |
| `test_mcp_cache_ttl.py` | NEW, ~6 tests | Cache hit within TTL, cache miss after TTL expiry, env var override, `invalidate_tool_cache()` forces immediate rescan, warm-up populates cache before first call |
| `test_mcp_incremental_scan.py` | NEW, ~4 tests | Single module scan adds new tools without clearing others, rescanned module updates tool definitions, scan non-existent module returns empty list + error |

### Stream 4: MCP Stress & Concurrency Tests

**Goal**: Prove the MCP infrastructure handles concurrent load without deadlocks, data corruption, or performance degradation.

| Test | File | What it validates |
|------|------|-------------------|
| `test_mcp_concurrent_tools.py` | NEW, ~8 tests | 50 concurrent `call_tool()` invocations via `asyncio.gather()` — all return correct results. 20 concurrent tool registrations — no duplicate entries, no dropped tools. 10 concurrent discovery scans — cache consistency maintained. Mixed read/write: concurrent `list_tools()` + `register_tool()` — no `RuntimeError` on dict mutation. |
| `test_mcp_stress.py` | NEW, ~5 tests | 1000 sequential tool calls — throughput ≥100 calls/s. Memory usage stable (no leak) after 10K calls (check via `tracemalloc`). Server handles malformed JSON-RPC gracefully (no crash). Client handles malformed server response gracefully. Large tool argument (1MB JSON) doesn't crash or timeout. |
| `test_mcp_transport_stress.py` | NEW, ~4 tests | HTTP transport: 50 concurrent requests to real `EphemeralServer`. Stdio transport: rapid message exchange (100 messages in 2s). Transport reconnect after server restart. Partial JSON response handling. |
| `test_mcp_tool_isolation.py` | NEW, ~5 tests | Tool A throws exception — Tool B still callable. Tool A modifies global state — Tool B sees clean state (verify via `threading.local()`). Tool A takes 5s — Tool B returns immediately (timeout isolation). Destructive tool blocked while safe tool proceeds. |

### Stream 5: Orchestrator v2 (async-first)

| Deliverable | File | Description |
|-------------|------|-------------|
| `AsyncParallelRunner` | `orchestrator/async_runner.py` (NEW) | Native `asyncio.TaskGroup` (3.11+) parallel execution. Inputs: list of async callables + optional dependency DAG. `asyncio.Semaphore` for concurrency limiting. `fail_fast` via `TaskGroup` exception propagation. Replaces thread-pool pattern in `parallel_runner.py` for async workloads. |
| `Workflow.run()` upgrade | `orchestrator/workflow.py:279–450` | Replace `asyncio.gather()` with `TaskGroup` for structured concurrency within topological levels. Preserve existing `RetryPolicy` integration and conditional task execution. Add `workflow_id` correlation for observability. |
| Unified retry | `orchestrator/retry_policy.py` | Wire `PipelineRetryExecutor` into `Workflow.run()` — currently `Workflow` has its own inline retry. Consolidate. Extract standalone `@with_retry` decorator from `PipelineRetryExecutor.execute_async()`. |
| `AsyncScheduler` | `orchestrator/scheduler/scheduler.py` | Add `priority: int` to `Job` model. New `AsyncScheduler` variant using `TaskGroup`. Wire scheduler lifecycle events into `EventBus`. |

**Tests**: `test_async_runner.py` (10 tasks, DAG, error propagation, semaphore), `test_scheduler_async.py` (5 jobs, priority, triggers).

### Stream 6: Observability Pipeline

| Deliverable | File | Description |
|-------------|------|-------------|
| WebSocket log handler | `logging_monitoring/ws_handler.py` (NEW) | `WebSocketLogHandler(logging.Handler)` for real-time structured log streaming. `asyncio.Queue` bridges sync→async. Filters: level, module, event type. |
| Structured JSON toggle | `logging_monitoring/logger_config.py` | `enable_structured_json(logger_name=None)`. `configure_all(level, json_mode, ws_endpoint)`. |
| Event→log bridge | `logging_monitoring/event_bridge.py` (NEW) | `EventLoggingBridge` subscribes to `EventBus.subscribe_typed()`, logs agent/workflow/MCP events as structured JSON with correlation IDs. |
| Scheduler events | `orchestrator/orchestrator_events.py` | Add `scheduler_job_started/completed/failed()` factories. |
| **MCP observability** | `model_context_protocol/server.py` | Add `_on_tool_call` hook: logs tool name, args hash, duration, result status, error code. Emits `EventBus` event `MCP_TOOL_CALLED`. Metrics: `mcp_tool_call_total`, `mcp_tool_call_duration_seconds`, `mcp_tool_call_errors_total` (Prometheus-style counters stored in server state, exposed as resource `codomyrmex://mcp/metrics`). |

**Tests**: `test_ws_handler.py`, `test_event_bridge.py`, `test_mcp_observability.py` (verify tool call metrics increment, duration tracked, error counter incremented on failure).

### Stream 7: Performance Baselines

| Deliverable | File | Description |
|-------------|------|-------------|
| CLI startup benchmark | `scripts/benchmark_startup.py` (NEW) | Measure `codomyrmex --help` wall-clock. Target: <500ms. |
| Module-level lazy loading | 4 heavy `__init__.py` files | Defer `matplotlib`, `chromadb`, `pyarrow`, `sentence_transformers`. |
| API benchmarks | `performance/benchmark.py` | Time: `create_codomyrmex_mcp_server()`, `get_tool_registry()`, `_discover_dynamic_tools()`, `Workflow.run()` (10-task DAG), `Scheduler.schedule()` (100 jobs). |
| Import profiling | CI script | `python -X importtime` → top-20 heaviest. Target: total <200ms. |
| **MCP discovery benchmark** | `tests/performance/test_mcp_performance.py` (NEW) | Cold discovery time <3s. Cached discovery <10ms. `call_tool()` overhead (excluding handler) <2ms. `create_codomyrmex_mcp_server()` <5s. |

**v0.1.8 Gate Criteria**:

- Full test suite 0 failures. MCP test count ≥200 (up from 137).
- Schema validation rejects 100% of invalid inputs in fuzz suite.
- Circuit breaker prevents cascade failures under 50-concurrent-request load.
- CLI startup <500ms, import time <200ms, MCP discovery (cached) <10ms.
- Event bridge captures all lifecycle events with correlation IDs.

---

## 🔧 v0.1.9 — PAI Workflow Hardening & CLI Diagnostics

**Theme**: "Bulletproof Workflows" | **Scope**: 5 work streams, ~30 deliverables

> **Codebase Baseline (after v0.1.8)**:
>
> **PAI Bridge & Trust** (1,627 lines):
>
> - `mcp_bridge.py` (1,042 lines): 18 static tools + auto-discovery. After v0.1.8: schema validation, error envelope, cached discovery with TTL.
> - `trust_gateway.py` (585 lines): 3-tier model (UNTRUSTED→VERIFIED→TRUSTED), `_is_destructive()` pattern detection. **No audit log**. **No input validation before trust check**.
> - `verify_capabilities()` returns simple dict. **No normalized shape** — consumers must handle variable keys.
>
> **Claude Code Workflows** (7 files, `.agent/workflows/`):
>
> - `codomyrmexAnalyze` (753B), `codomyrmexDocs` (679B), `codomyrmexMemory` (856B), `codomyrmexSearch` (846B), `codomyrmexStatus` (751B), `codomyrmexTrust` (1880B), `codomyrmexVerify` (1481B).
> - **No integration tests** — workflows are exercised manually only.
> - **No error recovery** — workflow failure produces unstructured Claude Code error.
>
> **CLI** (643 lines in `cli/core.py`):
>
> - Auto-discovered module commands. `--help`, `check`, `modules`, `status`, `shell`, `workflow`, `project`, `ai`, `analyze`, `build`, `test`, `fpf`, `skills`.
> - **No `doctor` subcommand**. No health diagnostics. No version sync check.
>
> **Concurrency** (13 files):
>
> - channels, distributed_lock, lock_manager, rate_limiter, semaphore, redis_lock. No managed async pool. No dead-letter queue.
> - `JSONFileStore.list_all()` doesn't hold lock during iteration (potential concurrent modification bug).

### Stream 1: PAI Bridge Hardening

| Deliverable | File | Description |
|-------------|------|-------------|
| **Capability response normalization** | `agents/pai/mcp_bridge.py` `verify_capabilities()` | Always returns canonical shape: `{ tools: { safe: list[str], destructive: list[str], total: int, by_category: dict[str, int] }, modules: { loaded: int, failed: list[{name, error}], total: int }, trust: { level: str, audit_entries: int, gateway_healthy: bool }, mcp: { server_name: str, transport: str, resources: int, prompts: int }, discovery: { cache_age_seconds: float, last_scan_duration_ms: float } }`. Wire to `_LazyToolSets.safe_tools()` / `.destructive_tools_set()`. |
| **Workflow listing tool** | `agents/pai/mcp_bridge.py` | `_tool_list_workflows()`: reads `.agent/workflows/*.md` YAML frontmatter → `{ workflows: [{ name, description, filepath, size_bytes }] }`. Error handling: malformed YAML returns partial results + `warnings` list. |
| **Cache invalidation tool** | `agents/pai/mcp_bridge.py` | `_tool_invalidate_cache(module: str | None = None)`: if`module` given, invalidate + rescan single module (incremental, from v0.1.8). If `None`, full cache clear. Returns`{ cleared: bool, rescan_duration_ms: float, new_tool_count: int }`. |
| **Tool versioning** | `model_context_protocol/discovery.py` | `@mcp_tool(..., version="1.0", deprecated=False, deprecated_message="Use X instead")`. Discovery registers version metadata. Server includes `x-version` in tool schema. `list_tools()` response includes `deprecated` flag. `_call_tool()` logs deprecation warning on first call. |
| **Tool dependency declaration** | `model_context_protocol/discovery.py` | `@mcp_tool(..., requires=["numpy", "chromadb"])`. Discovery checks `importlib.util.find_spec()` for each requirement. Missing deps: tool registered with `available=False` in schema. `_call_tool()` returns `MCPToolError(code="DEPENDENCY_MISSING", suggestion="uv sync --extra ...")`. |

### Stream 2: Trust Gateway Hardening

| Deliverable | File | Description |
|-------------|------|-------------|
| **Audit log** | `agents/pai/trust_gateway.py` | `_audit_log: list[dict]` on `TrustGateway`. Every `trusted_call_tool()` logs: `{ timestamp: ISO8601, tool_name: str, args_hash: str (SHA256 of canonical JSON), result_status: "success"|"error"|"blocked", trust_level: str, duration_ms: float, error_code: str|None }`. Thread-safe append via`threading.Lock`. |
| **Audit log API** | `agents/pai/trust_gateway.py` | `get_audit_log(since: datetime | None = None, tool_name: str | None = None, status: str | None = None) → list[dict]`.`export_audit_log(path: Path, format: str = "jsonl")`: JSONL or CSV.`clear_audit_log(before: datetime | None = None)`. Max log size: 10,000 entries (FIFO eviction). |
| **Pre-dispatch validation** | `agents/pai/trust_gateway.py` | Before trust check: validate tool args against schema (reuse v0.1.8 `validate_tool_arguments()`). Reject before even checking trust level — prevents `TRUSTED` tools from receiving garbage input. |
| **Trust escalation hooks** | `agents/pai/trust_gateway.py` | `on_trust_change: Callable[[TrustLevel, TrustLevel], None] | None`. Called on`trust_all()`,`reset_trust()`. Emits`EventBus` event `TRUST_LEVEL_CHANGED(old, new)`. Default hook: log via`codomyrmex.security` logger. |
| **Destructive tool confirmation** | `agents/pai/trust_gateway.py` | `require_confirmation: bool = False` on `TrustGateway`. When `True` and tool is destructive: instead of executing, return `{ "confirmation_required": true, "tool_name": str, "args_preview": dict, "confirm_token": uuid }`. Second call with `confirm_token` proceeds. Token expires after 60s. |

**Test Plan**:

| Test | File | What it validates |
|------|------|-------------------|
| `test_trust_audit_log.py` | NEW, ~12 tests | Log populated on tool call, args_hash deterministic, timestamp monotonically increasing, `get_audit_log(since=)` filters correctly, `get_audit_log(tool_name=)` filters, `export_audit_log()` writes valid JSONL, FIFO eviction at 10K entries, thread-safe concurrent appends (10 threads), `clear_audit_log()` works, blocked calls logged with `status="blocked"` |
| `test_trust_validation.py` | NEW, ~6 tests | Invalid args rejected before trust check, valid args pass through, schema errors include field details, trust level irrelevant for validation errors |
| `test_trust_escalation.py` | NEW, ~5 tests | Hook fired on `trust_all()`, hook fired on `reset_trust()`, EventBus event emitted, old/new levels correct |
| `test_trust_confirmation.py` | NEW, ~6 tests | Destructive tool returns confirmation prompt, valid token executes, expired token rejected, invalid token rejected, safe tool bypasses confirmation, confirmation disabled by default |

### Stream 3: Claude Code Workflow Integration Tests

All zero-mock, in `tests/integration/workflows/`:

| Test | Workflow | Assertions |
|------|----------|------------|
| `test_workflow_analyze.py` | `/codomyrmexAnalyze` on `src/codomyrmex/utils/` | Valid JSON with: `file_count ≥ 3`, `total_lines > 0`, `function_count > 0`, `analysis_duration_ms > 0` |
| `test_workflow_docs.py` | `/codomyrmexDocs` for 5 core modules | Non-empty README content for each of: `orchestrator`, `events`, `agents`, `model_context_protocol`, `logging_monitoring`. Verify markdown heading structure. |
| `test_workflow_status.py` | `/codomyrmexStatus` | Dict with keys: `system_status` (str), `pai_awareness` (bool), `mcp_health` (dict with `healthy`, `tool_count`), `trust_level` (str) |
| `test_workflow_trust.py` | Full trust lifecycle | `verify_capabilities()` → `trust_all()` → `trusted_call_tool('list_modules')` succeeds → `reset_trust()` → verify UNTRUSTED state → `trusted_call_tool()` raises/blocks |
| `test_workflow_verify.py` | `/codomyrmexVerify` | Dict with: `modules` ≥82, `tools` ≥535, `resources` ≥2, `prompts` ≥10, `trust.level`, `discovery.failed_modules` is empty list |
| `test_workflow_search.py` | `/codomyrmexSearch` for `"def main"` | ≥3 matching files including `cli/core.py`, results include line numbers |
| `test_workflow_memory.py` | `/codomyrmexMemory` | Add entry `"test_key": "test_value"` → recall by key → verify exact match → delete → verify deleted |
| `test_workflow_error.py` | Invalid module name | Structured error response with `error_type`, `suggestion`, no crash, no traceback leak |
| `test_workflow_roundtrip.py` | Full MCP round-trip | `MCPClient` connects to `create_codomyrmex_mcp_server()` → `list_tools()` returns ≥535 → `call_tool("codomyrmex.list_modules")` returns 82 modules → `read_resource("codomyrmex://status")` returns valid JSON → `get_prompt("analyze_module")` returns template with `{module_name}` placeholder |
| `test_workflow_concurrent.py` | 10 parallel workflows | Run 10 different workflow types concurrently via `asyncio.gather()`. All complete without deadlock. Results are independent (no cross-contamination). Total duration <30s. |

### Stream 4: CLI Doctor

New file `cli/doctor.py` (~300 lines), registered in `cli/core.py` via existing subparser pattern:

| Subcommand | Checks | Pass criteria |
|------------|--------|---------------|
| `codomyrmex doctor` | Module imports (all 82), tool registry count, MCP server instantiation, test suite dry-run (`pytest --co -q` exit 0) | All 82 imports succeed, tool count ≥535, server creates without error, pytest collects ≥8000 tests |
| `--pai` | PAI skill presence (`~/.claude/skills/PAI/SKILL.md`), `PAIBridge.get_status()`, tool count breakdown (safe/destructive), trust state, version sync (`PAI.md` ↔ `SKILL.md` ↔ `pyproject.toml`) | Skill file exists, all versions match, trust gateway initializes |
| `--workflows` | Parse all 7 `.agent/workflows/*.md`, validate YAML frontmatter, verify `description` field present, check referenced tool names exist in registry | All 7 workflows parse, all referenced tools found |
| `--rasp` | RASP completeness — scan all 82 module dirs for README.md, AGENTS.md, SPEC.md, PAI.md | 0 modules missing any RASP file |
| `--imports` | `python -X importtime -c "import codomyrmex"` → top-10 heaviest, flag any >100ms | Total import <200ms |
| `--mcp` | MCP server health: create server, `list_tools()`, `call_tool("codomyrmex.list_modules")`, `list_resources()`, `list_prompts()`. Discovery metrics. Circuit breaker states. | All MCP operations succeed, tool count matches registry |
| `--all` | Run all above checks | Composite exit code |
| `--json` | Output as structured JSON | Valid JSON on stdout |

Exit codes: 0=healthy, 1=warnings (e.g., deprecation notices), 2=errors (e.g., missing modules).

**Tests**: `test_cli_doctor.py` (~15 tests): each subcommand exit 0 on clean install, `--json` produces valid JSON, `--mcp` detects intentionally broken module, `--rasp` detects missing SPEC.md, `--imports` produces timing data.

### Stream 5: Concurrency Hardening

| Deliverable | File | Description |
|-------------|------|-------------|
| `JSONFileStore.list_all()` lock | `agentic_memory/stores.py` | Acquire `self._lock` during `list_all()` iteration (currently doesn't — race condition on concurrent `add()` + `list_all()`). |
| `AsyncWorkerPool` | `concurrency/pool.py` (NEW) | `asyncio.TaskGroup` + `Semaphore`. Methods: `submit(coro) → Future`, `shutdown(wait=True)`, `map(func, items)`. Integrates with `concurrency/semaphore.py`. |
| `DeadLetterQueue` | `concurrency/dead_letter.py` (NEW) | Failed MCP tool invocations. Fields: `tool_name`, `args`, `error`, `timestamp`, `retry_count`. Persistence: `~/.codomyrmex/dead_letters.json`. Methods: `add()`, `replay(tool_name)`, `purge(older_than)`, `list_entries(tool_name=None)`. Wire into `PipelineRetryExecutor` on `DEAD_LETTER` outcome. Expose as MCP resource `codomyrmex://dead-letters`. |

### Stream 6: Security Pre-Audit

| Deliverable | File | Description |
|-------------|------|-------------|
| Input validation | `agents/pai/mcp_bridge.py` | MCP tool args validated via `jsonschema.validate()` before dispatch (v0.1.8 prereq). v0.1.9: extend to trust gateway — validate args + trust level before allowing execution. |
| Honeytoken activation | `defense/active.py`, `conftest.py` | `CODOMYRMEX_TEST_MODE=1` → activate honeytoken patterns. `test_honeytoken_activation.py`: verify detection on simulated intrusion. |
| Dependency audit | CI | `uv pip audit` in GitHub Actions. Flag known CVEs. |

**v0.1.9 Gate Criteria**:

- All 10 Claude Code workflow integration tests pass.
- `codomyrmex doctor --all` exits 0 on clean install.
- Trust audit log captures 100% of tool invocations with correct args_hash.
- Dead-letter queue captures and replays failed tools.
- MCP test count ≥250 (up from ≥200 post-v0.1.8).
- Zero `jsonschema.ValidationError` passthrough (all caught and wrapped).

---

## 🤖 v0.2.0 — "Agents Я Us"

**Theme**: "Everything Works, Everything Connects" | **Scope**: Certification release

> This release certifies that every Codomyrmex capability is accessible, tested, and production-grade
> through PAI, Claude Code, and MCP interfaces. No new cognitive features — just bulletproof plumbing.

### MCP Coverage Certification

- [ ] Every module with public functions has auto-discovered MCP tools (target: 600+ tools)
- [ ] `MCPClient` ↔ `MCPServer` full round-trip verified (both stdio and HTTP transports)
- [ ] Tool count parity: `get_total_tool_count()` matches SKILL.md tool table exactly
- [ ] MCP tool argument schemas fully typed — eliminate all `Any` in tool signatures
- [ ] `_discover_dynamic_tools()` cached and <100ms (v0.1.8 prerequisite)
- [ ] Tool category taxonomy: every tool tagged with one of {analysis, generation, execution, query, mutation}
- [ ] Rate limiting operational via `RateLimiter` for external-facing tool invocations
- [ ] Circuit breaker operational for all tool categories
- [ ] Schema validation on 100% of tool invocations (no bypass path)

### PAI Integration Certification

- [ ] All 10+ Claude Code workflow integration tests pass (from v0.1.9)
- [ ] `verify_capabilities()` returns normalized, canonical response shape
- [ ] Full trust lifecycle tested end-to-end with audit log verification
- [ ] Skill manifest (`get_skill_manifest()`) matches actual capabilities — automated check in CI
- [ ] PAI version sync: `PAI.md` ↔ `SKILL.md` ↔ `agents/pai/__init__.py` ↔ `pyproject.toml` all `0.2.0`
- [ ] `PAIAGENTSYSTEM.md` agent-module mapping validated
- [ ] PAI Algorithm phase coverage: all 8 phases have ≥2 mapped Codomyrmex modules with working MCP tools

### Logging & Observability

- [ ] Structured JSON logging toggleable across all modules via `enable_structured_json()`
- [ ] `WebSocketLogHandler` streaming verified with real WebSocket connections
- [ ] `codomyrmex doctor` CLI fully operational with all subcommands
- [ ] `EventBus` → logging pipeline: all agent/workflow/scheduler/MCP events observable
- [ ] Correlation ID propagation: MCP tool invocation → event → log → audit trail
- [ ] MCP metrics resource (`codomyrmex://mcp/metrics`) with call counts, durations, error rates

### Concurrency & Performance

- [ ] `AsyncParallelRunner` for truly async concurrent workflow execution
- [ ] CLI startup <500ms, import time <200ms — enforced in CI
- [ ] All shared state thread-safe, verified by concurrent stress tests
- [ ] Dead-letter queue operational: failed MCP invocations captured, replayable
- [ ] Connection pooling on HTTP transport with DNS cache
- [ ] Memory profiling: `tracemalloc` snapshots for long-running orchestrator workflows

### Test Suite Certification

- [ ] Full regression: **0 failures**, ≤100 skips, 0 xfails
- [ ] MCP test count ≥300 (up from ≥250 post-v0.1.9)
- [ ] Coverage ≥80% on all actively maintained modules — enforced in CI
- [ ] Mutation testing on critical paths (MCP bridge, trust gateway, retry policy)
- [ ] Load testing: MCP server handles 100 concurrent tool invocations without deadlock
- [ ] Test execution time budget: full suite <600s

### Documentation Freeze

- [ ] All 82 modules have current README.md, SPEC.md, AGENTS.md, PAI.md (RASP complete)
- [ ] CHANGELOG.md complete through v0.2.0
- [ ] API reference auto-generated from docstrings (Sphinx or mkdocstrings)
- [ ] `SKILL.md` tool table auto-validated against registry
- [ ] Architecture diagrams reflect actual module dependencies

**Gate**: `codomyrmex doctor --all` exit 0. 0 test failures. Coverage ≥80%. MCP tool count ≥600. All workflows passing. PAI version sync validated.

---

## 🧠 v0.3.0 — "Active Inference"

**Theme**: "Thinking Agents" | **Scope**: Cognitive architecture on the hardened v0.2.0 base

> **Codebase Baseline**: `cerebrum/` has 25 .py files, `graph_rag/` has 4, `meme/` has 2, `prompt_engineering/` has 9,
> `llm/` has 29. All functional but largely unintegrated with agent core.

### Chain-of-Thought Reasoning

| Deliverable | File | Description |
|-------------|------|-------------|
| CoT prompting wrapper | `llm/chain_of_thought.py` (NEW) | `think()` → `reason()` → `conclude()` pipeline. Step-by-step, tree-of-thought, debate-style reasoning. Returns `ReasoningTrace` with confidence scores. |
| `ThinkingAgent` | `agents/core/thinking_agent.py` (NEW) | Extends `ReActAgent`. Overrides `plan()` with CoT. Stores traces in `AgentMemory`. |
| Sliding context window | `llm/context_manager.py` (NEW) | Token-aware sliding window. Strategies: FIFO, importance-weighted, semantic similarity. |
| Reasoning MCP tools | `agents/core/mcp_tools.py` | Expose `think`, `reason`, `get_reasoning_trace` as MCP tools. |

### Cerebrum + GraphRAG Integration

| Deliverable | File | Description |
|-------------|------|-------------|
| Case retrieval | `cerebrum/case_retrieval.py` (NEW) | `CaseBase` for past code patterns. Similarity search via `VectorStoreMemory`. |
| Graph-agent bridge | `graph_rag/agent_bridge.py` (NEW) | Wire graph retrieval into agent context. Entity linking. |
| Bayesian reasoning | `orchestrator/bayesian.py` (NEW) | Bayesian decision hooks for task selection. Prior/likelihood/posterior. |
| Knowledge distillation | `cerebrum/distillation.py` (NEW) | Extract reusable patterns from agent traces → `CaseBase`. |

### Memetic Analysis

| Deliverable | File | Description |
|-------------|------|-------------|
| Anti-pattern detector | `meme/anti_pattern_detector.py` (NEW) | Detect copy-paste drift, god objects, circular deps, dead code. |
| Concept drift tracker | `meme/drift_tracker.py` (NEW) | Track semantic drift between docs and code via LLM comparison. |

### Prompt Engineering Integration

| Deliverable | File | Description |
|-------------|------|-------------|
| Template→agent wiring | `prompt_engineering/agent_prompts.py` (NEW) | Dynamic prompt selection by task type. A/B testing support. |
| Context-aware prompts | `prompt_engineering/context.py` (NEW) | Enrich prompts with file history, similar code, past solutions. |

### Security Hardening

- [ ] `wallet/key_rotation.py`: automated key rotation scheduler
- [ ] `wallet/encrypted_storage.py`: AES-256-GCM encrypted credential storage
- [ ] Dependency scanning in CI/CD

**Gate**: ThinkingAgent produces valid reasoning traces. Case retrieval relevant. Anti-pattern detector flags ≥3 known patterns. All new code ≥80% coverage.

---

## 🐜 v0.4.0 — "Ant Colony"

**Theme**: "Swarm Orchestration" | **Scope**: Autonomous multi-agent collaboration

> **Codebase Baseline**: `collaboration/` 18 .py files, `agents/` 86 files (ReActAgent, no multi-agent),
> `orchestrator/` 26 files (no agent coordination), `identity/` 5 files. 359 test files.

### Swarm Protocol

| Deliverable | File | Description |
|-------------|------|-------------|
| `SwarmProtocol` | `collaboration/swarm/protocol.py` (NEW) | Typed multi-agent collaboration. Roles: Coder, Reviewer, DevOps, Architect, Tester. Consensus: majority vote, weighted expertise, veto. |
| `AgentPool` | `collaboration/swarm/pool.py` (NEW) | Managed pool with capability-based routing. Load balancing: round-robin, skill-match. |
| `SwarmMessage` | `collaboration/swarm/message.py` (NEW) | Inter-agent format extending `AgentMessage`. Intent: REQUEST/RESPONSE/BROADCAST. `thread_id`. |
| Agent identity | `identity/capability.py` (NEW) | Capability advertisement + matching. |
| Swarm MCP tools | `collaboration/swarm/mcp_tools.py` (NEW) | `create_swarm`, `assign_task`, `get_consensus`, `swarm_status`. |

### Self-Healing Workflows

| Deliverable | File | Description |
|-------------|------|-------------|
| Auto-diagnosis | `orchestrator/self_healing.py` (NEW) | On failure: invoke `ThinkingAgent` for root cause analysis. Pattern library. |
| Config-aware retry | `orchestrator/self_healing.py` | Detect config failures → auto-adjust → retry. |
| Diagnostics dead-letter | `orchestrator/self_healing.py` | Structured diagnostic reports with `related_cases`. |

### Project-Level Context

| Deliverable | File | Description |
|-------------|------|-------------|
| `ProjectContext` | `agents/context/project.py` (NEW) | Full repo structure awareness. |
| Repo indexer | `agents/context/indexer.py` (NEW) | Auto-index via `git_operations` + `coding.parsers`. Incremental. |
| Context-aware tool select | `agents/context/tool_selector.py` (NEW) | File type + task type → optimal MCP tools. |

### Meta-Agent

| Deliverable | File | Description |
|-------------|------|-------------|
| `MetaAgent` | `agents/meta/meta_agent.py` (NEW) | Self-improving: rewrites prompts based on outcomes. |
| Strategy library | `agents/meta/strategies.py` (NEW) | Persisted via `agentic_memory`. A/B testing. |
| Outcome scoring | `agents/meta/scoring.py` (NEW) | Multi-dimensional: correctness, efficiency, code quality, user satisfaction. |

**Gate**: Swarm completes 3-agent code review. Self-healing fixes ≥3 failure patterns. MetaAgent shows improvement over 10 iterations. MCP tools >700. All previous gates pass.

---

## 🔄 Ongoing Technical Debt

- [ ] Continuous removal of magic numbers and hardcoded paths
- [ ] Keep `SPEC.md` / `AGENTS.md` / `CHANGELOG.md` synchronized with code changes
- [ ] Enforce `mypy --strict` progressively across the codebase
- [ ] Keep PAI bridge versions synchronized: `PAI.md` ↔ `SKILL.md` ↔ `agents/pai/__init__.py` ↔ `pyproject.toml`
- [ ] Keep `skill-index.json` triggers/workflows consistent with actual skill files
- [ ] Maintain MCP tool count parity: SKILL.md ↔ `get_total_tool_count()` at release time
- [ ] Module RASP completeness: enforce via CI that all modules have README/AGENTS/SPEC/PAI
- [ ] Deprecation tracking: maintain list of deprecated APIs with removal target versions
