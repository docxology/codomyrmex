"""Unit tests for codomyrmex.skills.arscontexta.core module.

Supplements test_arscontexta.py with deeper coverage of core.py classes:
MethodologyGraph (get_by_domain, list_all, edge deduplication),
VaultHealthChecker (healthy vault, note counting),
ArsContextaManager (get_primitives, process_content, get_methodology_stats, get_config),
KernelConfig (get_by_name, get_by_layer, validate_dependencies with missing deps),
VaultConfig (to_dict serialization).
"""

import pytest

from codomyrmex.skills.arscontexta.core import (
    ArsContextaManager,
    KernelPrimitiveRegistry,
    MethodologyGraph,
    VaultHealthChecker,
)
from codomyrmex.skills.arscontexta.models import (
    HealthStatus,
    KernelConfig,
    KernelLayer,
    KernelPrimitive,
    ResearchClaim,
    VaultConfig,
)

# ============================================================================
# MethodologyGraph extended tests
# ============================================================================


@pytest.mark.unit
class TestMethodologyGraphExtended:
    """Extended tests for MethodologyGraph covering untested paths."""

    def test_get_by_domain(self):
        """get_by_domain filters claims by domain string."""
        graph = MethodologyGraph()
        c1 = ResearchClaim(claim_id="A", statement="s1", source="x", domain="cog-sci")
        c2 = ResearchClaim(claim_id="B", statement="s2", source="x", domain="km")
        c3 = ResearchClaim(claim_id="C", statement="s3", source="x", domain="cog-sci")
        graph.add_claim(c1)
        graph.add_claim(c2)
        graph.add_claim(c3)
        cog_claims = graph.get_by_domain("cog-sci")
        assert len(cog_claims) == 2
        ids = {c.claim_id for c in cog_claims}
        assert ids == {"A", "C"}

    def test_get_by_domain_no_match(self):
        """get_by_domain returns empty list when no claims match."""
        graph = MethodologyGraph()
        c1 = ResearchClaim(claim_id="A", statement="s1", source="x", domain="math")
        graph.add_claim(c1)
        assert graph.get_by_domain("physics") == []

    def test_list_all(self):
        """list_all returns all added claims."""
        graph = MethodologyGraph()
        for i in range(5):
            graph.add_claim(ResearchClaim(
                claim_id=f"RC-{i}", statement=f"s{i}", source="x", domain="d",
            ))
        all_claims = graph.list_all()
        assert len(all_claims) == 5

    def test_edge_deduplication(self):
        """Adding the same edge twice does not create duplicates."""
        graph = MethodologyGraph()
        c1 = ResearchClaim(claim_id="A", statement="s1", source="x", domain="d")
        c2 = ResearchClaim(claim_id="B", statement="s2", source="x", domain="d")
        graph.add_claim(c1)
        graph.add_claim(c2)
        graph.add_edge("A", "B")
        graph.add_edge("A", "B")  # duplicate
        related_a = graph.get_related("A")
        assert len(related_a) == 1

    def test_statistics_edge_count(self):
        """Statistics correctly count edges (bidirectional counted once)."""
        graph = MethodologyGraph()
        for i in range(4):
            graph.add_claim(ResearchClaim(
                claim_id=str(i), statement=f"s{i}", source="x", domain="d", confidence=0.5,
            ))
        graph.add_edge("0", "1")
        graph.add_edge("1", "2")
        graph.add_edge("2", "3")
        stats = graph.get_statistics()
        assert stats["total_claims"] == 4
        assert stats["total_edges"] == 3
        assert stats["avg_confidence"] == pytest.approx(0.5)

    def test_get_related_missing_claim(self):
        """get_related for nonexistent claim returns empty list."""
        graph = MethodologyGraph()
        assert graph.get_related("nonexistent") == []

    def test_empty_graph_statistics(self):
        """Statistics of empty graph return zero counts."""
        graph = MethodologyGraph()
        stats = graph.get_statistics()
        assert stats["total_claims"] == 0
        assert stats["total_edges"] == 0
        assert stats["avg_confidence"] == 0.0
        assert stats["domains"] == {}


