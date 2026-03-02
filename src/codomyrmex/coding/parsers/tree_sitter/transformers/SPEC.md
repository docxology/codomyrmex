# AST Transformers -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Reserved sub-module for syntax-aware code transformations. Will provide a visitor/rewriter framework for applying structural modifications to tree-sitter parse trees while preserving formatting.

## Architecture

Planned: Visitor pattern. A base `ASTTransformer` class will walk a `tree_sitter.Tree`, apply node-level transformations, and emit modified source text.

## Dependencies

- **Internal**: `parsers.tree_sitter.parsers` (for tree generation)
- **External**: `tree_sitter`

## Constraints

- Transformations must produce syntactically valid output.
- Source formatting outside the transformation scope must be preserved.
- Zero-mock: real tree-sitter trees required for transformation.
