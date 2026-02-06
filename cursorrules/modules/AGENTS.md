# Codomyrmex Agents — cursorrules/modules

**Version**: v0.2.0 | **Status**: Active | **Last Updated**: February 2026

## Purpose

Module-specific cursor rules (60 total) that supplement `general.cursorrules`. Each rule provides coding standards, testing requirements, and best practices for its respective source module.

## Agent Guidelines

### Rule Application

1. **Identify the module** you're working in (e.g., `security`, `agents`, `cloud`)
2. **Load the corresponding rule** from `modules/{module_name}.cursorrules`
3. **Apply rules in order**: file-specific → module-specific → cross-module → general

### Quick Module Lookup by Domain

| Domain | Key Modules |
|--------|-------------|
| **Security** | `security`, `defense`, `identity`, `wallet`, `privacy`, `encryption`, `auth` |
| **AI/Agents** | `agents`, `llm`, `agentic_memory`, `cerebrum`, `graph_rag` |
| **Infrastructure** | `cloud`, `orchestrator`, `cache`, `api`, `deployment`, `networking` |
| **Development** | `cli`, `testing`, `coding`, `utils`, `tree_sitter`, `static_analysis` |
| **Operations** | `containerization`, `ci_cd_automation`, `telemetry`, `metrics` |

### Standard Rule Template

All module rules follow this 8-section structure:
0. **Preamble** - Relationship to general.cursorrules

1. **Purpose & Context** - Core functionality
2. **Key Files & Structure** - Important files
3. **Coding Standards** - Language requirements
4. **Testing** - Test requirements
5. **Documentation** - Doc maintenance
6. **Specific Considerations** - Module-specific notes
7. **Final Check** - Verification steps

### When to Create New Rules

Create a new module rule when:

- A source module has unique coding requirements
- Module-specific testing patterns are needed
- Special security considerations apply
- Cross-cutting concerns don't cover the need

## Operating Contracts

- Module rules supplement (don't replace) general.cursorrules
- When conflicts occur, module rules take precedence
- Document any departures from general rules
- Ensure MCP interfaces remain consistent across modules

## Rule Categories Summary

| Category | Count | Examples |
|----------|-------|----------|
| Security & Identity | 7 | security, defense, identity |
| AI & Agents | 7 | agents, llm, cerebrum |
| Infrastructure | 9 | cloud, api, deployment |
| Development Tools | 14 | cli, testing, utils |
| Metrics & Testing | 5 | metrics, workflow_testing |
| Documentation & Build | 5 | documentation, build_synthesis |
| Operations | 7 | containerization, ci_cd_automation |
| Specialized | 6 | model_context_protocol, modeling_3d |
| **Total** | **60** | |

## Navigation Links

- **📁 Parent Directory**: [../README.md](../README.md) - cursorrules root
- **📄 File Rules**: [../file-specific/](../file-specific/) - 6 file-type rules
- **🔗 Cross-Module**: [../cross-module/](../cross-module/) - 8 cross-module rules
- **🏠 Project Root**: [../../README.md](../../README.md)
