# Codomyrmex Agents — config

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Configuration templates and examples for all Codomyrmex subsystems. Provides reusable configuration patterns for LLM providers, databases, monitoring, security, and workflows.

## Directory Structure

```
config/
├── api/           # API configuration templates
├── cache/         # Cache strategy configurations
├── database/      # Database connection configs
├── examples/      # Example configuration files
├── llm/           # LLM provider configurations
├── monitoring/    # Monitoring and alerting configs
├── security/      # Security policy templates
├── templates/     # Generic configuration templates
└── workflows/     # Workflow definition templates
```

## Active Components

| Component | Type | Description |
|-----------|------|-------------|
| `llm/` | Directory | LLM provider configs (OpenAI, Anthropic, Ollama) |
| `database/` | Directory | Database connection templates |
| `monitoring/` | Directory | Logging and metrics configuration |
| `security/` | Directory | Security policies and API key management |
| `workflows/` | Directory | Workflow orchestration templates |
| `templates/` | Directory | Base configuration templates |
| `examples/` | Directory | Working configuration examples |

## Agent Guidelines

### Configuration Quality Standards

1. **Security**: Never commit real credentials; use placeholders
2. **Validation**: All configs should have JSON Schema or Pydantic validation
3. **Documentation**: Each config file should have inline documentation
4. **Defaults**: Provide sensible defaults with override capability

### When Modifying Configurations

- Test configurations in isolation before integration
- Update corresponding documentation when adding new fields
- Ensure backward compatibility or document breaking changes
- Validate against schemas where available

### Configuration Categories

| Category | Purpose | Location |
|----------|---------|----------|
| **LLM** | AI provider settings | `llm/` |
| **Database** | Connection strings, pools | `database/` |
| **Monitoring** | Logging levels, metrics | `monitoring/` |
| **Security** | API keys, policies | `security/` |
| **Workflows** | Orchestration definitions | `workflows/` |

## Operating Contracts

- Maintain alignment between configurations and runtime requirements
- Ensure Model Context Protocol interfaces remain available for sibling agents
- Never expose sensitive credentials in configuration examples
- Use environment variables for secrets with clear documentation

## Navigation Links

- **📁 Parent**: [../README.md](../README.md) - Project root
- **📖 Config Docs**: [../docs/reference/](../docs/reference/) - Reference documentation
- **🔧 Deployment**: [../docs/deployment/](../docs/deployment/) - Deployment guides
- **🔒 Security**: [../docs/reference/security.md](../docs/reference/security.md) - Security practices