# ============================================================================
# VaultHealthChecker extended tests
# ============================================================================


@pytest.mark.unit
class TestVaultHealthCheckerExtended:
    """Extended tests for VaultHealthChecker."""

    def test_healthy_vault_with_all_spaces(self, tmp_path):
        """Vault with all three space directories reports HEALTHY."""
        (tmp_path / "self").mkdir()
        (tmp_path / "notes").mkdir()
        (tmp_path / "ops").mkdir()
        checker = VaultHealthChecker()
        report = checker.check(tmp_path)
        assert report.status == HealthStatus.HEALTHY
        assert set(report.spaces_present) == {"self", "notes", "ops"}
        assert report.warnings == []
        assert report.errors == []

    def test_vault_counts_md_files(self, tmp_path):
        """Health check counts .md files recursively."""
        (tmp_path / "self").mkdir()
        (tmp_path / "notes").mkdir()
        (tmp_path / "ops").mkdir()
        # Create some markdown files
        (tmp_path / "notes" / "note1.md").write_text("# Note 1")
        (tmp_path / "notes" / "note2.md").write_text("# Note 2")
        (tmp_path / "self" / "journal.md").write_text("# Journal")
        checker = VaultHealthChecker()
        report = checker.check(tmp_path)
        assert report.total_notes == 3

    def test_partial_spaces_warning(self, tmp_path):
        """Vault with only some space directories reports WARNING."""
        (tmp_path / "self").mkdir()
        # notes and ops missing
        checker = VaultHealthChecker()
        report = checker.check(tmp_path)
        assert report.status == HealthStatus.WARNING
        assert len(report.warnings) == 2
        assert report.spaces_present == ["self"]


# ============================================================================
# ArsContextaManager extended tests
# ============================================================================


@pytest.mark.unit
class TestArsContextaManagerExtended:
    """Extended tests for ArsContextaManager."""

    def test_get_primitives_all(self):
        """get_primitives without layer returns all 15."""
        mgr = ArsContextaManager()
        prims = mgr.get_primitives()
        assert len(prims) == 15
        assert all(isinstance(p, dict) for p in prims)

    def test_get_primitives_by_layer(self):
        """get_primitives with layer filter returns only that layer."""
        mgr = ArsContextaManager()
        foundation = mgr.get_primitives(layer="foundation")
        assert len(foundation) == 5
        assert all(p["layer"] == "foundation" for p in foundation)

    def test_get_primitives_invalid_layer(self):
        """get_primitives with invalid layer returns empty list."""
        mgr = ArsContextaManager()
        result = mgr.get_primitives(layer="nonexistent")
        assert result == []

    def test_process_content_no_handlers(self):
        """process_content passes through all 6 stages when no handlers registered."""
        mgr = ArsContextaManager()
        results = mgr.process_content("raw note content")
        assert len(results) == 6
        assert all(r.success for r in results)
        assert results[-1].output_content == "raw note content"

    def test_get_methodology_stats_empty(self):
        """get_methodology_stats on fresh manager returns zeros."""
        mgr = ArsContextaManager()
        stats = mgr.get_methodology_stats()
        assert stats["total_claims"] == 0
        assert stats["total_edges"] == 0

    def test_get_config_before_setup(self):
        """get_config returns None before setup is called."""
        mgr = ArsContextaManager()
        assert mgr.get_config() is None

    def test_get_config_after_setup(self, tmp_path):
        """get_config returns VaultConfig after setup."""
        mgr = ArsContextaManager()
        mgr.setup(tmp_path / "vault")
        cfg = mgr.get_config()
        assert isinstance(cfg, VaultConfig)
        assert cfg.vault_path == tmp_path / "vault"

    def test_health_no_vault_configured(self):
        """health() with no vault path and no setup returns ERROR."""
        mgr = ArsContextaManager()
        report = mgr.health()
        assert report.status == HealthStatus.ERROR
        assert len(report.errors) >= 1

    def test_health_with_explicit_path(self, tmp_path):
        """health() with explicit path checks that path."""
        (tmp_path / "self").mkdir()
        (tmp_path / "notes").mkdir()
        (tmp_path / "ops").mkdir()
        mgr = ArsContextaManager()
        report = mgr.health(vault_path=tmp_path)
        assert report.status == HealthStatus.HEALTHY

    def test_derive_config_returns_expected_keys(self):
        """derive_config returns dict with signals, summary, overall_confidence."""
        mgr = ArsContextaManager()
        result = mgr.derive_config("I use obsidian for zettelkasten")
        assert "signals" in result
        assert "summary" in result
        assert "overall_confidence" in result
        assert isinstance(result["signals"], list)
        assert result["overall_confidence"] > 0.0


