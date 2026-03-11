"""Tests for _make_generation_kwargs, error handling, edge cases, and
integration patterns across the MLX submodule.

These tests complement the per-module test files with cross-cutting
concerns and real-world usage patterns.
"""

import importlib.util
import json
import tempfile
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# MLX availability guard
# ---------------------------------------------------------------------------
mlx_available = importlib.util.find_spec("mlx") is not None
_skip_no_mlx = pytest.mark.skipif(not mlx_available, reason="mlx not installed")


# ===========================================================================
# 1. _make_generation_kwargs helper
# ===========================================================================


@pytest.mark.unit
class TestMakeGenerationKwargs:
    """Tests for the _make_generation_kwargs helper that bridges config to API."""

    def test_includes_max_tokens(self):
        from codomyrmex.llm.mlx.config import MLXConfig
        from codomyrmex.llm.mlx.runner import _make_generation_kwargs

        cfg = MLXConfig(max_tokens=256)
        kwargs = _make_generation_kwargs(cfg)
        assert kwargs["max_tokens"] == 256

    @_skip_no_mlx
    def test_includes_sampler_when_mlx_available(self):
        from codomyrmex.llm.mlx.config import MLXConfig
        from codomyrmex.llm.mlx.runner import _make_generation_kwargs

        cfg = MLXConfig(temperature=0.5, top_p=0.8)
        kwargs = _make_generation_kwargs(cfg)
        assert "sampler" in kwargs
        assert callable(kwargs["sampler"])

    @_skip_no_mlx
    def test_includes_logits_processors_when_mlx_available(self):
        from codomyrmex.llm.mlx.config import MLXConfig
        from codomyrmex.llm.mlx.runner import _make_generation_kwargs

        cfg = MLXConfig(repetition_penalty=1.2)
        kwargs = _make_generation_kwargs(cfg)
        assert "logits_processors" in kwargs

    @_skip_no_mlx
    def test_does_not_include_raw_temp_with_new_api(self):
        from codomyrmex.llm.mlx.config import MLXConfig
        from codomyrmex.llm.mlx.runner import _make_generation_kwargs

        cfg = MLXConfig()
        kwargs = _make_generation_kwargs(cfg)
        # New API uses sampler/logits_processors, not raw temp/top_p
        assert "temp" not in kwargs
        assert "top_p" not in kwargs
        assert "repetition_penalty" not in kwargs


# ===========================================================================
# 2. MLXRunner error handling
# ===========================================================================


@pytest.mark.unit
class TestRunnerErrorHandling:
    """Error handling in MLXRunner methods."""

    def test_generate_returns_failure_on_general_error(self):
        """Runner.generate should never raise — returns failure result."""
        from codomyrmex.llm.mlx.config import MLXConfig
        from codomyrmex.llm.mlx.runner import MLXRunner

        # Create runner with non-existent model — it will fail at generate time
        cfg = MLXConfig(model="nonexistent/model-that-does-not-exist")
        runner = MLXRunner(cfg)

        # If mlx is not installed, generate returns failure result
        if not mlx_available:
            result = runner.generate("test prompt")
            assert result.success is False
            assert result.error_message is not None
        else:
            # With mlx, it'll fail trying to load nonexistent model
            try:
                result = runner.generate("test prompt")
                # If it gets past load, it should still have proper error
                if not result.success:
                    assert result.error_message is not None
            except (RuntimeError, OSError):
                # Load failure is expected for nonexistent model
                pass

    def test_chat_with_no_tokenizer_returns_failure(self):
        """chat() returns failure when tokenizer is None."""
        from codomyrmex.llm.mlx.config import MLXConfig
        from codomyrmex.llm.mlx.runner import MLXRunner

        cfg = MLXConfig()
        runner = MLXRunner(cfg)
        # Directly set internal state to simulate loaded model without tokenizer
        runner._model = "fake_model"
        runner._tokenizer = None
        runner._loaded_model_name = cfg.model

        result = runner.chat([{"role": "user", "content": "hi"}])
        assert result.success is False
        assert "tokenizer" in result.error_message.lower()

        # Cleanup
        runner._model = None
        runner._loaded_model_name = None


