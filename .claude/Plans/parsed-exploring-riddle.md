# Plan: Run Test Suite, Fix Failures, Add Documentation Tests

## Context

The codomyrmex project has 348 test files (~1200 tests) across 78 modules. The user wants to:
1. Run the full test suite and identify all failures
2. Fix broken tests
3. Add and improve documentation tests for modules with real implementations but insufficient test coverage

The project enforces a **zero-mock policy** — all tests use real implementations and typed fakes. Coverage is auto-collected via pytest.ini.

## Phase 1: Run Full Test Suite and Capture Failures

Run the complete test suite and capture output:
```bash
uv run pytest src/codomyrmex --tb=short -q 2>&1 | tee /tmp/pytest_full_run.txt
```

Then run targeted tests on core modules to isolate failure domains:
```bash
uv run pytest src/codomyrmex/tests/unit/ --tb=short -q 2>&1 | tee /tmp/pytest_unit_run.txt
```

Categorize failures into:
- **Import errors** (broken imports, missing modules)
- **Assertion failures** (logic/API contract changes)
- **External dependency failures** (Docker, Ollama, network)
- **Timeout/resource failures**

## Phase 2: Fix Failing Tests

Fix tests in priority order:

1. **Import path fixes** — Update imports that reference moved/renamed modules
2. **Assertion fixes** — Update assertions to match current API return shapes
3. **Mark external tests** — Add `@pytest.mark.external` to tests requiring Docker/Ollama/network so they're skippable

## Phase 3: Add Documentation Tests for Undertested Modules

### Priority targets (real code with zero or near-zero tests):

### 3.1 — `coding/monitoring/` (239 lines, ZERO tests)

**Create:** `src/codomyrmex/tests/unit/coding/monitoring/test_coding_monitoring.py`

Test all 3 exported classes against their real implementations:
- `ExecutionMonitor` — `start_execution()`, `end_execution()`, `get_execution_stats()` (covers: initial state, tracking entries, status updates, stat aggregation, multi-execution independence)
- `ResourceMonitor` — `start_monitoring()`, `update_monitoring()`, `get_resource_usage()` (covers: start time recording, resource stats shape, peak >= start invariant)
- `MetricsCollector` (coding-specific, NOT utils/) — `record_execution()`, `get_summary()`, `get_language_stats()`, `clear()`

**Key files:** `src/codomyrmex/coding/monitoring/execution_monitor.py`, `resource_tracker.py`, `metrics_collector.py`

### 3.2 — `coding/sandbox/isolation.py` (310 lines, ZERO tests)

**Create:** `src/codomyrmex/tests/unit/coding/sandbox/test_sandbox_isolation.py`

- `ExecutionLimits` dataclass — default values, custom values, all 4 validation error paths (`time_limit`, `memory_limit`, `cpu_limit`, `max_output_chars`)
- `resource_limits_context` — enters/exits without error, restores limits on exception

**Key file:** `src/codomyrmex/coding/sandbox/isolation.py`

### 3.3 — `coding/static_analysis/` (1085 lines, 1 import test)

**Create:** `src/codomyrmex/tests/unit/static_analysis/test_static_analyzer_core.py`

- Enums: `AnalysisType`, `SeverityLevel`, `Language` — value verification, member count
- Dataclasses: `AnalysisResult`, `AnalysisSummary`, `CodeMetrics` — construction with required/optional fields
- `StaticAnalyzer` init — default project root, custom project root, tools_available shape
- `analyze_file()` on a real temp Python file — returns list of `AnalysisResult`
- `get_available_tools()` — returns list

**Key file:** `src/codomyrmex/coding/static_analysis/static_analyzer.py`
**Note:** Imports `pyrefly_runner` — test file must handle potential ImportError gracefully

### 3.4 — `model_context_protocol/tools.py` and `decorators.py` (684 lines, untested)

**Create:** `src/codomyrmex/tests/unit/model_context_protocol/test_mcp_tools.py`

- `read_file()` — existing file returns success+content+metadata, nonexistent returns error, max_size enforcement
- `write_file()` — creates file, content matches, returns byte count, creates parent dirs
- `list_directory()` — lists real directory entries, nonexistent path returns error, pattern filtering
- `analyze_python_file()` — on real temp .py file returns analysis dict
- `@mcp_tool` decorator — attaches `_mcp_tool` metadata, preserves function behavior, auto-generates schema from type hints

**Key files:** `src/codomyrmex/model_context_protocol/tools.py`, `decorators.py`

