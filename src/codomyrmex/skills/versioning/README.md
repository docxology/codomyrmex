# versioning

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

Skill version management and compatibility tracking. Provides semver-like version parsing, major-version compatibility checking between a skill's current version and a required version, and a version history registry for tracking all known versions of each skill over time.

## Key Exports

- **`SkillVersionManager`** -- Main version manager for skills. Maintains a version history registry keyed by skill ID. Methods: `get_version()` extracts the current version string from a skill instance or dict (defaults to "0.0.0"), `check_compatibility()` performs major-version semver compatibility checking and returns a dict with compatible (bool), current_version, and required_version, `list_versions()` returns all registered versions for a skill, and `register_version()` records a new version in the history.
- **`parse_version()`** -- Parses a semver-like version string (e.g., "1.2.3") into a tuple of integers for comparison.

## Directory Contents

- `__init__.py` - SkillVersionManager class and parse_version utility function
- `README.md` - This file
- `SPEC.md` - Module specification
- `AGENTS.md` - Agent integration notes
- `PAI.md` - PAI algorithm context
- `py.typed` - PEP 561 typing marker

## Navigation

- **Parent Module**: [skills](../README.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
