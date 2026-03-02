# Query Building -- Technical Specification

**Version**: v1.0.0 | **Status**: Active | **Last Updated**: March 2026

## Overview

Reserved sub-module for reusable tree-sitter S-expression query patterns and a programmatic query builder. Currently empty; query execution lives in `TreeSitterParser.query()`.

## Architecture

Planned: catalog of pre-built `.scm` query strings (functions, classes, imports, decorators) loadable by name. The query builder will compose S-expressions programmatically.

## Dependencies

- **Internal**: none currently
- **External**: `tree_sitter` query API

## Constraints

- Query strings must be valid tree-sitter S-expressions.
- All query results return lists of `(node, capture_name)` tuples.
- Zero-mock: real tree-sitter query execution required.
