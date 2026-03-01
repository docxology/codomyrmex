"""Unit tests for codomyrmex.skills.arscontexta services layer.

These tests supplement the existing test_arscontexta.py with deeper coverage
of KernelPrimitiveRegistry, ProcessingPipeline, and DerivationEngine,
imported from the package (which sources from core.py where the module-level
constants _DEFAULT_PRIMITIVES and _DIMENSION_KEYWORDS are defined).
"""

import pytest

from codomyrmex.skills.arscontexta import (
    DerivationEngine,
    KernelPrimitiveRegistry,
    ProcessingPipeline,
)
from codomyrmex.skills.arscontexta.models import (
    ConfigDimension,
    DimensionSignal,
    KernelConfig,
    KernelLayer,
    PipelineStage,
)


# ============================================================================
# KernelPrimitiveRegistry tests (from services.py)
# ============================================================================


@pytest.mark.unit
class TestServicesKernelPrimitiveRegistry:
    """Test KernelPrimitiveRegistry as exported from services.py."""

    def test_all_15_primitives_loaded(self):
        """Registry loads exactly 15 default primitives."""
        reg = KernelPrimitiveRegistry()
        assert len(reg.list_all()) == 15

    def test_foundation_layer_has_five(self):
        """Foundation layer contains 5 primitives."""
        reg = KernelPrimitiveRegistry()
        foundation = reg.list_by_layer(KernelLayer.FOUNDATION)
        assert len(foundation) == 5
        names = {p.name for p in foundation}
        assert "atomic-note" in names
        assert "unique-id" in names
        assert "plain-text" in names

    def test_convention_layer_has_five(self):
        """Convention layer contains 5 primitives."""
        reg = KernelPrimitiveRegistry()
        convention = reg.list_by_layer(KernelLayer.CONVENTION)
        assert len(convention) == 5
        names = {p.name for p in convention}
        assert "naming-convention" in names
        assert "front-matter" in names
        assert "folder-structure" in names

    def test_automation_layer_has_five(self):
        """Automation layer contains 5 primitives."""
        reg = KernelPrimitiveRegistry()
        automation = reg.list_by_layer(KernelLayer.AUTOMATION)
        assert len(automation) == 5
        names = {p.name for p in automation}
        assert "auto-backlink" in names
        assert "health-check" in names

    def test_get_nonexistent_returns_none(self):
        """Getting a nonexistent primitive returns None."""
        reg = KernelPrimitiveRegistry()
        assert reg.get("does-not-exist") is None

    def test_each_primitive_has_description(self):
        """Every primitive has a non-empty description."""
        reg = KernelPrimitiveRegistry()
        for prim in reg.list_all():
            assert prim.description, f"Primitive {prim.name} has no description"

    def test_to_kernel_config_primitives_match(self):
        """KernelConfig from registry contains the same primitives."""
        reg = KernelPrimitiveRegistry()
        cfg = reg.to_kernel_config()
        assert isinstance(cfg, KernelConfig)
        config_names = {p.name for p in cfg.primitives}
        registry_names = {p.name for p in reg.list_all()}
        assert config_names == registry_names

    def test_validate_primitive_nonexistent(self, tmp_path):
        """validate_primitive returns False for nonexistent primitive name."""
        reg = KernelPrimitiveRegistry()
        assert reg.validate_primitive("nonexistent", tmp_path) is False

    def test_validate_primitive_enabled_default(self, tmp_path):
        """validate_primitive returns True for enabled primitives (not folder-structure)."""
        reg = KernelPrimitiveRegistry()
        # atomic-note is enabled by default
        assert reg.validate_primitive("atomic-note", tmp_path) is True

    def test_validate_primitive_folder_structure_missing_dirs(self, tmp_path):
        """validate_primitive for folder-structure returns False when vault dirs missing."""
        reg = KernelPrimitiveRegistry()
        # tmp_path has no self/notes/ops subdirs
        assert reg.validate_primitive("folder-structure", tmp_path) is False

    def test_validate_primitive_folder_structure_with_dirs(self, tmp_path):
        """validate_primitive for folder-structure returns True when all vault dirs present."""
        reg = KernelPrimitiveRegistry()
        (tmp_path / "self").mkdir()
        (tmp_path / "notes").mkdir()
        (tmp_path / "ops").mkdir()
        assert reg.validate_primitive("folder-structure", tmp_path) is True


