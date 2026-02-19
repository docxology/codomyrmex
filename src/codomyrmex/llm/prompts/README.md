# prompts

**Version**: v0.1.7 | **Status**: Active | **Last Updated**: February 2026

## Overview

Prompt versioning, template management, and prompt engineering utilities. Provides a `PromptTemplate` class supporting variable substitution with defaults (`{var:default}`), conditionals (`{?var}...{/var}`), and validation of required variables. The `PromptBuilder` offers a fluent API for constructing multi-message prompts (system/user/assistant) outputting either API-compatible message lists or single strings. The `PromptRegistry` manages named templates with full version history, active-version selection, and JSON import/export.

## Key Exports

- **`PromptRole`** -- Enum of standard message roles (system, user, assistant, function, tool)
- **`Message`** -- Dataclass representing a single message with role, content, optional name, metadata, and `to_dict()` for API-compatible output
- **`PromptVersion`** -- Dataclass for a versioned prompt template with version string, template text, extracted variable names, creation timestamp, and content hash
- **`PromptTemplate`** -- Template engine with variable extraction, `render(**kwargs)` for substitution (supports defaults and conditionals), and `validate(**kwargs)` to check for missing required variables
- **`PromptBuilder`** -- Fluent builder for multi-message prompts with `system()`, `user()`, `assistant()`, `template()` methods and `build()` / `build_string()` output
- **`PromptRegistry`** -- Named template registry with version management, active-version tracking, `export_to_json()` / `import_from_json()` for persistence
- **`COMMON_TEMPLATES`** -- Dict of 5 pre-built `PromptTemplate` instances: code_review, summarize, translate, explain, json_output
- **`get_common_template()`** -- Look up a built-in template by name from `COMMON_TEMPLATES`

## Directory Contents

- `__init__.py` - All prompt logic: message model, template engine, fluent builder, versioned registry, common templates
- `README.md` - This file
- `AGENTS.md` - Agent integration notes
- `PAI.md` - PAI-specific documentation
- `SPEC.md` - Module specification
- `py.typed` - PEP 561 type-checking marker

## Navigation

- **Parent Module**: [llm](../README.md)
- **Project Root**: [../../../../README.md](../../../../README.md)
