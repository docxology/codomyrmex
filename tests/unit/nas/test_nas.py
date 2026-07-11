"""
Unit tests for the nas (Neural Architecture Search) module.

Tests cover:
- NASSearchSpace sampling and validation
- ArchConfig properties
- NASSearcher random and evolutionary search
- History tracking
- MCP tool interface
"""

import pytest

from codomyrmex.nas import (
    ArchConfig,
    NASSearcher,
    NASSearchSpace,
    evolutionary_search,
    random_search,
)

# ---------------------------------------------------------------------------
# ArchConfig
# ---------------------------------------------------------------------------


class TestArchConfig:
    """Architecture configuration tests."""

    @pytest.mark.unit
    def test_total_params_estimate_positive(self):
        config = ArchConfig(
            n_layers=4,
            d_model=256,
            n_heads=8,
            d_ff=1024,
            dropout=0.1,
            activation="relu",
        )
        assert config.total_params_estimate > 0

    @pytest.mark.unit
    def test_total_params_scales_with_layers(self):
        base = ArchConfig(
            n_layers=2, d_model=128, n_heads=4, d_ff=512, dropout=0.0, activation="relu"
        )
        deep = ArchConfig(
            n_layers=8, d_model=128, n_heads=4, d_ff=512, dropout=0.0, activation="relu"
        )
        assert deep.total_params_estimate > base.total_params_estimate

    @pytest.mark.unit
    def test_total_params_scales_with_width(self):
        narrow = ArchConfig(
            n_layers=4, d_model=64, n_heads=2, d_ff=256, dropout=0.0, activation="relu"
        )
        wide = ArchConfig(
            n_layers=4,
            d_model=512,
            n_heads=8,
            d_ff=2048,
            dropout=0.0,
            activation="relu",
        )
        assert wide.total_params_estimate > narrow.total_params_estimate

    @pytest.mark.unit
    def test_default_params_dict(self):
        config = ArchConfig(
            n_layers=1, d_model=64, n_heads=2, d_ff=128, dropout=0.0, activation="relu"
        )
        assert config.params == {}


# ---------------------------------------------------------------------------
# NASSearchSpace
# ---------------------------------------------------------------------------


class TestNASSearchSpace:
    """Search space sampling and validation."""

    @pytest.mark.unit
    def test_sample_returns_archconfig(self):
        space = NASSearchSpace()
        config = space.sample(seed=42)
        assert isinstance(config, ArchConfig)

    @pytest.mark.unit
    def test_sample_respects_constraints(self):
        """n_heads must divide d_model."""
        space = NASSearchSpace()
        for _ in range(50):
            config = space.sample()
            assert config.d_model % config.n_heads == 0, (
                f"d_model={config.d_model} not divisible by n_heads={config.n_heads}"
            )

    @pytest.mark.unit
    def test_sample_within_space(self):
        space = NASSearchSpace()
        config = space.sample(seed=42)
        assert config.n_layers in space.n_layers
        assert config.d_model in space.d_model
        assert config.n_heads in space.n_heads
        assert config.dropout in space.dropout
        assert config.activation in space.activation

    @pytest.mark.unit
    def test_sample_deterministic_with_seed(self):
        space = NASSearchSpace()
        config1 = space.sample(seed=123)
        config2 = space.sample(seed=123)
        assert config1.n_layers == config2.n_layers
        assert config1.d_model == config2.d_model

    @pytest.mark.unit
    def test_validate_valid_config(self):
        space = NASSearchSpace()
        config = space.sample(seed=42)
        assert space.validate(config) is True

    @pytest.mark.unit
    def test_validate_invalid_n_layers(self):
        space = NASSearchSpace()
        config = ArchConfig(
            n_layers=99,
            d_model=128,
            n_heads=4,
            d_ff=512,
            dropout=0.1,
            activation="relu",
        )
        assert space.validate(config) is False

    @pytest.mark.unit
    def test_validate_invalid_dropout(self):
        space = NASSearchSpace()
        config = ArchConfig(
            n_layers=4, d_model=128, n_heads=4, d_ff=512, dropout=1.5, activation="relu"
        )
        assert space.validate(config) is False

    @pytest.mark.unit
    def test_custom_search_space(self):
        space = NASSearchSpace(
            n_layers=[1, 2],
            d_model=[32, 64],
            n_heads=[2],
            d_ff_multiplier=[4],
            dropout=[0.0],
            activation=["gelu"],
        )
        config = space.sample(seed=42)
        assert config.n_layers in [1, 2]
        assert config.d_model in [32, 64]
        assert config.activation == "gelu"


# ---------------------------------------------------------------------------
# NASSearcher
# ---------------------------------------------------------------------------


