"""
Parameter-Efficient Fine-Tuning (PEFT) adapters.

Implements LoRA (Hu et al. 2021), Prefix Tuning (Li & Liang 2021),
and IA3 (Liu et al. 2022) as pure NumPy adapters. These demonstrate
the math behind PEFT methods without requiring PyTorch.
"""

import numpy as np
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class PEFTConfig:
    """Configuration for PEFT adapter creation."""

    method: str = "lora"  # "lora", "prefix", "ia3"
    rank: int = 4  # LoRA rank
    alpha: float = 8.0  # LoRA alpha
    num_virtual_tokens: int = 10  # Prefix tuning tokens
    target_modules: list = None


class PEFTAdapter(ABC):
    """Abstract base for PEFT adapters."""

    @abstractmethod
    def adapt(self, x: np.ndarray, **kwargs) -> np.ndarray:
        """Apply adaptation to input."""
        ...

    @property
    @abstractmethod
    def trainable_params(self) -> int:
        """Number of trainable parameters."""
        ...


class LoRAAdapter(PEFTAdapter):
    """
    LoRA adapter: add low-rank matrices to linear layers.

    Hu et al. 2021: For a pretrained weight W (d_out x d_in), instead of
    fine-tuning W directly, learn W + B @ A where A (rank x d_in) and
    B (d_out x rank) are low-rank. Scaled by alpha/rank.

    B is initialized to zero so the adapter starts as identity.
    """

    def __init__(self, d_in: int, d_out: int, rank: int = 4, alpha: float = 8.0):
        self.rank = rank
        self.scaling = alpha / rank
        scale = np.sqrt(2.0 / d_in)
        self.A = np.random.randn(rank, d_in) * scale
        self.B = np.zeros((d_out, rank))  # B=0 for zero init
        self.d_in = d_in
        self.d_out = d_out

    def adapt(self, x: np.ndarray, base_output: np.ndarray = None, **kwargs) -> np.ndarray:
        """Compute LoRA delta and add to base output."""
        lora_output = (x @ self.A.T) @ self.B.T * self.scaling
        if base_output is not None:
            return base_output + lora_output
        return lora_output

    @property
    def trainable_params(self) -> int:
        return self.rank * self.d_in + self.d_out * self.rank


class PrefixTuningAdapter(PEFTAdapter):
    """
    Prefix Tuning: learn virtual tokens prepended to attention keys/values.

    Li & Liang 2021: Instead of modifying model weights, prepend
    n_prefix_tokens trainable vectors to the key and value sequences.
    """

    def __init__(self, d_model: int, n_prefix: int = 10, n_layers: int = 2):
        self.d_model = d_model
        self.n_prefix = n_prefix
        self.n_layers = n_layers

        # Prefix keys and values per layer: (n_layers, n_prefix, d_model)
        scale = np.sqrt(1.0 / d_model)
        self.prefix_keys = np.random.randn(n_layers, n_prefix, d_model) * scale
        self.prefix_values = np.random.randn(n_layers, n_prefix, d_model) * scale

    def adapt(self, x: np.ndarray, layer_idx: int = 0, **kwargs) -> np.ndarray:
        """Prepend prefix tokens to input sequence.

        Args:
            x: Input tensor of shape (batch, seq_len, d_model)
            layer_idx: Which layer's prefix to use

        Returns:
            Tensor of shape (batch, n_prefix + seq_len, d_model)
        """
        prefix = self.prefix_keys[layer_idx % self.n_layers]  # (n_prefix, d_model)
        prefix_batch = np.tile(prefix[np.newaxis, :, :], (x.shape[0], 1, 1))
        return np.concatenate([prefix_batch, x], axis=1)

    @property
    def trainable_params(self) -> int:
        return 2 * self.n_layers * self.n_prefix * self.d_model  # keys + values


class IA3Adapter(PEFTAdapter):
    """
    IA3 (Infused Adapter by Inhibiting and Amplifying Inner Activations).

    Liu et al. 2022: Learn per-layer rescaling vectors l_k, l_v, l_ff.
    Output = (l_k . K, l_v . V, l_ff . FFN_act)

    Very parameter-efficient: only 3 vectors per layer.
    """

    def __init__(self, d_model: int, d_ff: int = None):
        self.d_model = d_model
        self.d_ff = d_ff or 4 * d_model

        # Initialized to ones (no modification at start)
        self.l_k = np.ones(d_model)  # Key rescaling
        self.l_v = np.ones(d_model)  # Value rescaling
        self.l_ff = np.ones(self.d_ff)  # FFN activation rescaling

    def adapt(self, x: np.ndarray, mode: str = "keys", **kwargs) -> np.ndarray:
        """Scale input by learned IA3 vector.

        Args:
            x: Input tensor
            mode: One of "keys", "values", "ffn"

        Returns:
            Rescaled tensor
        """
        if mode == "keys":
            return x * self.l_k
        elif mode == "values":
            return x * self.l_v
        elif mode == "ffn":
            return x * self.l_ff[: x.shape[-1]]
        return x

    @property
    def trainable_params(self) -> int:
        return self.d_model + self.d_model + self.d_ff  # l_k + l_v + l_ff
