"""Tests for the arscontexta skills submodule."""

import shutil
import tempfile
from pathlib import Path

import pytest

from codomyrmex.skills.arscontexta import (
    ArsContextaError,
    ArsContextaManager,
    ConfigDimension,
    DerivationEngine,
    DimensionSignal,
    HealthStatus,
    KernelConfig,
    KernelLayer,
    KernelPrimitive,
    KernelPrimitiveRegistry,
    MethodologyGraph,
    PipelineError,
    PipelineStage,
    PrimitiveValidationError,
    ProcessingPipeline,
    ResearchClaim,
    SkillType,
    StageResult,
    VaultConfig,
    VaultHealthChecker,
    VaultHealthReport,
    VaultNotFoundError,
    VaultSpace,
)


# ============================================================================
# Enum tests (5)
# ============================================================================


@pytest.mark.unit
class TestEnums:
    """Test all 6 enum classes."""

    def test_vault_space_values(self):
        """Test functionality: vault space values."""
        assert VaultSpace.SELF.value == "self"
        assert VaultSpace.NOTES.value == "notes"
        assert VaultSpace.OPS.value == "ops"
        assert len(VaultSpace) == 3

    def test_kernel_layer_values(self):
        """Test functionality: kernel layer values."""
        assert KernelLayer.FOUNDATION.value == "foundation"
        assert KernelLayer.CONVENTION.value == "convention"
        assert KernelLayer.AUTOMATION.value == "automation"
        assert len(KernelLayer) == 3

    def test_pipeline_stage_values(self):
        """Test functionality: pipeline stage values."""
        stages = [s.value for s in PipelineStage]
        assert stages == ["record", "reduce", "reflect", "reweave", "verify", "rethink"]
        assert len(PipelineStage) == 6

    def test_config_dimension_values(self):
        """Test functionality: config dimension values."""
        assert ConfigDimension.DOMAIN.value == "domain"
        assert ConfigDimension.TOOLCHAIN.value == "toolchain"
        assert ConfigDimension.LEARNING_STYLE.value == "learning_style"
        assert len(ConfigDimension) == 8

    def test_health_and_skill_type_values(self):
        """Test functionality: health and skill type values."""
        assert HealthStatus.HEALTHY.value == "healthy"
        assert HealthStatus.ERROR.value == "error"
        assert SkillType.PLUGIN.value == "plugin"
        assert SkillType.GENERATED.value == "generated"
        assert SkillType.HOOK.value == "hook"


# ============================================================================
# Dataclass serialization tests (5)
# ============================================================================


@pytest.mark.unit
class TestDataclasses:
    """Test to_dict() for all serializable dataclasses."""

    def test_kernel_primitive_to_dict(self):
        """Test functionality: kernel primitive to dict."""
        p = KernelPrimitive(
            name="atomic-note",
            layer=KernelLayer.FOUNDATION,
            description="Single-concept note",
            dependencies=["unique-id"],
        )
        d = p.to_dict()
        assert d["name"] == "atomic-note"
        assert d["layer"] == "foundation"
        assert d["dependencies"] == ["unique-id"]
        assert d["enabled"] is True

    def test_research_claim_to_dict(self):
        """Test functionality: research claim to dict."""
        c = ResearchClaim(
            claim_id="RC-001",
            statement="Spaced repetition improves retention",
            source="Ebbinghaus 1885",
            domain="cognitive-science",
            connected_primitives=["timestamping"],
            confidence=0.95,
        )
        d = c.to_dict()
        assert d["claim_id"] == "RC-001"
        assert d["confidence"] == 0.95
        assert "timestamping" in d["connected_primitives"]

    def test_dimension_signal_to_dict(self):
        """Test functionality: dimension signal to dict."""
        s = DimensionSignal(
            dimension=ConfigDimension.DOMAIN,
            value="software-engineering",
            confidence=0.8,
            source="user",
        )
        d = s.to_dict()
        assert d["dimension"] == "domain"
        assert d["value"] == "software-engineering"
        assert "timestamp" in d

    def test_stage_result_to_dict(self):
        """Test functionality: stage result to dict."""
        r = StageResult(
            stage=PipelineStage.RECORD,
            input_content="raw",
            output_content="processed",
            duration_ms=12.5,
        )
        d = r.to_dict()
        assert d["stage"] == "record"
        assert d["success"] is True
        assert d["duration_ms"] == 12.5

    def test_vault_health_report_to_dict(self):
        """Test functionality: vault health report to dict."""
        rpt = VaultHealthReport(
            status=HealthStatus.WARNING,
            spaces_present=["self", "notes"],
            warnings=["Missing space directory: ops"],
        )
        d = rpt.to_dict()
        assert d["status"] == "warning"
        assert len(d["spaces_present"]) == 2
        assert len(d["warnings"]) == 1


