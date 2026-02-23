# Personal AI Infrastructure - Ollama Context

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

**Module**: `llm.ollama`  
**Status**: Active

## Context

This module provides comprehensive Ollama LLM integration for the Codomyrmex ecosystem, enabling local, privacy-first AI operations.

## AI Strategy

As an AI agent, when working with this module:

1. **Respect Interfaces**: Use the public API from `__init__.py`:
   - `OllamaManager` - Core service management
   - `ModelRunner` - Advanced execution
   - `ConfigManager` - Configuration handling
   - `OutputManager` - Output persistence

2. **ExecutionOptions**: Import from `model_runner`:

   ```python
   from codomyrmex.llm.ollama.model_runner import ExecutionOptions
   ```

3. **Error Handling**: All external Ollama calls should be wrapped in try/except and logged via `logging_monitoring.get_logger()`.

4. **No Mocks**: Always use real Ollama API - no mocked responses.

## Key Files

| File | Purpose |
|------|---------|
| `__init__.py` | Public API exports |
| `ollama_manager.py` | Core Ollama interaction |
| `model_runner.py` | Execution with options |
| `config_manager.py` | Configuration |
| `output_manager.py` | Output management |
| `SPEC.md` | Functional specification |
| `AGENTS.md` | Technical documentation |
| `API_SPECIFICATION.md` | Complete API reference |

## Usage Pattern

```python
from codomyrmex.llm.ollama import OllamaManager, ModelRunner
from codomyrmex.llm.ollama.model_runner import ExecutionOptions

manager = OllamaManager(auto_start_server=True)
runner = ModelRunner(manager)

options = ExecutionOptions(temperature=0.7, max_tokens=512)
result = runner.run_with_options("llama3.1:latest", "prompt", options)
```

## Future Considerations

- **Telemetry**: Emit performance metrics through logging system
- **Caching**: Consider response caching for repeated prompts
- **Embeddings**: Potential embedding generation support
