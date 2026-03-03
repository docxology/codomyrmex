"""Unit tests for codomyrmex.neural -- Transformer, attention, layers, activations."""

import numpy as np
import pytest

from codomyrmex.neural import (
    Embedding,
    FeedForward,
    LayerNorm,
    MultiHeadAttention,
    PositionalEncoding,
    TransformerBlock,
    TransformerDecoder,
    TransformerEncoder,
    gelu,
    relu,
    scaled_dot_product_attention,
    swish,
)


class TestScaledDotProductAttention:
    @pytest.mark.unit
    def test_output_shape(self):
        Q = np.random.randn(2, 5, 16)  # batch=2, seq=5, d_k=16
        K = np.random.randn(2, 7, 16)
        V = np.random.randn(2, 7, 16)
        out, weights = scaled_dot_product_attention(Q, K, V)
        assert out.shape == (2, 5, 16)
        assert weights.shape == (2, 5, 7)

    @pytest.mark.unit
    def test_weights_sum_to_one(self):
        Q = np.random.randn(1, 4, 8)
        K = np.random.randn(1, 4, 8)
        V = np.random.randn(1, 4, 8)
        _, weights = scaled_dot_product_attention(Q, K, V)
        row_sums = np.sum(weights, axis=-1)
        np.testing.assert_allclose(row_sums, np.ones_like(row_sums), atol=1e-5)

    @pytest.mark.unit
    def test_scale_by_sqrt_dk(self):
        """Larger d_k should not cause NaN due to numerical scaling."""
        d_k = 64
        Q = np.random.randn(1, 10, d_k) * 1.0
        K = np.random.randn(1, 10, d_k) * 1.0
        V = np.random.randn(1, 10, d_k) * 1.0
        out, weights = scaled_dot_product_attention(Q, K, V)
        assert not np.any(np.isnan(weights))
        assert not np.any(np.isnan(out))

    @pytest.mark.unit
    def test_mask_zeros_out_positions(self):
        """Masked positions should receive near-zero attention weight."""
        Q = np.ones((1, 2, 4))
        K = np.ones((1, 3, 4))
        V = np.ones((1, 3, 4))
        # Mask out position 2 for all queries
        mask = np.array([[[True, True, False], [True, True, False]]])
        _, weights = scaled_dot_product_attention(Q, K, V, mask)
        # Masked position should get ~0 weight
        assert weights[0, 0, 2] < 1e-4
        assert weights[0, 1, 2] < 1e-4

    @pytest.mark.unit
    def test_single_element_sequence(self):
        Q = np.random.randn(1, 1, 8)
        K = np.random.randn(1, 1, 8)
        V = np.random.randn(1, 1, 8)
        out, weights = scaled_dot_product_attention(Q, K, V)
        assert out.shape == (1, 1, 8)
        np.testing.assert_allclose(weights[0, 0, 0], 1.0, atol=1e-6)


class TestMultiHeadAttention:
    @pytest.mark.unit
    def test_output_shape(self):
        mha = MultiHeadAttention(d_model=64, n_heads=4)
        x = np.random.randn(2, 10, 64)
        out, weights = mha(x, x, x)
        assert out.shape == (2, 10, 64)

    @pytest.mark.unit
    def test_attention_weights_shape(self):
        mha = MultiHeadAttention(d_model=32, n_heads=4)
        x = np.random.randn(1, 5, 32)
        _, weights = mha(x, x, x)
        assert weights.shape == (1, 4, 5, 5)  # (batch, n_heads, seq_q, seq_k)

    @pytest.mark.unit
    def test_cross_attention_shapes(self):
        mha = MultiHeadAttention(d_model=32, n_heads=2)
        q = np.random.randn(1, 5, 32)
        kv = np.random.randn(1, 10, 32)
        out, weights = mha(q, kv, kv)
        assert out.shape == (1, 5, 32)
        assert weights.shape == (1, 2, 5, 10)

    @pytest.mark.unit
    def test_d_model_must_divide_n_heads(self):
        with pytest.raises(AssertionError):
            MultiHeadAttention(d_model=30, n_heads=4)

    @pytest.mark.unit
    def test_single_head(self):
        mha = MultiHeadAttention(d_model=16, n_heads=1)
        x = np.random.randn(1, 4, 16)
        out, weights = mha(x, x, x)
        assert out.shape == (1, 4, 16)
        assert weights.shape == (1, 1, 4, 4)

    @pytest.mark.unit
    def test_attention_weights_sum_to_one(self):
        mha = MultiHeadAttention(d_model=32, n_heads=4)
        x = np.random.randn(2, 6, 32)
        _, weights = mha(x, x, x)
        row_sums = np.sum(weights, axis=-1)
        np.testing.assert_allclose(row_sums, np.ones_like(row_sums), atol=1e-4)


