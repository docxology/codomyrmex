# llm - Functional Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

LLM module providing language model integration, prompt management, and output handling for the Codomyrmex platform.

## Interface Contracts

### Base Provider (`llm.providers`)

```python
class LLMProvider(ABC):
    def complete(messages: List[Message], model: str = None, ...) -> CompletionResponse
    def complete_stream(messages: List[Message], model: str = None, ...) -> Iterator[str]
    async def complete_async(messages: List[Message], ...) -> CompletionResponse

class Message:
    role: str; content: str; tool_calls: List[dict] = None; ...

class CompletionResponse:
    content: str; model: str; usage: dict; tool_calls: List[dict]; ...
```

### Routing & Fallback (`llm.router`)

```python
class ModelRouter:
    def register_model(config: ModelConfig, provider: ModelProvider = None) -> None
    def select_model(required_capabilities: List[str] = None, ...) -> ModelConfig
    def complete(prompt: str, model_name: str = None, ...) -> str
```

### MCP Integration (`llm.mcp`)

```python
class MCPBridge:
    def register_tool(name: str, description: str, input_schema: dict, handler: Callable) -> None
    async def handle_request(message: dict) -> Optional[dict]
    async def run_stdio() -> None
```

### Guardrails (`llm.guardrails`)

```python
class Guardrail(ABC):
    def validate(content: str) -> ValidationResult

class SafetyGate:
    def add_guardrail(guardrail: Guardrail) -> None
    def check(content: str) -> bool  # Raises SafetyError if blocked
```

#### Local LLM (`llm.ollama`)

```python
class OllamaManager:
    def list_models() -> List[OllamaModel]
    def download_model(name: str) -> bool
    def run_model(prompt: str, options: ExecutionOptions) -> ModelExecutionResult

class ModelRunner:
    def run_streaming(prompt: str, ...) -> Iterator[str]
    def run_batch(prompts: List[str]) -> List[ModelExecutionResult]
```

### Fabric Integration (`llm.fabric`)

```python
class FabricManager:
    def list_items() -> List[FabricItem]
    def execute_pipeline(name: str, params: dict) -> dict
```

## Navigation Links

- **Human Documentation**: [README.md](README.md)
- **Technical Documentation**: [AGENTS.md](AGENTS.md)

## Detailed Architecture and Implementation

### Design Principles

1. **Strict Modularity**: Each component is isolated and communicates via well-defined APIs.
2. **Performance Optimization**: Implementation leverages lazy loading and intelligent caching to minimize resource overhead.
3. **Error Resilience**: Robust exception handling ensures system stability even under unexpected conditions.
4. **Extensibility**: The architecture is designed to accommodate future enhancements without breaking existing contracts.

### Technical Implementation

The codebase utilizes modern Python features (version 3.10+) to provide a clean, type-safe API. Interaction patterns are documented in the corresponding `AGENTS.md` and `SPEC.md` files, ensuring that both human developers and automated agents can effectively utilize these capabilities.

## Testing

```bash
uv run python -m pytest src/codomyrmex/tests/ -k llm -v
```
