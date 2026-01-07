# skills

## Signposting
- **Parent**: [codomyrmex](../README.md)
- **Children**:
    - [docs](docs/README.md)
    - [tests](tests/README.md)
- **Key Artifacts**:
    - [Agent Guide](AGENTS.md)
    - [Functional Spec](SPEC.md)

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview

Integration with the [vibeship-spawner-skills](https://github.com/vibeforge1111/vibeship-spawner-skills) repository, providing access to 462+ specialized skills organized across 35 categories. Enables skill management, syncing with upstream, and support for custom skills that can override upstream skills.

## Directory Contents
- `__init__.py` – Module exports and public API
- `skills_manager.py` – Main skill management interface
- `skill_loader.py` – YAML skill loading and parsing
- `skill_sync.py` – Git sync with upstream repository
- `skill_registry.py` – Skill discovery and indexing
- `skill_validator.py` – YAML schema validation
- `AGENTS.md` – Technical documentation
- `README.md` – This file
- `SPEC.md` – Functional specification
- `tests/` – Test suite
- `docs/` – Additional documentation

## Navigation
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: [README](../../../README.md)

## Getting Started

### Basic Usage

```python
from codomyrmex.skills import get_skills_manager

# Initialize skills manager
manager = get_skills_manager()
manager.initialize()

# List all skills
skills = manager.list_skills()
print(f"Found {len(skills)} skills")

# Get a specific skill
skill = manager.get_skill("backend", "api-design")
if skill:
    print(f"Skill: {skill.get('description', 'No description')}")

# Search skills
results = manager.search_skills("authentication")
for result in results:
    print(f"{result['category']}/{result['name']}")
```

### Syncing with Upstream

```python
# Manual sync
manager.sync_upstream()

# Force re-clone
manager.sync_upstream(force=True)

# Check upstream status
status = manager.get_upstream_status()
print(f"Upstream exists: {status['exists']}")
print(f"Last commit: {status.get('last_commit')}")
```

### Custom Skills

```python
# Add a custom skill (overrides upstream)
custom_skill = {
    "description": "My custom skill",
    "patterns": [
        {
            "name": "Custom Pattern",
            "description": "A custom pattern",
        }
    ]
}

manager.add_custom_skill("my-category", "my-skill", custom_skill)

# Custom skills automatically override upstream
skill = manager.get_skill("my-category", "my-skill")
```

### CLI Usage

```bash
# Sync with upstream
codomyrmex skills sync

# List all skills
codomyrmex skills list

# List skills in a category
codomyrmex skills list backend

# Get a specific skill
codomyrmex skills get backend api-design

# Search skills
codomyrmex skills search authentication
```

## Features

- **Upstream Integration**: Clone and sync with vibeship-spawner-skills repository
- **Custom Skills**: Add custom skills that override upstream
- **Skill Discovery**: Search and browse 462+ skills across 35 categories
- **Merge Logic**: Custom skills automatically override upstream with same name
- **Caching**: Optional caching for improved performance
- **MCP Tools**: Model Context Protocol integration for AI agents
- **CLI Commands**: Command-line interface for skill management

## Skill Categories

Skills are organized into 35 categories including:
- `ai-agents` - Autonomous agents and automation
- `backend` - APIs, microservices, queues
- `frontend` - React, mobile, state management
- `devops` - CI/CD, Docker, Kubernetes
- `security` - Auth, OWASP, compliance
- And 30+ more categories

See the [vibeship-spawner-skills repository](https://github.com/vibeforge1111/vibeship-spawner-skills) for the complete list.

