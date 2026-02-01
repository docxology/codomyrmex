# config

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Configuration templates and examples for the Codomyrmex platform. These configurations are used to customize module behavior, set up environments, and define workflows.

## Directory Structure

| Directory | Purpose |
|-----------|---------|
| [**api/**](api/) | API configuration (endpoints, rate limits, timeouts) |
| [**cache/**](cache/) | Caching configuration (Redis, memory, file) |
| [**database/**](database/) | Database connections and pooling |
| [**examples/**](examples/) | Example configuration files |
| [**llm/**](llm/) | LLM provider settings (OpenAI, Anthropic, Ollama) |
| [**monitoring/**](monitoring/) | Logging, metrics, and alerting |
| [**security/**](security/) | Authentication, encryption, API keys |
| [**templates/**](templates/) | Configuration templates |
| [**workflows/**](workflows/) | Workflow and pipeline definitions |

## Usage

```yaml
# Example: config/llm/providers.yaml
providers:
  ollama:
    enabled: true
    base_url: "http://localhost:11434"
    default_model: "llama2"

  openai:
    enabled: false
    api_key: "${OPENAI_API_KEY}"
```

## Best Practices

1. **Use Templates**: Copy from `templates/` and customize
2. **Environment Variables**: Store secrets in environment variables, not files
3. **Version Control**: Track configuration changes in git
4. **Validation**: Use `validation/` module to validate configs

## Companion Files

- [**AGENTS.md**](AGENTS.md) - Agent coordination
- [**SPEC.md**](SPEC.md) - Configuration specification
- [**PAI.md**](PAI.md) - Personal AI Infrastructure

## Navigation

- **Project Root**: [../README.md](../README.md)
- **Source Code**: [../src/codomyrmex/](../src/codomyrmex/)
