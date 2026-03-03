# Logit Processor -- Module Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

The logit processor module provides composable processors and convenience functions for manipulating language model logit distributions before token sampling. It implements standard sampling strategies (temperature scaling, top-k filtering, nucleus sampling, repetition penalty) as individual processor classes that can be chained via `LogitProcessorList`.

## Architecture

```
logit_processor/
  __init__.py         # Exports all processors and convenience functions
  processor.py        # Core processor classes and sampling functions
  mcp_tools.py        # MCP tool: process_logits
  PAI.md              # PAI integration documentation
  README.md           # Module overview
  AGENTS.md           # Agent integration guide
  SPEC.md             # This file
```

### Class Hierarchy

```
LogitProcessor (ABC)
  |-- TemperatureProcessor
  |-- TopKProcessor
  |-- TopPProcessor
  |-- RepetitionPenaltyProcessor
  |-- LogitProcessorList       (composite: chains processors in sequence)
```

### Processing Pipeline

```
Raw logits (numpy array)
  |
  v
[RepetitionPenaltyProcessor]  -- penalize repeated tokens
  |
  v
[TemperatureProcessor]        -- scale distribution
  |
  v
[TopKProcessor]               -- keep top-k, set rest to -inf
  |
  v
[TopPProcessor]               -- nucleus cutoff
  |
  v
Processed logits
  |
  v
softmax -> probability distribution -> np.random.choice
  |
  v
Sampled token ID (int)
```

## Data Flows

### Input

| Input | Type | Source | Description |
|-------|------|--------|-------------|
| `logits` | `np.ndarray` (shape `(vocab_size,)`) | LLM model output | Raw unnormalized log-probabilities |
| `input_ids` | `list[int]` or `None` | Caller | Previously generated token IDs for repetition penalty |
| `temperature` | `float` | Caller | Scaling factor for distribution sharpness |
| `top_k` | `int` | Caller | Number of top tokens to keep |
| `top_p` | `float` | Caller | Cumulative probability threshold for nucleus sampling |
| `repetition_penalty` | `float` | Caller | Penalty multiplier for repeated tokens |
| `seed` | `int` or `None` | Caller | Random seed for reproducible sampling |

### Output

| Output | Type | Description |
|--------|------|-------------|
| Processed logits | `np.ndarray` | Modified logit array (same shape as input) |
| Sampled token | `int` | Token ID selected from processed distribution |
| Greedy token | `int` | Argmax of original logits |

### MCP Tool Output (`process_logits`)

| Field | Type | Description |
|-------|------|-------------|
| `status` | `str` | `"success"` |
| `sampled_token` | `int` | Token ID from controlled sampling |
| `greedy_token` | `int` | Token ID from argmax |
| `top5_tokens` | `list[dict]` | Top 5 tokens with `id` and `prob` fields |
| `entropy` | `float` | Shannon entropy of the original distribution |

## Public Interface

### Abstract Base Class

```python
class LogitProcessor(ABC):
    @abstractmethod
    def __call__(
        self, logits: np.ndarray, input_ids: list[int] | None = None
    ) -> np.ndarray:
        """Process logits before sampling."""
```

### Processor Classes

```python
class TemperatureProcessor(LogitProcessor):
    def __init__(self, temperature: float = 1.0) -> None: ...
    # Raises ValueError if temperature <= 0

class TopKProcessor(LogitProcessor):
    def __init__(self, top_k: int = 50) -> None: ...
    # Raises ValueError if top_k <= 0

class TopPProcessor(LogitProcessor):
    def __init__(self, top_p: float = 0.9) -> None: ...
    # Raises ValueError if top_p not in (0, 1]

class RepetitionPenaltyProcessor(LogitProcessor):
    def __init__(self, penalty: float = 1.3) -> None: ...
    # Raises ValueError if penalty < 1.0

class LogitProcessorList(LogitProcessor):
    def __init__(self, processors: list[LogitProcessor]) -> None: ...
    def append(self, processor: LogitProcessor) -> None: ...
```

### Convenience Functions

```python
def sample_token(
    logits: np.ndarray,
    temperature: float = 1.0,
    top_k: int = 0,
    top_p: float = 1.0,
    repetition_penalty: float = 1.0,
    input_ids: list[int] | None = None,
    seed: int | None = None,
) -> int:
    """Sample next token with configurable strategy chain."""

def greedy_decode(logits: np.ndarray) -> int:
    """Return argmax token ID."""
```

### MCP Tool

```python
@mcp_tool(category="logit_processor")
def process_logits(
    logits: list[float],
    temperature: float = 1.0,
    top_k: int = 0,
    top_p: float = 1.0,
    repetition_penalty: float = 1.0,
    previous_tokens: list[int] | None = None,
    seed: int | None = None,
) -> dict:
    """Apply sampling strategies to language model logits."""
```

### Module Exports (`__init__.py`)

```python
__all__ = [
    "LogitProcessor",
    "LogitProcessorList",
    "RepetitionPenaltyProcessor",
    "TemperatureProcessor",
    "TopKProcessor",
    "TopPProcessor",
    "greedy_decode",
    "sample_token",
]
```

## Dependencies

| Dependency | Type | Description |
|------------|------|-------------|
| `numpy` | External (core) | Array operations, softmax, random sampling |
| `codomyrmex.model_context_protocol.decorators` | Internal | `@mcp_tool` decorator for MCP auto-discovery |

No optional dependencies. No external API access required.

## Configuration

This module has no file-based configuration. All behavior is controlled via function/constructor parameters at call time.

## Constraints and Limitations

1. **NumPy dependency**: All logit arrays must be `numpy.ndarray`. Python lists are accepted by the MCP tool and converted internally.
2. **Single-token sampling**: `sample_token` returns one token per call. For autoregressive generation, the caller must loop.
3. **Global RNG state**: When `seed` is provided, `np.random.seed()` is called, which affects global NumPy random state. This is a known limitation for concurrent usage.
4. **No GPU support**: All processing uses CPU-bound NumPy operations. For high-throughput inference, consider framework-native sampling (e.g., PyTorch `torch.multinomial`).
5. **No vocabulary mapping**: The module operates on raw logit indices. Token-to-text mapping is the caller's responsibility.
6. **Processor order matters**: The order of processors in `LogitProcessorList` affects results. The recommended order is: repetition penalty, temperature, top-k, top-p.

## Navigation Links

- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [README.md](../../../README.md)
- **Module README**: [README.md](README.md)
- **Agent Guide**: [AGENTS.md](AGENTS.md)
- **PAI Integration**: [PAI.md](PAI.md)
