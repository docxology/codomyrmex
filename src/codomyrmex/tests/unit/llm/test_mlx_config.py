"""Comprehensive tests for MLXConfig, MLXConfigPresets, and model recommendations.

All tests are pure logic — they run without mlx or mlx-lm installed.
"""

import pytest

# ===========================================================================
# 1. MLXConfig defaults
# ===========================================================================


@pytest.mark.unit
class TestMLXConfigDefaults:
    """Default values match the documented specification."""

    def test_default_model(self):
        from codomyrmex.llm.mlx.config import MLXConfig

        cfg = MLXConfig()
        assert cfg.model == "mlx-community/Llama-3.2-3B-Instruct-4bit"

    def test_default_temperature(self):
        from codomyrmex.llm.mlx.config import MLXConfig

        cfg = MLXConfig()
        assert cfg.temperature == 0.7

    def test_default_max_tokens(self):
        from codomyrmex.llm.mlx.config import MLXConfig

        cfg = MLXConfig()
        assert cfg.max_tokens == 1000

    def test_default_top_p(self):
        from codomyrmex.llm.mlx.config import MLXConfig

        cfg = MLXConfig()
        assert cfg.top_p == 0.9

    def test_default_repetition_penalty(self):
        from codomyrmex.llm.mlx.config import MLXConfig

        cfg = MLXConfig()
        assert cfg.repetition_penalty == 1.1

    def test_default_max_kv_size_none(self):
        from codomyrmex.llm.mlx.config import MLXConfig

        cfg = MLXConfig()
        assert cfg.max_kv_size is None

    def test_default_seed_none(self):
        from codomyrmex.llm.mlx.config import MLXConfig

        cfg = MLXConfig()
        assert cfg.seed is None

    def test_default_cache_dir_uses_home(self):
        from codomyrmex.llm.mlx.config import MLXConfig

        cfg = MLXConfig()
        assert ".cache" in cfg.cache_dir
        assert "mlx-models" in cfg.cache_dir


# ===========================================================================
# 2. MLXConfig programmatic overrides
# ===========================================================================


@pytest.mark.unit
class TestMLXConfigOverrides:
    """Programmatic arguments override defaults."""

    def test_custom_model(self):
        from codomyrmex.llm.mlx.config import MLXConfig

        cfg = MLXConfig(model="mlx-community/Mistral-7B-Instruct-v0.3-4bit")
        assert "Mistral" in cfg.model

    def test_custom_temperature(self):
        from codomyrmex.llm.mlx.config import MLXConfig

        cfg = MLXConfig(temperature=0.3)
        assert cfg.temperature == 0.3

    def test_custom_max_tokens(self):
        from codomyrmex.llm.mlx.config import MLXConfig

        cfg = MLXConfig(max_tokens=2000)
        assert cfg.max_tokens == 2000

    def test_custom_seed(self):
        from codomyrmex.llm.mlx.config import MLXConfig

        cfg = MLXConfig(seed=42)
        assert cfg.seed == 42

    def test_custom_max_kv_size(self):
        from codomyrmex.llm.mlx.config import MLXConfig

        cfg = MLXConfig(max_kv_size=4096)
        assert cfg.max_kv_size == 4096


# ===========================================================================
# 3. MLXConfig environment variable overrides
# ===========================================================================


