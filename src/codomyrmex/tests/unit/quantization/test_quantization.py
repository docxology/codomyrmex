"""Unit tests for Int8 and FP4 quantization."""

import numpy as np
import pytest

from codomyrmex.quantization import (
    FP4Quantizer,
    Int8Quantizer,
    compute_scale_zero_point,
    dequantize_fp4,
    dequantize_int8,
    per_channel_scale,
    quantize_fp4,
    quantize_int8,
)
from codomyrmex.quantization.utils import quantization_error


class TestInt8Quantization:
    """Tests for Int8 quantization roundtrip correctness."""

    @pytest.mark.unit
    def test_quantize_returns_int8(self):
        x = np.array([0.1, 0.5, -0.3, 1.0, -1.0], dtype=np.float32)
        qt = quantize_int8(x)
        assert qt.data.dtype == np.int8

    @pytest.mark.unit
    def test_int8_values_in_range(self):
        rng = np.random.default_rng(42)
        x = rng.standard_normal(100).astype(np.float32)
        qt = quantize_int8(x)
        assert qt.data.min() >= -128
        assert qt.data.max() <= 127

    @pytest.mark.unit
    def test_dequantize_close_to_original_asymmetric(self):
        x = np.array([0.1, 0.5, -0.3, 1.0, -1.0, 0.0], dtype=np.float32)
        qt = quantize_int8(x, scheme="asymmetric")
        reconstructed = dequantize_int8(qt)
        error = quantization_error(x, reconstructed)
        assert error["relative_error"] < 0.05  # <5% relative error

    @pytest.mark.unit
    def test_dequantize_close_to_original_symmetric(self):
        x = np.array([0.1, 0.5, -0.3, 1.0, -1.0, 0.0], dtype=np.float32)
        qt = quantize_int8(x, scheme="symmetric")
        reconstructed = dequantize_int8(qt)
        error = quantization_error(x, reconstructed)
        assert error["relative_error"] < 0.05

    @pytest.mark.unit
    def test_symmetric_zero_point_is_zero(self):
        x = np.array([-1.0, -0.5, 0.0, 0.5, 1.0], dtype=np.float32)
        qt = quantize_int8(x, scheme="symmetric")
        assert qt.zero_point == 0

    @pytest.mark.unit
    def test_asymmetric_scheme_stored(self):
        x = np.array([0.1, 0.5, -0.3], dtype=np.float32)
        qt = quantize_int8(x, scheme="asymmetric")
        assert qt.scheme == "asymmetric"

    @pytest.mark.unit
    def test_symmetric_scheme_stored(self):
        x = np.array([0.1, 0.5, -0.3], dtype=np.float32)
        qt = quantize_int8(x, scheme="symmetric")
        assert qt.scheme == "symmetric"

    @pytest.mark.unit
    def test_scale_positive(self):
        rng = np.random.default_rng(42)
        x = rng.standard_normal(50).astype(np.float32)
        qt = quantize_int8(x)
        assert float(qt.scale) > 0

    @pytest.mark.unit
    def test_original_dtype_preserved(self):
        x = np.array([1.0, 2.0], dtype=np.float32)
        qt = quantize_int8(x)
        assert qt.original_dtype == np.float32

    @pytest.mark.unit
    def test_dequantize_via_method(self):
        x = np.array([0.5, -0.5, 1.0], dtype=np.float32)
        qt = quantize_int8(x, scheme="asymmetric")
        reconstructed_method = qt.dequantize()
        reconstructed_func = dequantize_int8(qt)
        np.testing.assert_array_equal(reconstructed_method, reconstructed_func)

    @pytest.mark.unit
    def test_large_range_roundtrip(self):
        x = np.array([-100.0, 0.0, 100.0], dtype=np.float32)
        qt = quantize_int8(x, scheme="asymmetric")
        reconstructed = dequantize_int8(qt)
        error = quantization_error(x, reconstructed)
        assert error["relative_error"] < 0.05

    @pytest.mark.unit
    def test_single_value_quantize(self):
        x = np.array([3.14], dtype=np.float32)
        qt = quantize_int8(x)
        reconstructed = dequantize_int8(qt)
        assert reconstructed.shape == (1,)

    @pytest.mark.unit
    def test_all_zeros(self):
        x = np.zeros(10, dtype=np.float32)
        qt = quantize_int8(x)
        reconstructed = dequantize_int8(qt)
        np.testing.assert_allclose(reconstructed, x, atol=1e-6)

    @pytest.mark.unit
    def test_invalid_scheme_raises(self):
        x = np.array([1.0, 2.0], dtype=np.float32)
        with pytest.raises(ValueError, match="scheme"):
            quantize_int8(x, scheme="invalid")


