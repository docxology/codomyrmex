"""
Unit tests for the Distributed Training (FSDP simulation) module.

Tests cover:
- FSDPShard dataclass initialization
- all_gather reconstructs full tensor from shards
- reduce_scatter splits gradient with averaging
- AllReduce.sum and AllReduce.mean operations
- simulate_fsdp_step parameter update correctness
- Shard coverage (all params accounted for)
- MCP tool interface
"""

import numpy as np
import pytest

from codomyrmex.distributed_training import AllReduce, FSDPShard, simulate_fsdp_step
from codomyrmex.distributed_training.fsdp import all_gather, reduce_scatter

# ---------------------------------------------------------------------------
# FSDPShard
# ---------------------------------------------------------------------------


class TestFSDPShard:
    """Tests for FSDPShard dataclass."""

    @pytest.mark.unit
    def test_default_grad_shard_is_zeros(self):
        shard = FSDPShard(device_id=0, world_size=4, param_shard=np.ones(10))
        np.testing.assert_array_equal(shard.grad_shard, np.zeros(10))

    @pytest.mark.unit
    def test_explicit_grad_shard(self):
        grad = np.ones(10) * 0.5
        shard = FSDPShard(
            device_id=1, world_size=4, param_shard=np.ones(10), grad_shard=grad
        )
        np.testing.assert_array_equal(shard.grad_shard, grad)

    @pytest.mark.unit
    def test_device_id_stored(self):
        shard = FSDPShard(device_id=3, world_size=8, param_shard=np.zeros(5))
        assert shard.device_id == 3
        assert shard.world_size == 8


# ---------------------------------------------------------------------------
# all_gather
# ---------------------------------------------------------------------------


class TestAllGather:
    """Tests for the AllGather collective operation."""

    @pytest.mark.unit
    def test_all_gather_concatenates(self):
        """AllGather should concatenate all shards."""
        shards = [np.array([1.0, 2.0]), np.array([3.0, 4.0]), np.array([5.0, 6.0])]
        full = all_gather(shards)
        np.testing.assert_array_equal(full, np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0]))

    @pytest.mark.unit
    def test_all_gather_preserves_total_size(self):
        world_size = 4
        shard_size = 10
        shards = [np.random.randn(shard_size) for _ in range(world_size)]
        full = all_gather(shards)
        assert len(full) == world_size * shard_size

    @pytest.mark.unit
    def test_all_gather_single_shard(self):
        shard = np.array([1.0, 2.0, 3.0])
        full = all_gather([shard])
        np.testing.assert_array_equal(full, shard)


# ---------------------------------------------------------------------------
# reduce_scatter
# ---------------------------------------------------------------------------


class TestReduceScatter:
    """Tests for the ReduceScatter collective operation."""

    @pytest.mark.unit
    def test_reduce_scatter_shard_count(self):
        full_grad = np.random.randn(16)
        world_size = 4
        shards = reduce_scatter(full_grad, world_size)
        assert len(shards) == world_size

    @pytest.mark.unit
    def test_reduce_scatter_averages(self):
        """Each shard should be the corresponding slice divided by world_size."""
        full_grad = np.array([4.0, 8.0, 12.0, 16.0])
        world_size = 2
        shards = reduce_scatter(full_grad, world_size)
        np.testing.assert_array_equal(shards[0], np.array([2.0, 4.0]))
        np.testing.assert_array_equal(shards[1], np.array([6.0, 8.0]))

    @pytest.mark.unit
    def test_reduce_scatter_covers_all_elements(self):
        """Concatenating shards * world_size should reconstruct the original."""
        full_grad = np.random.randn(20)
        world_size = 4
        shards = reduce_scatter(full_grad, world_size)
        reconstructed = np.concatenate(shards) * world_size
        np.testing.assert_allclose(reconstructed, full_grad, atol=1e-12)


# ---------------------------------------------------------------------------
# AllReduce
# ---------------------------------------------------------------------------


class TestAllReduce:
    """Tests for AllReduce sum and mean operations."""

    @pytest.mark.unit
    def test_allreduce_sum(self):
        """AllReduce.sum should return the sum on all devices."""
        g1 = np.array([1.0, 2.0])
        g2 = np.array([3.0, 4.0])
        g3 = np.array([5.0, 6.0])
        results = AllReduce.sum([g1, g2, g3])
        expected = np.array([9.0, 12.0])
        for r in results:
            np.testing.assert_array_equal(r, expected)

    @pytest.mark.unit
    def test_allreduce_sum_broadcast_count(self):
        """Should return one result per input gradient."""
        grads = [np.random.randn(5) for _ in range(4)]
        results = AllReduce.sum(grads)
        assert len(results) == 4

    @pytest.mark.unit
    def test_allreduce_mean(self):
        """AllReduce.mean should return the average on all devices."""
        g1 = np.array([2.0, 4.0])
        g2 = np.array([6.0, 8.0])
        results = AllReduce.mean([g1, g2])
        expected = np.array([4.0, 6.0])
        for r in results:
            np.testing.assert_array_equal(r, expected)

    @pytest.mark.unit
    def test_allreduce_mean_all_same(self):
        """Mean of identical gradients should return the same gradient."""
        g = np.array([3.0, 7.0, 1.0])
        results = AllReduce.mean([g.copy(), g.copy(), g.copy()])
        for r in results:
            np.testing.assert_allclose(r, g, atol=1e-12)

    @pytest.mark.unit
    def test_allreduce_results_are_independent_copies(self):
        """Mutating one result should not affect others."""
        grads = [np.array([1.0, 2.0]), np.array([3.0, 4.0])]
        results = AllReduce.sum(grads)
        results[0][0] = 999.0
        assert results[1][0] != 999.0