# ============================================================================
# ProcessingPipeline tests (from services.py)
# ============================================================================


@pytest.mark.unit
class TestServicesProcessingPipeline:
    """Test ProcessingPipeline as exported from services.py."""

    def test_no_handlers_passthrough(self):
        """Pipeline with no handlers passes content through all 6 stages."""
        pipe = ProcessingPipeline()
        results = pipe.process("test content")
        assert len(results) == 6
        assert all(r.success for r in results)
        assert results[-1].output_content == "test content"

    def test_multiple_handlers_same_stage(self):
        """Multiple handlers on the same stage chain in order."""
        pipe = ProcessingPipeline()

        def append_a(content: str, ctx: dict) -> str:
            return content + "A"

        def append_b(content: str, ctx: dict) -> str:
            return content + "B"

        pipe.register_handler(PipelineStage.RECORD, append_a)
        pipe.register_handler(PipelineStage.RECORD, append_b)
        results = pipe.process("x")
        assert results[0].output_content == "xAB"

    def test_handler_receives_context(self):
        """Handlers receive the context dict passed to process()."""
        pipe = ProcessingPipeline()
        captured_ctx = {}

        def capture_handler(content: str, ctx: dict) -> str:
            captured_ctx.update(ctx)
            return content

        pipe.register_handler(PipelineStage.REFLECT, capture_handler)
        pipe.process("data", context={"key": "value"})
        assert captured_ctx.get("key") == "value"

    def test_get_results_returns_copy(self):
        """get_results returns a copy of the internal results list."""
        pipe = ProcessingPipeline()
        pipe.process("hello")
        results_a = pipe.get_results()
        results_b = pipe.get_results()
        assert results_a == results_b
        assert results_a is not results_b  # Different list objects

    def test_process_single_stage_with_no_handler(self):
        """process_single_stage passes content through when no handler registered."""
        pipe = ProcessingPipeline()
        result = pipe.process_single_stage(PipelineStage.VERIFY, "unchanged")
        assert result.success is True
        assert result.output_content == "unchanged"
        assert result.duration_ms >= 0

    def test_process_single_stage_error(self):
        """process_single_stage captures handler exceptions."""
        pipe = ProcessingPipeline()

        def failing_handler(content: str, ctx: dict) -> str:
            raise RuntimeError("handler crashed")

        pipe.register_handler(PipelineStage.RETHINK, failing_handler)
        result = pipe.process_single_stage(PipelineStage.RETHINK, "input")
        assert result.success is False
        assert result.error == "handler crashed"
        assert result.input_content == "input"

    def test_pipeline_stops_on_first_error(self):
        """Pipeline stops processing after first failed stage."""
        pipe = ProcessingPipeline()

        def fail_handler(content: str, ctx: dict) -> str:
            raise ValueError("fail at record")

        pipe.register_handler(PipelineStage.RECORD, fail_handler)
        results = pipe.process("start")
        # Only the RECORD stage should be in results (it failed, pipeline stopped)
        assert len(results) == 1
        assert results[0].success is False

    def test_stage_result_has_timing(self):
        """Each StageResult has a non-negative duration_ms."""
        pipe = ProcessingPipeline()
        results = pipe.process("quick")
        for r in results:
            assert r.duration_ms >= 0


# ============================================================================
# DerivationEngine tests (from services.py)
# ============================================================================


