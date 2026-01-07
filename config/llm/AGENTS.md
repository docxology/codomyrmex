# Codomyrmex Agents — config/llm

## Signposting
- **Parent**: [config](../AGENTS.md)
- **Self**: [llm Agents](AGENTS.md)
- **Children**:
    - [examples](examples/AGENTS.md)
- **Key Artifacts**:
    - [Functional Spec](SPEC.md)
    - [Human Readme](README.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose

LLM and AI model configuration templates for model definitions, provider configurations, and inference parameters. Used across `llm/`, `agents/`, `cerebrum/`, and `ai_code_editing/` modules.

## Active Components

- `README.md` – LLM configuration documentation
- `SPEC.md` – Functional specification
- `models.yaml` – Model definitions and parameters
- `providers.yaml` – LLM provider configurations (Ollama, OpenAI, Anthropic, etc.)
- `inference.yaml` – Inference parameter templates
- `examples/` – Example model configs

## Operating Contracts

- Maintain alignment between code, documentation, and LLM configurations.
- Ensure Model Context Protocol interfaces remain available for sibling agents.
- Record outcomes in shared telemetry and update TODO queues when necessary.
- Use environment variable references for API keys and sensitive configuration.
- Support multiple LLM providers and model types.

## Navigation Links

- **Human Documentation**: [README.md](README.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Examples**: [examples/](examples/README.md)
- **Parent**: [config](../AGENTS.md)
- **Project Root**: [README](../../README.md)

