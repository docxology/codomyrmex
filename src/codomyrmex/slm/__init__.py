"""Small Language Model -- tiny GPT-2 style transformer for on-device inference."""

from .model import SLM, SLMConfig, causal_mask

__all__ = ["SLM", "SLMConfig", "causal_mask"]
