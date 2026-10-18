"""Real configuration and optional native KV-cache regression checks."""

import importlib.util
import inspect
import os
from dataclasses import asdict

import pytest

from codomyrmex.llm.mlx.config import MLXConfig
from codomyrmex.llm.mlx.runner import MLXRunner, _make_generation_kwargs


@pytest.mark.unit
class TestMLXCacheConfiguration:
    """Cache controls must reach both generation paths without native imports."""

    @pytest.mark.parametrize(
        ("options", "expected_step"),
        [({}, 2048), ({"kv_bits": 4}, 512), ({"max_kv_size": 4096}, 1)],
    )
    def test_automatic_prefill_policy(self, options, expected_step):
        config = MLXConfig(**options)
        assert config.get_cache_kwargs()["prefill_step_size"] == expected_step

    @pytest.mark.parametrize("step", [1, 128, 512, 2048])
    def test_explicit_quantized_prefill_wins(self, step):
        config = MLXConfig(kv_bits=4, prefill_step_size=step)
        assert config.get_cache_kwargs()["prefill_step_size"] == step

    def test_bounded_cache_is_forwarded(self):
        config = MLXConfig(max_kv_size=4096)
        assert config.get_cache_kwargs() == {
            "max_kv_size": 4096,
            "prefill_step_size": 1,
        }
        assert config.get_generation_kwargs()["max_kv_size"] == 4096
        assert _make_generation_kwargs(config)["max_kv_size"] == 4096
        assert _make_generation_kwargs(config)["prefill_step_size"] == 1

    def test_quantized_cache_is_forwarded(self):
        config = MLXConfig(kv_bits=4, kv_group_size=32, quantized_kv_start=0)
        expected = {
            "prefill_step_size": 512,
            "kv_bits": 4,
            "kv_group_size": 32,
            "quantized_kv_start": 0,
        }
        assert config.get_cache_kwargs() == expected
        for key, value in expected.items():
            assert config.get_generation_kwargs()[key] == value
            assert _make_generation_kwargs(config)[key] == value

    def test_defaults_do_not_enable_quantization_or_rotation(self):
        assert MLXConfig().get_cache_kwargs() == {"prefill_step_size": 2048}

    def test_environment_and_explicit_precedence(self, monkeypatch):
        monkeypatch.setenv("MLX_PREFILL_STEP_SIZE", "128")
        monkeypatch.setenv("MLX_KV_BITS", "4")
        monkeypatch.setenv("MLX_KV_GROUP_SIZE", "32")
        monkeypatch.setenv("MLX_QUANTIZED_KV_START", "0")
        assert MLXConfig().get_cache_kwargs() == {
            "prefill_step_size": 128,
            "kv_bits": 4,
            "kv_group_size": 32,
            "quantized_kv_start": 0,
        }
        explicit = MLXConfig(
            prefill_step_size=512,
            kv_bits=8,
            kv_group_size=128,
            quantized_kv_start=100,
        )
        assert explicit.get_cache_kwargs() == {
            "prefill_step_size": 512,
            "kv_bits": 8,
            "kv_group_size": 128,
            "quantized_kv_start": 100,
        }

    def test_serialization_round_trip(self):
        config = MLXConfig(kv_bits=4, kv_group_size=32, quantized_kv_start=0)
        restored = MLXConfig(**config.to_dict())
        assert restored.to_dict() == config.to_dict()
        assert restored.get_cache_kwargs() == config.get_cache_kwargs()

    @pytest.mark.parametrize(
        "variable",
        [
            "MLX_MAX_KV_SIZE",
            "MLX_PREFILL_STEP_SIZE",
            "MLX_KV_BITS",
            "MLX_KV_GROUP_SIZE",
            "MLX_QUANTIZED_KV_START",
        ],
    )
    @pytest.mark.parametrize("value", ["not-an-int", "", "4.5"])
    def test_malformed_environment_is_rejected(self, monkeypatch, variable, value):
        monkeypatch.setenv(variable, value)
        with pytest.raises(ValueError, match=variable):
            MLXConfig()

    def test_explicit_cache_settings_ignore_malformed_environment(self, monkeypatch):
        monkeypatch.setenv("MLX_PREFILL_STEP_SIZE", "not-an-int")
        monkeypatch.setenv("MLX_KV_BITS", "not-an-int")
        assert (
            MLXConfig(prefill_step_size=128, kv_bits=4).get_cache_kwargs()[
                "prefill_step_size"
            ]
            == 128
        )

    @pytest.mark.parametrize(
        "options",
        [
            {"prefill_step_size": 0},
            {"prefill_step_size": -1},
            {"prefill_step_size": True},
            {"prefill_step_size": 1.5},
            {"max_kv_size": 4},
            {"max_kv_size": True},
            {"max_kv_size": 4096.5},
            {"max_kv_size": 4096, "prefill_step_size": 2},
            {"max_kv_size": 4096, "kv_bits": 4},
            {"kv_bits": 7},
            {"kv_bits": True},
            {"kv_group_size": 16},
            {"kv_group_size": 32.0},
            {"quantized_kv_start": -1},
            {"quantized_kv_start": False},
        ],
    )
    def test_invalid_cache_controls_are_rejected(self, options):
        config = MLXConfig(**options)
        assert not config.validate()["valid"]
        with pytest.raises(ValueError):
            config.get_cache_kwargs()
        with pytest.raises(ValueError):
            _make_generation_kwargs(config)

    @pytest.mark.parametrize("bits", [2, 3, 4, 5, 6, 8])
    def test_supported_quantization_bits(self, bits):
        assert MLXConfig(kv_bits=bits).validate()["valid"]

    def test_invalid_config_fails_before_loading(self):
        runner = MLXRunner(MLXConfig(max_kv_size=4096, kv_bits=4))
        result = runner.generate("Do not download a model")
        assert not result.success
        assert result.error_message is not None
        assert "max_kv_size" in result.error_message
        assert not runner.is_loaded
        chunks = list(runner.stream_generate("Do not download a model"))
        assert len(chunks) == 1
        assert chunks[0].done
        assert not chunks[0].success
        assert chunks[0].error_message is not None
        assert "max_kv_size" in chunks[0].error_message
        assert chunks[0].token_count == 0
        assert "max_kv_size" in chunks[0].content
        result = runner.chat([{"role": "user", "content": "hello"}])
        assert not result.success
        assert result.error_message is not None
        assert "max_kv_size" in result.error_message
        assert not runner.is_loaded


