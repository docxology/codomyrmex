# Codomyrmex Agents — src/codomyrmex/llm

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

Core Layer module providing LLM infrastructure for local and cloud model integration. Supports Ollama for local model execution and Fabric for AI pattern workflows, enabling privacy-focused AI development.

## Active Components

### Configuration

- `config.py` - LLM configuration management
  - Key Classes: `LLMConfig`, `LLMConfigPresets`
  - Key Functions: `get_config()`, `set_config()`, `reset_config()`

### Ollama Integration

- `ollama/` - Local model execution via Ollama
  - Key Classes: `OllamaManager`, `ModelRunner`, `OutputManager`, `ConfigManager`
  - Key Functions: `list_models()`, `pull_model()`, `generate()`

### Fabric Integration

- `fabric/` - Fabric AI pattern workflows
  - Key Classes: `FabricManager`, `FabricOrchestrator`, `FabricConfigManager`
  - Key Functions: `list_patterns()`, `run_pattern()`

### Prompt Templates

- `prompt_templates/` - Reusable prompt templates
  - Template files for common AI tasks

## Key Classes and Functions

| Class/Function | Module | Purpose |
| :--- | :--- | :--- |
| `LLMConfig` | config | Configuration data class |
| `LLMConfigPresets` | config | Pre-configured settings |
| `OllamaManager` | ollama | Manage Ollama installation and models |
| `ModelRunner` | ollama | Execute model inference |
| `FabricManager` | fabric | Manage Fabric patterns |
| `FabricOrchestrator` | fabric | Run Fabric workflows |
| `get_config()` | config | Get current configuration |

## Operating Contracts

1. **Logging**: Uses `logging_monitoring` for all LLM operation logging
2. **Local First**: Prioritize local models via Ollama for privacy
3. **Fallback**: Support cloud provider fallback when configured
4. **Configuration**: All settings via `LLMConfig` or environment variables
5. **Output Management**: Structured output capture and storage

## Usage Example

```python
from codomyrmex.llm import (
    OllamaManager,
    ModelRunner,
    LLMConfig,
    FabricOrchestrator
)

# Local model execution
manager = OllamaManager()
manager.pull_model("codellama:13b")

runner = ModelRunner(model="codellama:13b")
response = runner.generate("Explain this function:", code)

# Fabric pattern execution
fabric = FabricOrchestrator()
result = fabric.run_pattern("improve_code", input_text=code)
```

## Signposting

### Document Hierarchy

- **Self**: [AGENTS.md](AGENTS.md)
- **Parent**: [src/codomyrmex/AGENTS.md](../AGENTS.md)
- **Project Root**: [../../../AGENTS.md](../../../AGENTS.md)

### Sibling Modules

| Module | AGENTS.md | Purpose |
| :--- | :--- | :--- |
| agents | [../agents/AGENTS.md](../agents/AGENTS.md) | AI agent framework |
| cerebrum | [../cerebrum/AGENTS.md](../cerebrum/AGENTS.md) | Reasoning engine |
| model_context_protocol | [../model_context_protocol/AGENTS.md](../model_context_protocol/AGENTS.md) | MCP standards |

### Child Directories

| Directory | Purpose |
| :--- | :--- |
| ollama/ | Ollama integration |
| fabric/ | Fabric AI integration |
| prompt_templates/ | Prompt templates |
| outputs/ | Output storage |

### Related Documentation

- [README.md](README.md) - User documentation
- [PAI.md](PAI.md) - Personal AI Infrastructure
- [API_SPECIFICATION.md](API_SPECIFICATION.md) - API documentation
- [SPEC.md](SPEC.md) - Functional specification
