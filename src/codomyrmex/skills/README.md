# Skills Module

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

Integration with the [vibeship-spawner-skills](https://github.com/vibeforge1111/vibeship-spawner-skills) repository, providing access to 462+ specialized skills organized across 35 categories. Enables skill management, syncing with upstream, custom skill overrides, and a programmatic discovery framework for building and registering new skills.

## Features

- **Upstream Sync**: Clone and pull the vibeship-spawner-skills repository via git
- **YAML Skill Loading**: Parse skill definitions with merge logic (custom overrides upstream)
- **Skill Registry**: Index, categorize, and search skills by text, regex, or category
- **Skill Validation**: Validate YAML skill files against expected schema
- **Discovery Framework**: Define skills programmatically using ABCs, decorators, and registries
- **Execution Engine**: Run skills with error handling, timeouts, and chaining
- **Composition Patterns**: Chain, parallelize, and conditionally branch skill execution
- **Testing Framework**: Validate, benchmark, and run test cases against skills
- **Marketplace**: Discover and install skills from remote sources
- **Versioning**: Track skill versions and check compatibility
- **Permissions**: Manage access control for skill actions

## Quick Start

```python
from codomyrmex.skills import get_skills_manager

# Initialize with upstream sync
manager = get_skills_manager(auto_sync=True)
manager.initialize()

# List and search skills
skills = manager.list_skills(category="backend")
results = manager.search_skills("authentication")

# Get a specific skill
skill = manager.get_skill("backend", "api-design")
```

### Programmatic Skills with Discovery

```python
from codomyrmex.skills.discovery import skill, SkillCategory, SkillRegistry

registry = SkillRegistry()

@skill(name="summarize", category=SkillCategory.REASONING, registry=registry)
def summarize_text(text: str, max_length: int = 100) -> str:
    """Summarize input text."""
    return text[:max_length]

# Execute via registry
result = registry.execute(summarize_text.metadata.id, text="Hello world", max_length=5)
```

## Core Components

| Component | File | Purpose |
|---|---|---|
| `SkillsManager` | `skills_manager.py` | Main interface for all skill operations |
| `SkillLoader` | `skill_loader.py` | YAML loading with merge logic |
| `SkillSync` | `skill_sync.py` | Git synchronization with upstream |
| `SkillRegistry` | `skill_registry.py` | Indexing, search, and categorization |
| `SkillValidator` | `skill_validator.py` | Schema validation of YAML files |
| `get_skills_manager()` | `__init__.py` | Factory function for configured manager |

## Submodules

| Submodule | Purpose |
|---|---|
| `discovery/` | ABC-based skill framework with decorators and runtime registry |
| `execution/` | Skill execution with error handling, timeouts, chaining |
| `composition/` | Skill composition patterns (chain, parallel, conditional) |
| `testing/` | Test runner, validation, and benchmarking framework |
| `marketplace/` | Remote skill source discovery and installation |
| `versioning/` | Version tracking and compatibility checking |
| `permissions/` | Access control for skill actions |

## Directory Structure

```
src/codomyrmex/skills/
├── __init__.py              # Module exports, factory function
├── skills_manager.py        # Main SkillsManager class
├── skill_loader.py          # YAML loading and merge logic
├── skill_sync.py            # Git-based upstream sync
├── skill_registry.py        # Indexing and search
├── skill_validator.py       # Schema validation
├── discovery/               # Programmatic skill framework
├── execution/               # Runtime execution engine
├── composition/             # Composition patterns
├── testing/                 # Testing framework
├── marketplace/             # Remote sources
├── versioning/              # Version management
├── permissions/             # Access control
├── API_SPECIFICATION.md     # Full API reference
├── MCP_TOOL_SPECIFICATION.md # MCP tool definitions
├── SPEC.md                  # Functional specification
└── README.md                # This file
```

## Navigation

- **Full Documentation**: [docs/modules/skills/](../../../docs/modules/skills/)
- **API Specification**: [API_SPECIFICATION.md](API_SPECIFICATION.md)
- **MCP Tools**: [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md)
- **Functional Spec**: [SPEC.md](SPEC.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