def _tiny_model(**overrides):
    """Construct a real, randomly initialized model without network access."""
    from mlx_lm.models.llama import Model, ModelArgs

    options = {
        "model_type": "llama",
        "hidden_size": 64,
        "num_hidden_layers": 1,
        "intermediate_size": 128,
        "num_attention_heads": 2,
        "num_key_value_heads": 1,
        "rms_norm_eps": 1e-5,
        "vocab_size": 128,
    }
    return Model(ModelArgs(**(options | overrides)))


@pytest.mark.integration
@pytest.mark.skipif(
    os.environ.get("RUN_LIVE_MLX") != "1" or importlib.util.find_spec("mlx_lm") is None,
    reason="requires RUN_LIVE_MLX=1 and the native MLX backend",
)
class TestMLXNativeCacheControls:
    """Exercise upstream generation with a tiny random model, no downloads."""

    @pytest.mark.parametrize(
        "options",
        [
            {"max_kv_size": 16},
            {
                "kv_bits": 4,
                "kv_group_size": 32,
                "quantized_kv_start": 0,
                "prefill_step_size": 16,
            },
        ],
    )
    def test_real_generate_step_accepts_cache_kwargs(self, options):
        import mlx.core as mx
        from mlx_lm.generate import generate_step
        from mlx_lm.models.cache import QuantizedKVCache, RotatingKVCache
        from mlx_lm.sample_utils import make_sampler

        config = MLXConfig(max_tokens=2, **options)
        mx.random.seed(0)
        model = _tiny_model()
        kwargs = _make_generation_kwargs(config, model)
        kwargs["sampler"] = make_sampler(temp=0)
        inspect.signature(generate_step).bind(mx.array([1, 2]), None, **kwargs)
        prompt = mx.array([token % 128 for token in range(64)])
        output = list(generate_step(prompt, model, **kwargs))
        assert len(output) == 2
        assert all(0 <= token < 128 for token, _ in output)
        cache = kwargs["prompt_cache"][0]
        assert cache.offset >= 64
        if config.max_kv_size is not None:
            assert isinstance(cache, RotatingKVCache)
            assert cache.keep == 4
            assert cache.keys.shape[2] <= config.max_kv_size
            reference_kwargs = kwargs | {
                "prompt_cache": [RotatingKVCache(max_size=16, keep=4)],
                "prefill_step_size": 1,
            }
            reference = list(generate_step(prompt, model, **reference_kwargs))
            assert [token for token, _ in output] == [token for token, _ in reference]
            for (_, actual), (_, expected) in zip(output, reference, strict=True):
                assert mx.allclose(actual, expected, atol=1e-5).item()
        else:
            assert isinstance(cache, QuantizedKVCache)
            assert cache.bits == config.kv_bits

    @pytest.mark.parametrize("options", [{"max_kv_size": 16}, {"kv_bits": 4}])
    def test_model_specific_caches_are_rejected(self, options):
        model = _tiny_model(
            num_hidden_layers=2,
            layer_types=["full_attention", "sliding_attention"],
            sliding_window=8,
        )
        with pytest.raises(ValueError, match="model-specific cache layouts"):
            _make_generation_kwargs(MLXConfig(**options), model)

    def test_bounded_cache_retains_exact_sinks_and_recent_tokens(self):
        import mlx.core as mx

        cache = _make_generation_kwargs(MLXConfig(max_kv_size=16), _tiny_model())[
            "prompt_cache"
        ][0]
        for token in range(64):
            state = mx.full((1, 1, 1, 32), token)
            keys, values = cache.update_and_fetch(state, state)
            assert keys.shape[2] <= 16
        keys, values = cache.state
        expected = list(range(4)) + list(range(52, 64))
        assert keys[0, 0, :4, 0].tolist() == list(range(4))
        assert sorted(keys[0, 0, :, 0].tolist()) == expected
        assert sorted(values[0, 0, :, 0].tolist()) == expected
        assert cache.make_mask(1) is None

    @pytest.fixture
    def local_model_path(self, tmp_path):
        from mlx_lm.utils import save_config, save_model
        from tokenizers import Tokenizer
        from tokenizers.models import WordLevel
        from tokenizers.pre_tokenizers import Whitespace
        from transformers import PreTrainedTokenizerFast

        model = _tiny_model()
        save_model(tmp_path, model)
        save_config(
            {
                key: value
                for key, value in asdict(model.args).items()
                if value is not None
            },
            tmp_path / "config.json",
        )
        vocab = {"<unk>": 0, "<bos>": 1, "<eos>": 2}
        vocab.update({f"word{index}": index + 3 for index in range(125)})
        tokenizer = Tokenizer(WordLevel(vocab=vocab, unk_token="<unk>"))
        tokenizer.pre_tokenizer = Whitespace()
        wrapped = PreTrainedTokenizerFast(
            tokenizer_object=tokenizer,
            bos_token="<bos>",
            eos_token="<eos>",
            unk_token="<unk>",
        )
        wrapped.save_pretrained(tmp_path)
        return str(tmp_path)

    @pytest.mark.parametrize(
        "options",
        [{"max_kv_size": 16}, {"kv_bits": 4, "kv_group_size": 32}],
    )
    def test_runner_sync_stream_and_chat_with_local_model(
        self, local_model_path, options
    ):
        runner = MLXRunner(MLXConfig(model=local_model_path, max_tokens=2))
        config = MLXConfig(model=local_model_path, max_tokens=2, **options)
        prompt = " ".join(f"word{index}" for index in range(64))
        result = runner.generate(prompt, config=config)
        assert result.success, result.error_message
        assert runner.is_loaded
        chunks = list(runner.stream_generate(prompt, config=config))
        assert chunks[-1].done
        assert all(chunk.success for chunk in chunks), chunks[-1].error_message
        result = runner.chat([{"role": "user", "content": prompt}], config=config)
        assert result.success, result.error_message
        runner.unload_model()
