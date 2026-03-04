# Agentic Memory — Rules Submodule

**Version**: v0.3.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Hierarchical coding standards and automation rules for AI-assisted development across the Codomyrmex platform. Rules are organized by specificity level and applied in order of precedence.

This submodule exposes the 75 `.cursorrules` files via a Python API and three MCP tools, enabling AI agents to programmatically query which coding standards apply to any given file or module.

## Python API

```python
from codomyrmex.agentic_memory.rules import RuleEngine, RulePriority

engine = RuleEngine()

# Which rules apply when editing src/codomyrmex/agents/memory.py?
rule_set = engine.get_applicable_rules(
    file_path="memory.py",
    module_name="agentic_memory",
)
for rule in rule_set.resolved():  # FILE_SPECIFIC first, GENERAL last
    print(f"[{rule.priority.name}] {rule.name}")

# Get a specific module's rule
rule = engine.get_module_rule("agents")
section = rule.get_section(3)  # "Coding Standards & Practices for agents"
print(section.content)

# List all modules with rules
print(engine.list_module_names())  # ['agents', 'agentic_memory', 'cloud', ...]
```

## MCP Tools

Three tools are auto-discovered by the PAI MCP bridge:

| Tool | Description |
|------|-------------|
| `rules_list_modules` | List all module names with defined rules |
| `rules_get_module_rule` | Get the full rule for a specific module |
| `rules_get_applicable` | Get all applicable rules for a file/module context |

## Rule Hierarchy

Rules follow a specificity hierarchy (most specific wins):

| Priority | Category | Location | Count |
|----------|----------|----------|-------|
| 1 (Highest) | File-specific | `file-specific/` | 6 rules |
| 2 | Module-specific | `modules/` | 60 rules |
| 3 | Cross-module | `cross-module/` | 8 rules |
| 4 (Lowest) | General | `general.cursorrules` | 1 rule |
| | **Total** | | **75 rules** |

### Rule Index (auto-generated from filesystem scan)

<details>
<summary>Click to expand full rule index (75 rules)</summary>

| # | Category | Rule Name | File |
|---|----------|-----------|------|
| 1 | general | general | `general.cursorrules` |
| 2 | file-specific | CHANGELOG | `file-specific/CHANGELOG.cursorrules` |
| 3 | file-specific | README.md | `file-specific/README.md.cursorrules` |
| 4 | file-specific | SPEC | `file-specific/SPEC.cursorrules` |
| 5 | file-specific | json | `file-specific/json.cursorrules` |
| 6 | file-specific | python | `file-specific/python.cursorrules` |
| 7 | file-specific | yaml | `file-specific/yaml.cursorrules` |
| 8 | cross-module | build_synthesis | `cross-module/build_synthesis.cursorrules` |
| 9 | cross-module | data_visualization | `cross-module/data_visualization.cursorrules` |
| 10 | cross-module | logging_monitoring | `cross-module/logging_monitoring.cursorrules` |
| 11 | cross-module | model_context_protocol | `cross-module/model_context_protocol.cursorrules` |
| 12 | cross-module | output_module | `cross-module/output_module.cursorrules` |
| 13 | cross-module | pattern_matching | `cross-module/pattern_matching.cursorrules` |
| 14 | cross-module | static_analysis | `cross-module/static_analysis.cursorrules` |
| 15 | cross-module | template_module | `cross-module/template_module.cursorrules` |
| 16 | modules | agentic_memory | `modules/agentic_memory.cursorrules` |
| 17 | modules | agents | `modules/agents.cursorrules` |
| 18 | modules | ai_code_editing | `modules/ai_code_editing.cursorrules` |
| 19 | modules | api | `modules/api.cursorrules` |
| 20 | modules | api_documentation | `modules/api_documentation.cursorrules` |
| 21 | modules | auth | `modules/auth.cursorrules` |
| 22 | modules | build_synthesis | `modules/build_synthesis.cursorrules` |
| 23 | modules | cache | `modules/cache.cursorrules` |
| 24 | modules | cerebrum | `modules/cerebrum.cursorrules` |
| 25 | modules | ci_cd_automation | `modules/ci_cd_automation.cursorrules` |
| 26 | modules | cli | `modules/cli.cursorrules` |
| 27 | modules | cloud | `modules/cloud.cursorrules` |
| 28 | modules | code | `modules/code.cursorrules` |
| 29 | modules | coding | `modules/coding.cursorrules` |
| 30 | modules | config_management | `modules/config_management.cursorrules` |
| 31 | modules | containerization | `modules/containerization.cursorrules` |
| 32 | modules | data_visualization | `modules/data_visualization.cursorrules` |
| 33 | modules | database_management | `modules/database_management.cursorrules` |
| 34 | modules | defense | `modules/defense.cursorrules` |
| 35 | modules | deployment | `modules/deployment.cursorrules` |
| 36 | modules | documentation | `modules/documentation.cursorrules` |
| 37 | modules | encryption | `modules/encryption.cursorrules` |
| 38 | modules | environment_setup | `modules/environment_setup.cursorrules` |
| 39 | modules | events | `modules/events.cursorrules` |
| 40 | modules | git_operations | `modules/git_operations.cursorrules` |
| 41 | modules | graph_rag | `modules/graph_rag.cursorrules` |
| 42 | modules | identity | `modules/identity.cursorrules` |
| 43 | modules | language_models | `modules/language_models.cursorrules` |
| 44 | modules | llm | `modules/llm.cursorrules` |
| 45 | modules | logging_monitoring | `modules/logging_monitoring.cursorrules` |
| 46 | modules | market | `modules/market.cursorrules` |
| 47 | modules | metrics | `modules/metrics.cursorrules` |
| 48 | modules | model_context_protocol | `modules/model_context_protocol.cursorrules` |
| 49 | modules | modeling_3d | `modules/modeling_3d.cursorrules` |
| 50 | modules | module_template | `modules/module_template.cursorrules` |
| 51 | modules | networking | `modules/networking.cursorrules` |
| 52 | modules | notification | `modules/notification.cursorrules` |
| 53 | modules | ollama_integration | `modules/ollama_integration.cursorrules` |
| 54 | modules | orchestrator | `modules/orchestrator.cursorrules` |
| 55 | modules | pattern_matching | `modules/pattern_matching.cursorrules` |
| 56 | modules | performance | `modules/performance.cursorrules` |
| 57 | modules | physical_management | `modules/physical_management.cursorrules` |
| 58 | modules | plugin_system | `modules/plugin_system.cursorrules` |
| 59 | modules | privacy | `modules/privacy.cursorrules` |
| 60 | modules | project_orchestration | `modules/project_orchestration.cursorrules` |
| 61 | modules | prompt_testing | `modules/prompt_testing.cursorrules` |
| 62 | modules | security | `modules/security.cursorrules` |
| 63 | modules | security_audit | `modules/security_audit.cursorrules` |
| 64 | modules | serialization | `modules/serialization.cursorrules` |
| 65 | modules | skills | `modules/skills.cursorrules` |
| 66 | modules | static_analysis | `modules/static_analysis.cursorrules` |
| 67 | modules | system_discovery | `modules/system_discovery.cursorrules` |
| 68 | modules | telemetry | `modules/telemetry.cursorrules` |
| 69 | modules | terminal_interface | `modules/terminal_interface.cursorrules` |
| 70 | modules | testing | `modules/testing.cursorrules` |
| 71 | modules | tree_sitter | `modules/tree_sitter.cursorrules` |
| 72 | modules | utils | `modules/utils.cursorrules` |
| 73 | modules | validation | `modules/validation.cursorrules` |
| 74 | modules | wallet | `modules/wallet.cursorrules` |
| 75 | modules | workflow_testing | `modules/workflow_testing.cursorrules` |

