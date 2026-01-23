# Personal AI Infrastructure Context: config/llm/

## Purpose

LLM provider configuration for Ollama, OpenAI, Anthropic, and other model integrations.

## AI Agent Guidance

### Context for Agents

- Configures model endpoints, API keys, and parameters
- Supports local (Ollama) and remote (OpenAI, Anthropic) providers
- Fabric AI integration settings

### Configuration Patterns

- API keys via environment variables (`OPENAI_API_KEY`, etc.)
- Model selection by provider and name
- Temperature, max_tokens, and other generation parameters

### Related Modules

- `src/codomyrmex/llm/` - LLM abstraction layer
- `src/codomyrmex/agents/` - Agent configurations

## Cross-References

- [README.md](README.md) - Configuration overview
- [AGENTS.md](AGENTS.md) - Agent rules
- [SPEC.md](SPEC.md) - Schema specification