class TestLayerNorm:
    @pytest.mark.unit
    def test_output_mean_near_zero(self):
        ln = LayerNorm(d_model=16)
        x = np.random.randn(2, 8, 16) * 5.0 + 3.0
        out = ln(x)
        means = np.mean(out, axis=-1)
        np.testing.assert_allclose(means, np.zeros((2, 8)), atol=1e-5)

    @pytest.mark.unit
    def test_output_std_near_one(self):
        ln = LayerNorm(d_model=32)
        x = np.random.randn(1, 4, 32) * 10.0
        out = ln(x)
        stds = np.std(out, axis=-1)
        np.testing.assert_allclose(stds, np.ones_like(stds), atol=0.1)

    @pytest.mark.unit
    def test_preserves_shape(self):
        ln = LayerNorm(d_model=64)
        x = np.random.randn(3, 7, 64)
        assert ln(x).shape == (3, 7, 64)

    @pytest.mark.unit
    def test_learnable_params_initial_values(self):
        ln = LayerNorm(d_model=8)
        np.testing.assert_allclose(ln.gamma, np.ones(8))
        np.testing.assert_allclose(ln.beta, np.zeros(8))


class TestFeedForward:
    @pytest.mark.unit
    def test_output_shape(self):
        ff = FeedForward(d_model=32, d_ff=128)
        x = np.random.randn(2, 5, 32)
        out = ff(x)
        assert out.shape == (2, 5, 32)

    @pytest.mark.unit
    def test_different_from_input(self):
        ff = FeedForward(d_model=16, d_ff=64)
        x = np.random.randn(1, 3, 16)
        out = ff(x)
        assert not np.allclose(out, x)


class TestPositionalEncoding:
    @pytest.mark.unit
    def test_output_shape(self):
        pe = PositionalEncoding(d_model=32)
        x = np.zeros((1, 10, 32))
        out = pe(x)
        assert out.shape == (1, 10, 32)

    @pytest.mark.unit
    def test_different_positions_different_encodings(self):
        pe = PositionalEncoding(d_model=16)
        x = np.zeros((1, 5, 16))
        out = pe(x)
        # Each position should have a unique encoding
        assert not np.allclose(out[0, 0], out[0, 1])
        assert not np.allclose(out[0, 1], out[0, 2])

    @pytest.mark.unit
    def test_deterministic(self):
        pe = PositionalEncoding(d_model=16)
        x = np.zeros((1, 5, 16))
        out1 = pe(x)
        out2 = pe(x)
        np.testing.assert_allclose(out1, out2)

    @pytest.mark.unit
    def test_adds_to_input(self):
        pe = PositionalEncoding(d_model=8)
        x = np.ones((1, 3, 8))
        out = pe(x)
        # Output should differ from input (encoding added)
        assert not np.allclose(out, x)


class TestEmbedding:
    @pytest.mark.unit
    def test_output_shape(self):
        emb = Embedding(vocab_size=100, d_model=32)
        ids = np.array([[0, 5, 10, 99]])
        out = emb(ids)
        assert out.shape == (1, 4, 32)

    @pytest.mark.unit
    def test_different_tokens_different_embeddings(self):
        emb = Embedding(vocab_size=50, d_model=16)
        ids = np.array([[0, 1]])
        out = emb(ids)
        assert not np.allclose(out[0, 0], out[0, 1])

    @pytest.mark.unit
    def test_same_token_same_embedding(self):
        emb = Embedding(vocab_size=50, d_model=16)
        ids = np.array([[3, 3]])
        out = emb(ids)
        np.testing.assert_allclose(out[0, 0], out[0, 1])


class TestTransformerBlock:
    @pytest.mark.unit
    def test_output_shape_preserved(self):
        block = TransformerBlock(d_model=64, n_heads=4, d_ff=128)
        x = np.random.randn(2, 10, 64)
        out = block(x)
        assert out.shape == (2, 10, 64)

    @pytest.mark.unit
    def test_residual_connection_present(self):
        """Output should be different from input (residuals add information)."""
        block = TransformerBlock(d_model=32, n_heads=2, d_ff=64)
        x = np.random.randn(1, 5, 32)
        out = block(x)
        assert not np.allclose(out, x)

    @pytest.mark.unit
    def test_no_nan_in_output(self):
        block = TransformerBlock(d_model=16, n_heads=2, d_ff=32)
        x = np.random.randn(1, 8, 16)
        out = block(x)
        assert not np.any(np.isnan(out))


