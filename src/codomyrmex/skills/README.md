# Skills

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: January 2026

## Overview
The `skills` module manages the "Knowledge" and "Capabilities" of agents within the Codomyrmex system. A specialized subsystem separate from general plugins, Skills represent targeted task instruction sets (like "How to debug a react app" or "How to configure Nginx"). This module handles the loading, validation, and synchronization of these instruction sets into the agent's context window.

## Key Features
- **Skill Definitions**: Manages standard formats for skill instructions (typically markdown + code).
- **Registry**: `skill_registry.py` provides a searchable index of available skills.
- **Dynamic Loading**: `skill_loader.py` retrieves skill content on demand.
- **Synchronization**: `skill_sync.py` ensures local skill definitions match remote or shared repositories.
- **Validation**: `skill_validator.py` ensures skill files meet clarity and safety standards.

## Quick Start

```python
from codomyrmex.skills.skills_manager import SkillsManager

manager = SkillsManager(library_path="./skills_lib")

# List available skills
skills = manager.list_skills()
print(f"Available: {[s.name for s in skills]}")

# Load a specific skill for an agent
debug_skill = manager.load_skill("python_debugging")
agent.add_context(debug_skill.content)
```

## Module Structure

- `skills_manager.py`: Main entry point for skill operations.
- `skill_loader.py`: File I/O and parsing logic.
- `skill_registry.py`: In-memory storage of loaded skills.
- `skill_validator.py`: Quality assurance for skill content.
- `skill_sync.py`: Update logic for skill repositories.

## Navigation Links
- **Technical Documentation**: [AGENTS.md](AGENTS.md)
- **Functional Specification**: [SPEC.md](SPEC.md)
- **MCP Tool Specification**: [MCP_TOOL_SPECIFICATION.md](MCP_TOOL_SPECIFICATION.md)
- **📁 Parent Directory**: [codomyrmex](../README.md)
- **🏠 Project Root**: [README](../../../README.md)
