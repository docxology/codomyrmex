# Personal AI Infrastructure — Testing Module

**Version**: v1.1.9 | **Status**: Active | **Last Updated**: March 2026

## Overview

The Testing module provides PAI integration for test automation, enabling AI agents to generate, execute, and validate tests across the entire Codomyrmex platform. It is the primary gatekeeper for the PAI Algorithm's **VERIFY phase** — every hill-climbing iteration bottoms out here to determine whether the current solution meets ISC (Intelligent Success Criteria). Without this module, the PAI feedback loop has no objective quality signal.

The module consolidates property-based testing, fuzz testing, fixture lifecycle management, and typed data generation into a single cohesive package. It enforces the project's strict **zero-mock policy**: no `unittest.mock`, no `MagicMock`, no `monkeypatch` — tests run against real implementations with `@pytest.mark.skipif` guards when external dependencies are unavailable.

## PAI Capabilities

### Generated Test Scaffolds

Generate test scaffolds from source code for an agent to fill in. The generator lives in the `coding` module:

```python
from pathlib import Path

from codomyrmex.coding.test_generator import TestGenerator

# Generate test stubs from code
generator = TestGenerator()
suite = generator.from_source(Path("src/auth.py").read_text(), module_name="auth")

# Write generated tests
Path("tests/test_auth.py").write_text(suite.render())
```

`TestGenerator` parses the source with `ast` and emits one stub per public function, class and public method (`# TODO` plus `assert True`). It does not call an LLM; the agent replaces each stub body with real assertions against real implementations.

### Test Execution

The module does not wrap the test runner; run pytest (with pytest-cov) directly:

```python
import pytest

# Run tests with coverage; a non-zero exit code means failures or coverage below the floor
exit_code = pytest.main(["tests/", "-q", "--cov=src/codomyrmex", "--cov-fail-under=60"])
print(f"pytest exit code: {exit_code}")
```

Test results feed directly into PAI's VERIFY phase. A failing test suite signals the Algorithm to loop back through BUILD with the failure context, while a passing suite with sufficient coverage advances to LEARN.

### Fixture Management

Manage test data lifecycles with scoping and dependency resolution:

```python
from codomyrmex.testing.fixture_utils import FixtureManager, Fixture

# Create and register fixtures with lifecycle control
fixtures = FixtureManager()

fixtures.register(
    name="db_connection",
    setup_fn=lambda: create_test_database(),
    teardown_fn=lambda db: db.close(),
    scope="session"  # function | class | module | session
)

fixtures.register(
    name="auth_token",
    setup_fn=lambda: generate_test_token(),
    scope="function"
)

# Retrieve fixtures on demand (lazy initialization)
db = fixtures.get("db_connection")
token = fixtures.get("auth_token")

# Explicit teardown when done
fixtures.teardown()  # tears down all active fixtures
```

The `FixtureManager` ensures real resources are used in tests (databases, file systems, network connections) rather than mocked substitutes, aligning with the zero-mock policy. Fixtures are created lazily and torn down deterministically.

### Test Data Generators

The module provides typed data generators for property-based and fuzz testing:

- **`IntGenerator`** — Random integers within configurable `min_val`/`max_val` bounds (default: -1000 to 1000)
- **`FloatGenerator`** — Random floats within configurable bounds
- **`StringGenerator`** — Random strings with configurable length and charset
- **`ListGenerator`** — Random lists with element type strategies
- **`DictGenerator`** — Random dictionaries with key/value strategies
- **`OneOfGenerator`** — Selects from multiple generator strategies
- **`RecordGenerator`** — Structured records from field-level generators (name, email, dates)
- **`DatasetGenerator`** — Complete datasets with `generate(rows=N)` and `generate_csv()`
- **`NameGenerator`**, **`EmailGenerator`**, **`UUIDGenerator`**, **`DateGenerator`** — Domain-specific generators

All generators implement the `GeneratorStrategy` abstract base class with a single `generate()` method, making them composable and extensible.

### Property-Based Testing

Verify invariants across thousands of generated inputs:

```python
from codomyrmex.testing import property_test
from codomyrmex.testing.strategies import IntGenerator

# Decorate a property; returning False or raising records a failure
@property_test(iterations=1000, x=IntGenerator(min_val=-10000, max_val=10000))
def check_abs_non_negative(x):
    return abs(x) >= 0

check_abs_non_negative()  # raises AssertionError naming the first failing input
```

### Fuzz Testing

Discover edge cases through targeted fuzzing:

```python
from codomyrmex.testing import Fuzzer, FuzzingStrategy, FuzzResult, StringGenerator

fuzzer = Fuzzer(strategy=FuzzingStrategy.MUTATION, max_iterations=5000)

results: list[FuzzResult] = fuzzer.fuzz(parse_input, StringGenerator(max_length=256))
crashes = fuzzer.get_crashes()
if crashes:
    print(f"Found {len(crashes)} crash inputs")
```

## MCP Tools

Two tools are exposed via `@mcp_tool` in `mcp_tools.py` and auto-discovered by the PAI MCP bridge:

| Tool | Description |
| --- | --- |
| `testing_generate_data` | Generate `count` synthetic values with a named strategy (`int`, `float`, `string`, `list`, `dict`) |
| `testing_list_strategies` | List the available generator strategy names |

Test execution, test generation and coverage are not exposed as MCP tools. Future work should expose `run_tests`, `generate_tests`, and `get_coverage` as first-class MCP tools to eliminate the proxy overhead and enable direct PAI invocation.

## PAI Algorithm Phase Mapping

| Phase | Testing Contribution |
| --- | --- |
| **OBSERVE** | Scan existing test suites to assess current coverage, identify untested modules, and detect test quality gaps. `pytest --cov` provides the quantitative baseline. |
| **THINK** | Evaluate which test strategies (unit, integration, property-based, fuzz) are needed based on the task's ISC. Determine coverage thresholds and marker categories. |
| **PLAN** | Structure the test plan: which modules need new tests, which existing tests need updating, what fixtures are required, and what the coverage delta target is. |
| **BUILD** | `coding.test_generator.TestGenerator` scaffolds test stubs from source analysis. AI agents write tests BEFORE implementation (TDD). Generated tests must fail initially (Red phase). |
| **EXECUTE** | pytest executes the test suite. `Fuzzer` runs fuzz campaigns. Property tests verify invariants across generated inputs. |
| **VERIFY** | **Primary phase.** Compare test results against ISC: pass rate, coverage percentage, no regressions, no security marker failures. This is the hill-climbing gate — failure here loops back to BUILD. |
| **LEARN** | Capture test result trends, flaky test patterns, coverage progression, and generator effectiveness into `agentic_memory` for future test strategy optimization. |

## PAI Configuration

### Environment Variables

```bash
# Coverage enforcement threshold (0-100, default: 80)
export CODOMYRMEX_COVERAGE_TARGET=80

# Parallel test execution workers (default: auto-detect CPU count)
export CODOMYRMEX_TEST_PARALLELISM=4

# Test timeout in seconds (default: 300, per pyproject.toml addopts)
export CODOMYRMEX_TEST_TIMEOUT=300

# Property test default iterations
export CODOMYRMEX_PROPERTY_TEST_CASES=1000

# Fuzz test maximum iterations
export CODOMYRMEX_FUZZ_MAX_ITERATIONS=5000
```

### Pytest Marker Configuration

Defined in `pyproject.toml` (`[tool.pytest.ini_options]` → `markers`), these markers categorize tests for selective execution:

| Marker | Description | When to Use |
| --- | --- | --- |
| `@pytest.mark.unit` | Isolated component tests | Fast feedback, no external deps |
| `@pytest.mark.integration` | Cross-component tests | Real service interactions |
| `@pytest.mark.slow` | Long-running tests | CI only, not local dev loops |
| `@pytest.mark.performance` | Load and benchmarking | Regression detection |
| `@pytest.mark.examples` | Example validation | Documentation accuracy |
| `@pytest.mark.network` | Requires network access | Guarded with `skipif` |
| `@pytest.mark.database` | Requires database | Guarded with `skipif` |
| `@pytest.mark.external` | Requires external services | Guarded with `skipif` |
| `@pytest.mark.security` | Security-related tests | Pentester subagent tasks |
| `@pytest.mark.asyncio` | Asynchronous tests | Auto-mode via `asyncio_mode = auto` |
| `@pytest.mark.crypto` | Cryptography tests | Encryption module validation |
| `@pytest.mark.orchestrator` | Orchestrator/workflow tests | Multi-step pipeline verification |

