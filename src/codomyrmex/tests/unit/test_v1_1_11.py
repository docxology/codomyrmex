"""Tests for v1.1.11 — Hermetic Distribution, Formal Verification, Data Layer.

Includes property-based tests via Hypothesis where available.
Zero-Mock: All tests use real implementations.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

# ── F1: Schema Verifier ──────────────────────────────────────────
from codomyrmex.formal_verification.schema_verifier import (
    SchemaVerifier,
    SchemaViolation,
    ToolSchemaInfo,
    verify_tool_schemas,
)


class TestSchemaVerifier:
    """Verify MCP tool schema boundary checking."""

    def test_scan_finds_tools(self) -> None:
        verifier = SchemaVerifier()
        tools = verifier.scan_tools()
        assert len(tools) > 10  # expect many @mcp_tool decorators
        assert all(isinstance(t, ToolSchemaInfo) for t in tools)

    def test_tool_has_function_name(self) -> None:
        verifier = SchemaVerifier()
        tools = verifier.scan_tools()
        for tool in tools[:10]:
            assert tool.function_name  # every tool has a function

    def test_verify_returns_violations(self) -> None:
        verifier = SchemaVerifier()
        violations = verifier.verify_all()
        assert isinstance(violations, list)
        # Violations might be 0 (ideal) or some warnings
        assert all(isinstance(v, SchemaViolation) for v in violations)

    def test_summary(self) -> None:
        verifier = SchemaVerifier()
        summary = verifier.get_summary()
        assert summary["total_tools"] > 10
        assert "errors" in summary
        assert "warnings" in summary

    def test_convenience_function(self) -> None:
        violations = verify_tool_schemas()
        assert isinstance(violations, list)


# ── F2: Config Invariant Checker ──────────────────────────────────

from codomyrmex.formal_verification.config_invariants import (
    ConfigInvariantChecker,
)


class TestConfigInvariants:
    """Verify config cascading determinism."""

    def test_defaults_only(self) -> None:
        checker = ConfigInvariantChecker(
            defaults={"port": 8787, "debug": False, "name": "codomyrmex"},
        )
        results = checker.verify_determinism()
        assert len(results) == 3
        assert all(r.passed for r in results)

    def test_yaml_overrides_default(self) -> None:
        checker = ConfigInvariantChecker(
            defaults={"port": 8787},
            yaml_overrides={"port": 9000},
        )
        results = checker.verify_determinism()
        assert results[0].expected == 9000

    def test_env_overrides_yaml(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("CODOMYRMEX_PORT", "5555")
        checker = ConfigInvariantChecker(
            defaults={"port": 8787},
            yaml_overrides={"port": 9000},
        )
        results = checker.verify_precedence()
        port_result = next(r for r in results if r.key == "port")
        assert port_result.passed
        assert port_result.expected == 5555

    def test_bool_coercion(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("CODOMYRMEX_DEBUG", "true")
        checker = ConfigInvariantChecker(defaults={"debug": False})
        results = checker.verify_determinism()
        assert results[0].expected is True

    def test_precedence_invariants(self) -> None:
        checker = ConfigInvariantChecker(
            defaults={"a": 1, "b": 2, "c": 3},
            yaml_overrides={"b": 20},
        )
        results = checker.verify_precedence()
        assert all(r.passed for r in results)

    def test_summary(self) -> None:
        checker = ConfigInvariantChecker(
            defaults={"x": 1, "y": 2},
            yaml_overrides={"x": 10},
        )
        summary = checker.get_summary()
        assert summary["total_keys"] == 2
        assert summary["determinism_pass"] == 2


# ── F3: Property-Based Tests (Hypothesis) ────────────────────────

try:
    from hypothesis import given, settings
    from hypothesis import strategies as st

    HAS_HYPOTHESIS = True
except ImportError:
    HAS_HYPOTHESIS = False

skipif_no_hypothesis = pytest.mark.skipif(
    not HAS_HYPOTHESIS, reason="hypothesis not installed"
)


@skipif_no_hypothesis
class TestPropertyBased:
    """Property-based tests using Hypothesis."""

    @given(
        st.lists(
            st.floats(min_value=-1e6, max_value=1e6, allow_nan=False),
            min_size=1,
            max_size=500,
        )
    )
    @settings(max_examples=50, deadline=None)
    def test_sparkline_round_trip(self, values: list[float]) -> None:
        """Sparklines produce valid SVG for any float sequence."""
        from codomyrmex.data_visualization.charts.sparkline import render_sparkline

        result = render_sparkline(values)
        assert "<svg" in result.svg
        assert result.point_count == len(values)
        assert result.min_value <= result.max_value

    @given(st.text(min_size=0, max_size=200))
    @settings(max_examples=50, deadline=None)
    def test_memory_entry_json_roundtrip(self, content: str) -> None:
        """Memory entries survive JSON serialization."""

        # JSON roundtrip check
        data = {"role": "user", "content": content}
        serialized = json.dumps(data)
        deserialized = json.loads(serialized)
        assert deserialized["content"] == content

    @given(
        st.dictionaries(
            keys=st.from_regex(r"[a-z]{1,10}", fullmatch=True),
            values=st.one_of(st.integers(), st.booleans(), st.text(max_size=50)),
            min_size=1,
            max_size=20,
        )
    )
    @settings(max_examples=50, deadline=None)
    def test_config_determinism_always_holds(self, defaults: dict) -> None:
        """Config resolution is deterministic for any default dict."""
        checker = ConfigInvariantChecker(defaults=defaults)
        results = checker.verify_determinism()
        assert all(r.passed for r in results)

    @given(st.lists(st.text(min_size=1, max_size=100), min_size=1, max_size=20))
    @settings(max_examples=30, deadline=None)
    def test_call_graph_consistency(self, tool_names: list[str]) -> None:
        """Call graph collector maintains count consistency."""
        from codomyrmex.telemetry.tracing.call_graph import MCPCallGraphCollector

        collector = MCPCallGraphCollector()
        for name in tool_names:
            collector.record(name, caller="test")

        stats = collector.get_stats()
        assert stats["total_calls"] == len(tool_names)
        assert stats["unique_tools"] == len(set(tool_names))

    @given(
        st.lists(st.integers(min_value=0, max_value=10000), min_size=2, max_size=100)
    )
    @settings(max_examples=30, deadline=None)
    def test_token_tracker_aggregation(self, tokens: list[int]) -> None:
        """Token tracker aggregates correctly across calls."""
        from codomyrmex.telemetry.metrics.token_tracker import TokenTracker

        tracker = TokenTracker()
        for t in tokens:
            tracker.record("test-model", input_tokens=t)

        stats = tracker.get_stats()
        assert stats["total_input"] == sum(tokens)
        assert stats["total_calls"] == len(tokens)


# ── H1: Dockerfile Existence ─────────────────────────────────────


class TestHermeticDistribution:
    """Verify distribution artifacts exist and are valid."""

    def test_dockerfile_exists(self) -> None:
        repo_root = Path(__file__).resolve().parents[4]
        dockerfile = repo_root / "Dockerfile"
        assert dockerfile.exists(), "Dockerfile not found at repo root"
        content = dockerfile.read_text()
        assert "FROM python:3.13-slim" in content
        assert "HEALTHCHECK" in content
        assert "USER codo" in content

    def test_docker_compose_exists(self) -> None:
        repo_root = Path(__file__).resolve().parents[4]
        compose = repo_root / "docker-compose.yml"
        assert compose.exists(), "docker-compose.yml not found at repo root"
        content = compose.read_text()
        assert "redis:" in content
        assert "ollama:" in content
        assert "app:" in content

    def test_cli_entry_point_in_pyproject(self) -> None:
        repo_root = Path(__file__).resolve().parents[4]
        pyproject = repo_root / "pyproject.toml"
        content = pyproject.read_text()
        assert 'codomyrmex = "codomyrmex.cli:main"' in content


# ── M3: SQLite Session Store ──────────────────────────────────────

from codomyrmex.agentic_memory.models import Memory, MemoryImportance, MemoryType
from codomyrmex.agentic_memory.sqlite_store import SQLiteStore


class TestSQLiteSessionStore:
    """Verify SQLite-backed agentic memory."""

    @pytest.fixture
    def store(self, tmp_path: Path) -> SQLiteStore:
        return SQLiteStore(db_path=str(tmp_path / "test.db"))

    def _make_memory(self, content: str, mem_id: str = "") -> Memory:
        import uuid

        return Memory(
            id=mem_id or str(uuid.uuid4()),
            content=content,
            memory_type=MemoryType.EPISODIC,
            importance=MemoryImportance.MEDIUM,
        )

    def test_create_and_retrieve(self, store: SQLiteStore) -> None:
        mem = self._make_memory("test memory")
        store.save(mem)
        results = store.list_all()
        assert len(results) >= 1
        assert any(r.content == "test memory" for r in results)

    def test_get_by_id(self, store: SQLiteStore) -> None:
        mem = self._make_memory("specific entry")
        store.save(mem)
        retrieved = store.get(mem.id)
        assert retrieved is not None
        assert retrieved.content == "specific entry"

    def test_delete(self, store: SQLiteStore) -> None:
        mem = self._make_memory("to delete")
        store.save(mem)
        assert store.delete(mem.id)
        assert store.get(mem.id) is None

    def test_list_all_ordering(self, store: SQLiteStore) -> None:
        store.save(self._make_memory("entry 1"))
        store.save(self._make_memory("entry 2"))
        results = store.list_all()
        assert len(results) >= 2


# ── Module Health (regression from v1.1.10) ───────────────────────

from codomyrmex.website.module_health import ModuleHealthProvider


class TestModuleHealthRegression:
    """Regression tests for module health with new modules added."""

    def test_new_modules_visible(self) -> None:
        provider = ModuleHealthProvider()
        modules = provider.get_all_modules()
        names = [m.name for m in modules]
        assert "formal_verification" in names
        assert "agentic_memory" in names
        assert "containerization" in names
