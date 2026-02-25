"""Tests for cerebrum/distillation.py."""

from __future__ import annotations

from codomyrmex.cerebrum.distillation import (
    DistillationConfig,
    DistillationPipeline,
)
from codomyrmex.llm.models.reasoning import (
    Conclusion,
    ReasoningStep,
    ReasoningTrace,
    ThinkingDepth,
)


def _make_complete_trace(
    prompt: str = "test prompt",
    confidence: float = 0.7,
    steps: int = 3,
) -> ReasoningTrace:
    """Create a complete reasoning trace for testing."""
    trace = ReasoningTrace(prompt=prompt, depth=ThinkingDepth.NORMAL)
    for i in range(steps):
        trace.add_step(ReasoningStep(
            thought=f"Step {i+1} reasoning",
            confidence=confidence,
            step_type="analysis",
        ))
    trace.set_conclusion(Conclusion(
        action=f"Proceed with: {prompt}",
        justification="All steps converge",
        confidence=confidence,
    ))
    return trace


class TestDistillationConfig:
    """Test suite for DistillationConfig."""
    def test_defaults(self) -> None:
        cfg = DistillationConfig()
        assert cfg.min_confidence == 0.5
        assert cfg.min_steps == 2
        assert cfg.dedup_by_prompt is True


class TestDistillationPipeline:
    """Test suite for DistillationPipeline."""
    def test_distill_single_trace(self) -> None:
        pipeline = DistillationPipeline()
        traces = [_make_complete_trace()]
        cases = pipeline.distill(traces)
        assert len(cases) == 1
        assert cases[0].case_id.startswith("distilled-")

    def test_distill_features(self) -> None:
        pipeline = DistillationPipeline()
        traces = [_make_complete_trace(prompt="analyze module")]
        cases = pipeline.distill(traces)
        case = cases[0]
        assert case.features["prompt"] == "analyze module"
        assert case.features["step_count"] == 3
        assert "step_types" in case.features

    def test_distill_outcome(self) -> None:
        pipeline = DistillationPipeline()
        traces = [_make_complete_trace()]
        cases = pipeline.distill(traces)
        assert "action" in cases[0].outcome
        assert "justification" in cases[0].outcome

    def test_distill_context(self) -> None:
        pipeline = DistillationPipeline()
        traces = [_make_complete_trace()]
        cases = pipeline.distill(traces)
        assert "thoughts" in cases[0].context
        assert len(cases[0].context["thoughts"]) == 3

    def test_distill_skips_incomplete(self) -> None:
        pipeline = DistillationPipeline()
        trace = ReasoningTrace(prompt="incomplete")
        trace.add_step(ReasoningStep(thought="A", confidence=0.5))
        cases = pipeline.distill([trace])
        assert len(cases) == 0

    def test_distill_skips_low_confidence(self) -> None:
        pipeline = DistillationPipeline(
            config=DistillationConfig(min_confidence=0.8)
        )
        traces = [_make_complete_trace(confidence=0.3)]
        cases = pipeline.distill(traces)
        assert len(cases) == 0

    def test_distill_skips_few_steps(self) -> None:
        pipeline = DistillationPipeline(
            config=DistillationConfig(min_steps=5)
        )
        traces = [_make_complete_trace(steps=3)]
        cases = pipeline.distill(traces)
        assert len(cases) == 0

    def test_deduplication(self) -> None:
        pipeline = DistillationPipeline()
        t1 = _make_complete_trace(prompt="same prompt")
        t2 = _make_complete_trace(prompt="same prompt")
        cases = pipeline.distill([t1, t2])
        assert len(cases) == 1

    def test_dedup_disabled(self) -> None:
        pipeline = DistillationPipeline(
            config=DistillationConfig(dedup_by_prompt=False)
        )
        t1 = _make_complete_trace(prompt="same")
        t2 = _make_complete_trace(prompt="same")
        cases = pipeline.distill([t1, t2])
        assert len(cases) == 2

    def test_metadata_source(self) -> None:
        pipeline = DistillationPipeline()
        traces = [_make_complete_trace()]
        cases = pipeline.distill(traces)
        assert cases[0].metadata["source"] == "distillation"
        assert "trace_id" in cases[0].metadata


class TestBayesianInference:
    def test_distribution(self):
        from codomyrmex.cerebrum.inference.bayesian import Distribution
        d = Distribution(values=["A", "B"], probabilities=[0.3, 0.7])
        assert len(d.values) == 2

    def test_prior_builder(self):
        from codomyrmex.cerebrum.inference.bayesian import PriorBuilder
        builder = PriorBuilder()
        assert builder is not None

    def test_bayesian_network(self):
        from codomyrmex.cerebrum.inference.bayesian import BayesianNetwork
        bn = BayesianNetwork()
        assert bn is not None

    def test_inference_engine(self):
        from codomyrmex.cerebrum.inference.bayesian import (
            BayesianNetwork,
            InferenceEngine,
        )
        bn = BayesianNetwork()
        engine = InferenceEngine(network=bn)
        assert engine is not None


class TestVisualizationTheme:
    def test_color_palette(self):
        from codomyrmex.cerebrum.visualization.theme import ColorPalette
        p = ColorPalette(primary="#333", secondary="#666", accent="#0af")
        assert p.primary == "#333"

    def test_font_config(self):
        from codomyrmex.cerebrum.visualization.theme import FontConfig
        f = FontConfig(family="Arial")
        assert f.family == "Arial"

    def test_figure_config(self):
        from codomyrmex.cerebrum.visualization.theme import FigureConfig
        fc = FigureConfig(default_dpi=150)
        assert fc.default_dpi == 150

    def test_axis_config(self):
        from codomyrmex.cerebrum.visualization.theme import AxisConfig
        ac = AxisConfig(grid_alpha=0.5)
        assert ac.grid_alpha == 0.5

    def test_legend_config(self):
        from codomyrmex.cerebrum.visualization.theme import LegendConfig
        lc = LegendConfig(shadow=True, loc="upper right")
        assert lc.shadow is True


# Coverage push — cerebrum/visualization/base
class TestBaseVisualizer:
    """Tests for BaseVisualizer and theme utilities."""

    def test_get_default_theme(self):
        from codomyrmex.cerebrum.visualization.base import get_default_theme
        theme = get_default_theme()
        assert theme is not None


class TestBayesianDeep:
    """Deep tests for Bayesian inference execution paths."""

    def test_add_node_to_network(self):
        from codomyrmex.cerebrum.inference.bayesian import BayesianNetwork
        bn = BayesianNetwork()
        bn.add_node("weather", values=["rain", "no_rain"], prior=[0.3, 0.7])
        assert "weather" in bn.nodes

    def test_add_edge(self):
        from codomyrmex.cerebrum.inference.bayesian import BayesianNetwork
        bn = BayesianNetwork()
        bn.add_node("A", values=[0, 1], prior=[0.5, 0.5])
        bn.add_node("B", values=[0, 1], prior=[0.5, 0.5])
        bn.add_edge("A", "B")
        assert len(bn.edges) > 0
