"""Comprehensive tests for MLX quantization utilities.

All tests are pure logic — no mlx installation required.
"""

import json
import tempfile
from pathlib import Path

import pytest

# ===========================================================================
# 1. Quantization presets
# ===========================================================================


@pytest.mark.unit
class TestQuantizationPresets:
    """Tests for QUANTIZATION_PRESETS and QuantizationPreset dataclass."""

    def test_preset_keys(self):
        from codomyrmex.llm.mlx.quantization import QUANTIZATION_PRESETS

        assert set(QUANTIZATION_PRESETS.keys()) == {"q2", "q3", "q4", "q6", "q8"}

    def test_preset_bits_ordering(self):
        from codomyrmex.llm.mlx.quantization import QUANTIZATION_PRESETS

        bits = [QUANTIZATION_PRESETS[k].bits for k in ["q2", "q3", "q4", "q6", "q8"]]
        assert bits == [2, 3, 4, 6, 8]

    def test_preset_all_have_group_size(self):
        from codomyrmex.llm.mlx.quantization import QUANTIZATION_PRESETS

        for name, preset in QUANTIZATION_PRESETS.items():
            assert preset.group_size > 0, f"{name} has zero group_size"

    def test_preset_all_have_description(self):
        from codomyrmex.llm.mlx.quantization import QUANTIZATION_PRESETS

        for name, preset in QUANTIZATION_PRESETS.items():
            assert len(preset.description) > 5, f"{name} has short description"

    def test_default_quantization_is_q4(self):
        from codomyrmex.llm.mlx.quantization import DEFAULT_QUANTIZATION

        assert DEFAULT_QUANTIZATION == "q4"

    def test_preset_frozen(self):
        from codomyrmex.llm.mlx.quantization import QUANTIZATION_PRESETS

        with pytest.raises(AttributeError):
            QUANTIZATION_PRESETS["q4"].bits = 99


# ===========================================================================
# 2. Size estimation
# ===========================================================================


@pytest.mark.unit
class TestSizeEstimation:
    """Tests for estimate_model_size_gb."""

    def test_3b_4bit(self):
        from codomyrmex.llm.mlx.quantization import estimate_model_size_gb

        size = estimate_model_size_gb(3.0, bits=4)
        assert 1.0 <= size <= 2.0

    def test_7b_4bit(self):
        from codomyrmex.llm.mlx.quantization import estimate_model_size_gb

        size = estimate_model_size_gb(7.0, bits=4)
        assert 3.0 <= size <= 4.0

    def test_7b_8bit_double_4bit(self):
        from codomyrmex.llm.mlx.quantization import estimate_model_size_gb

        size_4 = estimate_model_size_gb(7.0, bits=4)
        size_8 = estimate_model_size_gb(7.0, bits=8)
        assert abs(size_8 - 2 * size_4) < 0.1

    def test_invalid_bits_raises(self):
        from codomyrmex.llm.mlx.quantization import estimate_model_size_gb

        with pytest.raises(ValueError, match="bits"):
            estimate_model_size_gb(3.0, bits=1)

        with pytest.raises(ValueError, match="bits"):
            estimate_model_size_gb(3.0, bits=32)

    def test_zero_params(self):
        from codomyrmex.llm.mlx.quantization import estimate_model_size_gb

        assert estimate_model_size_gb(0, bits=4) == 0.0


# ===========================================================================
# 3. RAM estimation
# ===========================================================================


@pytest.mark.unit
class TestRAMEstimation:
    """Tests for estimate_ram_required_gb."""

    def test_includes_weight_kv_and_overhead(self):
        from codomyrmex.llm.mlx.quantization import (
            estimate_model_size_gb,
            estimate_ram_required_gb,
        )

        weight_only = estimate_model_size_gb(7.0, bits=4)
        total = estimate_ram_required_gb(7.0, bits=4)
        assert total > weight_only  # KV cache + overhead adds to weight

    def test_larger_context_more_ram(self):
        from codomyrmex.llm.mlx.quantization import estimate_ram_required_gb

        ram_short = estimate_ram_required_gb(7.0, bits=4, context_length=2048)
        ram_long = estimate_ram_required_gb(7.0, bits=4, context_length=16384)
        assert ram_long > ram_short


# ===========================================================================
# 4. Quantization info reader
# ===========================================================================


@pytest.mark.unit
class TestQuantizationInfoReader:
    """Tests for read_quantization_info."""

    def test_missing_config(self):
        from codomyrmex.llm.mlx.quantization import read_quantization_info

        with tempfile.TemporaryDirectory() as td:
            assert read_quantization_info(td) == {}

    def test_top_level_quantization(self):
        from codomyrmex.llm.mlx.quantization import read_quantization_info

        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "config.json").write_text(
                json.dumps({"quantization": "4-bit"})
            )
            info = read_quantization_info(td)
            assert info["quantization"] == "4-bit"

    def test_nested_quantization_config(self):
        from codomyrmex.llm.mlx.quantization import read_quantization_info

        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "config.json").write_text(
                json.dumps({
                    "quantization_config": {
                        "bits": 4,
                        "group_size": 64,
                        "quant_method": "gptq",
                    }
                })
            )
            info = read_quantization_info(td)
            assert info["bits"] == 4
            assert info["group_size"] == 64
            assert info["quant_method"] == "gptq"

    def test_invalid_json(self):
        from codomyrmex.llm.mlx.quantization import read_quantization_info

        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "config.json").write_text("{bad json")
            assert read_quantization_info(td) == {}


# ===========================================================================
# 5. MLXQuantizer — preset lookup
# ===========================================================================


@pytest.mark.unit
class TestMLXQuantizerPresets:
    """Tests for MLXQuantizer preset management."""

    def test_get_preset_q4(self):
        from codomyrmex.llm.mlx.quantization import MLXQuantizer

        preset = MLXQuantizer.get_preset("q4")
        assert preset.bits == 4
        assert preset.group_size == 64

    def test_get_preset_unknown_raises(self):
        from codomyrmex.llm.mlx.quantization import MLXQuantizer

        with pytest.raises(KeyError, match="Unknown preset"):
            MLXQuantizer.get_preset("q999")

    def test_list_presets(self):
        from codomyrmex.llm.mlx.quantization import MLXQuantizer

        presets = MLXQuantizer.list_presets()
        assert isinstance(presets, dict)
        assert "q4" in presets
        assert len(presets) == 5
