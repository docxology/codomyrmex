"""Unit tests for Codomyrmex v1.3.2 Execution Capabilities deliverables.

Strict zero-mock policy on macOS host ensuring all bridges are fully concrete.
"""

import pytest

from codomyrmex.plugin_system.wasm import WasmSandbox, WasmSandboxError
from codomyrmex.quantization import QuantizationConfig, dequantize_array, quantize_array
from codomyrmex.spatial.coordinates.geodesic import generate_icosahedron
from codomyrmex.spatial.three_d.engine_3d import Vector3D
from codomyrmex.spatial.three_d.geodesic_bvh import build_bvh, ray_intersect_bvh


class TestWasmSandbox:
    """Test suite for the WebAssembly zero-trust execution sandbox."""

    def test_basic_execution(self):
        """Test simple mathematical execution with WAT format."""
        sandbox = WasmSandbox()
        # Compile a direct add function
        wat = """
        (module
            (func (export "add") (param i32 i32) (result i32)
                local.get 0
                local.get 1
                i32.add
            )
        )
        """
        result = sandbox.execute_plugin(wat, "add", 10, 32)
        assert result == 42

    def test_missing_function(self):
        """Test missing exported function raises precise error."""
        sandbox = WasmSandbox()
        wat = "(module)"
        with pytest.raises(
            WasmSandboxError, match="Export 'magic' not found in WASM module"
        ):
            sandbox.execute_plugin(wat, "magic")

    def test_not_a_function(self):
        """Test exported items that are not functions are rejected."""
        sandbox = WasmSandbox()
        wat = """
        (module
            (memory (export "mem") 1)
        )
        """
        with pytest.raises(WasmSandboxError, match="not a callable function"):
            sandbox.execute_plugin(wat, "mem")

    def test_fuel_timeout_protection(self):
        """Test that infinite loops are killed by fuel limits."""
        # Set a very low fuel budget
        sandbox = WasmSandbox(max_fuel=10)
        wat = """
        (module
            (func (export "run_forever")
                (loop $my_loop
                    br $my_loop
                )
            )
        )
        """
        with pytest.raises(
            WasmSandboxError, match="WASM Trap or Quota Exceeded|out of fuel"
        ):
            sandbox.execute_plugin(wat, "run_forever")

    def test_invalid_wat_syntax(self):
        """Test compiling syntax errors gracefully bubbles up."""
        sandbox = WasmSandbox()
        wat = "(module (func bad_syntax))"
        with pytest.raises(WasmSandboxError, match="execution failed"):
            sandbox.execute_plugin(wat, "anything")


class TestMLXQuantizer:
    """Test suite for the MLX array quantization module."""

    def test_quantization_config_validation(self):
        """Test invalid bit depths and group sizes raise ValueError."""
        with pytest.raises(ValueError, match="must be exactly 4, 8, or 16"):
            QuantizationConfig(bits=2)

        with pytest.raises(ValueError, match="group_size must be positive"):
            QuantizationConfig(group_size=0)

    def test_quantize_dequantize_int4(self):
        """Test full INT4 quantization round-trip on native MLX array."""
        mx = pytest.importorskip("mlx.core")

        # Original continuous floating point weights
        original = mx.random.normal((128, 128))
        config = QuantizationConfig(bits=4, group_size=32)

        wq, scales, biases = quantize_array(original, config)

        # In INT4 MLX, the data should be uint32 packing
        assert wq.dtype == mx.uint32
        assert scales is not None and biases is not None

        # Dequantize back
        reconstructed = dequantize_array(wq, scales, biases, config)

        # The reconstruction won't be identical, but should be same shape and roughly close
        assert reconstructed.shape == original.shape
        diff = mx.abs(original - reconstructed).max().item()
        assert diff < 1.0  # Safe threshold for random INT4 noise

    def test_quantize_dequantize_int8(self):
        """Test full INT8 quantization round-trip on native MLX array."""
        mx = pytest.importorskip("mlx.core")

        original = mx.random.normal((64, 64))
        config = QuantizationConfig(bits=8, group_size=64)

        wq, scales, biases = quantize_array(original, config)
        assert wq.dtype == mx.uint32  # MLX still uses packed unint32

        reconstructed = dequantize_array(wq, scales, biases, config)
        assert reconstructed.shape == original.shape

        # INT8 has much higher fidelity than INT4
        diff = mx.abs(original - reconstructed).max().item()
        assert diff < 0.1

    def test_quantize_fallback_fp16(self):
        """Test the 16-bit fallback logic bypassed structural quantization."""
        mx = pytest.importorskip("mlx.core")

        original = mx.random.normal((32, 32))
        config = QuantizationConfig(bits=16)

        wq, scales, biases = quantize_array(original, config)

        # Because we bypassed it, it should just be regular float16, no scales/biases
        assert wq.dtype == mx.float16
        assert scales is None
        assert biases is None

        # Reconstructs identically through fallback
        reconstructed = dequantize_array(wq, scales, biases, config)
        assert reconstructed.dtype == mx.float16

    def test_dequantize_missing_scales_biases(self):
        """Test error when dequantizing low-bit arrays without mandatory constants."""
        mx = pytest.importorskip("mlx.core")
        wq = mx.zeros((32, 32))
        config = QuantizationConfig(bits=4)

        with pytest.raises(ValueError, match="Scales and biases must be provided"):
            dequantize_array(wq, None, None, config)


class TestGeodesicBVH:
    """Test suite for the bounded volume hierarchy acceleration on geodesic meshes."""

    def test_bvh_construction(self):
        """Test partitioning correctly splits and nests the graph."""
        mesh = generate_icosahedron(radius=1.0)
        # By default an Icosahedron has 20 faces. Using max_faces=4 forces depth.
        bvh = build_bvh(mesh, max_faces=4)

        assert bvh.left is not None
        assert bvh.right is not None
        assert bvh.faces is None  # Root should be intermediate

        # Traverse to count leaf faces
        faces_collected = 0

        def traverse(node):
            nonlocal faces_collected
            if node.faces is not None:
                assert len(node.faces) <= 4
                faces_collected += len(node.faces)
            if node.left:
                traverse(node.left)
            if node.right:
                traverse(node.right)

        traverse(bvh)
        assert faces_collected == 20

    def test_ray_intersect_hit(self):
        """Test basic ray hitting the mesh outer hull."""
        mesh = generate_icosahedron(radius=2.0)
        bvh = build_bvh(mesh, max_faces=2)

        # Ray from outside pointing towards origin
        origin = Vector3D(5.0, 0.0, 0.0)
        direction = Vector3D(-1.0, 0.0, 0.0)

        t = ray_intersect_bvh(bvh, mesh, origin, direction)
        assert t is not None
        assert (
            2.0 < t < 4.0
        )  # Should hit approximately at x=2.0 (but offset by geometry shape)

    def test_ray_intersect_miss(self):
        """Test ray missing the mesh fails gracefully."""
        mesh = generate_icosahedron(radius=1.0)
        bvh = build_bvh(mesh, max_faces=5)

        # Far above the mesh, pointing up
        origin = Vector3D(0.0, 10.0, 0.0)
        direction = Vector3D(0.0, 1.0, 0.0)

        t = ray_intersect_bvh(bvh, mesh, origin, direction)
        assert t is None