@pytest.mark.unit
class TestMLXConfigEnvVars:
    """Environment variables override defaults when no programmatic value given."""

    def test_env_model(self, monkeypatch):
        from codomyrmex.llm.mlx.config import MLXConfig

        monkeypatch.setenv("MLX_MODEL", "test/model")
        cfg = MLXConfig()
        assert cfg.model == "test/model"

    def test_env_temperature(self, monkeypatch):
        from codomyrmex.llm.mlx.config import MLXConfig

        monkeypatch.setenv("MLX_TEMPERATURE", "0.42")
        cfg = MLXConfig()
        assert cfg.temperature == 0.42

    def test_env_max_tokens(self, monkeypatch):
        from codomyrmex.llm.mlx.config import MLXConfig

        monkeypatch.setenv("MLX_MAX_TOKENS", "512")
        cfg = MLXConfig()
        assert cfg.max_tokens == 512

    def test_env_max_kv_size(self, monkeypatch):
        from codomyrmex.llm.mlx.config import MLXConfig

        monkeypatch.setenv("MLX_MAX_KV_SIZE", "8192")
        cfg = MLXConfig()
        assert cfg.max_kv_size == 8192

    def test_invalid_env_float_falls_back(self, monkeypatch):
        from codomyrmex.llm.mlx.config import MLXConfig

        monkeypatch.setenv("MLX_TEMPERATURE", "not_a_number")
        cfg = MLXConfig()
        # Falls back to default 0.7
        assert cfg.temperature == 0.7


# ===========================================================================
# 4. MLXConfig validation
# ===========================================================================


@pytest.mark.unit
class TestMLXConfigValidation:
    """validate() catches out-of-range values."""

    def test_valid_default_config(self):
        from codomyrmex.llm.mlx.config import MLXConfig

        cfg = MLXConfig()
        result = cfg.validate()
        assert result["valid"] is True
        assert len(result["errors"]) == 0

    def test_invalid_temperature_high(self):
        from codomyrmex.llm.mlx.config import MLXConfig

        cfg = MLXConfig(temperature=3.0)
        result = cfg.validate()
        assert result["valid"] is False
        assert any("temperature" in e for e in result["errors"])

    def test_invalid_max_tokens_zero(self):
        from codomyrmex.llm.mlx.config import MLXConfig

        cfg = MLXConfig(max_tokens=-1)
        result = cfg.validate()
        assert result["valid"] is False
        assert any("max_tokens" in e for e in result["errors"])

    def test_invalid_top_p_over_one(self):
        from codomyrmex.llm.mlx.config import MLXConfig

        cfg = MLXConfig(top_p=1.5)
        result = cfg.validate()
        assert result["valid"] is False
        assert any("top_p" in e for e in result["errors"])

    def test_invalid_repetition_penalty_below_one(self):
        from codomyrmex.llm.mlx.config import MLXConfig

        cfg = MLXConfig(repetition_penalty=0.5)
        result = cfg.validate()
        assert result["valid"] is False
        assert any("repetition_penalty" in e for e in result["errors"])

    def test_empty_model_invalid(self):
        from codomyrmex.llm.mlx.config import MLXConfig

        cfg = MLXConfig(model="definitely-not-empty")
        cfg.model = ""
        result = cfg.validate()
        assert result["valid"] is False


# ===========================================================================
# 5. MLXConfig serialisation
# ===========================================================================


@pytest.mark.unit
class TestMLXConfigSerialisation:
    """to_dict and get_generation_kwargs produce correct output."""

    def test_to_dict_keys(self):
        from codomyrmex.llm.mlx.config import MLXConfig

        cfg = MLXConfig()
        d = cfg.to_dict()
        expected_keys = {
            "model",
            "temperature",
            "max_tokens",
            "top_p",
            "repetition_penalty",
            "max_kv_size",
            "cache_dir",
            "seed",
        }
        assert set(d.keys()) == expected_keys

    def test_generation_kwargs_maps_temp(self):
        from codomyrmex.llm.mlx.config import MLXConfig

        cfg = MLXConfig(temperature=0.3)
        kwargs = cfg.get_generation_kwargs()
        assert kwargs["temp"] == 0.3

    def test_generation_kwargs_includes_seed(self):
        from codomyrmex.llm.mlx.config import MLXConfig

        cfg = MLXConfig(seed=99)
        kwargs = cfg.get_generation_kwargs()
        assert kwargs["seed"] == 99

    def test_generation_kwargs_omits_seed_when_none(self):
        from codomyrmex.llm.mlx.config import MLXConfig

        cfg = MLXConfig()
        kwargs = cfg.get_generation_kwargs()
        assert "seed" not in kwargs


