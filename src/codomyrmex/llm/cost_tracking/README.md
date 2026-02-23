# cost_tracking

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Token counting, billing estimation, and usage analytics for LLM operations. Ships with a `MODEL_PRICING` registry covering OpenAI, Anthropic, Google, and Mistral models with per-1K-token input/output costs. The `TokenCounter` provides heuristic token estimation, `CostTracker` records usage events and generates time-windowed summaries broken down by model, and `BudgetGuard` enforces daily/monthly/total spending limits before requests are sent.

## Key Exports

- **`ModelProvider`** -- Enum of supported LLM providers (openai, anthropic, google, mistral, cohere, local, custom)
- **`ModelPricing`** -- Dataclass holding per-model pricing: input/output cost per 1K tokens, context window size, and a `calculate_cost()` method
- **`UsageRecord`** -- Dataclass for a single LLM usage event with model ID, token counts, cost, latency, timestamp, and metadata
- **`UsageSummary`** -- Aggregated usage summary over a time period with totals by model
- **`TokenCounter`** -- Heuristic token estimator using provider-specific characters-per-token ratios; supports single text and multi-message estimation
- **`CostTracker`** -- Usage tracker that records events, auto-calculates cost from the pricing registry, provides time-windowed summaries, and exports to JSON
- **`BudgetGuard`** -- Spending limiter with daily, monthly, and total budget caps; checks whether a request with estimated cost can proceed and reports remaining budget
- **`MODEL_PRICING`** -- Dict of pre-configured `ModelPricing` entries for 16 models across 4 providers
- **`estimate_cost()`** -- Convenience function for quick cost estimation given a model ID and input text
- **`count_tokens()`** -- Convenience function for quick token counting given text and provider name
- **`get_model_pricing()`** -- Look up `ModelPricing` for a model ID from the built-in registry

## Directory Contents

- `__init__.py` - All cost tracking logic: pricing registry, token counter, cost tracker, budget guard, convenience functions
- `README.md` - This file
- `AGENTS.md` - Agent integration notes
- `PAI.md` - PAI-specific documentation
- `SPEC.md` - Module specification
- `py.typed` - PEP 561 type-checking marker

## Navigation

- **Parent Module**: [llm](../README.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