</details>

## Mandatory Policies (Cannot Be Overridden)

These policies are defined in `general.cursorrules §2` and enforced at all levels:

| Policy | Summary |
|--------|---------|
| **Zero-Mock** | Never use mocks — real implementations, data factories, environment-gated tests |
| **UV-Only** | `pyproject.toml` + `uv sync` for all dependencies — no `pip install` or `requirements.txt` |
| **RASP** | Every directory needs `README.md`, `AGENTS.md`, `SPEC.md`, `PAI.md` |
| **Python ≥ 3.10** | All code compatible with Python 3.10+ |

## Directory Structure

```
src/codomyrmex/agentic_memory/rules/
├── __init__.py               # Public API (RuleEngine, RuleLoader, Rule, RuleSet, RulePriority)
├── engine.py                 # RuleEngine — hierarchy-aware resolution
├── loader.py                 # RuleLoader — parses .cursorrules files
├── registry.py               # RuleRegistry — indexed access by module/extension/cross-module
├── models.py                 # Rule, RuleSet, RulePriority, RuleSection dataclasses
├── mcp_tools.py              # MCP tools (rules_list_modules, rules_get_module_rule, rules_get_applicable)
├── general.cursorrules       # Universal coding standards + mandatory policies
├── cross-module/             # Rules for cross-cutting concerns (8 rules)
│   ├── logging_monitoring.cursorrules
│   ├── model_context_protocol.cursorrules
│   ├── static_analysis.cursorrules
│   └── ... (5 more)
├── file-specific/            # Rules for specific file types (6 rules)
│   ├── python.cursorrules
│   ├── yaml.cursorrules
│   ├── json.cursorrules
│   └── ... (3 more)
└── modules/                  # Module-specific rules (60 rules)
    ├── security.cursorrules
    ├── agents.cursorrules
    ├── cloud.cursorrules
    └── ... (57 more)
```

## Standard Rule Template (8 Sections)

All `.cursorrules` files follow this structure:
0. **Preamble**: Relationship to general.cursorrules

1. **Purpose & Context**: Core functionality, key technologies
2. **Key Files & Structure**: Important files to monitor
3. **Coding Standards**: Language and style requirements
4. **Testing**: Test requirements and strategies (Zero-Mock enforced)
5. **Documentation**: Documentation maintenance (RASP enforced)
6. **Specific Considerations**: Module-specific notes
7. **Final Check**: Verification steps before finalizing

## Quick Reference

| Need | File |
|------|------|
| Python code standards | `file-specific/python.cursorrules` |
| Security guidelines | `modules/security.cursorrules` |
| Logging patterns | `cross-module/logging_monitoring.cursorrules` |
| MCP tool specs | `cross-module/model_context_protocol.cursorrules` |
| General principles + policies | `general.cursorrules` |

## Companion Files

- [**AGENTS.md**](AGENTS.md) - AI agent guidelines for rule application
- [**SPEC.md**](SPEC.md) - Functional specification with architecture diagram
- [**PAI.md**](PAI.md) - Personal AI Infrastructure context

## Navigation

- **Parent Module**: [../README.md](../README.md) — Agentic Memory module
- **Source Code**: [../](../) — agentic_memory/ package root
- **Documentation**: [../../../../../docs/](../../../../../docs/)