class TestInt8Quantizer:
    """Tests for stateful Int8Quantizer class."""

    @pytest.mark.unit
    def test_calibrated_quantizer(self):
        x = np.linspace(-2.0, 2.0, 256, dtype=np.float32)
        quantizer = Int8Quantizer(scheme="asymmetric")
        qt = quantizer.quantize(x)
        reconstructed = quantizer.dequantize(qt)
        error = quantization_error(x, reconstructed)
        assert error["max_abs_error"] < 0.1

    @pytest.mark.unit
    def test_calibrate_sets_state(self):
        x = np.linspace(-1.0, 1.0, 100, dtype=np.float32)
        quantizer = Int8Quantizer(scheme="symmetric")
        quantizer.calibrate(x)
        assert quantizer._calibrated is True
        assert quantizer.scale is not None
        assert quantizer.zero_point is not None

    @pytest.mark.unit
    def test_auto_calibrate_on_first_quantize(self):
        x = np.array([0.5, -0.5, 1.0], dtype=np.float32)
        quantizer = Int8Quantizer()
        assert quantizer._calibrated is False
        qt = quantizer.quantize(x)
        assert quantizer._calibrated is True
        assert qt.data.dtype == np.int8

    @pytest.mark.unit
    def test_quantizer_symmetric_mode(self):
        x = np.array([-1.0, 0.0, 1.0], dtype=np.float32)
        quantizer = Int8Quantizer(scheme="symmetric")
        qt = quantizer.quantize(x)
        assert qt.scheme == "symmetric"
        assert qt.zero_point == 0


class TestFP4Quantization:
    """Tests for FP4 quantization."""

    @pytest.mark.unit
    def test_fp4_roundtrip_shape_preserved(self):
        x = np.array([0.1, 0.5, -0.3, 1.0, -1.0, 0.0, 0.25, -0.125], dtype=np.float32)
        ft = quantize_fp4(x)
        reconstructed = dequantize_fp4(ft)
        assert reconstructed.shape == x.shape

    @pytest.mark.unit
    def test_fp4_reconstructed_dtype_float32(self):
        rng = np.random.default_rng(42)
        x = rng.standard_normal(16).astype(np.float32)
        ft = quantize_fp4(x)
        reconstructed = dequantize_fp4(ft)
        assert reconstructed.dtype == np.float32

    @pytest.mark.unit
    def test_fp4_packing_even(self):
        """FP4 packs 2 values per byte, so packed size = ceil(n/2)."""
        rng = np.random.default_rng(42)
        x = rng.standard_normal(8).astype(np.float32)
        ft = quantize_fp4(x)
        assert len(ft.packed) == 4  # 8 fp4 values / 2 per byte

    @pytest.mark.unit
    def test_fp4_packing_odd(self):
        """Odd-length arrays should pad to ceil(n/2) bytes."""
        x = np.array([0.1, 0.5, -0.3, 1.0, -1.0], dtype=np.float32)
        ft = quantize_fp4(x)
        assert len(ft.packed) == 3  # ceil(5/2) = 3 bytes

    @pytest.mark.unit
    def test_fp4_scale_positive(self):
        rng = np.random.default_rng(42)
        x = rng.standard_normal(32).astype(np.float32)
        ft = quantize_fp4(x)
        assert ft.scale > 0

    @pytest.mark.unit
    def test_fp4_size_matches_input(self):
        x = np.array([0.1, 0.5, -0.3, 1.0], dtype=np.float32)
        ft = quantize_fp4(x)
        assert ft.size == 4

    @pytest.mark.unit
    def test_fp4_shape_matches_input(self):
        x = np.ones((3, 4), dtype=np.float32)
        ft = quantize_fp4(x)
        assert ft.shape == (3, 4)

    @pytest.mark.unit
    def test_fp4_all_zeros(self):
        x = np.zeros(8, dtype=np.float32)
        ft = quantize_fp4(x)
        reconstructed = dequantize_fp4(ft)
        np.testing.assert_allclose(reconstructed, x, atol=1e-6)

    @pytest.mark.unit
    def test_fp4_compression_ratio(self):
        quantizer = FP4Quantizer()
        x = np.ones(100, dtype=np.float32)
        assert quantizer.compression_ratio(x) == 8.0

    @pytest.mark.unit
    def test_fp4_quantizer_roundtrip(self):
        quantizer = FP4Quantizer()
        x = np.array([0.5, -0.5, 1.0, -1.0], dtype=np.float32)
        ft = quantizer.quantize(x)
        reconstructed = quantizer.dequantize(ft)
        assert reconstructed.shape == x.shape
        assert reconstructed.dtype == np.float32


