import pytest

from codomyrmex.matmul_kernel.mcp_tools import matmul_benchmark, matmul_compute


class TestMatmulMCPTools:
    @pytest.mark.unit
    def test_matmul_compute(self):
        a = [[1.0, 2.0], [3.0, 4.0]]
        b = [[5.0, 6.0], [7.0, 8.0]]

        result_dict = matmul_compute(a=a, b=b, tile_size=32)

        assert result_dict["status"] == "success"
        assert "result" in result_dict
        assert "shape" in result_dict
        assert "flops" in result_dict
        assert "max_error_vs_numpy" in result_dict
        assert "correct" in result_dict

        assert result_dict["shape"] == [2, 2]
        assert result_dict["correct"] is True

        expected_c = [[19.0, 22.0], [43.0, 50.0]]
        for i in range(2):
            for j in range(2):
                assert abs(result_dict["result"][i][j] - expected_c[i][j]) < 1e-4

    @pytest.mark.unit
    def test_matmul_benchmark(self):
        result_dict = matmul_benchmark(max_size=32)

        assert result_dict["status"] == "success"
        assert "results" in result_dict

        results = result_dict["results"]
        # With max_size 32, we expect sizes 16 and 32 to be in the results
        assert 16 in results
        assert 32 in results
        assert 64 not in results

        res_16 = results[16]
        assert res_16["size"] == 16
        assert "flops" in res_16
        assert "tiled_ms" in res_16
        assert "numpy_ms" in res_16
        assert "max_error" in res_16
        assert "correct" in res_16