class TestTransformerEncoder:
    @pytest.mark.unit
    def test_output_shape_float_input(self):
        enc = TransformerEncoder(n_layers=2, d_model=32, n_heads=4, d_ff=64)
        x = np.random.randn(2, 8, 32)
        out = enc(x)
        assert out.shape == (2, 8, 32)

    @pytest.mark.unit
    def test_output_shape_token_input(self):
        enc = TransformerEncoder(
            n_layers=1, d_model=16, n_heads=2, d_ff=32, vocab_size=100
        )
        x = np.random.randint(0, 100, (2, 6))
        out = enc(x)
        assert out.shape == (2, 6, 16)

    @pytest.mark.unit
    def test_multiple_layers(self):
        enc = TransformerEncoder(n_layers=4, d_model=32, n_heads=4, d_ff=64)
        x = np.random.randn(1, 5, 32)
        out = enc(x)
        assert out.shape == (1, 5, 32)
        assert not np.any(np.isnan(out))

    @pytest.mark.unit
    def test_single_layer(self):
        enc = TransformerEncoder(n_layers=1, d_model=16, n_heads=2, d_ff=32)
        x = np.random.randn(1, 3, 16)
        out = enc(x)
        assert out.shape == (1, 3, 16)


class TestTransformerDecoder:
    @pytest.mark.unit
    def test_output_shape(self):
        dec = TransformerDecoder(n_layers=2, d_model=32, n_heads=4, d_ff=64)
        tgt = np.random.randn(1, 5, 32)
        memory = np.random.randn(1, 10, 32)
        out = dec(tgt, memory)
        assert out.shape == (1, 5, 32)

    @pytest.mark.unit
    def test_cross_attention_different_lengths(self):
        dec = TransformerDecoder(n_layers=1, d_model=16, n_heads=2, d_ff=32)
        tgt = np.random.randn(2, 3, 16)
        memory = np.random.randn(2, 8, 16)
        out = dec(tgt, memory)
        assert out.shape == (2, 3, 16)

    @pytest.mark.unit
    def test_no_nan_in_output(self):
        dec = TransformerDecoder(n_layers=2, d_model=32, n_heads=4, d_ff=64)
        tgt = np.random.randn(1, 6, 32)
        memory = np.random.randn(1, 6, 32)
        out = dec(tgt, memory)
        assert not np.any(np.isnan(out))


class TestActivations:
    @pytest.mark.unit
    def test_gelu_at_zero(self):
        result = gelu(np.array([0.0]))
        assert abs(result[0]) < 1e-6

    @pytest.mark.unit
    def test_gelu_positive_for_positive_input(self):
        result = gelu(np.array([2.0]))
        assert result[0] > 0.0

    @pytest.mark.unit
    def test_gelu_near_negative_for_large_negative(self):
        result = gelu(np.array([-3.0]))
        assert abs(result[0]) < 0.01

    @pytest.mark.unit
    def test_relu_positive(self):
        np.testing.assert_allclose(relu(np.array([1.0, 2.0, -1.0])), [1.0, 2.0, 0.0])

    @pytest.mark.unit
    def test_relu_zero_for_negative(self):
        result = relu(np.array([-5.0, -0.1, 0.0]))
        np.testing.assert_allclose(result, [0.0, 0.0, 0.0])

    @pytest.mark.unit
    def test_swish_positive_input(self):
        x = np.array([1.0])
        # swish(x) = x * sigmoid(x), for x=1: 1 * sigmoid(1) ~ 0.731
        assert abs(swish(x)[0] - 0.7310585) < 1e-4

    @pytest.mark.unit
    def test_swish_at_zero(self):
        result = swish(np.array([0.0]))
        assert abs(result[0]) < 1e-6

    @pytest.mark.unit
    def test_activations_preserve_shape(self):
        x = np.random.randn(3, 4, 5)
        assert gelu(x).shape == (3, 4, 5)
        assert relu(x).shape == (3, 4, 5)
        assert swish(x).shape == (3, 4, 5)


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
