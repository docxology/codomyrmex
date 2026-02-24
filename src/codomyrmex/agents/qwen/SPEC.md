# Technical Specification - Qwen

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

**Module**: `codomyrmex.agents.qwen`  
**Last Updated**: 2026-01-29

## 1. Purpose

Qwen-Coder integration for multilingual code assistance

## 2. Architecture

### 2.1 Components

```
qwen/
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
# Primary exports from codomyrmex.agents.qwen
from codomyrmex.agents.qwen import (
    QwenClient,            # Qwen-Coder API client (OpenAI-compatible via DashScope)
)

# Key class signatures:
class QwenClient(APIAgentBase):
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

1. **DashScope compatible-mode endpoint**: Uses Alibaba's OpenAI-compatible gateway at `https://dashscope.aliyuncs.com/compatible-mode/v1`, allowing the standard `openai` client to drive Qwen models.
2. **Default model `qwen-coder-turbo`**: Targets the code-specialized Qwen variant; overridable via `qwen_model` config key.

### 4.2 Limitations

- Requires the `openai` package as a runtime dependency (guarded by `try/except ImportError`)
- API endpoint is hardcoded to the DashScope compatible-mode URL; self-hosted Qwen instances require config override

## 5. Testing

```bash
# Run tests for this module
uv run pytest src/codomyrmex/tests/unit/agents/qwen/
```

## 6. Future Considerations

- Support for Qwen-2.5-Coder and future model variants
- Configurable base URL for self-hosted or VPC-internal Qwen deployments