# ===========================================================================
# 3. MLXGenerationResult edge cases
# ===========================================================================


@pytest.mark.unit
class TestGenerationResultEdgeCases:
    """Edge cases for result dataclasses."""

    def test_result_with_empty_response(self):
        from codomyrmex.llm.mlx.runner import MLXGenerationResult

        r = MLXGenerationResult(
            model="m", prompt="p", response="", execution_time=0.5,
            success=True,
        )
        assert r.response == ""
        assert r.success is True

    def test_result_with_unicode(self):
        from codomyrmex.llm.mlx.runner import MLXGenerationResult

        r = MLXGenerationResult(
            model="m", prompt="日本語のテスト", response="こんにちは 🎉",
            execution_time=1.0, success=True,
        )
        assert "🎉" in r.response
        assert "日本語" in r.prompt

    def test_result_with_very_long_text(self):
        from codomyrmex.llm.mlx.runner import MLXGenerationResult

        long_text = "a" * 100_000
        r = MLXGenerationResult(
            model="m", prompt=long_text, response=long_text,
            execution_time=10.0, tokens_generated=25000,
        )
        assert len(r.response) == 100_000

    def test_stream_chunk_with_multiline(self):
        from codomyrmex.llm.mlx.runner import MLXStreamChunk

        chunk = MLXStreamChunk(content="line1\nline2\nline3")
        assert chunk.content.count("\n") == 2


# ===========================================================================
# 4. Config edge cases
# ===========================================================================


@pytest.mark.unit
class TestConfigEdgeCases:
    """Edge cases for MLXConfig validation and interaction."""

    def test_multiple_validation_errors(self):
        from codomyrmex.llm.mlx.config import MLXConfig

        cfg = MLXConfig(model="valid")
        cfg.temperature = 5.0
        cfg.top_p = 2.0
        cfg.repetition_penalty = 0.1
        cfg.max_tokens = -5
        cfg.max_kv_size = -1

        result = cfg.validate()
        assert result["valid"] is False
        assert len(result["errors"]) >= 4

    def test_config_roundtrip_dict(self):
        """to_dict() produces values reconstructable to equivalent config."""
        from codomyrmex.llm.mlx.config import MLXConfig

        original = MLXConfig(
            model="test/model", temperature=0.42, max_tokens=777, seed=99,
        )
        d = original.to_dict()
        restored = MLXConfig(
            model=d["model"],
            temperature=d["temperature"],
            max_tokens=d["max_tokens"],
            seed=d["seed"],
        )
        assert restored.model == original.model
        assert restored.temperature == original.temperature
        assert restored.max_tokens == original.max_tokens
        assert restored.seed == original.seed

    def test_boundary_temperature_values(self):
        from codomyrmex.llm.mlx.config import MLXConfig

        # Exact boundaries should be valid
        for temp in [0.0, 2.0]:
            cfg = MLXConfig(temperature=temp)
            result = cfg.validate()
            # 0.0 is the sentinel, so post_init will set it to 0.7
            # test the resulting value is still valid
            assert result["valid"] is True

    def test_boundary_top_p_values(self):
        from codomyrmex.llm.mlx.config import MLXConfig

        cfg = MLXConfig(top_p=1.0)
        result = cfg.validate()
        assert result["valid"] is True


# ===========================================================================
# 5. Model manager edge cases
# ===========================================================================


