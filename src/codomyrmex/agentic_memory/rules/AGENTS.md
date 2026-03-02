# Agentic Memory — Rules Submodule

**Version**: v0.3.0 | **Status**: Active | **Last Updated**: March 2026

## Purpose

Coding standards and automation rules for consistent code quality across the repository, now exposed as a Python module and MCP tools. Defines style guidelines, naming conventions, mandatory policies, and automated checks for AI-assisted development. AI agents can query applicable rules programmatically via `RuleEngine` or the three MCP tools.

## Directory Structure

```
src/codomyrmex/agentic_memory/rules/   # 75 rules + Python API
├── engine.py                           # RuleEngine — hierarchy-aware rule resolution
├── loader.py                           # RuleLoader — parses .cursorrules files
├── registry.py                         # RuleRegistry — indexed access by module/extension
├── models.py                           # Rule, RuleSet, RulePriority, RuleSection
├── mcp_tools.py                        # rules_list_modules, rules_get_module_rule, rules_get_applicable
├── __init__.py                         # Public API
├── general.cursorrules                 # Universal coding standards (1)
├── cross-module/                       # Cross-cutting concerns (8)
├── file-specific/                      # File type specific rules (6)
└── modules/                            # Per-module standards (60)
```

## Active Components

### Python API

| Component | Type | Description |
|-----------|------|-------------|
| `RuleEngine` | Class | Hierarchy-aware rule resolution; primary entry point |
| `RuleLoader` | Class | Parses `.cursorrules` files into `Rule` objects |
| `RuleRegistry` | Class | Indexed access by module name, file extension, cross-module |
| `Rule` | Dataclass | Parsed representation of one `.cursorrules` file |
| `RuleSet` | Dataclass | Collection of applicable rules; sortable by priority |
| `RulePriority` | Enum | `FILE_SPECIFIC=1 > MODULE=2 > CROSS_MODULE=3 > GENERAL=4` |
| `RuleSection` | Dataclass | One numbered section (§0–§7) from a rule file |

### MCP Tools (auto-discovered)

| Tool | Description |
|------|-------------|
| `rules_list_modules` | List all 60 module names with defined rules |
| `rules_get_module_rule` | Get full rule dict for a specific module |
| `rules_get_applicable` | Get all applicable rules for a file path and/or module, ordered highest priority first |

### Rule Files

| Component | Type | Description |
|-----------|------|-------------|
| `general.cursorrules` | Rules | Universal coding standards + mandatory policies |
| `cross-module/` | Directory | Cross-cutting concerns (8 rules) |
| `file-specific/` | Directory | File type specific rules (6 rules) |
| `modules/` | Directory | Per-module overrides (60 rules) |

## Rule Hierarchy

Rules follow a specificity hierarchy (most specific wins):

1. **File-specific** (`file-specific/`) — Rules for specific file patterns
2. **Module-specific** (`modules/`) — Per-module overrides
3. **Cross-module** (`cross-module/`) — Cross-cutting patterns
4. **General** (`general.cursorrules`) — Universal defaults

## Mandatory Policies

These policies are enforced globally and **cannot be overridden** by any rule level:

| Policy | Description |
|--------|-------------|
| **Zero-Mock** | Never use mocks, MagicMock, or test doubles — use real implementations |
| **UV-Only** | All dependencies via `pyproject.toml` + `uv sync` — never `pip install` |
| **RASP** | Every directory needs README.md, AGENTS.md, SPEC.md, PAI.md |
| **Python ≥ 3.10** | All code must be compatible with Python 3.10+ |
| **Type hints** | All functions must have type annotations |
| **Docstrings** | All public APIs must have Google-style docstrings |

## Agent Guidelines

### Using the Python API

```python
from codomyrmex.agentic_memory.rules import RuleEngine

engine = RuleEngine()

# Get all applicable rules when editing a Python file in the agents module
rule_set = engine.get_applicable_rules(
    file_path="memory.py",
    module_name="agentic_memory",
)
for rule in rule_set.resolved():  # FILE_SPECIFIC first, GENERAL last
    print(f"[{rule.priority.name}] {rule.name}")
    section = rule.get_section(3)  # "Coding Standards"
    if section:
        print(section.content[:200])
```

### Using MCP Tools

```
rules_get_applicable(file_path="memory.py", module_name="agentic_memory")
→ Returns list of rule dicts, FILE_SPECIFIC first

rules_get_module_rule(module_name="agents")
→ Returns full rule dict with sections and raw_content

rules_list_modules()
→ Returns sorted list of 60 module names
```

### Coding Standards

1. **Python**: PEP 8, type hints, Google-style docstrings
2. **Naming**: snake_case for variables/functions, PascalCase for classes
3. **Imports**: Group by standard library, third-party, local
4. **Dependencies**: Add via `uv add <package>` — never edit `pyproject.toml` manually for deps

### Testing Standards

1. **Zero-Mock**: Use real data factories, environment-gated tests, simulation modes
2. **Execution**: Run via `uv run pytest` — never raw `pytest`
3. **External Services**: Gate behind `@pytest.mark.skipif(not os.getenv("API_KEY"))`
4. **File Operations**: Use `tmp_path` fixture with real filesystem operations
5. **Rules tests**: Use real `.cursorrules` files from the `rules/` directory — no mocking

### When Modifying Rules

- Document rationale for rule changes
- Ensure backward compatibility where possible
- Test rules against existing codebase
- Update related documentation
- Never weaken mandatory policies (Zero-Mock, UV, RASP)

## Operating Contracts

- Rules apply to all code modifications
- Mandatory policies cannot be overridden at any level
- Ensure Model Context Protocol interfaces remain available for sibling agents
- Conflicts resolved by specificity hierarchy (except mandatory policies)
- Document exceptions with rationale

## Navigation Links

- **Parent**: [../README.md](../README.md) - Agentic Memory module
- **PAI Context**: [PAI.md](PAI.md) - AI infrastructure context
- **Spec**: [SPEC.md](SPEC.md) - Functional specification
- **Human Docs**: [README.md](README.md) - User documentation