class TestQuantizationError:
    """Tests for error metric computation."""

    @pytest.mark.unit
    def test_error_metrics_present(self):
        x = np.array([1.0, 2.0, 3.0], dtype=np.float32)
        y = np.array([1.1, 1.9, 3.05], dtype=np.float32)
        err = quantization_error(x, y)
        assert "max_abs_error" in err
        assert "mean_abs_error" in err
        assert "relative_error" in err
        assert "snr_db" in err

    @pytest.mark.unit
    def test_perfect_reconstruction_zero_error(self):
        x = np.array([1.0, 2.0, 3.0], dtype=np.float32)
        err = quantization_error(x, x.copy())
        assert err["max_abs_error"] < 1e-6
        assert err["mean_abs_error"] < 1e-6

    @pytest.mark.unit
    def test_snr_high_for_low_error(self):
        x = np.array([10.0, 20.0, 30.0], dtype=np.float32)
        y = np.array([10.001, 20.001, 30.001], dtype=np.float32)
        err = quantization_error(x, y)
        assert err["snr_db"] > 50  # Very high SNR for tiny error

    @pytest.mark.unit
    def test_relative_error_correct(self):
        x = np.array([1.0, 1.0, 1.0], dtype=np.float32)
        y = np.array([0.9, 0.9, 0.9], dtype=np.float32)
        err = quantization_error(x, y)
        assert abs(err["relative_error"] - 0.1) < 0.01  # ~10% relative error


class TestUtils:
    """Tests for utility functions."""

    @pytest.mark.unit
    def test_compute_scale_zero_point_asymmetric(self):
        scale, zp = compute_scale_zero_point(-1.0, 1.0, n_bits=8, scheme="asymmetric")
        assert scale > 0
        assert isinstance(zp, (int, np.integer))

    @pytest.mark.unit
    def test_compute_scale_zero_point_symmetric(self):
        scale, zp = compute_scale_zero_point(-1.0, 1.0, n_bits=8, scheme="symmetric")
        assert scale > 0
        assert zp == 0

    @pytest.mark.unit
    def test_per_channel_scale_shape(self):
        x = np.ones((4, 8), dtype=np.float32) * 2.0
        scales = per_channel_scale(x, axis=0)
        assert scales.shape == (4,)

    @pytest.mark.unit
    def test_per_channel_scale_values(self):
        x = np.array([[1.0, 2.0, 3.0], [-4.0, 0.5, 1.0]], dtype=np.float32)
        scales = per_channel_scale(x, axis=0)
        assert scales[0] == pytest.approx(3.0)
        assert scales[1] == pytest.approx(4.0)


class TestMCPTools:
    """Tests for MCP tool wrappers."""

    @pytest.mark.unit
    def test_quantize_tensor_int8(self):
        from codomyrmex.quantization.mcp_tools import quantize_tensor

        result = quantize_tensor([0.1, 0.5, -0.3, 1.0], method="int8")
        assert result["status"] == "success"
        assert result["method"] == "int8"
        assert "quantized_values" in result
        assert "error" in result
        assert "scale" in result

    @pytest.mark.unit
    def test_quantize_tensor_fp4(self):
        from codomyrmex.quantization.mcp_tools import quantize_tensor

        result = quantize_tensor(
            [0.1, 0.5, -0.3, 1.0, -1.0, 0.25, -0.25, 0.0], method="fp4"
        )
        assert result["status"] == "success"
        assert result["method"] == "fp4"
        assert "reconstructed" in result
        assert "error" in result

    @pytest.mark.unit
    def test_quantize_tensor_unknown_method(self):
        from codomyrmex.quantization.mcp_tools import quantize_tensor

        result = quantize_tensor([1.0, 2.0], method="fp16")
        assert result["status"] == "error"

    @pytest.mark.unit
    def test_quantization_benchmark(self):
        from codomyrmex.quantization.mcp_tools import quantization_benchmark

        result = quantization_benchmark(size=100)
        assert result["status"] == "success"
        assert "int8" in result
        assert "fp4" in result
        assert "size" in result
