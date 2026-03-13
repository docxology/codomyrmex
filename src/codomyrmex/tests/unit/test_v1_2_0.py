"""Tests for v1.2.0 — CLI Maturity, Quality Gates, SBOM.

Zero-Mock: All tests use real implementations.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

# ── CL1: Agent CLI ────────────────────────────────────────────────
from codomyrmex.cli.handlers.agent import (
    handle_agent_health,
    handle_agent_list,
    handle_agent_start,
)


class TestAgentCLI:
    """Verify agent CLI subcommands."""

    def test_agent_list(self) -> None:
        agents = handle_agent_list()
        assert isinstance(agents, list)
        assert len(agents) > 3  # hermes, claude, jules, etc.

    def test_agent_list_contains_hermes(self) -> None:
        agents = handle_agent_list()
        assert "hermes" in agents

    def test_agent_health_existing(self) -> None:
        status = handle_agent_health("hermes")
        assert status["exists"]
        assert status["has_init"]
        assert status["health"] in ("healthy", "degraded")

    def test_agent_health_missing(self) -> None:
        status = handle_agent_health("nonexistent_agent_xyz")
        assert not status["exists"]
        assert status["health"] == "degraded"

    def test_agent_start_missing(self) -> None:
        result = handle_agent_start("nonexistent_agent_xyz")
        assert result["status"] == "error"

    def test_agent_start_returns_dict(self) -> None:
        result = handle_agent_start("hermes", model="gemma3")
        assert isinstance(result, dict)
        assert result["agent"] == "hermes"


# ── CL2: Memory CLI ──────────────────────────────────────────────

from codomyrmex.cli.handlers.memory import (
    handle_memory_index,
    handle_memory_list,
    handle_memory_search,
    handle_memory_stats,
)


class TestMemoryCLI:
    """Verify memory CLI subcommands."""

    def test_memory_list(self) -> None:
        result = handle_memory_list(limit=5)
        assert isinstance(result, list)

    def test_memory_stats(self) -> None:
        stats = handle_memory_stats()
        assert isinstance(stats, dict)

    def test_memory_index_no_vault(self) -> None:
        result = handle_memory_index()
        assert result["status"] == "completed"
        assert result["vault_path"] is None

    def test_memory_index_nonexistent_vault(self) -> None:
        result = handle_memory_index(vault="/tmp/nonexistent_vault_xyz_123")
        assert result["status"] == "error"

    def test_memory_search(self) -> None:
        results = handle_memory_search("test")
        assert isinstance(results, list)


# ── CL3: Dashboard CLI ───────────────────────────────────────────

class TestDashboardCLI:
    """Verify dashboard CLI method exists."""

    def test_dashboard_method_exists(self) -> None:
        from codomyrmex.cli.core import Cli

        cli = Cli()
        assert hasattr(cli, "dashboard")

    def test_dashboard_signature(self) -> None:
        import inspect

        from codomyrmex.cli.core import Cli

        sig = inspect.signature(Cli.dashboard)
        params = list(sig.parameters.keys())
        assert "port" in params
        assert "host" in params


# ── CL4: Test CLI ────────────────────────────────────────────────

class TestTestCLI:
    """Verify test CLI improvements."""

    def test_test_method_exists(self) -> None:
        from codomyrmex.cli.core import Cli

        cli = Cli()
        assert hasattr(cli, "test")

    def test_test_accepts_coverage_flag(self) -> None:
        import inspect

        from codomyrmex.cli.core import Cli

        sig = inspect.signature(Cli.test)
        params = list(sig.parameters.keys())
        assert "coverage" in params
        assert "module_name" in params


# ── Q4: SBOM Generator ───────────────────────────────────────────

from codomyrmex.ci_cd_automation.sbom_generator import (
    SBOMComponent,
    SBOMGenerator,
)


class TestSBOMGenerator:
    """Verify SBOM generation."""

    def test_generate_produces_cyclonedx(self) -> None:
        gen = SBOMGenerator()
        sbom = gen.generate()
        assert sbom["bomFormat"] == "CycloneDX"
        assert sbom["specVersion"] == "1.5"

    def test_has_metadata(self) -> None:
        gen = SBOMGenerator()
        sbom = gen.generate()
        assert "metadata" in sbom
        assert sbom["metadata"]["component"]["name"] == "codomyrmex"

    def test_has_components(self) -> None:
        gen = SBOMGenerator()
        sbom = gen.generate()
        assert len(sbom["components"]) > 10  # many deps

    def test_components_have_purl(self) -> None:
        gen = SBOMGenerator()
        sbom = gen.generate()
        for comp in sbom["components"][:5]:
            assert comp["purl"].startswith("pkg:pypi/")

    def test_write_json(self, tmp_path: Path) -> None:
        gen = SBOMGenerator()
        sbom = gen.generate()
        out = gen.write_json(sbom, str(tmp_path / "sbom.json"))
        assert out.exists()
        loaded = json.loads(out.read_text())
        assert loaded["bomFormat"] == "CycloneDX"

    def test_summary(self) -> None:
        gen = SBOMGenerator()
        summary = gen.get_summary()
        assert summary["total_components"] > 10
        assert isinstance(summary["from_lock"], bool)

    def test_component_dataclass(self) -> None:
        comp = SBOMComponent(name="pytest", version="8.0.0")
        assert comp.purl == "pkg:pypi/pytest@8.0.0"


# ── CLI Wiring ────────────────────────────────────────────────────

class TestCLIWiring:
    """Verify new subcommands are wired into the CLI."""

    def test_agent_subcommand(self) -> None:
        from codomyrmex.cli.core import Cli

        assert hasattr(Cli, "agent")
        agent_cls = Cli.agent
        assert hasattr(agent_cls, "list")
        assert hasattr(agent_cls, "start")
        assert hasattr(agent_cls, "health")

    def test_memory_subcommand(self) -> None:
        from codomyrmex.cli.core import Cli

        assert hasattr(Cli, "memory")
        memory_cls = Cli.memory
        assert hasattr(memory_cls, "list")
        assert hasattr(memory_cls, "index")
        assert hasattr(memory_cls, "search")
        assert hasattr(memory_cls, "stats")

    def test_fire_compatible(self) -> None:
        """Verify the CLI class can be introspected by fire."""
        from codomyrmex.cli.core import Cli

        Cli()
        # Check all subcommand classes are instantiable
        agent = Cli.agent()
        memory = Cli.memory()
        assert agent is not None
        assert memory is not None
