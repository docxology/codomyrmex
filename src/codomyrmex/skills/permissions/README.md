# permissions

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

Skill capability permissions and access control. Manages a per-skill permission registry that tracks which actions each skill is authorized to perform. Supports granting, revoking, and querying individual or bulk permissions, enabling fine-grained access control over skill execution, modification, and deletion operations.

## Key Exports

- **`SkillPermissionManager`** -- Main permission manager for skills. Maintains an internal mapping of skill IDs to granted action sets. Methods: `check_permission()` tests if a specific action is allowed for a skill, `grant()` adds a single permission, `revoke()` removes a single permission, `list_permissions()` returns all permissions for a skill as a sorted list, `grant_all()` adds multiple permissions at once, and `revoke_all()` clears all permissions from a skill.

## Directory Contents

- `__init__.py` - SkillPermissionManager class with grant/revoke/check interface
- `README.md` - This file
- `SPEC.md` - Module specification
- `AGENTS.md` - Agent integration notes
- `PAI.md` - PAI algorithm context
- `py.typed` - PEP 561 typing marker

## Navigation

- **Parent Module**: [skills](../README.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
