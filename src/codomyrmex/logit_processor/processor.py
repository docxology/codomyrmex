"""Core logit processors for language model sampling.

Provides composable processors that modify logit distributions before
token sampling:

- ``TemperatureProcessor`` -- scale logits to control randomness
- ``TopKProcessor`` -- keep only the *k* highest-scoring tokens
- ``TopPProcessor`` -- nucleus sampling (cumulative probability cutoff)
- ``RepetitionPenaltyProcessor`` -- penalise previously generated tokens
- ``LogitProcessorList`` -- chain multiple processors in sequence

Convenience functions ``sample_token`` and ``greedy_decode`` combine
these into single-call sampling APIs.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

import numpy as np


class LogitProcessor(ABC):
    """Base class for logit processors applied during text generation."""

    @abstractmethod
    def __call__(
        self, logits: np.ndarray, input_ids: Optional[list[int]] = None
    ) -> np.ndarray:
        """Process logits before sampling.

        Args:
            logits: Raw logits array of shape ``(vocab_size,)``.
            input_ids: Previously generated token IDs (for repetition penalty).

        Returns:
            Modified logits array of same shape.
        """
        ...


class TemperatureProcessor(LogitProcessor):
    """Scale logits by temperature before softmax.

    - ``temperature < 1.0``: sharper distribution (more confident)
    - ``temperature > 1.0``: flatter distribution (more random)
    - ``temperature = 1.0``: no change
    """

    def __init__(self, temperature: float = 1.0) -> None:
        if temperature <= 0:
            raise ValueError(f"Temperature must be positive, got {temperature}")
        self.temperature = temperature

    def __call__(
        self, logits: np.ndarray, input_ids: Optional[list[int]] = None
    ) -> np.ndarray:
        return logits / self.temperature


class TopKProcessor(LogitProcessor):
    """Set all logits below the top-k to ``-inf``.

    Only the *k* highest logits will have non-zero probability after softmax.
    """

    def __init__(self, top_k: int = 50) -> None:
        if top_k <= 0:
            raise ValueError(f"top_k must be positive, got {top_k}")
        self.top_k = top_k

    def __call__(
        self, logits: np.ndarray, input_ids: Optional[list[int]] = None
    ) -> np.ndarray:
        k = min(self.top_k, len(logits))
        # Find k-th largest value threshold
        top_k_indices = np.argpartition(logits, -k)[-k:]
        mask = np.ones(len(logits), dtype=bool)
        mask[top_k_indices] = False
        result = logits.copy()
        result[mask] = float("-inf")
        return result


class TopPProcessor(LogitProcessor):
    """Nucleus sampling: keep top tokens whose cumulative probability reaches *p*.

    Sets logits below the nucleus threshold to ``-inf``.
    """

    def __init__(self, top_p: float = 0.9) -> None:
        if not 0 < top_p <= 1.0:
            raise ValueError(f"top_p must be in (0, 1], got {top_p}")
        self.top_p = top_p

    def __call__(
        self, logits: np.ndarray, input_ids: Optional[list[int]] = None
    ) -> np.ndarray:
        # Compute probabilities
        shifted = logits - np.max(logits)
        probs = np.exp(shifted) / np.sum(np.exp(shifted))

        # Sort by probability (descending)
        sorted_indices = np.argsort(probs)[::-1]
        sorted_probs = probs[sorted_indices]
        cumulative_probs = np.cumsum(sorted_probs)

        # Find cutoff: first index where cumulative prob > top_p
        # Keep that index too (ensure at least one token remains)
        cutoff_mask = cumulative_probs - sorted_probs > self.top_p

        # Set filtered logits to -inf
        filtered_indices = sorted_indices[cutoff_mask]
        result = logits.copy()
        result[filtered_indices] = float("-inf")
        return result


class RepetitionPenaltyProcessor(LogitProcessor):
    """Reduce probability of previously generated tokens.

    - ``penalty > 1.0``: reduces probability of repeated tokens
    - ``penalty = 1.0``: no effect

    For logits > 0: ``logit = logit / penalty``
    For logits < 0: ``logit = logit * penalty``
    """

    def __init__(self, penalty: float = 1.3) -> None:
        if penalty < 1.0:
            raise ValueError(
                f"Repetition penalty must be >= 1.0, got {penalty}"
            )
        self.penalty = penalty

    def __call__(
        self, logits: np.ndarray, input_ids: Optional[list[int]] = None
    ) -> np.ndarray:
        if not input_ids:
            return logits

        result = logits.copy()
        unique_ids = set(input_ids)
        for token_id in unique_ids:
            if 0 <= token_id < len(logits):
                if result[token_id] > 0:
                    result[token_id] /= self.penalty
                else:
                    result[token_id] *= self.penalty
        return result


class LogitProcessorList(LogitProcessor):
    """Apply a sequence of logit processors in order."""

    def __init__(self, processors: list[LogitProcessor]) -> None:
        self.processors = list(processors)

    def __call__(
        self, logits: np.ndarray, input_ids: Optional[list[int]] = None
    ) -> np.ndarray:
        result = logits
        for processor in self.processors:
            result = processor(result, input_ids)
        return result

    def append(self, processor: LogitProcessor) -> None:
        """Append a processor to the chain."""
        self.processors.append(processor)


def sample_token(
    logits: np.ndarray,
    temperature: float = 1.0,
    top_k: int = 0,
    top_p: float = 1.0,
    repetition_penalty: float = 1.0,
    input_ids: Optional[list[int]] = None,
    seed: Optional[int] = None,
) -> int:
    """Sample next token from logits using configurable sampling strategy.

    Applies processors in order:
    RepetitionPenalty -> Temperature -> TopK -> TopP -> Sample

    Args:
        logits: ``(vocab_size,)`` raw logits.
        temperature: Temperature for sampling.
        top_k: Top-k filtering (0 = disabled).
        top_p: Nucleus sampling probability (1.0 = disabled).
        repetition_penalty: Penalty for repeated tokens.
        input_ids: Previous token IDs for repetition penalty.
        seed: Random seed for reproducibility.

    Returns:
        Sampled token ID (int).
    """
    if seed is not None:
        np.random.seed(seed)

    processors: list[LogitProcessor] = []
    if repetition_penalty != 1.0:
        processors.append(RepetitionPenaltyProcessor(repetition_penalty))
    if temperature != 1.0:
        processors.append(TemperatureProcessor(temperature))
    if top_k > 0:
        processors.append(TopKProcessor(top_k))
    if top_p < 1.0:
        processors.append(TopPProcessor(top_p))

    processed = (
        LogitProcessorList(processors)(logits, input_ids)
        if processors
        else logits
    )

    # Convert to probabilities
    finite_mask = np.isfinite(processed)
    shifted = processed - np.max(processed[finite_mask])
    exp_logits = np.where(finite_mask, np.exp(shifted), 0.0)
    total = np.sum(exp_logits)
    if total == 0:
        # Fallback: uniform over valid tokens
        exp_logits[finite_mask] = 1.0
        total = np.sum(exp_logits)

    probs = exp_logits / total
    return int(np.random.choice(len(probs), p=probs))


def greedy_decode(logits: np.ndarray) -> int:
    """Return the argmax token (greedy decoding)."""
    return int(np.argmax(logits))
