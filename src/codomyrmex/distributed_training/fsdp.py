"""
Distributed training simulation (FSDP / DDP).

Implements simulations of Fully Sharded Data Parallel (FSDP) and
Distributed Data Parallel (DDP) collective operations. Useful for
understanding distributed training mechanics without actual multi-GPU setup.

Pure Python + NumPy. No PyTorch or NCCL dependency.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class FSDPShard:
    """
    Simulates one device's shard in Fully Sharded Data Parallel (FSDP).

    FSDP shards model parameters across devices. During forward:
    - All-gather to reconstruct full parameters
    - Run forward pass
    - Free gathered params (only keep shard)
    During backward:
    - All-gather again for gradient computation
    - Reduce-scatter gradients back to shards
    """

    device_id: int
    world_size: int
    param_shard: np.ndarray  # This device's param shard
    grad_shard: Optional[np.ndarray] = field(default=None)

    def __post_init__(self):
        if self.grad_shard is None:
            self.grad_shard = np.zeros_like(self.param_shard)


def all_gather(shards: list) -> np.ndarray:
    """
    Simulate AllGather: each device gets the full tensor from all devices.

    In real FSDP, this is a collective communication operation.
    Here we simply concatenate the shards.

    Args:
        shards: List of param shards, one per device

    Returns:
        Full parameter tensor (concatenation of all shards along axis 0)
    """
    return np.concatenate(shards, axis=0)


def reduce_scatter(full_grad: np.ndarray, world_size: int) -> list:
    """
    Simulate ReduceScatter: sum gradients then scatter shards.

    In real FSDP:
    1. Each device has a gradient for its local data
    2. ReduceScatter: sum all gradients, then scatter to one shard per device

    Here we simulate by splitting the gradient into shards.

    Args:
        full_grad: Full gradient tensor
        world_size: Number of devices

    Returns:
        List of gradient shards, one per device
    """
    total_size = full_grad.shape[0]
    shard_size = total_size // world_size
    shards = []
    for i in range(world_size):
        start = i * shard_size
        end = start + shard_size if i < world_size - 1 else total_size
        shards.append(full_grad[start:end] / world_size)  # average over devices
    return shards


class AllReduce:
    """
    AllReduce operation for gradient synchronization (used in DDP, not FSDP).

    Simulates ring AllReduce: sum gradients from all devices, broadcast back.
    """

    @staticmethod
    def sum(grads: list) -> list:
        """Sum all gradients across devices."""
        total = np.zeros_like(grads[0])
        for g in grads:
            total += g
        return [total.copy() for _ in grads]  # broadcast back

    @staticmethod
    def mean(grads: list) -> list:
        """Average all gradients across devices."""
        total = np.zeros_like(grads[0])
        for g in grads:
            total += g
        avg = total / len(grads)
        return [avg.copy() for _ in grads]


def simulate_fsdp_step(
    params: np.ndarray,
    gradients: list,  # One gradient per device
    world_size: int,
    learning_rate: float = 0.01,
) -> tuple:
    """
    Simulate one FSDP optimizer step.

    Args:
        params: Full parameter tensor (d,)
        gradients: List of gradient tensors, one per device
        world_size: Number of simulated devices
        learning_rate: SGD learning rate

    Returns:
        updated_params: New parameter tensor after gradient update
        shards: List of FSDPShard objects with updated shards
    """
    # AllReduce: average gradients across devices
    mean_grad = np.mean(gradients, axis=0)  # (d,)

    # Parameter update
    new_params = params - learning_rate * mean_grad

    # Shard updated params across devices
    param_size = len(new_params)
    shard_size = param_size // world_size

    shards = []
    for i in range(world_size):
        start = i * shard_size
        end = start + shard_size if i < world_size - 1 else param_size
        shard = new_params[start:end]
        grad_shard = mean_grad[start:end]
        shards.append(
            FSDPShard(
                device_id=i,
                world_size=world_size,
                param_shard=shard,
                grad_shard=grad_shard,
            )
        )

    return new_params, shards
