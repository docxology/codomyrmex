# Skills Module API Specification

**Version**: v0.1.0 | **Status**: Stable | **Last Updated**: January 2026

## 1. Overview
The `skills` module integrates the vibeship-spawner-skills repository, allowing agents to discover, load, and synchronize executable skills dynamically.

## 2. Core Components

### 2.1 Management
- **`SkillsManager`**: Front-end for all skill operations.
- **`get_skills_manager(...) -> SkillsManager`**: Factory function.

### 2.2 Internals
- **`SkillSync`**: Handles git-based synchronization with upstream repositories.
- **`SkillLoader`**: Loads skill definitions from disk.
- **`SkillRegistry`**: Runtime index of available skills.

## 3. Usage Example

```python
from codomyrmex.skills import get_skills_manager

# Initialize manager (optionally syncing from upstream)
manager = get_skills_manager(auto_sync=True)

# List available skills
skills = manager.list_skills()

# Load a specific skill
skill = manager.get_skill("python_expert")
```
