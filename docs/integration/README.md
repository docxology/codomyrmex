# Integration Documentation

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

Guides for integrating Codomyrmex with external systems, AI providers, and third-party services. Covers API integration patterns, authentication, and data exchange formats.

## Contents

| File | Description |
|------|-------------|
| [**external-systems.md**](external-systems.md) | Comprehensive external system integration guide |
| [**fabric-ai-integration.md**](fabric-ai-integration.md) | Fabric AI framework integration |
| [AGENTS.md](AGENTS.md) | Agent coordination for integration docs |
| [SPEC.md](SPEC.md) | Integration documentation specification |
| [PAI.md](PAI.md) | Personal AI integration patterns |

## Integration Categories

### AI Provider Integration

- **OpenAI**: GPT models, embeddings, function calling
- **Anthropic**: Claude models, tool use
- **Google**: Gemini models, multimodal
- **Ollama**: Local LLM deployment

### External Systems

- **Git Platforms**: GitHub, GitLab, Bitbucket
- **CI/CD**: GitHub Actions, Jenkins, CircleCI
- **Cloud**: AWS, GCP, Azure
- **Databases**: PostgreSQL, SQLite, Redis

### Protocol Support

- **MCP**: Model Context Protocol for AI tools
- **REST/GraphQL**: Standard API patterns
- **WebSocket**: Real-time communication

## Quick Integration Example

```python
from codomyrmex.llm import get_provider

# Connect to OpenAI
client = get_provider("openai")
response = client.complete("Write a function...")
```

## Related Documentation

- [API Reference](../reference/api.md) - Complete API documentation
- [LLM Module](../modules/llm/) - LLM integration details
- [MCP Module](../modules/model_context_protocol/) - MCP specification

## Navigation

- **Parent**: [docs/](../README.md)
- **Root**: [Project Root](../../README.md)
