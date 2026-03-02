"""Small Language Model -- tiny GPT-2 style transformer for on-device inference."""
from .model import SLMConfig, SLM, causal_mask

__all__ = ["SLMConfig", "SLM", "causal_mask"]