# ===========================================================================
# 6. MLXConfigPresets
# ===========================================================================


@pytest.mark.unit
class TestMLXConfigPresets:
    """Pre-built configs have expected characteristics."""

    def test_creative_high_temperature(self):
        from codomyrmex.llm.mlx.config import MLXConfigPresets

        cfg = MLXConfigPresets.creative()
        assert cfg.temperature >= 0.8

    def test_precise_low_temperature(self):
        from codomyrmex.llm.mlx.config import MLXConfigPresets

        cfg = MLXConfigPresets.precise()
        assert cfg.temperature <= 0.2

    def test_fast_short_output(self):
        from codomyrmex.llm.mlx.config import MLXConfigPresets

        cfg = MLXConfigPresets.fast()
        assert cfg.max_tokens <= 300

    def test_comprehensive_long_output(self):
        from codomyrmex.llm.mlx.config import MLXConfigPresets

        cfg = MLXConfigPresets.comprehensive()
        assert cfg.max_tokens >= 1500

    def test_coding_low_temperature(self):
        from codomyrmex.llm.mlx.config import MLXConfigPresets

        cfg = MLXConfigPresets.coding()
        assert cfg.temperature <= 0.3

    def test_all_presets_validate(self):
        from codomyrmex.llm.mlx.config import MLXConfigPresets

        for name in ["creative", "precise", "fast", "comprehensive", "coding"]:
            cfg = getattr(MLXConfigPresets, name)()
            result = cfg.validate()
            assert result["valid"] is True, f"Preset {name} failed: {result['errors']}"


# ===========================================================================
# 7. Model recommendations
# ===========================================================================


@pytest.mark.unit
class TestModelRecommendations:
    """RAM-tier model filtering."""

    def test_8gb_returns_small_models(self):
        from codomyrmex.llm.mlx.config import get_models_for_ram

        models = get_models_for_ram(8)
        assert len(models) >= 1
        assert all(m.min_ram_gb <= 8 for m in models)

    def test_16gb_returns_more_models(self):
        from codomyrmex.llm.mlx.config import get_models_for_ram

        models_8 = get_models_for_ram(8)
        models_16 = get_models_for_ram(16)
        assert len(models_16) >= len(models_8)

    def test_0gb_returns_empty(self):
        from codomyrmex.llm.mlx.config import get_models_for_ram

        models = get_models_for_ram(0)
        assert len(models) == 0

    def test_recommendations_have_repo_ids(self):
        from codomyrmex.llm.mlx.config import RECOMMENDED_MODELS

        for rec in RECOMMENDED_MODELS:
            assert "/" in rec.repo_id, f"Missing org/repo: {rec.repo_id}"
            assert rec.label
            assert rec.min_ram_gb >= 1


# ===========================================================================
# 8. Singleton accessor
# ===========================================================================


@pytest.mark.unit
class TestMLXConfigSingleton:
    """Global config singleton get/set/reset."""

    def test_get_returns_config(self):
        from codomyrmex.llm.mlx.config import get_mlx_config, reset_mlx_config

        reset_mlx_config()
        cfg = get_mlx_config()
        assert cfg is not None
        assert cfg.model

    def test_set_replaces(self):
        from codomyrmex.llm.mlx.config import (
            MLXConfig,
            get_mlx_config,
            reset_mlx_config,
            set_mlx_config,
        )

        reset_mlx_config()
        custom = MLXConfig(model="test/custom")
        set_mlx_config(custom)
        assert get_mlx_config().model == "test/custom"
        reset_mlx_config()

    def test_reset_clears(self):
        from codomyrmex.llm.mlx.config import (
            MLXConfig,
            get_mlx_config,
            reset_mlx_config,
            set_mlx_config,
        )

        set_mlx_config(MLXConfig(model="temporary"))
        reset_mlx_config()
        cfg = get_mlx_config()
        assert cfg.model != "temporary"
        reset_mlx_config()
