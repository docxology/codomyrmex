# soul — API Specification

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

The `codomyrmex.soul` module wraps [soul.py](https://github.com/menonpg/soul.py) to provide persistent LLM agent memory via plain markdown files. The public Python API centres on `SoulAgent`.

---

## Module-Level Exports

```python
from codomyrmex.soul import (
    SoulAgent,          # Primary wrapper class
    HAS_SOUL,           # bool — True when soul-agent is installed
    SoulError,          # Base exception
    SoulImportError,    # Raised when soul-agent is absent
    SoulMemoryError,    # Raised on MEMORY.md write failure
    SoulProviderError,  # Raised on LLM call failure
)
```

---

## Class: `SoulAgent`

```python
class SoulAgent:
    def __init__(
        self,
        soul_path: str = "SOUL.md",
        memory_path: str = "MEMORY.md",
        provider: str = "anthropic",
        api_key: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
    ) -> None: ...
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `soul_path` | `str` | `"SOUL.md"` | Path to the agent identity file |
| `memory_path` | `str` | `"MEMORY.md"` | Path to the conversation log |
| `provider` | `str` | `"anthropic"` | LLM provider: `'anthropic'`, `'openai'`, `'openai-compatible'` |
| `api_key` | `str \| None` | `None` | API key; reads from env var when None |
| `model` | `str \| None` | `None` | Model override; uses provider default when None |
| `base_url` | `str \| None` | `None` | Base URL for openai-compatible endpoints |

### Raises

- `SoulImportError` — soul-agent is not installed
- `SoulError` — soul.py Agent construction failed

---

### `SoulAgent.ask`

```python
def ask(self, question: str, remember: bool = True) -> str:
```

Query the agent.  When `remember=True` the question and response are appended to MEMORY.md.

**Returns**: The agent's text response.

**Raises**: `SoulProviderError` on LLM failure.

---

### `SoulAgent.remember`

```python
def remember(self, note: str) -> None:
```

Append a free-form note to MEMORY.md without triggering an LLM call.

**Raises**: `SoulMemoryError` on write failure.

---

### `SoulAgent.reset_conversation`

```python
def reset_conversation(self) -> None:
```

Clear the in-session conversation buffer.  MEMORY.md is **not** modified.

---

### `SoulAgent.memory_stats`

```python
def memory_stats(self) -> dict[str, Any]:
```

Return a dictionary with:

| Key | Type | Description |
|-----|------|-------------|
| `soul_path` | `str` | SOUL.md path |
| `memory_path` | `str` | MEMORY.md path |
| `provider` | `str` | LLM provider |
| `soul_exists` | `bool` | Whether SOUL.md exists |
| `soul_size_bytes` | `int` | SOUL.md size in bytes |
| `memory_exists` | `bool` | Whether MEMORY.md exists |
| `memory_size_bytes` | `int` | MEMORY.md size in bytes |

---

## Exception Hierarchy

```
CodomyrmexError
└── SoulError                  # codomyrmex.soul.exceptions
    ├── SoulImportError        # soul-agent not installed
    ├── SoulMemoryError        # file I/O failure
    └── SoulProviderError      # LLM call failure
```

---

## Usage Examples

### Basic usage

```python
from codomyrmex.soul import SoulAgent

agent = SoulAgent(provider="anthropic")
reply = agent.ask("My name is Ada and I work on type theory.")
print(reply)
```

### Custom paths

```python
agent = SoulAgent(
    soul_path="/agents/ada/SOUL.md",
    memory_path="/agents/ada/MEMORY.md",
    provider="anthropic",
)
```

### Local Ollama

```python
agent = SoulAgent(
    provider="openai-compatible",
    base_url="http://localhost:11434/v1",
    model="llama3",
)
```

### Checking availability before use

```python
from codomyrmex.soul import HAS_SOUL, SoulAgent, SoulImportError

if not HAS_SOUL:
    raise RuntimeError("Install soul-agent: uv sync --extra soul")

agent = SoulAgent()
```

### Error handling

```python
from codomyrmex.soul import SoulAgent
from codomyrmex.soul.exceptions import SoulProviderError

agent = SoulAgent()
try:
    reply = agent.ask("Hello")
except SoulProviderError as exc:
    print(f"LLM call failed: {exc}")
```

---

## Navigation

- **Human Guide**: [README.md](README.md)
- **MCP Tools**: [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md)
- **Technical Spec**: [SPEC.md](SPEC.md)
- **Parent**: [codomyrmex](../API_SPECIFICATION.md)
