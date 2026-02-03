# Codomyrmex Agents — docs/modules

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Comprehensive documentation hub for all 80+ Codomyrmex modules. Provides API specifications, usage guides, tutorials, and integration patterns for every module in the system.

## Key Documentation Files

| File | Description | Priority |
|------|-------------|----------|
| [overview.md](overview.md) | Complete module system overview | High |
| [relationships.md](relationships.md) | Inter-module dependencies | High |
| [dependency-graph.md](dependency-graph.md) | Visual dependency graph | Medium |
| [ollama_integration.md](ollama_integration.md) | Local LLM integration | Medium |

## Module Categories

### 🏗️ Foundation (High Priority)

- [logging_monitoring/](logging_monitoring/) - Centralized logging
- [environment_setup/](environment_setup/) - Environment validation
- [config_management/](config_management/) - Configuration management
- [model_context_protocol/](model_context_protocol/) - MCP implementation

### 🤖 AI & Intelligence

- [agents/](agents/) - AI agent framework
- [cerebrum/](cerebrum/) - Case-based reasoning
- [llm/](llm/) - LLM provider abstraction
- [skills/](skills/) - Skills framework

### 🛡️ Secure Cognitive (New)

- `identity/` - 3-Tier personas, bio-verification
- `wallet/` - Self-custody, Natural Ritual recovery
- `defense/` - Active defense, rabbit holes
- `market/` - Reverse auctions, demand aggregation
- `privacy/` - Crumb scrubbing, mixnet routing

> **Source**: [src/codomyrmex/identity/](../../src/codomyrmex/identity/), [wallet/](../../src/codomyrmex/wallet/), [defense/](../../src/codomyrmex/defense/), [market/](../../src/codomyrmex/market/), [privacy/](../../src/codomyrmex/privacy/)

### 📊 Analysis & Visualization

- [static_analysis/](static_analysis/) - Code quality analysis
- [pattern_matching/](pattern_matching/) - Code patterns
- [data_visualization/](data_visualization/) - Charts and plots
- [coding/](coding/) - Safe code execution

### 🔧 Build & Deploy

- [build_synthesis/](build_synthesis/) - Build automation
- [ci_cd_automation/](ci_cd_automation/) - CI/CD pipelines
- [containerization/](containerization/) - Container management
- [git_operations/](git_operations/) - Git automation

### 🌐 Service & Integration

- [orchestrator/](orchestrator/) - Workflow orchestration
- [api/](api/) - API infrastructure
- [events/](events/) - Event system
- [plugin_system/](plugin_system/) - Plugin architecture

## Agent Quality Standards

1. **Documentation Completeness**: Each module docs folder should have README.md, AGENTS.md, SPEC.md
2. **Accuracy**: Documentation must match current source code implementations
3. **Examples**: Include working code examples for all key features
4. **Navigation**: Maintain proper links to source and related modules

## Operating Contracts

- Keep documentation synchronized with source code changes
- Ensure Model Context Protocol tool specs are documented
- Update module relationships when dependencies change
- Record new modules in overview.md and relationships.md

## Navigation Links

- **📁 Parent**: [docs/](../README.md)
- **🏠 Root**: [../../README.md](../../README.md)
- **📦 Source**: [src/codomyrmex/](../../src/codomyrmex/)
