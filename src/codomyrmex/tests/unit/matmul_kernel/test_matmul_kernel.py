import numpy as np
import pytest

from codomyrmex.matmul_kernel import batched_matmul, matmul_flops, tiled_matmul


class TestTiledMatmul:
    @pytest.mark.unit
    def test_small_square(self):
        A = np.array([[1, 2], [3, 4]], dtype=np.float32)
        B = np.array([[5, 6], [7, 8]], dtype=np.float32)
        C = tiled_matmul(A, B)
        expected = A @ B
        np.testing.assert_allclose(C, expected, rtol=1e-5)

    @pytest.mark.unit
    def test_rectangular(self):
        A = np.random.randn(10, 20).astype(np.float32)
        B = np.random.randn(20, 15).astype(np.float32)
        C = tiled_matmul(A, B)
        expected = A @ B
        np.testing.assert_allclose(C, expected, rtol=1e-4)

    @pytest.mark.unit
    def test_output_shape(self):
        A = np.random.randn(8, 12).astype(np.float32)
        B = np.random.randn(12, 6).astype(np.float32)
        C = tiled_matmul(A, B)
        assert C.shape == (8, 6)

    @pytest.mark.unit
    def test_tile_size_variation(self):
        A = np.random.randn(32, 32).astype(np.float32)
        B = np.random.randn(32, 32).astype(np.float32)
        expected = A @ B
        for tile_size in [8, 16, 32, 64]:
            C = tiled_matmul(A, B, tile_size=tile_size)
            # Wider tolerance for small tile sizes: different accumulation
            # order in float32 changes rounding (expected numerical behavior)
            np.testing.assert_allclose(
                C, expected, rtol=1e-3, err_msg=f"Failed for tile_size={tile_size}"
            )

    @pytest.mark.unit
    def test_identity_matrix(self):
        A = np.random.randn(5, 5).astype(np.float32)
        identity = np.eye(5, dtype=np.float32)
        C = tiled_matmul(A, identity)
        np.testing.assert_allclose(C, A, rtol=1e-5)


class TestBatchedMatmul:
    @pytest.mark.unit
    def test_batched_shape(self):
        A = np.random.randn(3, 4, 5).astype(np.float32)
        B = np.random.randn(3, 5, 6).astype(np.float32)
        C = batched_matmul(A, B)
        assert C.shape == (3, 4, 6)

    @pytest.mark.unit
    def test_batched_correctness(self):
        A = np.random.randn(2, 3, 4).astype(np.float32)
        B = np.random.randn(2, 4, 3).astype(np.float32)
        C = batched_matmul(A, B)
        for b in range(2):
            expected = A[b] @ B[b]
            np.testing.assert_allclose(C[b], expected, rtol=1e-4)


class TestFlops:
    @pytest.mark.unit
    def test_flops_formula(self):
        # MxK @ KxN needs 2*M*K*N FLOPs (1 mul + 1 add per element)
        assert matmul_flops(2, 3, 4) == 2 * 2 * 3 * 4
        assert matmul_flops(100, 100, 100) == 2_000_000
