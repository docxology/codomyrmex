# skills - Tests

## Overview

Test suite for the skills module, covering skill loading, syncing, registry, and management operations.

## Test Files

- `test_skill_loader.py` - Tests for SkillLoader
- `test_skill_sync.py` - Tests for SkillSync
- `test_skills_manager.py` - Tests for SkillsManager

## Running Tests

```bash
# Run all skills tests
pytest src/codomyrmex/skills/tests/

# Run specific test file
pytest src/codomyrmex/skills/tests/test_skill_loader.py

# Run with coverage
pytest src/codomyrmex/skills/tests/ --cov=codomyrmex.skills
```