# ============================================================================
# KernelPrimitiveRegistry tests (5)
# ============================================================================


@pytest.mark.unit
class TestKernelPrimitiveRegistry:
    """Test the kernel primitive registry."""

    def test_default_primitives_loaded(self):
        """Test functionality: default primitives loaded."""
        reg = KernelPrimitiveRegistry()
        assert len(reg.list_all()) == 15

    def test_get_by_name(self):
        """Test functionality: get by name."""
        reg = KernelPrimitiveRegistry()
        p = reg.get("atomic-note")
        assert p is not None
        assert p.layer == KernelLayer.FOUNDATION
        assert reg.get("nonexistent") is None

    def test_list_by_layer(self):
        """Test functionality: list by layer."""
        reg = KernelPrimitiveRegistry()
        foundation = reg.list_by_layer(KernelLayer.FOUNDATION)
        assert len(foundation) == 5
        convention = reg.list_by_layer(KernelLayer.CONVENTION)
        assert len(convention) == 5
        automation = reg.list_by_layer(KernelLayer.AUTOMATION)
        assert len(automation) == 5

    def test_to_kernel_config(self):
        """Test functionality: to kernel config."""
        reg = KernelPrimitiveRegistry()
        cfg = reg.to_kernel_config()
        assert isinstance(cfg, KernelConfig)
        assert len(cfg.primitives) == 15
        assert cfg.get_by_name("link-syntax") is not None

    def test_validate_dependencies(self):
        """Test functionality: validate dependencies."""
        reg = KernelPrimitiveRegistry()
        cfg = reg.to_kernel_config()
        missing = cfg.validate_dependencies()
        assert missing == [], f"Unexpected unresolved deps: {missing}"


# ============================================================================
# ProcessingPipeline tests (4)
# ============================================================================


@pytest.mark.unit
class TestProcessingPipeline:
    """Test the 6R processing pipeline."""

    def test_passthrough_no_handlers(self):
        """Test functionality: passthrough no handlers."""
        pipe = ProcessingPipeline()
        results = pipe.process("hello world")
        assert len(results) == 6
        for r in results:
            assert r.success is True
        # With no handlers, output equals input at each stage
        assert results[-1].output_content == "hello world"

    def test_handler_registration_and_execution(self):
        """Test functionality: handler registration and execution."""
        pipe = ProcessingPipeline()

        def upper_handler(content: str, ctx: dict) -> str:
            return content.upper()

        pipe.register_handler(PipelineStage.RECORD, upper_handler)
        results = pipe.process("hello")
        # After RECORD stage, content should be uppercased
        assert results[0].output_content == "HELLO"
        # Subsequent stages pass through the uppercased content
        assert results[-1].output_content == "HELLO"

    def test_error_handling(self):
        """Test functionality: error handling."""
        pipe = ProcessingPipeline()

        def bad_handler(content: str, ctx: dict) -> str:
            raise ValueError("boom")

        pipe.register_handler(PipelineStage.REDUCE, bad_handler)
        results = pipe.process("test")
        # RECORD succeeds (no handler), REDUCE fails
        assert results[0].success is True
        assert results[1].success is False
        assert results[1].error == "boom"
        # Pipeline stops after failure
        assert len(results) == 2

    def test_single_stage_processing(self):
        """Test functionality: single stage processing."""
        pipe = ProcessingPipeline()

        def exclaim(content: str, ctx: dict) -> str:
            return content + "!"

        pipe.register_handler(PipelineStage.REFLECT, exclaim)
        result = pipe.process_single_stage(PipelineStage.REFLECT, "wow")
        assert result.success is True
        assert result.output_content == "wow!"
        assert result.stage == PipelineStage.REFLECT