@pytest.mark.unit
class TestServicesDerivationEngine:
    """Test DerivationEngine as exported from services.py."""

    def test_empty_engine_confidence_is_zero(self):
        """Fresh engine with no signals has 0.0 confidence."""
        engine = DerivationEngine()
        assert engine.get_overall_confidence() == 0.0

    def test_ingest_signal_appears_in_summary(self):
        """Directly ingested signal appears in dimension summary."""
        engine = DerivationEngine()
        sig = DimensionSignal(
            dimension=ConfigDimension.TOOLCHAIN,
            value="obsidian",
            confidence=0.8,
            source="test",
        )
        engine.ingest_signal(sig)
        summary = engine.get_dimension_summary()
        assert "toolchain" in summary
        assert len(summary["toolchain"]) == 1
        assert summary["toolchain"][0]["value"] == "obsidian"

    def test_ingest_from_text_matches_multiple_dimensions(self):
        """Text with multiple keywords triggers signals across dimensions."""
        engine = DerivationEngine()
        signals = engine.ingest_from_text("I use vim for daily research notes in markdown")
        dims = {s.dimension for s in signals}
        assert ConfigDimension.TOOLCHAIN in dims      # "vim"
        assert ConfigDimension.TEMPORAL_SCOPE in dims  # "daily"
        assert ConfigDimension.DOMAIN in dims          # "research"
        assert ConfigDimension.OUTPUT_FORMAT in dims   # "markdown"

    def test_ingest_from_text_case_insensitive(self):
        """Keyword matching is case-insensitive."""
        engine = DerivationEngine()
        signals = engine.ingest_from_text("OBSIDIAN and ZETTELKASTEN")
        values = {s.value for s in signals}
        assert "obsidian" in values
        assert "zettelkasten" in values

    def test_ingest_from_text_no_matches(self):
        """Text with no matching keywords returns empty list."""
        engine = DerivationEngine()
        signals = engine.ingest_from_text("completely irrelevant gibberish xyzzy")
        assert signals == []

    def test_overall_confidence_average(self):
        """Overall confidence is the average of all signal confidences."""
        engine = DerivationEngine()
        engine.ingest_signal(DimensionSignal(
            dimension=ConfigDimension.DOMAIN, value="a", confidence=0.8,
        ))
        engine.ingest_signal(DimensionSignal(
            dimension=ConfigDimension.DOMAIN, value="b", confidence=0.4,
        ))
        assert engine.get_overall_confidence() == pytest.approx(0.6)

    def test_reset_clears_all_signals(self):
        """Reset removes all ingested signals."""
        engine = DerivationEngine()
        engine.ingest_from_text("obsidian research")
        assert engine.get_overall_confidence() > 0
        engine.reset()
        assert engine.get_overall_confidence() == 0.0
        assert engine.get_dimension_summary() == {}

    def test_ingest_from_text_custom_source(self):
        """Source parameter is stored in emitted signals."""
        engine = DerivationEngine()
        signals = engine.ingest_from_text("software design", source="api")
        for sig in signals:
            assert sig.source == "api"

    def test_all_eight_dimensions_coverable(self):
        """Each of the 8 config dimensions can be triggered by keywords."""
        engine = DerivationEngine()
        # This text contains at least one keyword per dimension
        text = (
            "software zettelkasten detail daily solo markdown obsidian visual"
        )
        signals = engine.ingest_from_text(text)
        dims_found = {s.dimension for s in signals}
        assert ConfigDimension.DOMAIN in dims_found
        assert ConfigDimension.METHODOLOGY in dims_found
        assert ConfigDimension.ABSTRACTION_LEVEL in dims_found
        assert ConfigDimension.TEMPORAL_SCOPE in dims_found
        assert ConfigDimension.COLLABORATION_MODE in dims_found
        assert ConfigDimension.OUTPUT_FORMAT in dims_found
        assert ConfigDimension.TOOLCHAIN in dims_found
        assert ConfigDimension.LEARNING_STYLE in dims_found