Run specific categories: `uv run pytest -m unit` or combine: `uv run pytest -m "unit and not slow"`.

## PAI Best Practices

### 1. TDD with PAI: Tests Before Implementation

The PAI Algorithm enforces test-driven development by generating tests in the BUILD phase before writing implementation code. This is the Red-Green-Refactor cycle:

```python
# Step 1 (RED): AI writes tests that define expected behavior,
# optionally starting from TestGenerator().from_source(...) stubs
# Tests MUST fail — the implementation does not exist yet

# Step 2 (GREEN): AI writes minimal implementation to pass tests
# Engineer subagent implements src/new_feature.py

# Step 3 (REFACTOR): AI improves code while keeping tests green
# Tests remain the contract — refactoring cannot break them
```

### 2. Zero-Mock Policy: External Dependency Handling

This project prohibits `unittest.mock`, `MagicMock`, and `pytest-mock` for replacing production behavior. Narrow `monkeypatch` use for environment variables, working directories, and other test-input isolation is permitted by the repository testing contract. Handle unavailable external dependencies with `skipif` guards:

```python
import os
import pytest

HAS_REDIS = os.getenv("REDIS_HOST") is not None

@pytest.mark.skipif(not HAS_REDIS, reason="Redis not available")
@pytest.mark.external
def test_cache_operations():
    """Test against a real Redis instance — no mocks."""
    from codomyrmex.cache.backends.redis_backend import RedisCache
    client = RedisCache()  # host/port from REDIS_HOST / REDIS_PORT
    client.set("key", "value")
    assert client.get("key") == "value"
```

When an external service is unavailable, the test is **skipped** — never faked. A passing test then represents observed behavior for the exercised configuration, not a universal verification claim.

### 3. Coverage-Driven ISC: Make Coverage a Verification Gate

Integrate coverage thresholds into the PAI Algorithm's ISC so the VERIFY phase treats insufficient coverage as a failure, triggering another BUILD iteration:

```python
import pytest

# In PAI ISC definition:
isc_criteria = {
    "tests_pass": True,
    "coverage_minimum": 0.60,        # project-wide line coverage floor
    "no_regressions": True,           # No previously-passing tests now fail
    "security_markers_clean": True,   # All @pytest.mark.security tests pass
}

# VERIFY phase checks (pytest-cov enforces the floor):
floor = int(isc_criteria["coverage_minimum"] * 100)
exit_code = pytest.main(["tests/", "--cov=src/codomyrmex", f"--cov-fail-under={floor}"])

if exit_code != pytest.ExitCode.OK:
    # Loop back to BUILD — generate more tests
    pass
```

## Architecture Role

**Core Layer** — The testing module sits in the Core layer of Codomyrmex's architecture.

- **Dependencies**: `logging_monitoring/` (structured test output and result logging), `validation/` (shared `Result`/`ResultStatus` schemas)
- **Consumed by**: `ci_cd_automation/` (pipeline test execution), `orchestrator/` (test workflows and DAG steps), `security/` (security test coordination)
- **Consolidates**: `workflow/` (end-to-end workflow testing), `chaos/` (fault injection and resilience testing)

The testing module is the only module that every other module depends on indirectly — all modules have tests, and all tests flow through the testing infrastructure.

## Navigation

- **Self**: [PAI.md](PAI.md)
- **Parent**: [../PAI.md](../PAI.md) — Source-level PAI module map
- **Root Bridge**: [../../../PAI.md](../../../PAI.md) — Authoritative PAI system bridge doc
- **Siblings**: [README.md](README.md) | [AGENTS.md](AGENTS.md) | [SPEC.md](SPEC.md)