# ============================================================================
# DerivationEngine tests (4)
# ============================================================================


@pytest.mark.unit
class TestDerivationEngine:
    """Test the derivation engine."""

    def test_signal_ingestion(self):
        """Test functionality: signal ingestion."""
        engine = DerivationEngine()
        sig = DimensionSignal(
            dimension=ConfigDimension.DOMAIN,
            value="science",
            confidence=0.9,
        )
        engine.ingest_signal(sig)
        summary = engine.get_dimension_summary()
        assert "domain" in summary
        assert len(summary["domain"]) == 1

    def test_text_keyword_extraction(self):
        """Test functionality: text keyword extraction."""
        engine = DerivationEngine()
        signals = engine.ingest_from_text("I use obsidian for zettelkasten research notes")
        # Should match: obsidian (toolchain), zettelkasten (methodology), research (domain)
        dimensions_found = {s.dimension for s in signals}
        assert ConfigDimension.TOOLCHAIN in dimensions_found
        assert ConfigDimension.METHODOLOGY in dimensions_found
        assert ConfigDimension.DOMAIN in dimensions_found

    def test_dimension_summary(self):
        """Test functionality: dimension summary."""
        engine = DerivationEngine()
        engine.ingest_from_text("software design overview")
        summary = engine.get_dimension_summary()
        # "software" -> domain, "design" -> domain, "overview" -> abstraction_level
        assert len(summary) >= 1

    def test_overall_confidence_and_reset(self):
        """Test functionality: overall confidence and reset."""
        engine = DerivationEngine()
        assert engine.get_overall_confidence() == 0.0
        engine.ingest_from_text("obsidian zettelkasten")
        conf = engine.get_overall_confidence()
        assert conf > 0.0
        engine.reset()
        assert engine.get_overall_confidence() == 0.0


# ============================================================================
# MethodologyGraph tests (3)
# ============================================================================


@pytest.mark.unit
class TestMethodologyGraph:
    """Test the methodology graph."""

    def test_add_and_retrieve_claims(self):
        """Test functionality: add and retrieve claims."""
        graph = MethodologyGraph()
        c1 = ResearchClaim(
            claim_id="RC-001",
            statement="Spaced repetition aids memory",
            source="Ebbinghaus",
            domain="cognitive-science",
        )
        c2 = ResearchClaim(
            claim_id="RC-002",
            statement="Atomic notes reduce cognitive load",
            source="Ahrens 2017",
            domain="knowledge-management",
        )
        graph.add_claim(c1)
        graph.add_claim(c2)
        assert graph.count() == 2
        assert graph.get_claim("RC-001") is c1
        assert graph.get_claim("nonexistent") is None

    def test_edges_and_related(self):
        """Test functionality: edges and related."""
        graph = MethodologyGraph()
        c1 = ResearchClaim(claim_id="A", statement="A", source="x", domain="d")
        c2 = ResearchClaim(claim_id="B", statement="B", source="x", domain="d")
        c3 = ResearchClaim(claim_id="C", statement="C", source="x", domain="d")
        graph.add_claim(c1)
        graph.add_claim(c2)
        graph.add_claim(c3)
        graph.add_edge("A", "B")
        graph.add_edge("A", "C")
        related = graph.get_related("A")
        related_ids = {r.claim_id for r in related}
        assert related_ids == {"B", "C"}
        # Bidirectional
        assert len(graph.get_related("B")) == 1
        assert graph.get_related("B")[0].claim_id == "A"

    def test_get_by_primitive_and_statistics(self):
        """Test functionality: get by primitive and statistics."""
        graph = MethodologyGraph()
        c1 = ResearchClaim(
            claim_id="RC-1",
            statement="S1",
            source="src",
            domain="d1",
            connected_primitives=["atomic-note"],
            confidence=0.9,
        )
        c2 = ResearchClaim(
            claim_id="RC-2",
            statement="S2",
            source="src",
            domain="d2",
            connected_primitives=["link-syntax"],
            confidence=0.7,
        )
        graph.add_claim(c1)
        graph.add_claim(c2)
        by_prim = graph.get_by_primitive("atomic-note")
        assert len(by_prim) == 1
        assert by_prim[0].claim_id == "RC-1"

        stats = graph.get_statistics()
        assert stats["total_claims"] == 2
        assert stats["avg_confidence"] == pytest.approx(0.8)
        assert "d1" in stats["domains"]


