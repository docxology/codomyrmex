"""Zero-mock tests for neural MCP tools."""
import pytest
import numpy as np

class TestMCPTools:
    @pytest.mark.unit
    def test_transformer_encode_output_shape(self):
        from codomyrmex.neural.mcp_tools import transformer_encode

        result = transformer_encode(
            sequence_length=6, d_model=32, n_heads=4, n_layers=1
        )
        assert result["status"] == "success"
        assert result["output_shape"] == [1, 6, 32]

    @pytest.mark.unit
    def test_transformer_encode_returns_all_params(self):
        from codomyrmex.neural.mcp_tools import transformer_encode

        result = transformer_encode(
            sequence_length=4, d_model=16, n_heads=2, n_layers=3
        )
        assert result["d_model"] == 16
        assert result["n_heads"] == 2
        assert result["n_layers"] == 3
        assert result["sequence_length"] == 4

    @pytest.mark.unit
    def test_attention_forward_shapes(self):
        from codomyrmex.neural.mcp_tools import attention_forward

        result = attention_forward(seq_len=4, d_model=16, n_heads=2)
        assert result["status"] == "success"
        assert result["output_shape"] == [1, 4, 16]
        assert result["attention_weights_shape"] == [1, 2, 4, 4]

    @pytest.mark.unit
    def test_attention_forward_d_k(self):
        from codomyrmex.neural.mcp_tools import attention_forward

        result = attention_forward(seq_len=3, d_model=32, n_heads=8)
        assert result["d_k"] == 4  # 32 // 8

    @pytest.mark.unit
    def test_transformer_encode_invalid_d_model(self):
        from codomyrmex.neural.mcp_tools import transformer_encode

        # d_model (10) must be divisible by n_heads (3)
        with pytest.raises(AssertionError, match="must be divisible"):
            transformer_encode(
                sequence_length=4, d_model=10, n_heads=3, n_layers=1
            )

    @pytest.mark.unit
    def test_attention_forward_invalid_d_model(self):
        from codomyrmex.neural.mcp_tools import attention_forward

        with pytest.raises(AssertionError, match="must be divisible"):
            attention_forward(seq_len=4, d_model=20, n_heads=3)

    @pytest.mark.unit
    def test_transformer_encode_default_args(self):
        from codomyrmex.neural.mcp_tools import transformer_encode

        # Test calling with default arguments
        result = transformer_encode()
        assert result["status"] == "success"
        assert result["output_shape"] == [1, 8, 64]
        assert result["d_model"] == 64
        assert result["n_heads"] == 4
        assert result["n_layers"] == 2
        assert result["sequence_length"] == 8

    @pytest.mark.unit
    def test_attention_forward_default_args(self):
        from codomyrmex.neural.mcp_tools import attention_forward

        # Test calling with default arguments
        result = attention_forward()
        assert result["status"] == "success"
        assert result["output_shape"] == [1, 6, 32]
        assert result["attention_weights_shape"] == [1, 4, 6, 6]
        assert result["d_k"] == 8