# ---------------------------------------------------------------------------
# simulate_fsdp_step
# ---------------------------------------------------------------------------


class TestSimulateFSDPStep:
    """Tests for the full FSDP step simulation."""

    @pytest.mark.unit
    def test_parameter_update_correct(self):
        """new_params = old_params - lr * mean_grad."""
        np.random.seed(42)
        params = np.array([1.0, 2.0, 3.0, 4.0])
        grad1 = np.array([0.1, 0.2, 0.3, 0.4])
        grad2 = np.array([0.3, 0.4, 0.1, 0.2])
        lr = 0.01
        world_size = 2

        mean_grad = (grad1 + grad2) / 2
        expected_params = params - lr * mean_grad

        new_params, shards = simulate_fsdp_step(
            params, [grad1, grad2], world_size=world_size, learning_rate=lr
        )
        np.testing.assert_allclose(new_params, expected_params, atol=1e-12)

    @pytest.mark.unit
    def test_shards_cover_all_params(self):
        """Concatenating all param shards should reconstruct updated params."""
        np.random.seed(42)
        param_size = 16
        world_size = 4
        params = np.random.randn(param_size)
        gradients = [np.random.randn(param_size) for _ in range(world_size)]

        new_params, shards = simulate_fsdp_step(
            params, gradients, world_size=world_size
        )
        reconstructed = np.concatenate([s.param_shard for s in shards])
        np.testing.assert_allclose(reconstructed, new_params, atol=1e-12)

    @pytest.mark.unit
    def test_correct_number_of_shards(self):
        params = np.random.randn(12)
        gradients = [np.random.randn(12) for _ in range(3)]
        _, shards = simulate_fsdp_step(params, gradients, world_size=3)
        assert len(shards) == 3

    @pytest.mark.unit
    def test_device_ids_sequential(self):
        params = np.random.randn(8)
        gradients = [np.random.randn(8) for _ in range(4)]
        _, shards = simulate_fsdp_step(params, gradients, world_size=4)
        assert [s.device_id for s in shards] == [0, 1, 2, 3]

    @pytest.mark.unit
    def test_grad_shards_match_mean_grad(self):
        """Each shard's grad_shard should be a slice of the mean gradient."""
        np.random.seed(42)
        params = np.random.randn(8)
        grad1 = np.random.randn(8)
        grad2 = np.random.randn(8)
        mean_grad = (grad1 + grad2) / 2

        _, shards = simulate_fsdp_step(params, [grad1, grad2], world_size=2)
        reconstructed_grad = np.concatenate([s.grad_shard for s in shards])
        np.testing.assert_allclose(reconstructed_grad, mean_grad, atol=1e-12)

    @pytest.mark.unit
    def test_zero_gradients_no_change(self):
        """With zero gradients, params should not change."""
        params = np.array([1.0, 2.0, 3.0, 4.0])
        zero_grads = [np.zeros(4), np.zeros(4)]
        new_params, _ = simulate_fsdp_step(params, zero_grads, world_size=2)
        np.testing.assert_array_equal(new_params, params)


# ---------------------------------------------------------------------------
# MCP tool
# ---------------------------------------------------------------------------


class TestMCPTool:
    """Tests for distributed training MCP tool interface."""

    @pytest.mark.unit
    def test_fsdp_simulate_step_tool(self):
        from codomyrmex.distributed_training.mcp_tools import fsdp_simulate_step

        result = fsdp_simulate_step(
            param_size=256, world_size=4, learning_rate=0.01, seed=42
        )
        assert result["status"] == "success"
        assert result["world_size"] == 4
        assert len(result["shard_sizes"]) == 4
        assert sum(result["shard_sizes"]) == 256

    @pytest.mark.unit
    def test_fsdp_tool_has_mcp_metadata(self):
        from codomyrmex.distributed_training.mcp_tools import fsdp_simulate_step

        assert hasattr(fsdp_simulate_step, "_mcp_tool")
        assert fsdp_simulate_step._mcp_tool["category"] == "distributed_training"
