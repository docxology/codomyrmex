# Model-Specific Configurations

This document provides model-specific configuration examples and recommendations for Ollama models used with Codomyrmex.

## rnj-1:8b

**Context Window**: 32K tokens  
**Recommended Use**: General purpose, code generation, analysis

### Basic Configuration

```python
from codomyrmex.llm.ollama import ExecutionOptions

options = ExecutionOptions(
    temperature=0.7,
    top_p=0.9,
    top_k=40,
    repeat_penalty=1.1,
    max_tokens=2048,
    context_window=32768
)
```

### Presets

#### Fast Mode
- Temperature: 0.1
- Top P: 0.5
- Max Tokens: 512
- Use for: Quick responses, simple tasks

#### Creative Mode
- Temperature: 0.9
- Top P: 0.95
- Max Tokens: 2048
- Use for: Creative writing, brainstorming

#### Balanced Mode (Default)
- Temperature: 0.7
- Top P: 0.9
- Max Tokens: 1024
- Use for: General purpose tasks

#### Precise Mode
- Temperature: 0.3
- Top P: 0.7
- Max Tokens: 2048
- Use for: Code generation, technical tasks

#### Long Form Mode
- Temperature: 0.7
- Top P: 0.9
- Max Tokens: 4096
- Use for: Long documents, detailed analysis

### Use Case Configurations

#### Code Generation
```python
options = ExecutionOptions(
    temperature=0.2,
    top_p=0.8,
    max_tokens=2048,
    format="text"
)
```

#### Creative Writing
```python
options = ExecutionOptions(
    temperature=0.9,
    top_p=0.95,
    max_tokens=2048,
    format="text"
)
```

#### Analysis (JSON Output)
```python
options = ExecutionOptions(
    temperature=0.5,
    top_p=0.9,
    max_tokens=2048,
    format="json"
)
```

#### Conversation
```python
options = ExecutionOptions(
    temperature=0.7,
    top_p=0.9,
    max_tokens=1024,
    format="text"
)
```

## Modular Configuration

All parameters in `ExecutionOptions` are independently configurable:

- `temperature`: Controls randomness (0.0-2.0)
- `top_p`: Nucleus sampling threshold (0.0-1.0)
- `top_k`: Top-k sampling (1-100)
- `repeat_penalty`: Penalty for repetition (1.0-2.0)
- `max_tokens`: Maximum output length
- `context_window`: Maximum context size (32768 for rnj-1:8b)
- `format`: Output format ("text" or "json")
- `system_prompt`: System-level instructions

## Loading Model Configuration

```python
from codomyrmex.llm.ollama import ConfigManager
import json

config_manager = ConfigManager()

# Load model-specific config
with open("examples/llm/ollama/rnj_1_8b_config.json") as f:
    config = json.load(f)

# Save for use with ConfigManager
config_manager.save_model_config("rnj-1:8b", config)
```

## Testing Configuration

All configurations are tested with real Ollama API calls (no mocks). See `scripts/llm/ollama/test_all_parameters_rnj.py` for comprehensive parameter testing.


## Navigation Links

- **Parent**: [Project Overview](../README.md)
- **Module Index**: [All Agents](../../AGENTS.md)
- **Documentation**: [Reference Guides](../../../../docs/README.md)
- **Home**: [Root README](../../../README.md)
