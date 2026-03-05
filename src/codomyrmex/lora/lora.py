"""
LoRA (Low-Rank Adaptation) implementation.

Implements the LoRA technique from Hu et al. (2021) for parameter-efficient
fine-tuning. A pretrained weight W_0 is reparameterized as W = W_0 + B @ A * (alpha / r),
where A and B are low-rank matrices with r << min(d, k).

Pure Python + NumPy. No PyTorch dependency.
"""

from dataclasses import dataclass, field

import numpy as np


@dataclass
class LoRAConfig:
    """Configuration for LoRA adaptation."""

    rank: int = 4  # Low-rank dimension r
    alpha: float = 8.0  # Scaling factor (lora_alpha)
    dropout: float = 0.0  # Dropout on LoRA path
    target_modules: list = field(default_factory=list)  # Module names to apply LoRA to

    @property
    def scaling(self) -> float:
        """Compute the LoRA scaling factor alpha / r."""
        return self.alpha / self.rank


class LoRALayer:
    """
    LoRA weight adaptation layer.

    For a pretrained weight W_0 in R^{d x k}, LoRA reparameterizes:
    W = W_0 + B @ A * (alpha / r)

    where A in R^{r x k}, B in R^{d x r}, and r << min(d, k).

    During training: only A and B are updated. W_0 is frozen.
    At merge time: W_merged = W_0 + B @ A * scaling

    Args:
        weight: Pretrained weight matrix W_0 (d, k)
        config: LoRA configuration
    """

    def __init__(self, weight: np.ndarray, config: LoRAConfig | None = None):
        """
        Initialize the LoRA layer.

        Args:
            weight: The pretrained weight matrix W_0 (d, k).
            config: Optional configuration for the LoRA layer. If None,
                default LoRAConfig is used.
        """
        self.config = config or LoRAConfig()
        self.W_0 = weight.copy()  # Frozen base weight
        d, k = weight.shape
        r = self.config.rank

        # A initialized with Kaiming uniform, B initialized to zero
        # (so initial LoRA output is zero, i.e., no modification at start)
        self.A = np.random.randn(r, k) * np.sqrt(2.0 / k)
        self.B = np.zeros((d, r))  # B=0 means initial delta = 0

        self._merged = False

    def forward(self, x: np.ndarray) -> np.ndarray:
        """
        Compute the forward pass through the LoRA-adapted weight.

        For x: (batch, k) or (batch, seq, k):
        base: x @ W_0^T
        lora: x @ A^T @ B^T * scaling = x @ (B @ A)^T * scaling
        output = base + lora
        """
        if self._merged:
            # W has been merged: W_merged = W_0 + B @ A * scaling
            return x @ self.W_0.T

        base = x @ self.W_0.T
        lora = x @ self.A.T @ self.B.T * self.config.scaling
        return base + lora

    def merge(self) -> "LoRALayer":
        """Merge LoRA weights into base weight (for inference)."""
        if not self._merged:
            delta = self.B @ self.A * self.config.scaling
            self.W_0 = self.W_0 + delta
            self._merged = True
        return self

    def unmerge(self, original_weight: np.ndarray) -> "LoRALayer":
        """Restore original weights (for continued training)."""
        self.W_0 = original_weight.copy()
        self._merged = False
        return self

    def get_delta(self) -> np.ndarray:
        """Return the LoRA weight delta: B @ A * scaling."""
        return self.B @ self.A * self.config.scaling

    @property
    def effective_rank(self) -> int:
        """Actual rank of the delta matrix."""
        delta = self.get_delta()
        return int(np.linalg.matrix_rank(delta))

    def __call__(self, x: np.ndarray) -> np.ndarray:
        """Call forward."""
        return self.forward(x)


def apply_lora(weight: np.ndarray, rank: int = 4, alpha: float = 8.0) -> LoRALayer:
    """
    Wrap a weight matrix with LoRA adaptation.

    Args:
        weight: The pretrained weight matrix (d, k) to wrap.
        rank: The low-rank dimension r for the LoRA adaptation.
        alpha: The scaling factor alpha for the LoRA adaptation.

    Returns:
        A LoRALayer instance that wraps the original weight matrix
        with LoRA parameters A and B.
    """
    config = LoRAConfig(rank=rank, alpha=alpha)
    return LoRALayer(weight, config)


def merge_lora(lora_layer: LoRALayer) -> np.ndarray:
    """
    Merge LoRA into base weight and return merged weight matrix.

    Args:
        lora_layer: The LoRALayer instance to merge.

    Returns:
        The merged weight matrix W_0 + B @ A * scaling.
    """
    lora_layer.merge()
    return lora_layer.W_0.copy()