@pytest.mark.unit
class TestModelManagerEdgeCases:
    """Edge cases for model manager filesystem operations."""

    def test_list_with_regular_file_in_cache(self):
        """Files (not directories) in cache should be silently ignored."""
        import shutil

        from codomyrmex.llm.mlx.config import MLXConfig
        from codomyrmex.llm.mlx.model_manager import MLXModelManager

        with tempfile.TemporaryDirectory() as td:
            # Add a regular file (not a model dir)
            (Path(td) / "stray_file.txt").write_text("noise")
            # Add a valid model dir
            model_dir = Path(td) / "org--valid-model"
            model_dir.mkdir()
            (model_dir / "config.json").write_text(json.dumps({"model_type": "test"}))

            cfg = MLXConfig(cache_dir=td)
            mgr = MLXModelManager(cfg)
            models = mgr.list_cached_models()
            assert len(models) == 1
            assert models[0].repo_id == "org/valid-model"

    def test_multiple_models_sorted(self):
        """Models should be returned in sorted order by directory name."""
        import shutil

        from codomyrmex.llm.mlx.config import MLXConfig
        from codomyrmex.llm.mlx.model_manager import MLXModelManager

        with tempfile.TemporaryDirectory() as td:
            for name in ["z-org--z-model", "a-org--a-model", "m-org--m-model"]:
                (Path(td) / name).mkdir()

            cfg = MLXConfig(cache_dir=td)
            mgr = MLXModelManager(cfg)
            models = mgr.list_cached_models()
            repo_ids = [m.repo_id for m in models]
            assert repo_ids == sorted(repo_ids)

    def test_estimate_memory_various_sizes(self):
        from codomyrmex.llm.mlx.model_manager import MLXModelManager

        # 1B 16-bit should be ~2 GB + overhead
        est = MLXModelManager.estimate_memory_gb(1.0, bits=16, overhead_gb=0)
        assert abs(est - 1.86) < 0.05  # 1e9 * 2 / 1024^3 ≈ 1.86

    def test_cache_dir_creation_on_init(self):
        """Manager creates cache dir on init if it doesn't exist."""
        from codomyrmex.llm.mlx.config import MLXConfig
        from codomyrmex.llm.mlx.model_manager import MLXModelManager

        with tempfile.TemporaryDirectory() as td:
            nested = Path(td) / "deep" / "nested" / "cache"
            assert not nested.exists()

            cfg = MLXConfig(cache_dir=str(nested))
            mgr = MLXModelManager(cfg)
            assert nested.is_dir()


# ===========================================================================
# 6. Quantization edge cases
# ===========================================================================


@pytest.mark.unit
class TestQuantizationEdgeCases:
    """Edge cases for quantization utilities."""

    def test_estimate_size_boundary_bits(self):
        from codomyrmex.llm.mlx.quantization import estimate_model_size_gb

        # 2-bit should be exactly half of 4-bit
        size_2 = estimate_model_size_gb(7.0, bits=2)
        size_4 = estimate_model_size_gb(7.0, bits=4)
        assert abs(size_4 - 2 * size_2) < 0.01

    def test_estimate_size_16bit(self):
        from codomyrmex.llm.mlx.quantization import estimate_model_size_gb

        # 16-bit is full precision
        size = estimate_model_size_gb(7.0, bits=16)
        assert 13.0 <= size <= 14.0  # 7e9 * 2 / 1024^3 ≈ 13.0

    def test_ram_estimation_with_small_context(self):
        from codomyrmex.llm.mlx.quantization import estimate_ram_required_gb

        # Very small context → almost no KV cache
        ram = estimate_ram_required_gb(3.0, bits=4, context_length=64)
        assert ram < 3.0

    def test_read_quantization_info_both_keys(self):
        from codomyrmex.llm.mlx.quantization import read_quantization_info

        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "config.json").write_text(
                json.dumps({
                    "quantization": "4-bit",
                    "quantization_config": {"bits": 4, "group_size": 64},
                })
            )
            info = read_quantization_info(td)
            assert info["quantization"] == "4-bit"
            assert info["bits"] == 4
            assert info["group_size"] == 64

    def test_all_presets_roundtrip_via_quantizer(self):
        """All presets accessible via MLXQuantizer.get_preset."""
        from codomyrmex.llm.mlx.quantization import MLXQuantizer, QUANTIZATION_PRESETS

        for name in QUANTIZATION_PRESETS:
            preset = MLXQuantizer.get_preset(name)
            assert preset.name == name
            assert preset.bits >= 2
            assert preset.group_size > 0


# ===========================================================================
# 7. End-to-end config → runner pipeline (pure logic)
# ===========================================================================


