# Codomyrmex Agents — docs/integration

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

External system integration documentation. Covers AI providers, cloud services, Git platforms, and third-party APIs.

## Active Components

| File | Priority | Description |
|------|----------|-------------|
| [external-systems.md](external-systems.md) | **Critical** | Comprehensive integration guide |
| [fabric-ai-integration.md](fabric-ai-integration.md) | High | Fabric AI framework |
| [README.md](README.md) | Medium | Directory overview |
| [SPEC.md](SPEC.md) | Medium | Functional specification |

## Agent Guidelines

### Integration Quality Standards

1. **Authentication**: Document all auth methods (API keys, OAuth, tokens)
2. **Rate Limits**: Include rate limiting guidance for each provider
3. **Error Handling**: Document common error codes and recovery
4. **Examples**: Provide working integration code snippets

### When Modifying Integration Docs

- Verify API endpoints are current
- Test authentication flows with real credentials
- Update version requirements for external SDKs
- Add new providers as they become supported

### Integration Categories

- **AI Providers**: OpenAI, Anthropic, Google, Ollama
- **Git Platforms**: GitHub, GitLab, Bitbucket
- **Cloud**: AWS, GCP, Azure
- **MCP**: Model Context Protocol standard

## Operating Contracts

- Maintain alignment between integration docs and actual APIs
- Ensure Model Context Protocol interfaces remain available for sibling agents
- Record outcomes in shared telemetry and update TODO queues when necessary

## Navigation Links

- **📁 Parent Directory**: [docs/](../README.md)
- **🏠 Project Root**: [../../README.md](../../README.md)
- **📦 Related**: [LLM Module](../modules/llm/) | [MCP Module](../modules/model_context_protocol/)
