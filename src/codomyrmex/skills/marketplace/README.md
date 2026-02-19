# marketplace

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

Skill discovery and installation from external sources and repositories. Provides a marketplace client that manages a registry of remote skill sources (defaulting to the vibeship-spawner-skills GitHub repository), supports searching remote sources for skills by query, installing skills by ID from a named source, and adding or removing custom source configurations.

## Key Exports

- **`SkillMarketplace`** -- Main marketplace client for remote skill discovery and installation. Manages a list of source configurations (each with name, URL, and type). Methods: `search_remote()` searches sources for skills matching a query, `install()` installs a skill by ID from a source, `list_sources()` returns all configured sources, `add_source()` registers a new remote source, and `remove_source()` removes a source by name.

## Directory Contents

- `__init__.py` - SkillMarketplace class with source management and search/install interface
- `README.md` - This file
- `SPEC.md` - Module specification
- `AGENTS.md` - Agent integration notes
- `PAI.md` - PAI algorithm context
- `py.typed` - PEP 561 typing marker

## Navigation

- **Parent Module**: [skills](../README.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
