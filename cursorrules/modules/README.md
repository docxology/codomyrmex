# Module-Specific Cursor Rules

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

Module-specific rules that supplement `general.cursorrules`. Each rule file follows the 8-section template and contains coding standards, testing requirements, and best practices for its respective module.

## Rule Categories (60 total)

### Security & Identity (7)

| Rule | Purpose |
|------|---------|
| `security` | Security scanning, vulnerability detection |
| `defense` | Active defense, threat response |
| `identity` | Persona management, verification |
| `wallet` | Self-custody, key management |
| `privacy` | Privacy-preserving operations |
| `encryption` | Cryptographic operations |
| `auth` | Authentication, authorization |

### AI & Agents (7)

| Rule | Purpose |
|------|---------|
| `agents` | Multi-agent framework |
| `llm` | LLM provider abstraction |
| `agentic_memory` | Long-term agent memory |
| `cerebrum` | CEREBRUM reasoning framework |
| `graph_rag` | Graph-based RAG |
| `language_models` | Language model utilities |
| `ollama_integration` | Ollama local LLM integration |

### Infrastructure (9)

| Rule | Purpose |
|------|---------|
| `cloud` | Multi-cloud provider integration |
| `orchestrator` | Workflow execution engine |
| `cache` | Caching strategies |
| `telemetry` | OpenTelemetry observability |
| `events` | Event-driven architecture |
| `api` | REST/GraphQL API infrastructure |
| `deployment` | Deployment automation |
| `networking` | HTTP clients, WebSocket |
| `database_management` | Database operations |

### Development Tools (14)

| Rule | Purpose |
|------|---------|
| `cli` | Command-line interface |
| `validation` | Data validation |
| `testing` | Test utilities, fixtures |
| `serialization` | JSON, MessagePack, protobuf |
| `coding` | Code manipulation, AST |
| `utils` | Common utilities |
| `skills` | Skill framework |
| `plugin_system` | Plugin architecture |
| `tree_sitter` | Syntax tree parsing |
| `ai_code_editing` | AI-assisted editing |
| `static_analysis` | Code quality analysis |
| `pattern_matching` | Pattern matching utilities |
| `config_management` | Configuration handling |
| `environment_setup` | Environment configuration |

### Metrics & Testing (5)

| Rule | Purpose |
|------|---------|
| `metrics` | Metrics collection |
| `workflow_testing` | E2E workflow tests |
| `prompt_testing` | LLM prompt evaluation |
| `logging_monitoring` | Logging and monitoring |
| `performance` | Performance optimization |

### Documentation & Build (5)

| Rule | Purpose |
|------|---------|
| `documentation` | Documentation standards |
| `api_documentation` | API doc generation |
| `build_synthesis` | Build processes |
| `data_visualization` | Visualization patterns |
| `module_template` | Module templates |

### Operations (7)

| Rule | Purpose |
|------|---------|
| `containerization` | Docker, containers |
| `ci_cd_automation` | CI/CD pipelines |
| `git_operations` | Git workflows |
| `terminal_interface` | Terminal utilities |
| `notification` | Multi-channel notifications |
| `market` | Marketplace functionality |
| `project_orchestration` | Project coordination |

### Specialized (6)

| Rule | Purpose |
|------|---------|
| `model_context_protocol` | MCP tools and resources |
| `modeling_3d` | 3D modeling utilities |
| `physical_management` | Physical asset tracking |
| `system_discovery` | System inspection |
| `security_audit` | Security audit tools |
| `code` | Code utilities |

## Rule Hierarchy

```
file-specific/ (highest priority)
    ↓
modules/ ← You are here (60 rules)
    ↓
cross-module/
    ↓
general.cursorrules (lowest priority)
```

## Companion Files

- [**AGENTS.md**](AGENTS.md) - Agent guidelines
- [**SPEC.md**](SPEC.md) - Functional specification

## Navigation

- **Parent**: [../README.md](../README.md)
- **Cross-Module**: [../cross-module/](../cross-module/)
- **File-Specific**: [../file-specific/](../file-specific/)
- **Project Root**: [../../README.md](../../README.md)
