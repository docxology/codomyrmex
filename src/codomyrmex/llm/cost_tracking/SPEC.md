# Technical Specification - Cost Tracking

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

**Module**: `codomyrmex.llm.cost_tracking`  
**Last Updated**: 2026-01-29

## 1. Purpose

Token counting, billing estimation, and usage analytics

## 2. Architecture

### 2.1 Components

```
cost_tracking/
├── __init__.py          # Module exports
├── README.md            # Documentation
├── AGENTS.md            # Agent guidelines
├── SPEC.md              # This file
├── PAI.md               # Personal AI context
└── core.py              # Core implementation
```

### 2.2 Dependencies

- Python 3.10+
- Parent module: `llm`

## 3. Interfaces

### 3.1 Public API

```python
# Primary exports from codomyrmex.llm.cost_tracking
from codomyrmex.llm.cost_tracking import (
    ModelProvider,         # Enum: OPENAI, ANTHROPIC, GOOGLE, MISTRAL, COHERE, LOCAL, CUSTOM
    ModelPricing,          # Dataclass: model_id + provider + input/output cost per 1k tokens + context_window
    UsageRecord,           # Dataclass: model_id + input/output tokens + cost + latency_ms + timestamp
    UsageSummary,          # Dataclass: aggregated totals for a time period, with per-model breakdown
    TokenCounter,          # Heuristic token estimator (chars-per-token + word-based weighted average)
    CostTracker,           # Record usage, estimate costs, generate summaries, export to JSON
    BudgetGuard,           # Enforce daily/monthly/total spending limits before requests
    MODEL_PRICING,         # Dict of built-in pricing for GPT-4o, Claude 3.5, Gemini 2.0, Mistral, etc.
    estimate_cost,         # Quick cost estimate: (model_id, input_text, output_tokens) -> float
    count_tokens,          # Quick token count: (text, provider_name) -> int
    get_model_pricing,     # Look up ModelPricing by model_id
)

# Key class signatures:
class CostTracker:
    def __init__(self, custom_pricing: dict[str, ModelPricing] | None = None): ...
    def record(self, model_id: str, input_tokens: int, output_tokens: int, latency_ms: float = 0.0, metadata: dict | None = None) -> UsageRecord: ...
    def estimate_cost(self, model_id: str, input_text: str, estimated_output_tokens: int = 500) -> tuple[int, int, float]: ...
    def get_summary(self, period_days: int | None = None, start_date: datetime | None = None, end_date: datetime | None = None) -> UsageSummary: ...
    def get_records(self, model_id: str | None = None, limit: int = 100) -> list[UsageRecord]: ...
    def export_to_json(self) -> str: ...

class BudgetGuard:
    def __init__(self, daily_limit: float | None = None, monthly_limit: float | None = None, total_limit: float | None = None): ...
    def can_proceed(self, estimated_cost: float = 0.0) -> bool: ...
    def record_spend(self, amount: float) -> None: ...
    def get_remaining(self) -> dict[str, float | None]: ...

class TokenCounter:
    @classmethod
    def estimate_tokens(cls, text: str, provider: ModelProvider = ModelProvider.OPENAI) -> int: ...
    @classmethod
    def estimate_messages_tokens(cls, messages: list[dict[str, str]], provider: ModelProvider = ModelProvider.OPENAI) -> int: ...
```

### 3.2 Configuration

Environment variables:
- `CODOMYRMEX_*`: Configuration options

## 4. Implementation Notes

### 4.1 Design Decisions

1. **Heuristic token estimation over tokenizer dependency**: `TokenCounter` uses a weighted average of character-based and word-based estimates per provider, trading accuracy for zero external dependencies.
2. **Built-in pricing table**: `MODEL_PRICING` ships with current pricing for major providers (OpenAI, Anthropic, Google, Mistral), and `CostTracker` accepts `custom_pricing` overrides for custom or updated rates.
3. **Budget guard with three limit tiers**: `BudgetGuard` enforces independent daily, monthly, and total spend limits, checked before each request via `can_proceed()`.

### 4.2 Limitations

- Token estimates are heuristic-based; for billing-accurate counts, use `tiktoken` (OpenAI) or provider-specific tokenizers.
- `MODEL_PRICING` is a snapshot of late-2025/early-2026 prices and must be manually updated as providers change pricing.
- `CostTracker` and `BudgetGuard` store records in-memory only; data is lost on process restart.

## 5. Testing

```bash
# Run tests for this module
uv run pytest src/codomyrmex/tests/unit/llm/cost_tracking/
```

## 6. Future Considerations

- Add persistent storage backend (SQLite) for `CostTracker` records
- Integrate `tiktoken` for exact OpenAI token counting when available
- Add webhook/alert support in `BudgetGuard` when spend approaches limits