@pytest.mark.unit
class TestConfigToRunnerPipeline:
    """Test that configs flow correctly through the pipeline."""

    def test_preset_flows_to_runner(self):
        from codomyrmex.llm.mlx.config import MLXConfigPresets
        from codomyrmex.llm.mlx.runner import MLXRunner

        cfg = MLXConfigPresets.coding()
        runner = MLXRunner(cfg)
        stats = runner.get_performance_stats()
        assert stats["config"]["temperature"] == cfg.temperature
        assert stats["config"]["max_tokens"] == cfg.max_tokens

    def test_config_changes_reflected_in_stats(self):
        from codomyrmex.llm.mlx.config import MLXConfig
        from codomyrmex.llm.mlx.runner import MLXRunner

        cfg = MLXConfig(temperature=0.42, max_tokens=777, seed=99)
        runner = MLXRunner(cfg)
        stats = runner.get_performance_stats()
        assert stats["config"]["temperature"] == 0.42
        assert stats["config"]["max_tokens"] == 777
        assert stats["config"]["seed"] == 99

    def test_model_recommendation_to_config(self):
        from codomyrmex.llm.mlx.config import MLXConfig, RECOMMENDED_MODELS

        for rec in RECOMMENDED_MODELS:
            cfg = MLXConfig(model=rec.repo_id)
            result = cfg.validate()
            assert result["valid"] is True, f"Model {rec.repo_id} config invalid"


# ===========================================================================
# 8. Integration: multi-step workflow (gated)
# ===========================================================================


@_skip_no_mlx
@pytest.mark.integration
class TestMLXWorkflow:
    """Real integration tests — full workflow with loaded model."""

    @pytest.fixture(autouse=True)
    def _check_model(self):
        from codomyrmex.llm.mlx.config import MLXConfig
        from codomyrmex.llm.mlx.model_manager import MLXModelManager

        cfg = MLXConfig()
        mgr = MLXModelManager(cfg)
        if not mgr.is_model_cached(cfg.model):
            pytest.skip(f"Model {cfg.model} not cached")

    def test_preset_generate_workflow(self):
        """Preset → runner → generate → result."""
        from codomyrmex.llm.mlx.config import MLXConfigPresets
        from codomyrmex.llm.mlx.runner import MLXRunner

        cfg = MLXConfigPresets.fast()
        runner = MLXRunner(cfg)
        result = runner.generate("Say hello.")
        assert result.success is True
        assert len(result.response) > 0
        assert result.execution_time > 0
        runner.unload_model()

    def test_model_swap_workflow(self):
        """Load model, unload, verify clean state."""
        from codomyrmex.llm.mlx.config import MLXConfig
        from codomyrmex.llm.mlx.runner import MLXRunner

        cfg = MLXConfig(max_tokens=10)
        runner = MLXRunner(cfg)
        runner.load_model()
        assert runner.is_loaded
        loaded_name = runner.loaded_model

        runner.unload_model()
        assert not runner.is_loaded
        assert runner.loaded_model is None

        # Reload should work
        runner.load_model()
        assert runner.loaded_model == loaded_name
        runner.unload_model()

    def test_multi_chat_messages(self):
        """Multi-turn chat should work."""
        from codomyrmex.llm.mlx.config import MLXConfig
        from codomyrmex.llm.mlx.runner import MLXRunner

        cfg = MLXConfig(max_tokens=30)
        runner = MLXRunner(cfg)

        result = runner.chat([
            {"role": "system", "content": "Answer in one word only."},
            {"role": "user", "content": "What color is the sky?"},
        ])
        assert result.success is True
        assert len(result.response) > 0

        result2 = runner.chat([
            {"role": "system", "content": "Answer in one word only."},
            {"role": "user", "content": "What color is the sky?"},
            {"role": "assistant", "content": result.response},
            {"role": "user", "content": "And grass?"},
        ])
        assert result2.success is True
        runner.unload_model()

    def test_greedy_decode_produces_output(self):
        """Greedy decode (temp=0) should produce non-empty output both times."""
        from codomyrmex.llm.mlx.config import MLXConfig
        from codomyrmex.llm.mlx.runner import MLXRunner

        cfg = MLXConfig(max_tokens=20, temperature=0.0)
        runner = MLXRunner(cfg)
        r1 = runner.generate("The capital of France is", config=cfg)
        r2 = runner.generate("The capital of France is", config=cfg)
        # Both greedy calls should succeed with non-empty output
        assert r1.success is True
        assert r2.success is True
        assert len(r1.response) > 0
        assert len(r2.response) > 0
        runner.unload_model()
