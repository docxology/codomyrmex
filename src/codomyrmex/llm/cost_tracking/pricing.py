"""LLM model pricing data (as of late 2025 / early 2026 — prices change!)."""

from .models import ModelPricing, ModelProvider

MODEL_PRICING: dict[str, ModelPricing] = {
    # OpenAI
    "gpt-4o": ModelPricing("gpt-4o", ModelProvider.OPENAI, 0.0025, 0.01, 128000),
    "gpt-4o-mini": ModelPricing(
        "gpt-4o-mini", ModelProvider.OPENAI, 0.00015, 0.0006, 128000
    ),
    "gpt-4-turbo": ModelPricing(
        "gpt-4-turbo", ModelProvider.OPENAI, 0.01, 0.03, 128000
    ),
    "gpt-4": ModelPricing("gpt-4", ModelProvider.OPENAI, 0.03, 0.06, 8192),
    "gpt-3.5-turbo": ModelPricing(
        "gpt-3.5-turbo", ModelProvider.OPENAI, 0.0005, 0.0015, 16385
    ),
    "o1": ModelPricing("o1", ModelProvider.OPENAI, 0.015, 0.06, 200000),
    "o1-mini": ModelPricing("o1-mini", ModelProvider.OPENAI, 0.003, 0.012, 128000),
    # Anthropic
    "claude-3-5-sonnet": ModelPricing(
        "claude-3-5-sonnet", ModelProvider.ANTHROPIC, 0.003, 0.015, 200000
    ),
    "claude-3-opus": ModelPricing(
        "claude-3-opus", ModelProvider.ANTHROPIC, 0.015, 0.075, 200000
    ),
    "claude-3-haiku": ModelPricing(
        "claude-3-haiku", ModelProvider.ANTHROPIC, 0.00025, 0.00125, 200000
    ),
    # Google
    "gemini-1.5-pro": ModelPricing(
        "gemini-1.5-pro", ModelProvider.GOOGLE, 0.00125, 0.005, 2000000
    ),
    "gemini-1.5-flash": ModelPricing(
        "gemini-1.5-flash", ModelProvider.GOOGLE, 0.000075, 0.0003, 1000000
    ),
    "gemini-2.0-flash": ModelPricing(
        "gemini-2.0-flash", ModelProvider.GOOGLE, 0.0001, 0.0004, 1000000
    ),
    # Mistral
    "mistral-large": ModelPricing(
        "mistral-large", ModelProvider.MISTRAL, 0.002, 0.006, 128000
    ),
    "mistral-small": ModelPricing(
        "mistral-small", ModelProvider.MISTRAL, 0.0002, 0.0006, 32000
    ),
    "codestral": ModelPricing(
        "codestral", ModelProvider.MISTRAL, 0.0002, 0.0006, 32000
    ),
}
