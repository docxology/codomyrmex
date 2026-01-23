# Codomyrmex Agents — config

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Purpose
Configuration templates and examples.

## Active Components
- `README.md` – Project file
- `SPEC.md` – Project file
- `api/` – Directory containing api components
- `cache/` – Directory containing cache components
- `database/` – Directory containing database components
- `examples/` – Directory containing examples components
- `llm/` – Directory containing llm components
- `monitoring/` – Directory containing monitoring components
- `security/` – Directory containing security components
- `templates/` – Directory containing templates components
- `workflows/` – Directory containing workflows components

## Operating Contracts

1. **Template Structure**: Configurations organized by domain (llm, database, cache, etc.)
2. **Environment Variables**: Sensitive values use environment variable substitution
3. **Examples**: Working examples in examples/ subdirectory
4. **Validation**: Configurations validate against schemas

## Signposting

### Document Hierarchy

- **Self**: [AGENTS.md](AGENTS.md)
- **Parent**: [../AGENTS.md](../AGENTS.md) - Project root agent coordination
- **Project Root**: [../README.md](../README.md)

### Sibling Directories

| Directory | AGENTS.md | Purpose |
| :--- | :--- | :--- |
| src/ | [../src/AGENTS.md](../src/AGENTS.md) | Source code |
| docs/ | [../docs/AGENTS.md](../docs/AGENTS.md) | Documentation |
| scripts/ | [../scripts/AGENTS.md](../scripts/AGENTS.md) | Automation scripts |

### Child Directories

| Directory | Purpose |
| :--- | :--- |
| llm/ | LLM provider configuration |
| database/ | Database connections and pools |
| cache/ | Cache backend configuration |
| security/ | Authentication and API keys |
| api/ | API configuration |
| monitoring/ | Monitoring settings |
| workflows/ | CI/CD workflow configs |
| templates/ | Configuration templates |
| examples/ | Working configuration examples |

### Related Documentation

- [README.md](README.md) - Configuration overview
- [SPEC.md](SPEC.md) - Functional specification
- [examples/](examples/) - Example configurations
