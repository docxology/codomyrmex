# tree_sitter

**Version**: v0.1.0 | **Status**: Active | **Last Updated**: February 2026

## Overview

The tree_sitter module provides high-fidelity source code parsing across multiple programming languages using the tree-sitter parsing library. It wraps the tree-sitter `Parser` and `Language` APIs for syntax tree construction, pattern-based querying via S-expression queries, and code transformation -- enabling advanced static analysis, refactoring, and intelligent code auditing within the Codomyrmex ecosystem.

## Key Exports

- **`TreeSitterParser`** -- Wrapper around tree-sitter's `Parser` class. Accepts a language instance, parses source code strings into syntax trees via `parse()`, and executes S-expression queries against trees via `query()` to capture matching nodes.
- **`LanguageManager`** -- Manages tree-sitter language libraries. Provides `load_language()` to load languages from shared libraries (.so/.dll/.dylib), `get_language()` to retrieve loaded instances, and `discover_languages()` to auto-detect all language libraries in a directory.
- **`parsers`** -- Submodule containing the `TreeSitterParser` implementation
- **`languages`** -- Submodule containing `LanguageManager` for multi-language support
- **`queries`** -- Submodule for S-expression query definitions and tree pattern matching
- **`transformers`** -- Submodule for syntax tree transformations and code rewriting

## Directory Contents

- `__init__.py` - Module entry point; exports parser, language manager, and submodules
- `parsers/` - Parser implementation (`parser.py`) wrapping tree-sitter's core `Parser`
- `languages/` - Language management (`languages.py`) for loading and discovering language grammars
- `queries/` - S-expression query definitions for structural code pattern matching
- `transformers/` - Syntax tree transformation utilities for code rewriting
- `AGENTS.md` - Agent integration specification
- `API_SPECIFICATION.md` - Programmatic interface documentation
- `SPEC.md` - Module specification
- `PAI.md` - PAI integration notes

## Navigation

- **Full Documentation**: [docs/modules/tree_sitter/](../../../docs/modules/tree_sitter/)
- **Parent Directory**: [codomyrmex](../README.md)
- **Project Root**: ../../../README.md
