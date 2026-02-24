# Technical Specification - Deepseek

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

**Module**: `codomyrmex.agents.deepseek`  
**Last Updated**: 2026-01-29

## 1. Purpose

DeepSeek Coder integration for code generation and analysis

## 2. Architecture

### 2.1 Components

```
deepseek/
├── __init__.py          # Module exports
├── README.md            # Documentation
├── AGENTS.md            # Agent guidelines
├── SPEC.md              # This file
├── PAI.md               # Personal AI context
└── core.py              # Core implementation
```

### 2.2 Dependencies

- Python 3.10+
- Parent module: `agents`

## 3. Interfaces

### 3.1 Public API

```python
# Primary exports from codomyrmex.agents.deepseek
from codomyrmex.agents.deepseek import (
    DeepSeekClient,        # DeepSeek Coder API client (OpenAI-compatible)
)

# Key class signatures:
class DeepSeekClient(APIAgentBase):
    def __init__(self, config: dict[str, Any] | None = None): ...
    def _execute_impl(self, request: AgentRequest) -> AgentResponse: ...
    def _stream_impl(self, request: AgentRequest) -> Iterator[str]: ...
    def _build_messages(self, request: AgentRequest) -> list[dict[str, str]]: ...
```

### 3.2 Configuration

Environment variables:
- `CODOMYRMEX_*`: Configuration options

## 4. Implementation Notes

### 4.1 Design Decisions

1. **OpenAI-compatible endpoint**: Uses the `openai` Python client pointed at `https://api.deepseek.com/v1`, sharing retry, token extraction, and error handling from `APIAgentBase`.
2. **Default model `deepseek-coder`**: Targets the code-specialized model by default; overridable via `deepseek_model` config key.

### 4.2 Limitations

- Requires the `openai` package as a runtime dependency (guarded by `try/except ImportError`)
- API endpoint is hardcoded to `https://api.deepseek.com/v1`; self-hosted or alternative endpoints require config override

## 5. Testing

```bash
# Run tests for this module
uv run pytest src/codomyrmex/tests/unit/agents/deepseek/
```

## 6. Future Considerations

- Support for DeepSeek-V3 and future model variants
- Configurable base URL for self-hosted DeepSeek deployments