# ============================================================================
# VaultHealthChecker tests (2)
# ============================================================================


@pytest.mark.unit
class TestVaultHealthChecker:
    """Test vault health diagnostics."""

    def test_missing_vault_returns_error(self):
        """Test functionality: missing vault returns error."""
        checker = VaultHealthChecker()
        report = checker.check(Path("/nonexistent/vault/path"))
        assert report.status == HealthStatus.ERROR
        assert len(report.errors) >= 1

    def test_empty_vault_returns_warning(self):
        """Test functionality: empty vault returns warning."""
        checker = VaultHealthChecker()
        tmp = Path(tempfile.mkdtemp())
        try:
            report = checker.check(tmp)
            # Directory exists but no space subdirs
            assert report.status == HealthStatus.WARNING
            assert len(report.warnings) == 3  # self, notes, ops missing
            assert report.spaces_present == []
        finally:
            shutil.rmtree(tmp)


# ============================================================================
# ArsContextaManager tests (3)
# ============================================================================


@pytest.mark.unit
class TestArsContextaManager:
    """Test the orchestrator."""

    def test_setup_creates_config(self):
        """Test functionality: setup creates config."""
        tmp = Path(tempfile.mkdtemp())
        try:
            mgr = ArsContextaManager()
            cfg = mgr.setup(tmp / "vault")
            assert isinstance(cfg, VaultConfig)
            assert (tmp / "vault" / "self").is_dir()
            assert (tmp / "vault" / "notes").is_dir()
            assert (tmp / "vault" / "ops").is_dir()
            assert len(cfg.kernel.primitives) == 15
        finally:
            shutil.rmtree(tmp)

    def test_health_on_temp_vault(self):
        """Test functionality: health on temp vault."""
        tmp = Path(tempfile.mkdtemp())
        try:
            mgr = ArsContextaManager()
            mgr.setup(tmp / "vault")
            report = mgr.health()
            assert report.status == HealthStatus.HEALTHY
            assert set(report.spaces_present) == {"self", "notes", "ops"}
        finally:
            shutil.rmtree(tmp)

    def test_derive_config(self):
        """Test functionality: derive config."""
        mgr = ArsContextaManager()
        result = mgr.derive_config("I use obsidian for zettelkasten research")
        assert "signals" in result
        assert "summary" in result
        assert "overall_confidence" in result
        assert result["overall_confidence"] > 0.0


# ============================================================================
# Exception hierarchy test (1 — bonus, keeps total at 30 with class grouping)
# ============================================================================


@pytest.mark.unit
def test_exception_hierarchy():
    """Verify exception inheritance chain."""
    assert issubclass(VaultNotFoundError, ArsContextaError)
    assert issubclass(PrimitiveValidationError, ArsContextaError)
    assert issubclass(PipelineError, ArsContextaError)
    assert issubclass(ArsContextaError, Exception)