### 3.5 — `validation/examples_validator.py` (438 lines, ZERO tests)

**Create:** `src/codomyrmex/tests/unit/validation/test_examples_validator.py`

- Enums: `ValidationSeverity`, `ValidationType` — value verification
- Dataclasses: `ValidationIssue` (required + optional fields), `ModuleValidationResult` (success/failure with issues)
- `ExamplesValidator` init — accepts root_dir, output_dir, parallel_jobs; defaults correct

**Key file:** `src/codomyrmex/validation/examples_validator.py`

### 3.6 — `utils/metrics.py` (223 lines, ZERO tests)

**Create:** `src/codomyrmex/tests/unit/utils/test_utils_metrics.py`

- `MetricsCollector` singleton — identity check, `increment()`, `set_gauge()`, `observe()` histogram, `get_all()` shape, labels create distinct keys, `reset()` clears all
- `timed_metric` context manager — records histogram with `_duration_ms` suffix
- `count_calls` decorator — increments `_calls_total` on success, `_errors_total` on exception
- `ModuleHealth` — `register()`, `check()`, `check_all()`, `is_healthy()`
- `export_prometheus()` — returns string with Prometheus format
- **Critical:** Each test must call `metrics.reset()` in `setup_method` to avoid singleton cross-contamination

**Key file:** `src/codomyrmex/utils/metrics.py`

### 3.7 — `terminal_interface/utils/terminal_utils.py` (479 lines, untested)

**Create:** `src/codomyrmex/tests/unit/terminal_interface/test_terminal_utils.py`

- `TerminalFormatter` — init with/without colors, COLORS/STYLES dicts populated, `colorize()` includes ANSI codes when enabled, plain text when disabled

**Key file:** `src/codomyrmex/terminal_interface/utils/terminal_utils.py`

## Files Summary

| Action | File | Reason |
|--------|------|--------|
| Create | `tests/unit/coding/monitoring/test_coding_monitoring.py` | 239 lines, 0 tests |
| Create | `tests/unit/coding/sandbox/test_sandbox_isolation.py` | 310 lines, 0 tests |
| Create | `tests/unit/static_analysis/test_static_analyzer_core.py` | 1085 lines, 1 test |
| Create | `tests/unit/model_context_protocol/test_mcp_tools.py` | 684 lines, 0 unit tests |
| Create | `tests/unit/validation/test_examples_validator.py` | 438 lines, 0 tests |
| Create | `tests/unit/utils/test_utils_metrics.py` | 223 lines, 0 tests |
| Create | `tests/unit/terminal_interface/test_terminal_utils.py` | 479 lines, 0 tests |
| Modify | Various test files with import/assertion failures | Fix broken tests from Phase 1 |

All paths relative to `src/codomyrmex/`.

## Phase 4: Verification

1. Run full unit test suite — confirm new tests pass and no regressions:
   ```bash
   uv run pytest src/codomyrmex/tests/unit/ --tb=short -q
   ```

2. Run only new test files to verify independently:
   ```bash
   uv run pytest src/codomyrmex/tests/unit/coding/monitoring/ \
                 src/codomyrmex/tests/unit/coding/sandbox/ \
                 src/codomyrmex/tests/unit/static_analysis/test_static_analyzer_core.py \
                 src/codomyrmex/tests/unit/model_context_protocol/test_mcp_tools.py \
                 src/codomyrmex/tests/unit/validation/test_examples_validator.py \
                 src/codomyrmex/tests/unit/utils/test_utils_metrics.py \
                 src/codomyrmex/tests/unit/terminal_interface/test_terminal_utils.py \
                 -v --tb=short
   ```

3. Verify zero-mock compliance — grep new test files for forbidden imports:
   ```bash
   grep -rn "unittest.mock\|MagicMock\|patch(" <new test files>
   ```

## Design Principles

- **Zero-mock policy**: All tests use real implementations with real filesystem, real dataclasses, real function calls
- **Existing fixtures**: Leverage `tmp_path` (pytest built-in), `real_logger_fixture`, `real_code_samples` from root conftest
- **Singleton safety**: `utils/metrics.MetricsCollector` is a singleton — every test class resets via `metrics.reset()` in `setup_method`
- **Platform awareness**: `resource_limits_context` uses `resource.setrlimit` (Unix-only) — tests should handle `OSError` gracefully on unsupported platforms
- **Import safety**: `static_analyzer.py` imports `pyrefly_runner` — test file wraps import in try/except with `pytest.importorskip` or `skipIf`
