# AST Transformers -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Placeholder submodule for AST transformation and visitor pattern utilities. Intended to provide tools for walking, modifying, and transforming parsed syntax trees produced by the tree-sitter parser.

## Architecture

This submodule is currently a namespace placeholder. The `__init__.py` exports an empty `__all__` list. AST traversal is currently handled by callers using tree-sitter's native node traversal API directly.

## Current State

- `__init__.py`: Module docstring ("AST transformation and visitors") and empty `__all__` -- no transformer classes implemented yet.
- Future scope: visitor base class, node transformation pipeline, and code generation from modified trees.

## Planned Interface

When implemented, the module would expose:

| Class / Function | Purpose |
|-----------------|---------|
| `ASTVisitor` | Base class implementing the visitor pattern for tree-sitter nodes |
| `ASTTransformer` | Visitor subclass that returns modified nodes for tree rewriting |
| `NodeFilter` | Predicate-based node selection for targeted transformations |
| `CodeGenerator` | Reconstruct source code from a (possibly modified) syntax tree |

## Dependencies

- **Internal**: `tree_sitter.parsers` (provides parsed trees), `tree_sitter.queries` (node selection)
- **External**: `tree_sitter` (node traversal API)

## Constraints

- Not yet implemented; importing yields an empty namespace.
- Tree-sitter trees are immutable in the native API; "transformation" typically means generating new source text rather than mutating the tree in place.
- Zero-mock: `NotImplementedError` for unimplemented paths.

## Navigation

- [README.md](README.md) | [AGENTS.md](AGENTS.md)
- Parent: [tree_sitter](../README.md)