class TestNASSearcher:
    """Searcher random and evolutionary strategies."""

    @pytest.fixture
    def simple_eval_fn(self):
        """Evaluation function that prefers more layers."""

        def eval_fn(config: ArchConfig) -> float:
            return float(config.n_layers)

        return eval_fn

    @pytest.mark.unit
    def test_random_search_returns_config(self, simple_eval_fn):
        space = NASSearchSpace()
        searcher = NASSearcher(space, simple_eval_fn)
        best = searcher.random_search(n_trials=10, seed=42)
        assert isinstance(best, ArchConfig)

    @pytest.mark.unit
    def test_random_search_history_tracked(self, simple_eval_fn):
        space = NASSearchSpace()
        searcher = NASSearcher(space, simple_eval_fn)
        searcher.random_search(n_trials=15, seed=42)
        assert len(searcher.history) == 15

    @pytest.mark.unit
    def test_evolutionary_search_returns_config(self, simple_eval_fn):
        space = NASSearchSpace()
        searcher = NASSearcher(space, simple_eval_fn)
        best = searcher.evolutionary_search(n_generations=3, population_size=6, seed=42)
        assert isinstance(best, ArchConfig)

    @pytest.mark.unit
    def test_evolutionary_search_improves(self):
        """Best score after evolution should be >= first generation average."""
        space = NASSearchSpace()

        def eval_fn(config: ArchConfig) -> float:
            return float(config.n_layers * config.d_model)

        searcher = NASSearcher(space, eval_fn)
        searcher.evolutionary_search(n_generations=5, population_size=10, seed=42)

        # Get first generation scores and last generation best
        first_gen_scores = [s for _, s in searcher.history[:10]]
        first_gen_best = max(first_gen_scores)
        _overall_best_config, overall_best_score = searcher.best()

        assert overall_best_score >= first_gen_best

    @pytest.mark.unit
    def test_history_tracked(self, simple_eval_fn):
        space = NASSearchSpace()
        searcher = NASSearcher(space, simple_eval_fn)
        searcher.random_search(n_trials=5, seed=42)
        searcher.evolutionary_search(n_generations=2, population_size=4, seed=42)
        # history should contain entries from both searches
        assert len(searcher.history) > 5

    @pytest.mark.unit
    def test_best_raises_on_empty(self, simple_eval_fn):
        space = NASSearchSpace()
        searcher = NASSearcher(space, simple_eval_fn)
        with pytest.raises(RuntimeError, match="No search history"):
            searcher.best()

    @pytest.mark.unit
    def test_best_returns_max_score(self, simple_eval_fn):
        space = NASSearchSpace()
        searcher = NASSearcher(space, simple_eval_fn)
        searcher.random_search(n_trials=20, seed=42)
        _best_config, best_score = searcher.best()
        all_scores = [s for _, s in searcher.history]
        assert best_score == max(all_scores)


# ---------------------------------------------------------------------------
# Convenience Functions
# ---------------------------------------------------------------------------


class TestConvenienceFunctions:
    """Top-level random_search and evolutionary_search functions."""

    @pytest.mark.unit
    def test_random_search_function(self):
        space = NASSearchSpace()
        result = random_search(space, lambda c: float(c.n_layers), n_trials=10)
        assert isinstance(result, ArchConfig)

    @pytest.mark.unit
    def test_evolutionary_search_function(self):
        space = NASSearchSpace()
        result = evolutionary_search(
            space, lambda c: float(c.d_model), n_generations=3, population_size=6
        )
        assert isinstance(result, ArchConfig)


# ---------------------------------------------------------------------------
# Mutation
# ---------------------------------------------------------------------------


class TestMutation:
    """Mutation operator tests."""

    @pytest.mark.unit
    def test_mutate_produces_valid_config(self):
        """Mutated configs should still have valid head/model divisibility."""
        space = NASSearchSpace()

        def eval_fn(c):
            return 1.0

        searcher = NASSearcher(space, eval_fn)
        parent = space.sample(seed=42)
        for _ in range(50):
            child = searcher._mutate(parent)
            assert child.d_model % child.n_heads == 0

    @pytest.mark.unit
    def test_mutate_changes_something(self):
        """At least one dimension should differ after mutation (usually)."""
        space = NASSearchSpace()

        def eval_fn(c):
            return 1.0

        searcher = NASSearcher(space, eval_fn)
        parent = space.sample(seed=42)
        # Run many mutations; at least some should differ
        changed = False
        for _ in range(20):
            child = searcher._mutate(parent)
            if (
                child.n_layers != parent.n_layers
                or child.d_model != parent.d_model
                or child.dropout != parent.dropout
                or child.activation != parent.activation
            ):
                changed = True
                break
        assert changed


# ---------------------------------------------------------------------------
# MCP Tools
# ---------------------------------------------------------------------------


class TestMCPTools:
    """MCP tool interface tests."""

    @pytest.mark.unit
    def test_sample_architecture_tool(self):
        from codomyrmex.nas.mcp_tools import nas_sample_architecture

        result = nas_sample_architecture(seed=42)
        assert "n_layers" in result
        assert "d_model" in result
        assert "total_params_estimate" in result
        assert result["d_model"] % result["n_heads"] == 0

    @pytest.mark.unit
    def test_random_search_tool(self):
        from codomyrmex.nas.mcp_tools import nas_random_search

        result = nas_random_search(n_trials=10, seed=42)
        assert "best_config" in result
        assert "best_score" in result
        assert "total_evaluated" in result
        assert result["total_evaluated"] == 10