# ============================================================================
# KernelConfig extended tests
# ============================================================================


@pytest.mark.unit
class TestKernelConfigExtended:
    """Extended tests for KernelConfig dataclass methods."""

    def test_get_by_name_found(self):
        """get_by_name returns the matching primitive."""
        cfg = KernelConfig(primitives=[
            KernelPrimitive(name="alpha", layer=KernelLayer.FOUNDATION, description="A"),
            KernelPrimitive(name="beta", layer=KernelLayer.CONVENTION, description="B"),
        ])
        p = cfg.get_by_name("alpha")
        assert p is not None
        assert p.name == "alpha"

    def test_get_by_name_not_found(self):
        """get_by_name returns None when name not present."""
        cfg = KernelConfig(primitives=[
            KernelPrimitive(name="alpha", layer=KernelLayer.FOUNDATION, description="A"),
        ])
        assert cfg.get_by_name("missing") is None

    def test_get_by_layer(self):
        """get_by_layer returns only primitives of the given layer."""
        cfg = KernelConfig(primitives=[
            KernelPrimitive(name="a", layer=KernelLayer.FOUNDATION, description="A"),
            KernelPrimitive(name="b", layer=KernelLayer.CONVENTION, description="B"),
            KernelPrimitive(name="c", layer=KernelLayer.FOUNDATION, description="C"),
        ])
        foundation = cfg.get_by_layer(KernelLayer.FOUNDATION)
        assert len(foundation) == 2

    def test_validate_dependencies_with_missing(self):
        """validate_dependencies returns names of unresolved deps."""
        cfg = KernelConfig(primitives=[
            KernelPrimitive(
                name="child",
                layer=KernelLayer.AUTOMATION,
                description="C",
                dependencies=["parent-a", "parent-b"],
            ),
            KernelPrimitive(name="parent-a", layer=KernelLayer.FOUNDATION, description="PA"),
        ])
        missing = cfg.validate_dependencies()
        assert "parent-b" in missing
        assert "parent-a" not in missing

    def test_validate_dependencies_all_resolved(self):
        """validate_dependencies returns empty list when all deps resolved."""
        reg = KernelPrimitiveRegistry()
        cfg = reg.to_kernel_config()
        assert cfg.validate_dependencies() == []


# ============================================================================
# VaultConfig tests
# ============================================================================


@pytest.mark.unit
class TestVaultConfig:
    """Test VaultConfig dataclass serialization."""

    def test_to_dict_structure(self, tmp_path):
        """to_dict returns expected keys and types."""
        cfg = VaultConfig(vault_path=tmp_path / "vault")
        d = cfg.to_dict()
        assert "vault_path" in d
        assert "kernel" in d
        assert "active_spaces" in d
        assert "created_at" in d
        assert d["active_spaces"] == ["self", "notes", "ops"]

    def test_to_dict_with_primitives(self, tmp_path):
        """to_dict includes kernel primitives when populated."""
        reg = KernelPrimitiveRegistry()
        cfg = VaultConfig(
            vault_path=tmp_path,
            kernel=reg.to_kernel_config(),
        )
        d = cfg.to_dict()
        assert len(d["kernel"]["primitives"]) == 15
